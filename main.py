import time
import schedule

from tool.report import daily_report, check_server_status

# 스케줄 설정
schedule.every().day.at("05:08").do(daily_report)  # 하루 1번 보고
schedule.every(1).minutes.do(check_server_status)   # 매 1분마다 상태 확인

# 메인 루프
if __name__ == "__main__":
    print("Monitoring started...")
    
    while True:
        schedule.run_pending()
        time.sleep(1)
