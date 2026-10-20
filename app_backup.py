import os
import random
import sqlite3
from functools import wraps

from flask import (
    Flask, render_template, request, jsonify,
    redirect, url_for, session, flash
)
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)

app.secret_key = os.environ.get(
    "QUIZ_CROREPATI_SECRET",
    "dev-only-change-this-before-deployment"
)

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax"
)

DATABASE = os.path.join(
    os.path.dirname(__file__),
    "quiz_crorepati.db"
)


# --------------------------------------------------
# DATABASE
# --------------------------------------------------

def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with get_db_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)


def login_required(view_function):
    @wraps(view_function)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash(
                "Please sign in or create an account before playing.",
                "info"
            )
            return redirect(url_for("login"))

        return view_function(*args, **kwargs)

    return wrapped


init_db()


# --------------------------------------------------
# TEMPORARY SAMPLE QUESTIONS
# These will be replaced by AI-generated questions
# after a suitable free AI option is verified.
# --------------------------------------------------

SAMPLE_QUESTIONS = {
    "Biology": [
        {
            "question": "Which organ pumps blood throughout the human body?",
            "options": ["Lungs", "Heart", "Kidneys", "Brain"],
            "answer": "Heart",
            "explanation": "The heart pumps blood throughout the body."
        },
        {
            "question": "Which part of a plant absorbs water from the soil?",
            "options": ["Flower", "Leaf", "Root", "Fruit"],
            "answer": "Root",
            "explanation": "Roots absorb water and minerals from the soil."
        },
        {
            "question": "Which gas do humans need for cellular respiration?",
            "options": ["Oxygen", "Nitrogen", "Helium", "Hydrogen"],
            "answer": "Oxygen",
            "explanation": "Cells use oxygen during aerobic respiration."
        },
        {
            "question": "What is the basic unit of life?",
            "options": ["Organ", "Tissue", "Cell", "Bone"],
            "answer": "Cell",
            "explanation": "The cell is the basic structural and functional unit of life."
        },
        {
            "question": "Which organ helps humans breathe?",
            "options": ["Liver", "Lungs", "Stomach", "Kidneys"],
            "answer": "Lungs",
            "explanation": "The lungs exchange oxygen and carbon dioxide."
        }
    ],

    "History": [
        {
            "question": "Who was the first Mughal emperor of India?",
            "options": ["Akbar", "Shah Jahan", "Babur", "Humayun"],
            "answer": "Babur",
            "explanation": "Babur founded the Mughal Empire in India in 1526."
        },
        {
            "question": "In which year did India gain independence?",
            "options": ["1942", "1947", "1950", "1935"],
            "answer": "1947",
            "explanation": "India became independent on 15 August 1947."
        },
        {
            "question": "Who was known as the Iron Man of India?",
            "options": [
                "Jawaharlal Nehru",
                "Sardar Vallabhbhai Patel",
                "Subhas Chandra Bose",
                "Bhagat Singh"
            ],
            "answer": "Sardar Vallabhbhai Patel",
            "explanation": "Sardar Vallabhbhai Patel was widely known as the Iron Man of India."
        },
        {
            "question": "Who built the Taj Mahal?",
            "options": ["Akbar", "Babur", "Shah Jahan", "Aurangzeb"],
            "answer": "Shah Jahan",
            "explanation": "Shah Jahan commissioned the Taj Mahal in memory of Mumtaz Mahal."
        },
        {
            "question": "Who led the Dandi March in 1930?",
            "options": [
                "Mahatma Gandhi",
                "B. R. Ambedkar",
                "Bhagat Singh",
                "Bal Gangadhar Tilak"
            ],
            "answer": "Mahatma Gandhi",
            "explanation": "Mahatma Gandhi led the Salt March as part of the independence movement."
        }
    ],

    "Mathematics": [
        {
            "question": "What is 12 × 8?",
            "options": ["84", "96", "108", "88"],
            "answer": "96",
            "explanation": "12 multiplied by 8 equals 96."
        },
        {
            "question": "What is the square of 9?",
            "options": ["18", "72", "81", "99"],
            "answer": "81",
            "explanation": "9 multiplied by 9 equals 81."
        },
        {
            "question": "What is 25% of 200?",
            "options": ["25", "40", "50", "75"],
            "answer": "50",
            "explanation": "25% of 200 is 50."
        },
        {
            "question": "How many degrees are in a right angle?",
            "options": ["45", "90", "180", "360"],
            "answer": "90",
            "explanation": "A right angle measures exactly 90 degrees."
        },
        {
            "question": "What is the value of 15 + 27?",
            "options": ["32", "40", "42", "45"],
            "answer": "42",
            "explanation": "15 plus 27 equals 42."
        }
    ],

    "Science": [
        {
            "question": "Which planet is known as the Red Planet?",
            "options": ["Venus", "Jupiter", "Mars", "Mercury"],
            "answer": "Mars",
            "explanation": "Mars looks reddish because of iron oxide on its surface."
        },
        {
            "question": "What is the chemical formula for water?",
            "options": ["CO2", "H2O", "O2", "NaCl"],
            "answer": "H2O",
            "explanation": "A water molecule contains two hydrogen atoms and one oxygen atom."
        },
        {
            "question": "What force pulls objects toward Earth?",
            "options": ["Friction", "Magnetism", "Gravity", "Electricity"],
            "answer": "Gravity",
            "explanation": "Gravity attracts objects with mass toward one another."
        },
        {
            "question": "At normal atmospheric pressure, water boils at what temperature?",
            "options": ["0°C", "50°C", "100°C", "150°C"],
            "answer": "100°C",
            "explanation": "Water boils at 100°C at standard atmospheric pressure."
        },
        {
            "question": "Which star is closest to Earth?",
            "options": ["Sirius", "The Sun", "Polaris", "Proxima Centauri"],
            "answer": "The Sun",
            "explanation": "The Sun is Earth's nearest star."
        }
    ],

    "Geography": [
        {
            "question": "What is the largest ocean on Earth?",
            "options": [
                "Atlantic Ocean",
                "Indian Ocean",
                "Arctic Ocean",
                "Pacific Ocean"
            ],
            "answer": "Pacific Ocean",
            "explanation": "The Pacific Ocean is the largest ocean on Earth."
        },
        {
            "question": "Which is the highest mountain above sea level?",
            "options": ["K2", "Mount Everest", "Kangchenjunga", "Lhotse"],
            "answer": "Mount Everest",
            "explanation": "Mount Everest is the highest mountain above sea level."
        },
        {
            "question": "Which continent is India part of?",
            "options": ["Europe", "Africa", "Asia", "South America"],
            "answer": "Asia",
            "explanation": "India is a country in South Asia."
        },
        {
            "question": "Which imaginary line divides Earth into Northern and Southern Hemispheres?",
            "options": [
                "Prime Meridian",
                "Equator",
                "Tropic of Cancer",
                "Arctic Circle"
            ],
            "answer": "Equator",
            "explanation": "The Equator divides Earth into the Northern and Southern Hemispheres."
        },
        {
            "question": "What is the capital of Japan?",
            "options": ["Seoul", "Beijing", "Bangkok", "Tokyo"],
            "answer": "Tokyo",
            "explanation": "Tokyo is the capital of Japan."
        }
    ],

    "General Knowledge": [
        {
            "question": "What is the capital of India?",
            "options": ["Mumbai", "New Delhi", "Chennai", "Kolkata"],
            "answer": "New Delhi",
            "explanation": "New Delhi is the capital of India."
        },
        {
            "question": "What is the national animal of India?",
            "options": ["Lion", "Elephant", "Bengal tiger", "Leopard"],
            "answer": "Bengal tiger",
            "explanation": "The Bengal tiger is India's national animal."
        },
        {
            "question": "Which is the largest planet in our solar system?",
            "options": ["Earth", "Saturn", "Jupiter", "Neptune"],
            "answer": "Jupiter",
            "explanation": "Jupiter is the largest planet in our solar system."
        },
        {
            "question": "How many colours are traditionally listed in a rainbow?",
            "options": ["Five", "Six", "Seven", "Eight"],
            "answer": "Seven",
            "explanation": "A traditional description of a rainbow lists seven colours."
        },
        {
            "question": "Which instrument is used to measure temperature?",
            "options": ["Barometer", "Thermometer", "Compass", "Anemometer"],
            "answer": "Thermometer",
            "explanation": "A thermometer measures temperature."
        }
    ]
}


