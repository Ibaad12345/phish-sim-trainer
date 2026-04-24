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
    conn = sqlite3.connect('phish_tracker.db')
    c = conn.cursor()
    
    # 1. Basic Stats
    c.execute("SELECT COUNT(*) FROM sent_emails")
    total_sent = c.fetchone()[0]
    
    # 2. Advanced Breakdown: Count clicks grouped by their trigger type
    # This query joins our two tables together to see the "Why" behind the click
    query = """
        SELECT sent_emails.trigger_type, COUNT(interactions.id)
        FROM interactions
        JOIN sent_emails ON interactions.user_id = sent_emails.uuid
        WHERE interactions.action LIKE 'CLICKED%'
        GROUP BY sent_emails.trigger_type
    """
    c.execute(query)
    breakdown = c.fetchall() # This returns a list like [('Urgency', 5), ('Authority', 2)]
    
    conn.close()

    # Build the HTML for the breakdown list
    breakdown_html = "".join([f"<li>{trigger}: <strong>{count} clicks</strong></li>" for trigger, count in breakdown])

    return f"""
    <html>
    <head>
        <title>Phish Analytics</title>
        <style>
            body {{ font-family: sans-serif; padding: 40px; background: #f4f7f6; color: #333; }}
            .card {{ background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); max-width: 600px; margin: auto; }}
            h1 {{ color: #2c3e50; border-bottom: 2px solid #eee; padding-bottom: 10px; }}
            .stat-box {{ background: #e9ecef; padding: 15px; border-radius: 8px; margin: 10px 0; }}
            .breakdown-list {{ list-style: none; padding: 0; }}
            .breakdown-list li {{ padding: 8px 0; border-bottom: 1px solid #eee; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>📊 Vulnerability Report</h1>
            <div class="stat-box">
                <strong>Total Campaign Reach:</strong> {total_sent} users
            </div>
            
            <h3>Psychological Vulnerability Breakdown</h3>
            <ul class="breakdown-list">
                {breakdown_html if breakdown_html else "<li>No clicks detected yet.</li>"}
            </ul>
            
            <br>
            <a href="/dashboard" style="text-decoration: none; color: #007bff;">🔄 Refresh Data</a>
        </div>
    </body>
    </html>
    """

if __name__ == "__main__":
    app.run(port=5000, debug=True)