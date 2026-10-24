
import os
import json
import random
import secrets
import sqlite3
from functools import wraps

from flask import (
    Flask, render_template, request, jsonify,
    redirect, url_for, session, flash
)
from werkzeug.security import generate_password_hash, check_password_hash
from question_bank import QUESTION_BANK
from gemini_quiz import generate_quiz_questions


app = Flask(__name__)

app.secret_key = os.environ.get(
    "QUIZ_CROREPATI_SECRET",
    "dev-only-change-this-before-deployment"
)

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax"
)

DATABASE = os.path.join(os.path.dirname(__file__), "quiz_crorepati.db")

PRIZE_LADDER = [
    1_000, 2_000, 3_000, 5_000,
    10_000, 20_000, 40_000, 80_000,
    160_000, 320_000, 640_000, 1_250_000,
    2_500_000, 5_000_000, 10_000_000, 70_000_000
]

SAFETY_MILESTONES = {5, 10}


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

        connection.execute("""
            CREATE TABLE IF NOT EXISTS games (
                id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                subject TEXT NOT NULL,
                questions_json TEXT NOT NULL,
                current_index INTEGER NOT NULL DEFAULT 0,
                score INTEGER NOT NULL DEFAULT 0,
                winnings INTEGER NOT NULL DEFAULT 0,
                used_lifelines TEXT NOT NULL DEFAULT '[]',
                status TEXT NOT NULL DEFAULT 'playing',
                selected_answers TEXT NOT NULL DEFAULT '{}',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS game_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                subject TEXT NOT NULL,
                score INTEGER NOT NULL,
                winnings INTEGER NOT NULL,
                result TEXT NOT NULL,
                played_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)


init_db()


def login_required(view_function):
    @wraps(view_function)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Please sign in or create an account before playing.", "info")
            return redirect(url_for("login"))
        return view_function(*args, **kwargs)
    return wrapped


def get_game():
    game_id = session.get("game_id")
    user_id = session.get("user_id")

    if not game_id or not user_id:
        return None

    with get_db_connection() as connection:
        return connection.execute(
            "SELECT * FROM games WHERE id = ? AND user_id = ?",
            (game_id, user_id)
        ).fetchone()


def game_questions(game):
    return json.loads(game["questions_json"])


def used_lifelines(game):
    return json.loads(game["used_lifelines"])


def update_game(game_id, **fields):
    if not fields:
        return

    allowed = {
        "current_index", "score", "winnings", "used_lifelines",
        "status", "selected_answers"
    }

    if not set(fields).issubset(allowed):
        raise ValueError("Invalid game update field.")

    assignments = ", ".join(f"{field} = ?" for field in fields)
    values = list(fields.values())
    values.extend([game_id, session["user_id"]])

    with get_db_connection() as connection:
        connection.execute(
            f"UPDATE games SET {assignments} WHERE id = ? AND user_id = ?",
            values
        )


def record_game_result(game, result):
    with get_db_connection() as connection:
        connection.execute("""
            INSERT INTO game_history
            (user_id, subject, score, winnings, result)
            VALUES (?, ?, ?, ?, ?)
        """, (
            game["user_id"],
            game["subject"],
            game["score"],
            game["winnings"],
            result
        ))


def finish_game(game, result, winnings=None):
    if game["status"] != "playing":
        return

    if winnings is None:
        winnings = game["winnings"]

    update_game(
        game["id"],
        status=result,
        winnings=winnings
    )
    refreshed = get_game()
    record_game_result(refreshed, result)


def current_question(game):
    questions = game_questions(game)
    index = game["current_index"]

    if not 0 <= index < len(questions):
        return None

    return questions[index]


def valid_question_request(data, game):
    if not game or game["status"] != "playing":
        return None, (jsonify({"error": "No active game. Start a new quiz."}), 400)

    index = data.get("index")

    if type(index) is not int or index != game["current_index"]:
        return None, (jsonify({"error": "That is not the current question."}), 400)

    question = current_question(game)

    if not question:
        return None, (jsonify({"error": "No question is available."}), 400)

    return question, None


# --------------------------------------------------
# HOME PAGE
# --------------------------------------------------

@app.route("/")
@login_required
def home():
    return render_template("index.html", username=session.get("username"))


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
                    cursor = connection.execute("""
                        INSERT INTO users (username, email, password_hash)
                        VALUES (?, ?, ?)
                    """, (
                        username,
                        email,
                        generate_password_hash(password)
                    ))
                    user_id = cursor.lastrowid

                session.clear()
                session["user_id"] = user_id
                session["username"] = username

                flash("Your account is ready. Welcome to Quiz Crorepati!", "success")
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
            user = connection.execute("""
                SELECT id, username, password_hash
                FROM users WHERE email = ?
            """, (email,)).fetchone()

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
# START A NEW QUIZ
# --------------------------------------------------

@app.route("/quiz")
@login_required
def quiz():
    subject = request.args.get("subject", "")

    if subject not in QUESTION_BANK:
        return "Invalid subject. Please return to the homepage.", 400

    questions = generate_quiz_questions(subject)
    game_id = secrets.token_urlsafe(24)

    with get_db_connection() as connection:
        connection.execute("""
            INSERT INTO games (id, user_id, subject, questions_json)
            VALUES (?, ?, ?, ?)
        """, (
            game_id,
            session["user_id"],
            subject,
            json.dumps(questions)
        ))

    session["game_id"] = game_id

    return render_template(
        "quiz.html",
        subject=subject,
        total_questions=16,
        prize_ladder=PRIZE_LADDER
    )


# --------------------------------------------------
# GET CURRENT QUESTION
# --------------------------------------------------

@app.route("/get-question", methods=["POST"])
@login_required
def get_question_route():
    game = get_game()

    if not game or game["status"] != "playing":
        return jsonify({"error": "No active game. Start a new quiz."}), 400

    question = current_question(game)

    if question is None:
        return jsonify({"error": "No question is available."}), 400

    return jsonify({
        "question": question["question"],
        "options": question["options"],
        "index": game["current_index"],
        "total": len(game_questions(game)),
        "score": game["score"],
        "winnings": game["winnings"],
        "prize": PRIZE_LADDER[game["current_index"]],
        "used_lifelines": used_lifelines(game)
    })


# --------------------------------------------------
# CHECK ANSWER
# --------------------------------------------------

@app.route("/check-answer", methods=["POST"])
@login_required
def check_answer():
    data = request.get_json(silent=True) or {}
    game = get_game()

    question, error = valid_question_request(data, game)
    if error:
        return error

    selected_answer = data.get("answer", "")

    if selected_answer not in question["options"]:
        return jsonify({"error": "Invalid answer option."}), 400

    answers = json.loads(game["selected_answers"])

    if str(game["current_index"]) in answers:
        return jsonify({"error": "This question has already been answered."}), 400

    answers[str(game["current_index"])] = selected_answer
    correct = selected_answer == question["answer"]
    new_score = game["score"] + (1 if correct else 0)

    response = {
        "correct": correct,
        "correct_answer": question["answer"],
        "explanation": question["explanation"],
        "score": new_score,
        "index": game["current_index"]
    }

    update_game(game["id"], selected_answers=json.dumps(answers), score=new_score)

    if not correct:
        questions_answered = game["current_index"]
        secured = 0

        if questions_answered >= 10:
            secured = PRIZE_LADDER[9]
        elif questions_answered >= 5:
            secured = PRIZE_LADDER[4]

        finish_game(get_game(), "lost", secured)
        response.update({
            "game_over": True,
            "winnings": secured,
            "message": "That answer was incorrect. Your game has ended."
        })
        return jsonify(response)

    new_winnings = PRIZE_LADDER[game["current_index"]]
    update_game(game["id"], winnings=new_winnings)

    if game["current_index"] == len(game_questions(game)) - 1:
        finish_game(get_game(), "won", new_winnings)
        response.update({
            "game_over": True,
            "winnings": new_winnings,
            "message": "Congratulations! You completed all 16 questions!"
        })
    else:
        update_game(game["id"], current_index=game["current_index"] + 1)
        response.update({
            "game_over": False,
            "winnings": new_winnings,
            "next_index": game["current_index"] + 1
        })

    return jsonify(response)


# --------------------------------------------------
# USE A LIFELINE ONCE PER GAME
# --------------------------------------------------

def mark_lifeline_used(game, name):
    used = used_lifelines(game)

    if name in used:
        return False

    used.append(name)
    update_game(game["id"], used_lifelines=json.dumps(used))
    return True


@app.route("/use-fifty-fifty", methods=["POST"])
@login_required
def use_fifty_fifty():
    data = request.get_json(silent=True) or {}
    game = get_game()

    question, error = valid_question_request(data, game)
    if error:
        return error

    if not mark_lifeline_used(game, "fifty_fifty"):
        return jsonify({"error": "You have already used 50:50."}), 400

    wrong = [option for option in question["options"] if option != question["answer"]]
    removed = random.sample(wrong, min(2, len(wrong)))
    remaining = [option for option in question["options"] if option not in removed]

    return jsonify({
        "options": remaining,
        "used_lifelines": used_lifelines(get_game())
    })


@app.route("/use-audience-poll", methods=["POST"])
@login_required
def use_audience_poll():
    data = request.get_json(silent=True) or {}
    game = get_game()

    question, error = valid_question_request(data, game)
    if error:
        return error

    if not mark_lifeline_used(game, "audience_poll"):
        return jsonify({"error": "You have already used the Audience Poll."}), 400

    options = question["options"]
    correct_answer = question["answer"]

    # Simulated audience results: weighted toward the correct answer.
    weights = [random.randint(5, 20) for _ in options]
    correct_index = options.index(correct_answer)
    weights[correct_index] = random.randint(35, 65)

    total = sum(weights)
    percentages = {
        option: round(weight * 100 / total)
        for option, weight in zip(options, weights)
    }

    return jsonify({
        "poll": percentages,
        "used_lifelines": used_lifelines(get_game())
    })


@app.route("/use-phone-friend", methods=["POST"])
@login_required
def use_phone_friend():
    data = request.get_json(silent=True) or {}
    game = get_game()

    question, error = valid_question_request(data, game)
    if error:
        return error

    if not mark_lifeline_used(game, "phone_friend"):
        return jsonify({"error": "You have already used Phone-a-Friend."}), 400

    suggested = random.choice(question["options"])
    confidence = random.randint(40, 90)

    return jsonify({
        "answer": suggested,
        "confidence_percentage": confidence,
        "reason": (
            f"Your friend thinks '{suggested}' may be correct, "
            f"but is only {confidence}% confident. "
            "This is a simulated lifeline."
        ),
        "used_lifelines": used_lifelines(get_game())
    })



# --------------------------------------------------
# QUIT CURRENT GAME
# --------------------------------------------------

@app.route("/quit-game", methods=["POST"])
@login_required
def quit_game():
    game = get_game()

    if not game or game["status"] != "playing":
        return jsonify({"error": "There is no active game to quit."}), 400

    finish_game(game, "quit", game["winnings"])

    return jsonify({
        "message": "You have quit the game.",
        "winnings": game["winnings"],
        "score": game["score"]
    })


# --------------------------------------------------
# GAME HISTORY
# --------------------------------------------------

@app.route("/game-history")
@login_required
def game_history():
    with get_db_connection() as connection:
        history = connection.execute("""
            SELECT subject, score, winnings, result, played_at
            FROM game_history
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT 50
        """, (session["user_id"],)).fetchall()

    return render_template("history.html", history=history)


# --------------------------------------------------
# START APPLICATION
# --------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)
