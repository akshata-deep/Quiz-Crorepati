import random
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Temporary sample questions for testing.
# Later, we will replace these with AI-generated questions.

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
            "explanation": "25% of 200 is 0.25 multiplied by 200, which equals 50."
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
            "options": ["Prime Meridian", "Equator", "Tropic of Cancer", "Arctic Circle"],
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


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/quiz")
def quiz():
    subject = request.args.get("subject", "")

    if subject not in SAMPLE_QUESTIONS:
        return "Invalid subject. Please return to the homepage.", 400

    return render_template("quiz.html", subject=subject)


@app.route("/get-question", methods=["POST"])
def get_question():
    data = request.get_json(silent=True) or {}
    subject = data.get("subject", "")
    index = data.get("index")

    if subject not in SAMPLE_QUESTIONS:
        return jsonify({"error": "Invalid subject."}), 400

    if type(index) is not int or not 0 <= index < len(SAMPLE_QUESTIONS[subject]):
        return jsonify({"error": "Invalid question number."}), 400

    question = SAMPLE_QUESTIONS[subject][index]

    # The correct answer stays on the server until submission.
    return jsonify({
        "question": question["question"],
        "options": question["options"],
        "index": index,
        "total": len(SAMPLE_QUESTIONS[subject])
    })


@app.route("/check-answer", methods=["POST"])
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

@app.route("/use-fifty-fifty", methods=["POST"])
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




if __name__ == "__main__":
    app.run(debug=True)
