<div align="center">

# Server-Status-Report

### 🖥️ Tracking the status of the server and sending reports to the mail

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
    SERVER_NAME = #Server name
    SMTP_SERVER = 'smtp.gmail.com'
    SMTP_PORT = 587
    EMAIL_ADDRESS = #Gmail address to send
    EMAIL_PASSWORD = #Gmail APP password
    RECIPIENT_EMAIL = #Email address to receive
    ```


