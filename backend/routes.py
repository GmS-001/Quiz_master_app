# backend/routes.py
from functools import wraps
from flask_jwt_extended import jwt_required, get_jwt,get_jwt_identity, verify_jwt_in_request
from .models import Subject, Chapter, Quiz, Question,Score # We'll need the Subject model
from flask import Blueprint, request, jsonify
from .models import User
from .extensions import db
from flask_jwt_extended import create_access_token
from datetime import date

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
    return jsonify({'id': subject.id, 'name': subject.name, 'description': subject.description})

@auth_bp.route('/subjects/<int:subject_id>', methods=['DELETE'])
@admin_required()
def delete_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    db.session.delete(subject)
    db.session.commit()
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
    return jsonify({'message': 'Chapter updated successfully'})

@auth_bp.route('/chapters/<int:chapter_id>', methods=['DELETE'])
@admin_required()
def delete_chapter(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    db.session.delete(chapter)
    db.session.commit()
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
    return jsonify({'message': 'Quiz updated successfully'})


@auth_bp.route('/quizzes/<int:quiz_id>', methods=['DELETE'])
@admin_required()
def delete_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    db.session.delete(quiz)
    db.session.commit()
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
    return jsonify({'message': 'Question updated successfully'})


@auth_bp.route('/questions/<int:question_id>', methods=['DELETE'])
@admin_required()
def delete_question(question_id):
    question = Question.query.get_or_404(question_id)
    db.session.delete(question)
    db.session.commit()
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
        
    return jsonify(content_tree)



@auth_bp.route('/quizzes/<int:quiz_id>/submit', methods=['POST'])
@jwt_required()
def submit_quiz(quiz_id):
    user_id = int(get_jwt_identity())
    data = request.get_json()
    user_answers = data.get('answers') # e.g., {'question_id': 'selected_option'}
    tab_switches = data.get('tabSwitches', 0)

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
            'user_answer': user_answer,
            'correct_answer': question.correct_option,
            'is_correct': is_correct
        })

    # Save the score to the database
    new_score = Score(
        score_achieved=score,
        total_questions=len(questions),
        tab_switches=tab_switches,
        user_id=user_id,
        quiz_id=quiz_id
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
        'breakdown': results_breakdown
    }
    from .celery_worker import send_quiz_report_email
    # Trigger the background task. .delay() runs it with Celery.
    send_quiz_report_email.delay(result_payload)

    # Return the detailed results to the frontend
    return jsonify(result_payload)