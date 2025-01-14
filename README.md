<div align="center">

# Server-Status-Report

### 🖥️ Tracking server status(CPU, Memory, GPU, Disk) and sending reports to email

🚀 [`Korean version`](kr.md)

</div>

# 📌 Function

- Create an email report on tracking servers from the previous day at 8 a.m. daily(attached as an image to the email)

<div align="center">

|<img width="473" alt="daily" src="https://github.com/user-attachments/assets/f0f33322-d858-43ee-a5fe-1d6e13a28e62" />|<img width="473" alt="daily" src="https://github.com/user-attachments/assets/8e438fe1-7d14-4d83-b873-2d3a15595edd" />|
|:---:|:---:|

</div>

- Check resources every minute and send email when it exceeds 80%(reminders of unresolved issues every 6 hours)

<div align="center">
<img width="473" alt="cpu" src="https://github.com/user-attachments/assets/2c3b4a86-ed51-4135-97a6-ae7ae8b1172c" />
<img width="473" alt="mem" src="https://github.com/user-attachments/assets/9a4443ff-b949-4606-93f4-30636d9013e4" />
<img width="473" alt="disk" src="https://github.com/user-attachments/assets/b076fd5c-4f2c-4d3f-8c59-7096d0b31a22" />
</div>

- Notification of service start by email(e.g. on reboot)

<div align="center">
<img width="770" alt="start" src="https://github.com/user-attachments/assets/c8e0567b-de65-4807-bc11-6ce3e027ab2c" />
</div>

# ✏️ Usase

> [!Note]
> -  `Gmail` based on the use of the sending account

1. Git clone and Install python requirements

    ``` shell
    git clone https://github.com/the0807/Server-Status-Report
    cd Server-Status-Report
    pip install -r requirements.txt
    ```

2. Create an `APP password` in Gmail

    a. Go to Google Account
    
    🚀 [`Google Account`](https://accounts.google.com/v3/signin/identifier?continue=https%3A%2F%2Fmyaccount.google.com%3Futm_source%3Daccount-marketing-page%26utm_medium%3Dgo-to-account-button%26gar%3DWzEzMywiMjM2NzM2Il0%26sl%3Dtrue&ifkv=AVdkyDmnPWDR9uanvAauARFKVXAJ4SLijtuxBEvXOOB8SbKVA0UoVEh1l46qBSr2Hqyas1GcEg_oDA&service=accountsettings&flowName=GlifWebSignIn&flowEntry=ServiceLogin&dsh=S-704455896%3A1736697975308393&ddm=1)
    
    b. Search `App Password`

    c. Type an `app name` and click the Create button

    d. Copy the password that appears when the window appears

> [!Caution]
> - If you close the window, you won't see the password again, so make sure to copy it

3. Create `.env` and fill in the contents below

    ``` shell
    SERVER_NAME = # Server name
    SMTP_SERVER = 'smtp.gmail.com'
    SMTP_PORT = 587
    EMAIL_ADDRESS = # Gmail address to send
    EMAIL_PASSWORD = # Gmail APP password
    RECIPIENT_EMAIL = # Email address to receive
    ```

4. Set to `systemd` service

    a. Create `server_status.service`

    ``` shell
    sudo vim /etc/systemd/system/server_status.service

    # Add content below(Please modify it according to your path)
    [Unit]
    Description=Server Status Monitoring Script
    After=multi-user.target

    [Service]
    # Make sure the ExecStart, WorkingDirectory path is correct
    ExecStart=/usr/bin/python3 /home/ubuntu/Server-Status-Report/main.py
    WorkingDirectory=/home/ubuntu/Server-Status-Report
    Restart=on-failure
    RestartSec=30s
    # Make sure the User is correct
    User=ubuntu

    [Install]
    WantedBy=multi-user.target
    ```

    b. Enable and Start Services

    ``` shell
    # When you modify `server_status.service`, run the command again below
    sudo systemctl daemon-reload
    sudo systemctl enable server_status.service
    sudo systemctl start server_status.service
    ```

    c. Check the status of the service
    ``` shell
    sudo systemctl status server_status.service
    ```

> [!Note]
> -  If you receive a email notification when you start the server, it will run normally

# ❗️ Troubleshooting

### ⭐️ If the status of the service is Fail
Run `ExecStart` of the `server_status.service` file directly from the terminal to identify the problem.

``` shell
# Check real-time logs
journalctl -f server_status.service
```