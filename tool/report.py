import psutil
import time
import subprocess
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

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
                gpu_status.append({
                    'used_memory': used_memory,
                    'total_memory': total_memory,
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
        <span style="font-weight: bold;">GPU {i}:</span> 
        {gpu['used_memory']}MB / {gpu['total_memory']}MB 
        (<span style="color:{get_color(gpu['utilization'])};">{gpu['utilization']}%</span>)
        <br>
            """
            body += gpu_info
        
    # 닫는 태그 추가
    body += """
    </body>
</html>
    """

    # 이메일 전송
    send_email(f"[{SERVER_NAME}] Daily Server Report({now.strftime('%Y-%m-%d')})", body)
    
# 상태 확인 함수
def check_server_status():
    global last_alert_status
    subject = None
    
    now = datetime.now()
    
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
            send_email(subject, body)
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
            send_email(subject, body)
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
            body += f"""
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
            send_email(subject, body)
            last_alert_status["disk"] = {"alerted": True, "last_sent": now}
    else:
        last_alert_status["disk"]["alerted"] = False
