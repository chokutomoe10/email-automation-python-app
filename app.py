from sqlalchemy import create_engine, Column, String, Integer, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from flask import Flask, jsonify
from flask_mail import Mail, Message
from datetime import datetime
import os
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

app = Flask(__name__)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = "mikhaelbani7@gmail.com"
app.config['MAIL_PASSWORD'] = os.environ.get('PASSWORD')
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

Base = declarative_base()

class Email(Base):
    __tablename__ = 'saving_emails'
    id = Column("id", Integer, primary_key=True)
    event_id = Column("event_id", Integer)
    email_subject = Column("email_subject", String)
    email_content = Column("email_content", String)
    timestamp = Column("timestamp", TIMESTAMP)

    def __init__(self, id, event_id, email_subject, email_content, timestamp):
        self.id = id
        self.event_id = event_id
        self.email_subject = email_subject
        self.email_content = email_content
        self.timestamp = timestamp

engine = create_engine('sqlite:///newdb.db', echo=True)
Base.metadata.create_all(bind=engine)

Session = sessionmaker(bind=engine)
session = Session()

@app.route("/save_emails/<event_id>/<email_subject>/<email_content>/<timestamp>", methods=['POST'])
def saving_emails(event_id, email_subject, email_content, timestamp):
    id = 9
    event_id = 1
    email_subject = "Send New Emails"
    email_content = "first try"
    newtime = "08 Feb 2024 16:07"
    timestamp = datetime.strptime(newtime, "%d %b %Y %H:%M").replace(second=0, microsecond=0)

    email = Email(id, event_id, email_subject, email_content, timestamp)
    session.add(email)
    session.commit()
    
    return jsonify({"message":"Sent Email Success"})


def sending_emails(email_subject, email_content):
    with app.app_context():
        sender = "mikhaelbani7@gmail.com"
        recipients = ["mikhaelbani7@gmail.com", "blackwhip.q@gmail.com"]
        msg = Message(email_subject, sender=sender, recipients=recipients)
        msg.body = email_content
        mail.send(msg)

def check_data_and_send_emails():
    rows = session.query(Email).all()

    for row in rows:
        now = datetime.now().replace(second=0, microsecond=0)
        print(now)
        print(row.timestamp)
        if (now == row.timestamp):
            sending_emails(row.email_subject, row.email_content)

scheduler = BackgroundScheduler()
scheduler.start()

scheduler.add_job(func=check_data_and_send_emails, trigger=IntervalTrigger(minutes=1), id='check_data_and_send_emails_id', name='check and send the emails', replace_existing=True)

if __name__ == "__main__":
    app.run(debug=True)