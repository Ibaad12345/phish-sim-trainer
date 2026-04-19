from flask import Flask, request, redirect
import sqlite3
from datetime import datetime

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('phish_tracker.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            action TEXT,
            timestamp DATETIME)
    ''')
    conn.commit()
    conn.close()

init_db()


@app.route('/click')
def catch_click():

    user_id = request.args.get('id')
# Save the CLICK to the database

    conn = sqlite3.connect('phish_tracker.db')
    c = conn.cursor()
    c.execute("INSERT INTO interactions (user_id, action, timestamp) VALUES (?, ?, ?)", 
              (user_id, 'CLICK', datetime.now()))
    conn.commit()
    conn.close()
    
    print(f"\n[!] ALERT: Click detected and saved for: {user_id}")
    # This is where we will eventually change the redirect to your 'Teachable Moment' page
    return redirect("https://www.google.com")

@app.route('/report')
def catch_report():
    user_id = request.args.get('id')
    
    # Save the REPORT to the database
    conn = sqlite3.connect('sim_data.db')
    c = conn.cursor()
    c.execute("INSERT INTO interactions (user_id, action, timestamp) VALUES (?, ?, ?)", 
              (user_id, 'REPORT', datetime.now()))
    conn.commit()
    conn.close()
    
    print(f"\n[+] SUCCESS: User {user_id} reported the attempt. Saved to DB.")
    return "<h1>Thank you!</h1><p>Your report has been submitted to the IT Security Team.</p>"

if __name__ == "__main__":
    app.run(port=5000, debug=True)