import uuid
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sqlite3


# --- CONFIGURATION ---
# MailHog default SMTP port is 1025
SMTP_SERVER = "localhost"
SMTP_PORT = 1025
sender_email = "security@microsoft-verify.com"  # A fake address
receiver_email = "test-user@example.com"        # Your "target"
subject = "Critical Security Alert: Unauthorized Login"
# 1. Generate a random, unique ID
unique_id = str(uuid.uuid4())
trigger_type = "Authority"  # This is the "hook" that tells us which phish they got

# 3. Create the URLs using the UUID instead of the email
tracking_url = f"http://localhost:5000/click?id={unique_id}"
report_url = f"http://localhost:5000/report?id={unique_id}"

print(f"Generated UUID {unique_id} for trigger: {trigger_type}")


# Register the ID in the database so the tracker knows what it is later
def register_phish(u_id, email, trigger):
    conn = sqlite3.connect('phish_tracker.db')
    c = conn.cursor()
    # We need a new table for this! 
    c.execute('''CREATE TABLE IF NOT EXISTS sent_emails
                 (uuid TEXT PRIMARY KEY, target_email TEXT, trigger_type TEXT)''')
    c.execute("INSERT INTO sent_emails (uuid, target_email, trigger_type) VALUES (?, ?, ?)", 
              (u_id, email, trigger))
    conn.commit()
    conn.close()

# Run this before sending
register_phish(unique_id, receiver_email, trigger_type)

body = f"""
<html>
<body style="font-family: Arial, sans-serif;">
    <h2>Security Alert</h2>
    <p>We detected a login to your account from a new IP address in Moscow, Russia.</p>
    <p>If this was not you, please click the button below to secure your account:</p>
    
    <a href="{tracking_url}" 
       style="background-color: #d9534f; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">
       Secure Account Now
    </a>
    
    <br><br>
    <p>Is this email suspicious? <a href="{report_url}">Report this to Security Team</a></p>
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
