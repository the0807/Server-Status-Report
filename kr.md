<div align="center">

# Server-Status-Report

### 🖥️ Tracking server status(CPU, Memory, GPU, Disk) and sending reports to mail

🚀 [`English version`](README.md)

</div>

# 📌 Function
- 매일 오전 8시에 전날의 서버 추적에 관한 이메일 보고서를 보내기(메일에 이미지로 첨부)

<div align="center">
<img width="473" alt="daily" src="https://github.com/user-attachments/assets/b4587ed9-6a02-4d2d-821f-255cb59680d3" />
</div>

- 매분 리소스 사용량을 확인하고 80%를 초과하면 이메일 보내기(해결 되지않은 문제는 6시간마다 다시 알림)

<div align="center">
<img width="473" alt="cpu" src="https://github.com/user-attachments/assets/2c3b4a86-ed51-4135-97a6-ae7ae8b1172c" />
<img width="473" alt="mem" src="https://github.com/user-attachments/assets/9a4443ff-b949-4606-93f4-30636d9013e4" />
<img width="473" alt="disk" src="https://github.com/user-attachments/assets/b076fd5c-4f2c-4d3f-8c59-7096d0b31a22" />
</div>

# ✏️ Usase

> [!Note]
> -  본 프로젝트는 발신 계정으로 `Gmail`을 사용함

1. Git clone 후 python 패키지 설치하기

    ``` shell
    git clone https://github.com/the0807/Server-Status-Report
    cd Server-Status-Report
    pip install -r requirements.txt
    ```

2. Gmail에서 `앱 패스워드` 생성하기

    a. Google Account 접속하기
    
    🚀 [`Google Account`](https://accounts.google.com/v3/signin/identifier?continue=https%3A%2F%2Fmyaccount.google.com%3Futm_source%3Daccount-marketing-page%26utm_medium%3Dgo-to-account-button%26gar%3DWzEzMywiMjM2NzM2Il0%26sl%3Dtrue&ifkv=AVdkyDmnPWDR9uanvAauARFKVXAJ4SLijtuxBEvXOOB8SbKVA0UoVEh1l46qBSr2Hqyas1GcEg_oDA&service=accountsettings&flowName=GlifWebSignIn&flowEntry=ServiceLogin&dsh=S-704455896%3A1736697975308393&ddm=1)
    
    b. `App Password` 검색하기

    c. `앱 이름`을 입력하고 생성 버튼 클릭하기

    d. 창이 나타날 때 나타나는 비밀번호 복사하기

> [!Caution]
> - 창을 닫으면 비밀번호가 다시 표시되지 않으므로 반드시 복사하세요

3. `.env` 파일을 생성 한 후 아래의 내용 입력하기

    ``` shell
    SERVER_NAME = # Server name
    SMTP_SERVER = 'smtp.gmail.com'
    SMTP_PORT = 587
    EMAIL_ADDRESS = # Gmail address to send
    EMAIL_PASSWORD = # Gmail APP password
    RECIPIENT_EMAIL = # Email address to receive
    ```

4. `systemd` 서비스 등록하기

    a. `server_status.service` 생성하기

    ``` shell
    sudo vim /etc/systemd/system/server_status.service

    # 아래에 내용을 추가하세요(경로에 따라 수정)
    [Unit]
    Description=Server Status Monitoring Script
    After=network.target

    [Service]
    # ExecStart, WorkingDirectory 경로가 올바른지 확인하세요.
    ExecStart=/usr/bin/python3 /home/ubuntu/Server-Status-Report/main.py
    WorkingDirectory=/home/ubuntu/Server-Status-Report
    Restart=always
    # 사용자가 올바른지 확인하세요.
    User=ubuntu

    [Install]
    WantedBy=multi-user.target
    ```

    b. 서비스 활성화 및 시작

    ``` shell
    sudo systemctl daemon-reload
    sudo systemctl enable server_status.service
    sudo systemctl start server_status.service
    ```

    c. 서비스 상태 확인
    ``` shell
    sudo systemctl status server_status.service
    ```

# ❗️ Troubleshooting

### ⭐️ 서비스 상태가 실패인 경우
터미널에서 `server_status.service` 파일의 `ExecStart`를 직접 실행하여 문제를 확인하세요.