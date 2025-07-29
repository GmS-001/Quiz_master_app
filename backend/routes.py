# backend/routes.py
from functools import wraps
from flask_jwt_extended import jwt_required, get_jwt,get_jwt_identity, verify_jwt_in_request
from .models import Subject, Chapter, Quiz, Question,Score # We'll need the Subject model
from flask import Blueprint, request, jsonify
from .models import User
from .extensions import db
from flask_jwt_extended import create_access_token
from datetime import date
from .extensions import redis_client
import json
from sqlalchemy import func
# Why use a Blueprint? It helps in organizing the application into
# distinct components. We can have one blueprint for authentication,
# one for quizzes, etc., keeping our code clean and modular.
auth_bp = Blueprint('auth', __name__)

# This is our custom decorator to protect routes for admins only
def admin_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request() # Ensures a valid JWT is present
            claims = get_jwt()
            if claims.get("is_admin"):
                return fn(*args, **kwargs)
            else:
                return jsonify(msg="Admins only!"), 403 # 403 Forbidden
        return decorator
    return wrapper


@auth_bp.route('/login', methods=['POST'])
def login():
    """Handles user login and returns a JWT."""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"msg": "Username and password are required"}), 400

    user = User.query.filter_by(username=username).first()

    # Check if user exists and password is correct
    if user and user.check_password(password):
        # Create a dictionary for additional claims in the JWT
        additional_claims = {"is_admin": user.is_admin}
        # Create the access token with the user's id as the identity
        # and additional claims
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims=additional_claims
        )
        return jsonify(access_token=access_token)

    return jsonify({"msg": "Bad username or password"}), 401


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username') # This is the user's email

    # Check if user (email) already exists
    if User.query.filter_by(username=username).first():
        return jsonify(message="An account with this email already exists"), 409

    new_user = User(
        username=username,
        full_name=data.get('fullName'),
        qualification=data.get('qualification'),
        gender=data.get('gender'),
        phone_number=data.get('phoneNumber'),
        address=data.get('address'),
        city=data.get('city'),
        state=data.get('state'),
        country=data.get('country')
    )
    new_user.set_password(data.get('password'))

    # Handle date of birth conversion from string (YYYY-MM-DD)
    dob_str = data.get('dob')
    if dob_str:
        try:
            new_user.date_of_birth = date.fromisoformat(dob_str)
        except (ValueError, TypeError):
            return jsonify(message="Invalid date format for DOB. Use YYYY-MM-DD."), 400

    db.session.add(new_user)
    db.session.commit()

    return jsonify(message="User created successfully"), 201



@auth_bp.route('/subjects', methods=['POST'])
@admin_required() # Protect this route so only admins can access it
def create_subject():
    data = request.get_json()
    new_subject = Subject(name=data['name'], description=data.get('description'))
    db.session.add(new_subject)
    db.session.commit()
    redis_client.delete("content-tree")
    return jsonify({'message': 'Subject created successfully'}), 201

@auth_bp.route('/subjects', methods=['GET'])
@jwt_required() # Any logged-in user can view subjects
def get_subjects():
    subjects = Subject.query.all()
    # Convert the list of subject objects to a list of dictionaries
    subjects_list = [{'id': s.id, 'name': s.name, 'description': s.description} for s in subjects]
    return jsonify(subjects_list)

@auth_bp.route('/subjects/<int:subject_id>', methods=['PUT'])
@admin_required()
def update_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    data = request.get_json()
    subject.name = data.get('name', subject.name)
    subject.description = data.get('description', subject.description)
    db.session.commit()
    redis_client.delete("content-tree")
    return jsonify({'id': subject.id, 'name': subject.name, 'description': subject.description})

@auth_bp.route('/subjects/<int:subject_id>', methods=['DELETE'])
@admin_required()
def delete_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    db.session.delete(subject)
    db.session.commit()
    redis_client.delete("content-tree")
    return jsonify({'message': 'Subject deleted successfully'})




@auth_bp.route('/subjects/<int:subject_id>/chapters', methods=['POST'])
@admin_required()
def create_chapter(subject_id):
    # Ensure the subject exists before adding a chapter to it
    Subject.query.get_or_404(subject_id)
    data = request.get_json()
    new_chapter = Chapter(
        name=data['name'], 
        description=data.get('description'), 
        subject_id=subject_id
    )
    db.session.add(new_chapter)
    db.session.commit()
    redis_client.delete("content-tree")
    return jsonify({'message': 'Chapter created successfully'}), 201

