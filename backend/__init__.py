# backend/app.py
from flask import Flask, jsonify
from flask_cors import CORS
from .config import Config
from .extensions import db, migrate, jwt,mail
from .celery_init import celery_init_app
import click


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    # Initialize extensions with the app
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    mail.init_app(app)
    CORS(app)
    from .routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api')
    @app.route('/')
    def index():
        return jsonify({'message': 'Welcome to the Quiz Master API!'})
    
    @app.cli.command("create-admin")
    def create_admin():
        """Creates the initial admin user."""
        from .models import User
        # Check if an admin user already exists
        if User.query.filter_by(is_admin=True).first():
            print("Admin user already exists.")
            return

        admin_user = User(
            username="admin@quizmaster.com",
            full_name="Quiz Master Admin",
            is_admin=True
        )
        # IMPORTANT: Use a secure password in a real application!
        admin_user.set_password("AdminPassword123")
        db.session.add(admin_user)
        db.session.commit()
        print("Admin user created successfully.")

    @app.cli.command("reset-admin-password")
    @click.argument("new_password")
    def reset_admin_password(new_password):
        """Resets the admin user's password."""
        from .models import User
        
        # Why use @click.argument? It allows us to pass a value
        # (the new password) directly on the command line.

        admin_user = User.query.filter_by(is_admin=True).first()
        if admin_user:
            admin_user.set_password(new_password)
            db.session.commit()
            print("Admin password has been reset successfully.")
        else:
            print("Admin user not found.")

    # In backend/__init__.py, inside the create_app function

    @app.cli.command("seed-db")
    def seed_db():
        """Seeds the database with all subjects, chapters, quizzes, and real questions."""
        from .models import Subject, Chapter, Quiz, Question
        from .extensions import db
        import json

        # Clear existing data
        db.session.query(Question).delete()
        db.session.query(Quiz).delete()
        db.session.query(Chapter).delete()
        db.session.query(Subject).delete()
        db.session.commit()
        print("Cleared old data.")

        # A comprehensive bank of questions for all subjects
        questions_json = """
        {
        "Physics": {
            "Mechanics": [
            {"q": "What is the SI unit of force?", "o": ["Watt", "Joule", "Newton", "Pascal"], "a": 3},
            {"q": "Which of Newton's laws is also known as the law of inertia?", "o": ["First Law", "Second Law", "Third Law", "Fourth Law"], "a": 1},
            {"q": "What is the formula for kinetic energy?", "o": ["mgh", "1/2 mv^2", "ma", "F*d"], "a": 2},
            {"q": "What type of simple machine is a seesaw?", "o": ["Pulley", "Inclined Plane", "Wedge", "Lever"], "a": 4},
            {"q": "What is the acceleration due to gravity on Earth (approx)?", "o": ["9.8 m/s^2", "3.7 m/s^2", "1.6 m/s^2", "11.2 m/s^2"], "a": 1}
            ],
            "Electromagnetism": [
            {"q": "What is the unit of electric charge?", "o": ["Ampere", "Coulomb", "Volt", "Ohm"], "a": 2},
            {"q": "Which material is a good conductor of electricity?", "o": ["Rubber", "Glass", "Copper", "Wood"], "a": 3},
            {"q": "What does a transformer do?", "o": ["Changes AC voltage", "Stores charge", "Measures current", "Resists current flow"], "a": 1},
            {"q": "Who is credited with the discovery of the electron?", "o": ["Isaac Newton", "Albert Einstein", "J.J. Thomson", "Marie Curie"], "a": 3},
            {"q": "What is Ohm's Law?", "o": ["P=VI", "F=ma", "V=IR", "E=mc^2"], "a": 3}
            ]
        },
        "Chemistry": {
            "Atomic Structure": [
            {"q": "What is the atomic number of Carbon?", "o": ["12", "14", "6", "8"], "a": 3},
            {"q": "Which particle is found in the nucleus and has no charge?", "o": ["Proton", "Electron", "Neutron", "Photon"], "a": 3},
            {"q": "What is the chemical symbol for Gold?", "o": ["Ag", "Au", "Go", "Gd"], "a": 2},
            {"q": "How many electrons can the first electron shell hold?", "o": ["8", "16", "2", "4"], "a": 3},
            {"q": "What are isotopes?", "o": ["Atoms with different protons", "Atoms with different neutrons", "Atoms with different electrons", "Charged atoms"], "a": 2}
            ],
            "Chemical Bonding": [
            {"q": "What type of bond is formed by sharing electrons?", "o": ["Ionic", "Covalent", "Metallic", "Hydrogen"], "a": 2},
            {"q": "What is the chemical formula for table salt?", "o": ["H2O", "CO2", "C6H12O6", "NaCl"], "a": 4},
            {"q": "Which of these is a noble gas?", "o": ["Oxygen", "Nitrogen", "Helium", "Hydrogen"], "a": 3},
            {"q": "What is a cation?", "o": ["A negatively charged ion", "A neutral atom", "A positively charged ion", "A type of bond"], "a": 3},
            {"q": "What does a pH of 7 indicate?", "o": ["Acidic", "Basic", "Neutral", "Highly Reactive"], "a": 3}
            ]
        },
        "Computers": {
            "Data Structures": [
            {"q": "Which data structure uses LIFO (Last-In, First-Out)?", "o": ["Queue", "Stack", "Array", "Linked List"], "a": 2},
            {"q": "What is the time complexity of a binary search?", "o": ["O(n)", "O(log n)", "O(n^2)", "O(1)"], "a": 2},
            {"q": "A collection of nodes and edges is called a?", "o": ["Tree", "Graph", "Heap", "Stack"], "a": 2},
            {"q": "Which of these is not a linear data structure?", "o": ["Array", "Stack", "Tree", "Queue"], "a": 3},
            {"q": "Which data structure uses FIFO (First-In, First-Out)?", "o": ["Stack", "Array", "Queue", "Tree"], "a": 3}
            ],
            "Operating Systems": [
            {"q": "What does OS stand for?", "o": ["Open Source", "Operating System", "Order of Significance", "Optical Sensor"], "a": 2},
            {"q": "Which of these is a mobile OS?", "o": ["Windows 11", "macOS", "Android", "Linux Mint"], "a": 3},
            {"q": "What is the core of an operating system called?", "o": ["Shell", "Kernel", "API", "Driver"], "a": 2},
            {"q": "What is 'multitasking'?", "o": ["Running multiple OS", "Running multiple users", "Running multiple tasks at once", "Multiple monitors"], "a": 3},
            {"q": "What is virtual memory?", "o": ["RAM", "A flash drive", "Memory on the cloud", "A memory management technique"], "a": 4}
            ]
        },
        "History": {
            "Ancient Civilizations": [
            {"q": "Where did the ancient Olympic Games originate?", "o": ["Rome", "Egypt", "Greece", "Persia"], "a": 3},
            {"q": "The Great Wall of China was primarily built to protect against who?", "o": ["Mongols", "Japanese", "Romans", "Vikings"], "a": 1},
            {"q": "Hieroglyphics is the writing system of which civilization?", "o": ["Mesopotamia", "Indus Valley", "Ancient Egypt", "Ancient China"], "a": 3},
            {"q": "Who was the first Roman Emperor?", "o": ["Julius Caesar", "Augustus", "Nero", "Constantine"], "a": 2},
            {"q": "The ancient city of Babylon was located in modern-day what?", "o": ["Egypt", "Iran", "Turkey", "Iraq"], "a": 4}
            ],
            "Modern World History": [
            {"q": "World War I began in which year?", "o": ["1905", "1914", "1920", "1939"], "a": 2},
            {"q": "The first man to walk on the moon was?", "o": ["Yuri Gagarin", "Buzz Aldrin", "Michael Collins", "Neil Armstrong"], "a": 4},
            {"q": "The Cold War was a conflict primarily between the USA and who?", "o": ["China", "The Soviet Union", "Germany", "Japan"], "a": 2},
            {"q": "Who was the first female Prime Minister of the United Kingdom?", "o": ["Queen Elizabeth II", "Theresa May", "Margaret Thatcher", "Indira Gandhi"], "a": 3},
            {"q": "The fall of the Berlin Wall in 1989 led to the reunification of which country?", "o": ["Korea", "Vietnam", "Germany", "Yugoslavia"], "a": 3}
            ]
        },
        "Maths": {
            "Calculus": [
            {"q": "Who is considered a co-inventor of calculus?", "o": ["Einstein", "Euclid", "Pythagoras", "Leibniz"], "a": 4},
            {"q": "What does an integral of a function represent?", "o": ["The slope", "The area under the curve", "The maximum value", "The rate of change"], "a": 2},
            {"q": "What is the derivative of x^2?", "o": ["2x", "x", "x^3/3", "2"], "a": 1},
            {"q": "What is the limit of 1/x as x approaches infinity?", "o": ["1", "Infinity", "0", "Undefined"], "a": 3},
            {"q": "d/dx (sin(x)) = ?", "o": ["-sin(x)", "cos(x)", "-cos(x)", "tan(x)"], "a": 2}
            ],
            "Linear Algebra": [
            {"q": "What is a matrix with the same number of rows and columns called?", "o": ["Vector", "Scalar", "Square matrix", "Identity matrix"], "a": 3},
            {"q": "What is the determinant of a 2x2 matrix [[a, b], [c, d]]?", "o": ["a+b+c+d", "ac-bd", "ad-bc", "ab-cd"], "a": 3},
            {"q": "What is a vector with a magnitude of 1 called?", "o": ["Unit vector", "Zero vector", "Scalar vector", "Normal vector"], "a": 1},
            {"q": "What is the result of multiplying a matrix by its inverse?", "o": ["The zero matrix", "The matrix itself", "Its transpose", "The identity matrix"], "a": 4},
            {"q": "What is an eigenvector?", "o": ["A special vector", "A vector that changes direction", "A vector that doesn't change direction when a transformation is applied", "The largest vector"], "a": 3}
            ]
        }
        }
        """
        
        data = json.loads(questions_json)

        for subject_name, chapters in data.items():
            new_subject = Subject(name=subject_name)
            db.session.add(new_subject)
            db.session.flush()

            for chapter_name, questions_list in chapters.items():
                new_chapter = Chapter(name=chapter_name, subject_id=new_subject.id)
                db.session.add(new_chapter)
                db.session.flush()

                quiz1_questions = questions_list[:10]
                quiz2_questions = questions_list[:15] if len(questions_list) >= 15 else questions_list

                # Create the 10-minute quiz with 10 questions
                quiz1 = Quiz(chapter_id=new_chapter.id, time_duration="00:10", remarks=f"{chapter_name} - Quick Test")
                db.session.add(quiz1)
                db.session.flush()
                for q_data in quiz1_questions:
                    q = Question(quiz_id=quiz1.id, question_statement=q_data['q'], option1=q_data['o'][0], option2=q_data['o'][1], option3=q_data['o'][2], option4=q_data['o'][3], correct_option=q_data['a'])
                    db.session.add(q)

                # Create the 15-minute quiz with 15 questions
                quiz2 = Quiz(chapter_id=new_chapter.id, time_duration="00:15", remarks=f"{chapter_name} - Advanced Test")
                db.session.add(quiz2)
                db.session.flush()
                for q_data in quiz2_questions:
                    q = Question(quiz_id=quiz2.id, question_statement=q_data['q'], option1=q_data['o'][0], option2=q_data['o'][1], option3=q_data['o'][2], option4=q_data['o'][3], correct_option=q_data['a'])
                    db.session.add(q)

        db.session.commit()
        print("Database seeded successfully with all content!")
                
    return app

# Create celery app
celery_app = celery_init_app(create_app())
    




