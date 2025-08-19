# Quiz Master - V2

Quiz Master is a feature-rich, full-stack web application designed for online exam preparation. It features a modern, decoupled architecture with a Vue.js single-page application (SPA) frontend and a Flask RESTful API backend. The platform supports two distinct roles: an **Admin** with complete control over quiz content and user management, and **Users** who can register, take quizzes in a proctored environment, and track their performance over time.

![Quiz Attempt Screenshot](https://i.imgur.com/uR1Bfpl.png)

## Key Features

### Admin Functionalities
- **Secure Admin Login:** Separate, pre-seeded credentials for the Quiz Master.
- **Content Management (CRUD):** Full create, read, update, and delete capabilities for subjects, chapters, quizzes, and questions.
- **Analytics Dashboard:** At-a-glance view of user registrations, total quizzes taken, and overall performance distribution with charts.
- **Automatic Cache Invalidation:** The Redis cache is automatically cleared whenever content is updated, ensuring users always see the latest data.

### User Functionalities
- **Detailed User Registration:** Users can create a profile with comprehensive personal details.
- **Proctored Quiz Interface:** An immersive quiz environment with:
    - **Live Camera Monitoring:** Ensures user presence during the exam.
    - **Tab-Switching Detection:** Tracks how many times a user leaves the quiz tab.
    - **Copy/Paste Prevention:** Disables text selection and copying to prevent cheating.
- **Persistent State:** The quiz timer and user's answers are saved to `sessionStorage`, so progress is not lost on a page refresh.
- **Detailed Results Page:** Instant feedback after submission with score, performance charts, and a detailed question-by-question breakdown.
- **Quiz History:** Users can view a list of all past attempts and click to see the detailed results for any specific attempt.
- **Asynchronous Operations:** Background jobs for sending email reports and exporting score history as a CSV file, ensuring the UI remains fast and responsive.

## Tech Stack & Architecture

The application is built on a decoupled architecture, which separates the frontend and backend concerns for better scalability and maintainability.

- **Frontend (Vue.js):**
  - **Framework:** Vue 3
  - **Routing:** Vue Router
  - **State Management:** Vuex
  - **HTTP Client:** Axios
  - **UI/Styling:** Bootstrap 5
  - **Charting:** Chart.js

- **Backend (Flask):**
  - **Framework:** Flask
  - **Database ORM:** SQLAlchemy
  - **Authentication:** Flask-JWT-Extended
  - **Background Tasks:** Celery
  - **API Communication:** Flask-Cors
  - **Email:** Flask-Mail

- **Database & Services:**
  - **Primary Database:** SQLite
  - **Caching & Message Broker:** Redis

## Getting Started

To run this project locally, you will need `Python 3.10+`, `Node.js v18+`, and `Redis`.

### 1. Backend Setup
```bash
# Navigate to the project root directory
cd quiz_master_app

# Create and activate a virtual environment
cd backend
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Initialize and upgrade the database
# (Run from the root `quiz_master_app` directory)
cd ..
python -m flask db init
python -m flask db migrate -m "Initial migration"
python -m flask db upgrade

# Create the admin user
python -m flask create-admin

# Run the Flask server
python -m flask run