@auth_bp.route('/subjects/<int:subject_id>/chapters', methods=['GET'])
@jwt_required()
def get_chapters_for_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    chapters = subject.chapters
    chapters_list = [{'id': c.id, 'name': c.name, 'description': c.description, 'subject_id': c.subject_id} for c in chapters]
    return jsonify(chapters_list)

@auth_bp.route('/chapters/<int:chapter_id>', methods=['PUT'])
@admin_required()
def update_chapter(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    data = request.get_json()
    chapter.name = data.get('name', chapter.name)
    chapter.description = data.get('description', chapter.description)
    db.session.commit()
    redis_client.delete("content-tree")
    return jsonify({'message': 'Chapter updated successfully'})

@auth_bp.route('/chapters/<int:chapter_id>', methods=['DELETE'])
@admin_required()
def delete_chapter(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    db.session.delete(chapter)
    db.session.commit()
    redis_client.delete("content-tree")
    return jsonify({'message': 'Chapter deleted successfully'})

@auth_bp.route('/subjects/<int:subject_id>', methods=['GET'])
@jwt_required()
def get_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    return jsonify({'id': subject.id, 'name': subject.name, 'description': subject.description})



@auth_bp.route('/chapters/<int:chapter_id>/quizzes', methods=['POST'])
@admin_required()
def create_quiz(chapter_id):
    # Ensure the chapter exists
    Chapter.query.get_or_404(chapter_id)
    data = request.get_json()
    new_quiz = Quiz(
        time_duration=data['time_duration'], # e.g., "00:30"
        remarks=data.get('remarks'),
        chapter_id=chapter_id
    )
    db.session.add(new_quiz)
    db.session.commit()
    redis_client.delete("content-tree")
    return jsonify({'message': 'Quiz created successfully'}), 201


@auth_bp.route('/chapters/<int:chapter_id>/quizzes', methods=['GET'])
@jwt_required()
def get_quizzes_for_chapter(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    quizzes = chapter.quizzes
    quiz_list = [{'id': q.id, 'time_duration': q.time_duration, 'remarks': q.remarks, 'chapter_id': q.chapter_id} for q in quizzes]
    return jsonify(quiz_list)

@auth_bp.route('/quizzes/<int:quiz_id>', methods=['GET'])
@jwt_required()
def get_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    return jsonify({'id': quiz.id, 'time_duration': quiz.time_duration, 'remarks': quiz.remarks})

@auth_bp.route('/quizzes/<int:quiz_id>', methods=['PUT'])
@admin_required()
def update_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    data = request.get_json()
    quiz.time_duration = data.get('time_duration', quiz.time_duration)
    quiz.remarks = data.get('remarks', quiz.remarks)
    db.session.commit()
    redis_client.delete("content-tree")
    return jsonify({'message': 'Quiz updated successfully'})


@auth_bp.route('/quizzes/<int:quiz_id>', methods=['DELETE'])
@admin_required()
def delete_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    db.session.delete(quiz)
    db.session.commit()
    redis_client.delete("content-tree")
    return jsonify({'message': 'Quiz deleted successfully'})



@auth_bp.route('/quizzes/<int:quiz_id>/questions', methods=['POST'])
@admin_required()
def create_question(quiz_id):
    # Ensure the quiz exists
    Quiz.query.get_or_404(quiz_id)
    data = request.get_json()
    new_question = Question(
        question_statement=data['question_statement'],
        option1=data['option1'],
        option2=data['option2'],
        option3=data['option3'],
        option4=data['option4'],
        correct_option=data['correct_option'],
        quiz_id=quiz_id
    )
    db.session.add(new_question)
    db.session.commit()
    redis_client.delete("content-tree")
    return jsonify({'message': 'Question created successfully'}), 201


@auth_bp.route('/quizzes/<int:quiz_id>/questions', methods=['GET'])
@jwt_required()
def get_questions_for_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = quiz.questions
    questions_list = [
        {
            'id': q.id,
            'question_statement': q.question_statement,
            'option1': q.option1,
            'option2': q.option2,
            'option3': q.option3,
            'option4': q.option4,
            'correct_option': q.correct_option
        } for q in questions
    ]
    return jsonify(questions_list)


@auth_bp.route('/questions/<int:question_id>', methods=['PUT'])
@admin_required()
def update_question(question_id):
    question = Question.query.get_or_404(question_id)
    data = request.get_json()
    question.question_statement = data.get('question_statement', question.question_statement)
    question.option1 = data.get('option1', question.option1)
    question.option2 = data.get('option2', question.option2)
    question.option3 = data.get('option3', question.option3)
    question.option4 = data.get('option4', question.option4)
    question.correct_option = data.get('correct_option', question.correct_option)
    db.session.commit()
    redis_client.delete("content-tree")
    return jsonify({'message': 'Question updated successfully'})


@auth_bp.route('/questions/<int:question_id>', methods=['DELETE'])
@admin_required()
def delete_question(question_id):
    question = Question.query.get_or_404(question_id)
    db.session.delete(question)
    db.session.commit()
    redis_client.delete("content-tree")
    return jsonify({'message': 'Question deleted successfully'})


@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_user_profile():
    # get_jwt_identity() safely returns the identity of the current user from the token
    current_user_id = get_jwt_identity()
    user = User.query.get_or_404(current_user_id)
    
    profile_data = {
        "id": user.id,
        "username": user.username,
        "fullName": user.full_name,
        "qualification": user.qualification,
        "dob": user.date_of_birth.isoformat() if user.date_of_birth else None,
        "gender": user.gender,
        "phoneNumber": user.phone_number,
        "address": user.address,
        "city": user.city,
        "state": user.state,
        "country": user.country,
        "isAdmin": user.is_admin
    }
    return jsonify(profile_data)



@auth_bp.route('/content-tree', methods=['GET'])
@jwt_required()
def get_content_tree():
    """
    Returns a nested structure of all subjects, chapters, and quizzes.
    This is more efficient than making separate API calls for each level.
    """
    cache_key = "content-tree"
    cached_data = redis_client.get(cache_key)

    if cached_data:
        # If data is in the cache, return it directly
        return jsonify(json.loads(cached_data))
    subjects = Subject.query.order_by(Subject.name).all()
    content_tree = []
    for subject in subjects:
        subject_data = {
            'id': subject.id,
            'name': subject.name,
            'chapters': []
        }
        for chapter in subject.chapters:
            chapter_data = {
                'id': chapter.id,
                'name': chapter.name,
                'quizzes': []
            }
            for quiz in chapter.quizzes:
                quiz_data = {
                    'id': quiz.id,
                    'remarks': quiz.remarks,
                    'time_duration': quiz.time_duration
                }
                chapter_data['quizzes'].append(quiz_data)
            subject_data['chapters'].append(chapter_data)
        content_tree.append(subject_data)
        # Store the fresh data in the cache for 10 minutes (600 seconds)
    redis_client.setex(cache_key, 600, json.dumps(content_tree))
        
    return jsonify(content_tree)



@auth_bp.route('/quizzes/<int:quiz_id>/submit', methods=['POST'])
@jwt_required()
def submit_quiz(quiz_id):
    user_id = int(get_jwt_identity())
    data = request.get_json()
    user_answers = data.get('answers') 
    tab_switches = data.get('tabSwitches', 0)
    time_taken = data.get('timeTaken')
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = quiz.questions

    score = 0
    results_breakdown = []

    for question in questions:
        is_correct = False
        user_answer = user_answers.get(str(question.id))
        if user_answer is not None and int(user_answer) == question.correct_option:
            score += 1
            is_correct = True

        results_breakdown.append({
        'question_id': question.id,
        'question_statement': question.question_statement,
        'option1': question.option1, 
        'option2': question.option2, 
        'option3': question.option3, 
        'option4': question.option4, 
        'user_answer': user_answer,
        'correct_answer': question.correct_option,
        'is_correct': is_correct
    })

    new_score = Score(
        score_achieved=score,
        total_questions=len(questions),
        tab_switches=tab_switches,
        user_id=user_id,
        quiz_id=quiz_id,
        time_taken=time_taken,
        results_breakdown=results_breakdown
    )
    db.session.add(new_score)
    db.session.commit()

    # Prepare the data payload for the email task and frontend
    result_payload = {
        'user_id': user_id,
        'quiz_id': quiz_id,
        'score_id': new_score.id,
        'score_achieved': score,
        'total_questions': len(questions),
        'tab_switches': tab_switches,
        'time_taken': time_taken, 
        'breakdown': results_breakdown
    }
    from .celery_worker import send_quiz_report_email
    # Trigger the background task. .delay() runs it with Celery.
    send_quiz_report_email.delay(result_payload)

    # Return the detailed results to the frontend
    return jsonify(result_payload)


@auth_bp.route('/export-csv', methods=['POST'])
@jwt_required()
def trigger_csv_export():
    user_id = int(get_jwt_identity())
    from .celery_worker import generate_csv_report
    task = generate_csv_report.delay(user_id)
    return jsonify({'task_id': task.id}), 202

@auth_bp.route('/task-status/<task_id>', methods=['GET'])
@jwt_required()
def get_task_status(task_id):
    from . import celery_app
    task = celery_app.AsyncResult(task_id)

    if task.state == 'SUCCESS':
        response = {
            'state': task.state,
            'result': task.result, # The CSV data string
            'status': 'Task completed!'
        }
    elif task.state == 'FAILURE':
        response = {
            'state': task.state,
            'status': str(task.info) # The error message
        }
    else:
        # This covers 'PENDING' and other states
        response = {
            'state': task.state,
            'status': 'In progress...'
        }
    return jsonify(response)


@auth_bp.route('/scores/history', methods=['GET'])
@jwt_required()
def get_score_history():
    user_id = int(get_jwt_identity())
    scores = Score.query.filter_by(user_id=user_id).order_by(Score.timestamp.desc()).all()
    
    history_list = []
    for score in scores:
        history_list.append({
            'score_id': score.id,
            'quiz_remarks': score.quiz.remarks,
            'subject_name': score.quiz.chapter.subject.name,
            'score_achieved': score.score_achieved,
            'total_questions': score.total_questions,
            'timestamp': score.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        })
        
    return jsonify(history_list)


@auth_bp.route('/result/<int:score_id>', methods=['GET'])
@jwt_required()
def get_past_result(score_id):
    user_id = int(get_jwt_identity())
    score = Score.query.filter_by(id=score_id, user_id=user_id).first_or_404()

    # Reconstruct the breakdown with full question details
    detailed_breakdown = []
    if score.results_breakdown:
        for item in score.results_breakdown:
            question = Question.query.get(item['question_id'])
            if question:
                item['option1'] = question.option1
                item['option2'] = question.option2
                item['option3'] = question.option3
                item['option4'] = question.option4
            detailed_breakdown.append(item)

    return jsonify({
        'score_id': score.id,
        'quiz_id': score.quiz_id,
        'time_taken': score.time_taken,
        'score_achieved': score.score_achieved,
        'total_questions': score.total_questions,
        'tab_switches': score.tab_switches,
        'breakdown': detailed_breakdown
    })

@auth_bp.route('/admin/summary-stats', methods=['GET'])
@admin_required()
def get_summary_stats():
    total_users = User.query.filter_by(is_admin=False).count()
    total_quizzes_taken = Score.query.count()
    
    # Calculate score distribution for a chart
    scores = [s.score_achieved / s.total_questions for s in Score.query.all() if s.total_questions > 0]
    
    high_scores = len([s for s in scores if s >= 0.8]) # 80% or higher
    medium_scores = len([s for s in scores if 0.5 <= s < 0.8]) # 50% - 79%
    low_scores = len([s for s in scores if s < 0.5]) # Below 50%
    
    return jsonify({
        'total_users': total_users,
        'total_quizzes_taken': total_quizzes_taken,
        'score_distribution': {
            'high': high_scores,
            'medium': medium_scores,
            'low': low_scores
        }
    })



@auth_bp.route('/quiz/<int:quiz_id>/time-stats', methods=['GET'])
@jwt_required()
def get_quiz_time_stats(quiz_id):
    # Calculate average time for this quiz
    avg_time = db.session.query(func.avg(Score.time_taken)).filter(Score.quiz_id == quiz_id).scalar()

    # Create a subquery to count the total number of questions for the quiz
    question_count_subquery = db.session.query(func.count(Question.id)).filter(Question.quiz_id == quiz_id).scalar_subquery()

    # Find the fastest time for a perfect score using the subquery
    fastest_perfect_time = db.session.query(func.min(Score.time_taken))\
        .filter(Score.quiz_id == quiz_id)\
        .filter(Score.score_achieved == question_count_subquery)\
        .scalar()

    # Handle cases where queries return None and ensure types are correct
    avg_time_val = float(avg_time) if avg_time is not None else 0
    fastest_perfect_val = fastest_perfect_time if fastest_perfect_time is not None else 0

    return jsonify({
        'average_time': avg_time_val,
        'fastest_perfect_time': fastest_perfect_val
    })