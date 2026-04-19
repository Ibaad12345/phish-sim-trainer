import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- CONFIGURATION ---
# MailHog default SMTP port is 1025
SMTP_SERVER = "localhost"
SMTP_PORT = 1025

# --- THE BAIT ---
sender_email = "security@microsoft-verify.com"  # A fake address
receiver_email = "test-user@example.com"        # Your "target"
subject = "Critical Security Alert: Unauthorized Login"

# This is the "Tracking Link" pointing to your Flask server (which we'll make next)
# The 'id' lets you know which user clicked.
tracking_url = f"http://localhost:5000/click?id={receiver_email}"

body = f"""
<html>
<body>
    <h2>Security Alert</h2>
    <p>We detected a login to your account from a new IP address in Moscow, Russia.</p>
    <p>If this was not you, please click the button below to secure your account:</p>
    <a href="{tracking_url}" 
       style="background-color: #d9534f; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
       Secure Account Now
    </a>
    <p>Thank you,<br>The Security Team</p>
</body>
</html>
"""

# --- PREPARE THE EMAIL ---
msg = MIMEMultipart()
msg['From'] = sender_email
msg['To'] = receiver_email
msg['Subject'] = subject
msg.attach(MIMEText(body, 'html'))

# --- SEND IT ---
try:
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.sendmail(sender_email, receiver_email, msg.as_string())
    print("Successfully sent phish to MailHog!")
except Exception as e:
    print(f"Error: {e}")


# --- THE BAIT ---
tracking_url = f"http://localhost:5000/click?id={receiver_email}"
report_url = f"http://localhost:5000/report?id={receiver_email}" # New!

body = f"""
<html>
<body>
    <h2>Security Alert</h2>
    <p>We detected a login to your account from a new IP address.</p>
    <a href="{tracking_url}" style="background-color: #d9534f; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
       Secure Account Now
    </a>
    <br><br>
    <p>Is this email suspicious? <a href="{report_url}">Report this to Security Team</a></p>
</body>
</html>
"""