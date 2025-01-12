import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()

# 이메일 설정
SMTP_SERVER = os.environ.get('SMTP_SERVER')
SMTP_PORT = os.environ.get('SMTP_PORT')
EMAIL_ADDRESS = os.environ.get('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')
RECIPIENT_EMAIL = os.environ.get('RECIPIENT_EMAIL')

# 파일 경로
IMG_SAVE_PATH = 'log.png'

# 이메일 보내기 함수
def send_email(subject, body, daily):
    msg = MIMEMultipart('alternative')
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = RECIPIENT_EMAIL
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'html'))
    
    if daily == True:
        # 그래프 이미지 첨부
        with open(IMG_SAVE_PATH, 'rb') as img_file:
            img = MIMEImage(img_file.read())
            img.add_header('Content-ID', '<graph_image>')
            img.add_header('Content-Disposition', 'inline', filename=os.path.basename(IMG_SAVE_PATH))
            msg.attach(img)
            
        # 이미지 첨부 파일로 추가
        with open(IMG_SAVE_PATH, 'rb') as img_file:
            attach_image = MIMEImage(img_file.read())
            attach_image.add_header('Content-Disposition', 'attachment', filename=os.path.basename(IMG_SAVE_PATH))
            msg.attach(attach_image)

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            
            server.send_message(msg)
        print(f"[INFO] Success to send email at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    except Exception as e:
        print(f"[ERROR] Failed to send email: {e}")