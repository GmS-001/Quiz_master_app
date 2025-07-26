# backend/celery_worker.py
from flask import current_app
from flask_mail import Message
from .models import User , Score
from . import celery_app
from .extensions import db
from datetime import datetime, timedelta # Import the celery_app from __init__.py

@celery_app.task
def send_quiz_report_email(result_data):
    """A background task to send a quiz report email."""
    user = User.query.get(result_data['user_id'])
    if not user:
        return "User not found."

    subject = f"Your Quiz Result for Quiz #{result_data['quiz_id']}"
    body = f"""
    Hi {user.full_name},

    Here is your result for the recent quiz you took.
    Score: {result_data['score_achieved']} / {result_data['total_questions']}
    Tab Switches Detected: {result_data['tab_switches']}

    Keep up the great work!
    - The Quiz Master Team
    """

    msg = Message(subject,
                  sender=current_app.config['MAIL_DEFAULT_SENDER'],
                  recipients=[user.username],
                  body=body)

    mail = current_app.extensions.get('mail')
    mail.send(msg)
    return f"Email sent to {user.username}"

@celery_app.task
def send_daily_reminders():
    """Finds users who haven't taken a quiz in 3 days and sends a reminder."""
    three_days_ago = datetime.utcnow() - timedelta(days=3)
    
    # Find IDs of users who HAVE taken a quiz recently
    recent_users_q = db.session.query(Score.user_id).filter(Score.timestamp > three_days_ago).distinct()
    recent_user_ids = [r[0] for r in recent_users_q.all()]

    # Find users who are NOT in the recent list (and are not admins)
    users_to_remind = User.query.filter(User.is_admin == False, User.id.notin_(recent_user_ids)).all()

    for user in users_to_remind:
        subject = "Friendly Reminder from Quiz Master!"
        body = f"Hi {user.full_name},\n\nWe've missed you! There are new quizzes waiting for you. Come back and test your knowledge.\n\n- The Quiz Master Team"
        
        msg = Message(subject,
                      sender=current_app.config['MAIL_DEFAULT_SENDER'],
                      recipients=[user.username],
                      body=body)
        
        mail = current_app.extensions.get('mail')
        mail.send(msg)

    return f"Sent reminders to {len(users_to_remind)} users."