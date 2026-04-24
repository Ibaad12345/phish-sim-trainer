from flask import Flask, request, render_template,redirect
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

    c.execute('''
        CREATE TABLE IF NOT EXISTS sent_emails (
            uuid TEXT PRIMARY KEY, 
            target_email TEXT, 
            trigger_type TEXT)
    ''')
    conn.commit()
    conn.close()

init_db()


@app.route('/click')
def catch_click():

    u_id = request.args.get('id')
    
    conn = sqlite3.connect('phish_tracker.db')
    c = conn.cursor()
    
    # --- NEW: LOOKUP THE TRIGGER ---
    # We find out: Was this the 'Urgency' email or 'Authority'?
    c.execute("SELECT trigger_type FROM sent_emails WHERE uuid = ?", (u_id,))
    result = c.fetchone()
    trigger = result[0] if result else "Unknown"
    
    # --- LOG THE SPECIFIC ACTION ---
    action_text = f"CLICKED ({trigger})"
    c.execute("INSERT INTO interactions (user_id, action, timestamp) VALUES (?, ?, ?)", 
              (u_id, action_text, datetime.now()))
    conn.commit()
    conn.close()
    
    print(f"\n[!] ALERT: {trigger} phish clicked! ID: {u_id}")
    
    # --- NEW: SHOW THE TEACHABLE MOMENT ---
    # This sends the 'trigger' word to your gotcha.html file
    return render_template('gotcha.html', trigger_type=trigger)

@app.route('/report')
def catch_report():
    u_id = request.args.get('id')
    
    conn = sqlite3.connect('phish_tracker.db')
    c = conn.cursor()
    
    # Find out which trigger they successfully spotted
    c.execute("SELECT trigger_type FROM sent_emails WHERE uuid = ?", (u_id,))
    result = c.fetchone()
    trigger = result[0] if result else "Unknown"

    c.execute("INSERT INTO interactions (user_id, action, timestamp) VALUES (?, ?, ?)", 
              (u_id, f"REPORTED ({trigger})", datetime.now()))
    conn.commit()
    conn.close()
    
    print(f"\n[+] SUCCESS: User reported the {trigger} attempt!")
    return "<h1>Thank you!</h1><p>Your report has been submitted to the IT Security Team.</p>"


@app.route('/dashboard')
def dashboard():
    # Get the search query from the URL (e.g., /dashboard?search=test)
    search_query = request.args.get('search', '')
    
    conn = sqlite3.connect('phish_tracker.db')
    c = conn.cursor()
    
    # 1. Basic Stats
    c.execute("SELECT COUNT(*) FROM sent_emails")
    total_sent = c.fetchone()[0]
    
    # 2. Filtered Interactions (Search Logic)
    if search_query:
        c.execute("SELECT user_id, action, timestamp FROM interactions WHERE user_id LIKE ?", ('%' + search_query + '%',))
    else:
        c.execute("SELECT user_id, action, timestamp FROM interactions ORDER BY timestamp DESC LIMIT 10")
    
    recent_activity = c.fetchall()
    conn.close()

    return render_template('dashboard.html', 
                           total_sent=total_sent, 
                           activity=recent_activity, 
                           search=search_query)

if __name__ == "__main__":
    app.run(port=5000, debug=True)