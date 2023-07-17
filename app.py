from flask import Flask, render_template, request
import psycopg2
import requests
import json
from datetime import datetime

app = Flask(__name__)

# PostgreSQL Verbindung herstellen
conn = psycopg2.connect(
    host="localhost",
    port="5432",
    database="db",
    user="admin",
    password="admin"
)

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Anmeldeformular verarbeiten
        name = request.form['name']
        password = request.form['password']

        if name == 'admin' and password == 'admin':
            return render_template('push_notification.html')
        else:
            return 'Falscher Anmeldename oder Passwort'

    return render_template('login.html')

@app.route('/send-notification', methods=['POST'])
def send_notification():
    message = request.form.get('message')
    current_date = datetime.today().strftime('%Y-%m-%d')

    # Daten in die PostgreSQL-Datenbank einfügen
    cur = conn.cursor()
    #cur.execute("INSERT INTO queries (question) VALUES (%s);", (message,))
    cur.execute("INSERT INTO queries (question, answered, date, answer ) VALUES (%s, %s, %s, %s) RETURNING id;",
                (message, False, current_date, None))
    conn.commit()
    cur.close()

    token = request.form.get('token')

    if token and message:
        send_push_notification(token, message)
        return 'Nachricht erfolgreich gesendet und Benachrichtigung verschickt!'
    else:
        return 'Ungültiger Token oder Nachricht', 400

def send_push_notification(token, message):
    url = 'https://exp.host/--/api/v2/push/send'
    headers = {'Content-Type': 'application/json'}
    body = {
        'to': token,
        'sound': 'default',
        'title': "You've got a new message! 📬",
        'body': message,
        'data': {'message': message}
    }
    response = requests.post(url, headers=headers, data=json.dumps(body))
    if response.status_code == 200:
        print('Notification sent successfully')
    else:
        print('Failed to send notification:', response.content)

if __name__ == '__main__':
    app.run(debug=True)
