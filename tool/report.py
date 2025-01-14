import psutil
import time
import subprocess
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

import csv
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.dates import DateFormatter

from tool.send import send_email

load_dotenv()

# 서버 구분을 위한 이름 설정
SERVER_NAME = os.environ.get('SERVER_NAME')

# 이전 상태와 마지막 알림 시간을 저장할 전역 변수
last_alert_status = {
    "cpu": {"alerted": False, "last_sent": None},
    "memory": {"alerted": False, "last_sent": None},
    "disk": {"alerted": False, "last_sent": None},
}

# 알림 재발송 간격
ALERT_INTERVAL = timedelta(hours=6)

# 파일 경로
CSV_FILE_PATH = 'log.csv'
IMG_SAVE_PATH = 'report.png'

# GPU 상태 확인 함수
def get_gpu_status():
    try:
        result = subprocess.run(['nvidia-smi', '--query-gpu=memory.used,memory.total,utilization.gpu', '--format=csv,noheader,nounits'],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            gpu_data = result.stdout.strip().split('\n')
            gpu_status = []
            for gpu in gpu_data:
                used_memory, total_memory, utilization = map(int, gpu.split(','))
                
                used_memory_gb = used_memory / 1024
                used_memory_gb_rounded = round(used_memory_gb, 2)
                
                total_memory_gb = total_memory / 1024
                total_memory_gb_rounded = round(total_memory_gb, 2)
                
                percentage = (used_memory_gb / total_memory_gb) * 100
                percentage_rounded = round(percentage, 1)
                
                gpu_status.append({
                    'used_memory': used_memory_gb_rounded,
                    'total_memory': total_memory_gb_rounded,
                    'memory_percent': percentage_rounded,
                    'utilization': utilization
                })
            return gpu_status
    except FileNotFoundError:
        return None  # GPU가 없는 경우
    
# 색상 설정 함수
def get_color(value):
    if value > 80:
        return "red"
    elif value > 50:
        return "orange"
    else:
        return "green"

# 하루 1번 실행 (전체 보고)
def daily_report():
    now = datetime.now()
    
    if not os.path.exists(CSV_FILE_PATH):
        print("No data available for the report.")
        return
    
    # CSV 데이터 읽기
    data = pd.read_csv(CSV_FILE_PATH)
    data['timestamp'] = pd.to_datetime(data['timestamp'])
    
    # GPU 관련 열 추출
    gpu_utilization_columns = [col for col in data.columns if 'gpu_' in col and '_utilization' in col]
    gpu_memory_columns = [col for col in data.columns if 'gpu_' in col and '_memory_usage' in col]

    # 그래프 수 계산 (기본 CPU, 메모리, 디스크 + 각 GPU 별 1개씩)
    num_graphs = 3 + len(gpu_utilization_columns)

    # 그래프 생성
    fig, ax = plt.subplots(num_graphs, 1, figsize=(14, 5 * num_graphs))
    
    # 전체 제목 설정
    fig.suptitle(f"[{SERVER_NAME}] Server Status Report({now.strftime('%Y-%m-%d')})", fontsize=28)
    
    # DateFormatter를 사용하여 시간만 표시)
    time_format = DateFormatter('%H:%M')
    
    # CPU 그래프
    ax[0].plot(data['timestamp'], data['cpu_usage'], label='CPU Usage (%)', color=sns.color_palette()[0], linewidth=2)
    ax[0].set_title('CPU Usage Over Time', fontsize=16)
    ax[0].set_xlabel('Time')
    ax[0].set_ylabel('Usage (%)')
    ax[0].legend(loc='upper right')
    ax[0].xaxis.set_major_formatter(time_format)
    ax[0].set_ylim(0, 100)
    
    # 메모리 그래프
    ax[1].plot(data['timestamp'], data['memory_usage'], label='Memory Usage (%)', color=sns.color_palette()[1], linewidth=2)
    ax[1].set_title('Memory Usage Over Time', fontsize=16)
    ax[1].set_xlabel('Time')
    ax[1].set_ylabel('Usage (%)')
    ax[1].legend(loc='upper right')
    ax[1].xaxis.set_major_formatter(time_format)
    ax[1].set_ylim(0, 100)
    
    # 디스크 그래프
    ax[2].plot(data['timestamp'], data['disk_usage'], label='Disk Usage (%)', color=sns.color_palette()[2], linewidth=2)
    ax[2].set_title('Disk Usage Over Time', fontsize=16)
    ax[2].set_xlabel('Time')
    ax[2].set_ylabel('Usage (%)')
    ax[2].legend(loc='upper right')
    ax[2].xaxis.set_major_formatter(time_format)
    ax[2].set_ylim(0, 100)
    
    # GPU 그래프
    for idx, (gpu_util, gpu_mem) in enumerate(zip(gpu_utilization_columns, gpu_memory_columns), start=3):
        gpu_id = gpu_util.split('_')[1]  # GPU ID 추출
        ax[idx].plot(data['timestamp'], data[gpu_util], label=f'GPU {gpu_id} Utilization (%)', color=sns.color_palette()[3], linewidth=2)
        ax[idx].plot(data['timestamp'], data[gpu_mem], label=f'GPU {gpu_id} Memory Usage (%)', color=sns.color_palette()[0], linewidth=2)
        ax[idx].set_title(f'GPU {gpu_id} Usage Over Time', fontsize=16)
        ax[idx].set_xlabel('Time')
        ax[idx].set_ylabel('Usage (%)')
        ax[idx].legend(loc='upper right')
        ax[idx].xaxis.set_major_formatter(time_format)
        ax[idx].set_ylim(0, 100)
    
    plt.tight_layout(rect=[0, 0, 1, 0.97])
    plt.subplots_adjust(hspace=0.4)
    
    # 그래프를 이미지로 저장
    plt.savefig(IMG_SAVE_PATH, format='png', bbox_inches='tight')
    plt.close()
    
    # CSV 삭제
    os.remove(CSV_FILE_PATH)
    
    # 메모리, CPU, GPU 정보 가져오기
    memory = psutil.virtual_memory()
    cpu_percent = psutil.cpu_percent(interval=1)
    gpu_status = get_gpu_status()
    
    # 디스크 정보 가져오기 (루트 디렉토리 기준)
    disk = psutil.disk_usage('/')
    
    # 메모리 사용량 (GB)
    total_memory_gb = memory.total / (1024 ** 3)
    used_memory_gb = memory.used / (1024 ** 3)
    
    # 디스크 사용량 (GB)
    total_disk_gb = disk.total / (1024 ** 3)
    used_disk_gb = disk.used / (1024 ** 3)
    
    body = f"""
<html>
    <body>
        <p><span style="font-weight: bold;">[{SERVER_NAME}] Daily Server Report({now.strftime('%Y-%m-%d')})</span></p> 
        
        <p><span style="font-weight: bold;">CPU Usage:</span> 
            <span style="color:{get_color(cpu_percent)};">{cpu_percent}%</span>
        </p>
        
        <p><span style="font-weight: bold;">Memory Usage:</span> 
            {used_memory_gb:.2f}GB / {total_memory_gb:.2f}GB 
            (<span style="color:{get_color(memory.percent)};">{memory.percent}%</span>)
        </p>
        
        <p><span style="font-weight: bold;">Disk Usage:</span> 
            {used_disk_gb:.2f}GB / {total_disk_gb:.2f}GB 
            (<span style="color:{get_color(disk.percent)};">{disk.percent}%</span>)
        </p>

    """

    # GPU가 있다면 내용 추가
    if gpu_status:
        for i, gpu in enumerate(gpu_status):
            gpu_info = f"""
        <p>
        <span style="font-weight: bold;">GPU {i} Utilization:</span> 
        <span style="color:{get_color(gpu['utilization'])};">{gpu['utilization']}%</span>
        <br>
        <span style="font-weight: bold;">GPU {i} Memory Usage:</span> 
        {gpu['used_memory']}GB / {gpu['total_memory']}GB 
        (<span style="color:{get_color(gpu['memory_percent'])};">{gpu['memory_percent']}%</span>)
        </p>
            """
            body += gpu_info
    
    body += f"""
        <p><span style="font-weight: bold;"></span></p>
        <img src="cid:graph_image">
    """

    # 닫는 태그 추가
    body += """
    </body>
</html>
    """

    # 이메일 전송
    send_email(f"[{SERVER_NAME}] Daily Server Report({now.strftime('%Y-%m-%d')})", body, True)
    
# 상태 확인 함수
def check_server_status():
    global last_alert_status
    subject = None
    
    now = datetime.now()
    
    write_header = not os.path.exists(CSV_FILE_PATH)
    
    # CPU 사용량 확인
    cpu_percent = psutil.cpu_percent(interval=1)
    if cpu_percent > 80:
        last_sent = last_alert_status["cpu"]["last_sent"]
        if not last_alert_status["cpu"]["alerted"] or (last_sent and now - last_sent >= ALERT_INTERVAL):
            subject = f"[{SERVER_NAME}] High CPU Usage Alert({now.strftime('%Y-%m-%d %H:%M:%S')})"
            body = f"""
<html>
    <body>
        <p><span style="font-weight: bold;">[{SERVER_NAME}] High CPU Usage Alert({now.strftime('%Y-%m-%d %H:%M:%S')})</span></p> 
        
        <p><span style="font-weight: bold;">CPU Usage:</span> 
            <span style="color:{get_color(cpu_percent)};">{cpu_percent}%</span>
        </p>
    </body>
</html>
            """
        
            # 이메일 전송
            send_email(subject, body, False)
            last_alert_status["cpu"] = {"alerted": True, "last_sent": now}
    else:
        last_alert_status["cpu"]["alerted"] = False

    # 메모리 사용량 확인
    memory = psutil.virtual_memory()

    total_memory_gb = memory.total / (1024 ** 3)
    used_memory_gb = memory.used / (1024 ** 3)

    if memory.percent > 80:
        last_sent = last_alert_status["memory"]["last_sent"]
        if not last_alert_status["memory"]["alerted"] or (last_sent and now - last_sent >= ALERT_INTERVAL):
            subject = f"[{SERVER_NAME}] High Memory Usage Alert({now.strftime('%Y-%m-%d %H:%M:%S')})"
            body = f"""
<html>
    <body>
        <p><span style="font-weight: bold;">[{SERVER_NAME}] High Memory Usage Alert({now.strftime('%Y-%m-%d %H:%M:%S')})</span></p> 
        
        <p><span style="font-weight: bold;">Memory Usage:</span> 
            {used_memory_gb:.2f}GB / {total_memory_gb:.2f}GB 
            (<span style="color:{get_color(memory.percent)};">{memory.percent}%</span>)
        </p>
    </body>
</html>
            """
    
            # 이메일 전송
            send_email(subject, body, False)
            last_alert_status["memory"] = {"alerted": True, "last_sent": now}
    else:
        last_alert_status["memory"]["alerted"] = False
    
    # 디스크 사용량 확인
    disk = psutil.disk_usage('/')

    total_disk_gb = disk.total / (1024 ** 3)
    used_disk_gb = disk.used / (1024 ** 3)
    
    if disk.percent > 80:
        last_sent = last_alert_status["disk"]["last_sent"]
        if not last_alert_status["disk"]["alerted"] or (last_sent and now - last_sent >= ALERT_INTERVAL):
            subject = f"[{SERVER_NAME}] High Disk Usage Alert({now.strftime('%Y-%m-%d %H:%M:%S')})"
            body = f"""
<html>
    <body>
        <p><span style="font-weight: bold;">[{SERVER_NAME}] High Disk Usage Alert({now.strftime('%Y-%m-%d %H:%M:%S')})</span></p> 
        
        <p><span style="font-weight: bold;">Disk Usage:</span> 
            {used_disk_gb:.2f}GB / {total_disk_gb:.2f}GB 
            (<span style="color:{get_color(disk.percent)};">{disk.percent}%</span>)
        </p>
    </body>
</html>
            """

            # 이메일 전송
            send_email(subject, body, False)
            last_alert_status["disk"] = {"alerted": True, "last_sent": now}
    else:
        last_alert_status["disk"]["alerted"] = False

    # GPU 상태 확인
    gpu_status = get_gpu_status()

    # CSV 파일에 데이터 저장
    row = {
        "timestamp": now.strftime('%Y-%m-%d %H:%M:%S'),
        "cpu_usage": cpu_percent,
        "memory_usage": memory.percent,
        "disk_usage": disk.percent
    }
    if gpu_status:
        for i, gpu in enumerate(gpu_status):
            row[f"gpu_{i}_utilization"] = gpu['utilization']
            row[f"gpu_{i}_memory_usage"] = gpu['memory_percent']
    
    with open(CSV_FILE_PATH, 'a', newline='') as csvfile:
        fieldnames = row.keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        writer.writerow(row)