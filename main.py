import time
import schedule
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

from tool.report import daily_report, check_server_status
from tool.send import send_email

load_dotenv()

# 서버 구분을 위한 이름 설정
SERVER_NAME = os.environ.get('SERVER_NAME')

# 스케줄 설정
schedule.every().day.at("08:00").do(daily_report)  # 하루 1번 보고
schedule.every(1).minutes.do(check_server_status)   # 매 1분마다 상태 확인

# 메인 루프
if __name__ == "__main__":
    now = datetime.now()
    print("Monitoring started...")
    
    body = f"""
<html>
    <body>
        <p><span style="font-weight: bold;">[{SERVER_NAME}] Server Status Reporting Service Enabled({now.strftime('%Y-%m-%d %H:%M:%S')})</span></p>
        
        <p>
        - Create an email report on tracking servers from the previous day at 8 a.m. daily(attached as an image to the email)
        </p>
        
         <p>
        - Check resources every minute and send email when it exceeds 80%(reminders of unresolved issues every 6 hours)
        </p>
    </body>
</html>
    """
    
    # 이메일 전송
    send_email(f"[{SERVER_NAME}] Server Status Reporting Service Enabled({now.strftime('%Y-%m-%d %H:%M:%S')})", body, False)
    
    while True:
        schedule.run_pending()
        time.sleep(1)
