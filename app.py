from flask import Flask, render_template, request, jsonify # type: ignore
import sqlite3
from pathlib import Path
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart



app = Flask(__name__)

def send_email_notification(name, email, message):
    sender_email = "shornellchabalala60@gmail.com"  # Replace with your email
    sender_password = "cmnu xnsa foly tjvv "  # Use the App Password from Google
    receiver_email = "shornellchabalala60@gmail,com"

    subject = f"New Message from {name}"
    body = f"""
    Name: {name}
    Email: {email}
    Message: {message}
    """
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
    except Exception as e:
        print(f"Email sending failed: {e}")

# Define the database path
DB_PATH = Path(__file__).parent / 'messages.db'

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send_message', methods=['POST'])
def send_message():
    try:
        data = request.get_json() if request.is_json else request.form
        name = data.get('name')
        email = data.get('email')
        message = data.get('message')

        if not all([name, email, message]):
            return jsonify({
                'success': False,
                'error': 'Please fill in all fields.'
            }), 400

        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO messages (name, email, message)
                VALUES (?, ?, ?)
            ''', (name, email, message))
            conn.commit()

        # Send email notification
        send_email_notification(name, email, message)

        return jsonify({
            'success': True,
            'message': 'Your message has been sent successfully!'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'An error occurred: {str(e)}'
        }), 500

if __name__ == '__main__':
    app.run(debug=True)