# --------------------------------------------------
# HOME PAGE
# --------------------------------------------------

@app.route("/")
@login_required
def home():
    return render_template(
        "index.html",
        username=session.get("username")
    )


# --------------------------------------------------
# REGISTER
# --------------------------------------------------

@app.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return redirect(url_for("home"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if len(username) < 3:
            flash("Username must contain at least 3 characters.", "error")

        elif "@" not in email or "." not in email.split("@")[-1]:
            flash("Please enter a valid email address.", "error")

        elif len(password) < 8:
            flash("Password must be at least 8 characters long.", "error")

        elif password != confirm_password:
            flash("The passwords do not match.", "error")

        else:
            try:
                with get_db_connection() as connection:
                    cursor = connection.execute(
                        """
                        INSERT INTO users
                        (username, email, password_hash)
                        VALUES (?, ?, ?)
                        """,
                        (
                            username,
                            email,
                            generate_password_hash(password)
                        )
                    )
                    user_id = cursor.lastrowid

                session.clear()
                session["user_id"] = user_id
                session["username"] = username

                flash(
                    "Your account is ready. Welcome to Quiz Crorepati!",
                    "success"
                )

                return redirect(url_for("home"))

            except sqlite3.IntegrityError:
                flash(
                    "That username or email is already registered. "
                    "Please sign in or use another one.",
                    "error"
                )

    return render_template("auth.html", mode="register")


# --------------------------------------------------
# LOGIN
# --------------------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("home"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        with get_db_connection() as connection:
            user = connection.execute(
                """
                SELECT id, username, email, password_hash
                FROM users
                WHERE email = ?
                """,
                (email,)
            ).fetchone()

        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["username"] = user["username"]

            return redirect(url_for("home"))

        flash("Email or password is incorrect.", "error")

    return render_template("auth.html", mode="login")


# --------------------------------------------------
# LOGOUT
# --------------------------------------------------

@app.route("/logout", methods=["POST"])
@login_required
def logout():
    session.clear()
    flash("You have signed out.", "info")
    return redirect(url_for("login"))


# --------------------------------------------------
# QUIZ PAGE
# --------------------------------------------------

@app.route("/quiz")
@login_required
def quiz():
    subject = request.args.get("subject", "")

    if subject not in SAMPLE_QUESTIONS:
        return "Invalid subject. Please return to the homepage.", 400

    return render_template("quiz.html", subject=subject)


# --------------------------------------------------
# GET QUESTION
# The correct answer is not sent to the browser here.
# --------------------------------------------------

@app.route("/get-question", methods=["POST"])
@login_required
def get_question():
    data = request.get_json(silent=True) or {}

    subject = data.get("subject", "")
    index = data.get("index")

    if subject not in SAMPLE_QUESTIONS:
        return jsonify({"error": "Invalid subject."}), 400

    if type(index) is not int or not 0 <= index < len(SAMPLE_QUESTIONS[subject]):
        return jsonify({"error": "Invalid question number."}), 400

    question = SAMPLE_QUESTIONS[subject][index]

    return jsonify({
        "question": question["question"],
        "options": question["options"],
        "index": index,
        "total": len(SAMPLE_QUESTIONS[subject])
    })


# --------------------------------------------------
# CHECK ANSWER
# --------------------------------------------------

@app.route("/check-answer", methods=["POST"])
@login_required
def check_answer():
    data = request.get_json(silent=True) or {}

    subject = data.get("subject", "")
    index = data.get("index")
    selected_answer = data.get("answer", "")

    if subject not in SAMPLE_QUESTIONS:
        return jsonify({"error": "Invalid subject."}), 400

    if type(index) is not int or not 0 <= index < len(SAMPLE_QUESTIONS[subject]):
        return jsonify({"error": "Invalid question number."}), 400

    question = SAMPLE_QUESTIONS[subject][index]

    if selected_answer not in question["options"]:
        return jsonify({"error": "Invalid answer option."}), 400

    is_correct = selected_answer == question["answer"]

    return jsonify({
        "correct": is_correct,
        "correct_answer": question["answer"],
        "explanation": question["explanation"]
    })


# --------------------------------------------------
# 50:50 LIFELINE
# --------------------------------------------------

@app.route("/use-fifty-fifty", methods=["POST"])
@login_required
def use_fifty_fifty():
    data = request.get_json(silent=True) or {}

    subject = data.get("subject", "")
    index = data.get("index")

    if subject not in SAMPLE_QUESTIONS:
        return jsonify({"error": "Invalid subject."}), 400

    if type(index) is not int or not 0 <= index < len(SAMPLE_QUESTIONS[subject]):
        return jsonify({"error": "Invalid question number."}), 400

    question = SAMPLE_QUESTIONS[subject][index]

    wrong_options = [
        option for option in question["options"]
        if option != question["answer"]
    ]

    removed_options = random.sample(wrong_options, 2)

    remaining_options = [
        option for option in question["options"]
        if option not in removed_options
    ]

    return jsonify({"options": remaining_options})


# --------------------------------------------------
# PHONE-A-FRIEND LIFELINE
# This is a simulation, not a real phone call.
# --------------------------------------------------

@app.route("/use-phone-friend", methods=["POST"])
@login_required
def use_phone_friend():
    data = request.get_json(silent=True) or {}

    subject = data.get("subject", "")
    index = data.get("index")

    if subject not in SAMPLE_QUESTIONS:
        return jsonify({"error": "Invalid subject."}), 400

    if type(index) is not int or not 0 <= index < len(SAMPLE_QUESTIONS[subject]):
        return jsonify({"error": "Invalid question number."}), 400

    question = SAMPLE_QUESTIONS[subject][index]

    suggested_answer = random.choice(question["options"])
    confidence_score = random.randint(1, 10)
    confidence_percentage = confidence_score * 10

    reason = (
        f"I chose '{suggested_answer}' because it seemed like a possible "
        f"answer to the question: '{question['question']}'. "
        f"I'm {confidence_percentage}% confident, but I could be wrong. "
        "Please think carefully before submitting your answer."
    )

    return jsonify({
        "answer": suggested_answer,
        "confidence_score": confidence_score,
        "confidence_percentage": confidence_percentage,
        "reason": reason
    })


# --------------------------------------------------
# START APPLICATION
# --------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)