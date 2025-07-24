# backend/routes.py
from functools import wraps
from flask_jwt_extended import jwt_required, get_jwt, verify_jwt_in_request
from .models import Subject,Chapter # We'll need the Subject model
from flask import Blueprint, request, jsonify
from .models import User
from .extensions import db
from flask_jwt_extended import create_access_token

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