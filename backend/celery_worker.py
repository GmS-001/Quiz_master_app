# backend/celery_worker.py
from flask import current_app
from flask_mail import Message
from .models import User , Score
import csv
import io
from . import celery_app
from .extensions import db
from datetime import datetime, timedelta, timezone
from dateutil.relativedelta import relativedelta


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


@celery_app.task
def generate_csv_report(user_id):
    """Generates a CSV report of a user's scores."""
    user = User.query.get(user_id)
    if not user:
        return None

    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow(['Subject', 'Chapter', 'Quiz Remarks', 'Score', 'Total Questions', 'Date Taken'])

    for score in user.scores:
        writer.writerow([
            score.quiz.chapter.subject.name,
            score.quiz.chapter.name,
            score.quiz.remarks,
            score.score_achieved,
            score.total_questions,
            score.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        ])

    return output.getvalue()

@celery_app.task
def send_monthly_reports():
    """Generates and emails a monthly activity report to each user."""
    today = datetime.now(timezone.utc)
    # Calculate the start and end of the previous month
    end_of_last_month = today.replace(day=1) - timedelta(days=1)
    start_of_last_month = end_of_last_month.replace(day=1)
    
    users = User.query.filter_by(is_admin=False).all()

    for user in users:
        scores = Score.query.filter(
            Score.user_id == user.id,
            Score.timestamp.between(start_of_last_month, today.replace(day=1))
        ).all()

        if not scores:
            continue # Skip users with no activity

        quizzes_taken = len(scores)
        total_score = sum(s.score_achieved for s in scores)
        total_possible = sum(s.total_questions for s in scores)
        average_score = (total_score / total_possible * 100) if total_possible > 0 else 0

        subject = f"Your Quiz Master Report for {start_of_last_month.strftime('%B %Y')}"
        
        # We build the report as an HTML string
        html_body = f"""
        <html>
          <body>
            <h2>Hi {user.full_name},</h2>
            <p>Here is your activity summary for the month of {start_of_last_month.strftime('%B %Y')}:</p>
            <ul>
              <li><strong>Quizzes Taken:</strong> {quizzes_taken}</li>
              <li><strong>Total Score:</strong> {total_score} / {total_possible}</li>
              <li><strong>Average Score:</strong> {average_score:.2f}%</li>
            </ul>
            <p>Keep up the great work!</p>
            <p>- The Quiz Master Team</p>
          </body>
        </html>
        """
        
        msg = Message(subject,
                      sender=current_app.config['MAIL_DEFAULT_SENDER'],
                      recipients=[user.username],
                      html=html_body) # Use the 'html' parameter for HTML emails
        
        mail = current_app.extensions.get('mail')
        mail.send(msg)

    return f"Sent monthly reports to active users."