import random

# ==========================================
# QUIZ CROREPATI
# Educational KBC-style quiz game
# ==========================================

GAME_NAME = "QUIZ CROREPATI"

# Virtual prize money for 16 questions
PRIZE_LADDER = [
    1_000,
    2_000,
    3_000,
    5_000,
    10_000,
    20_000,
    40_000,
    80_000,
    1_60_000,
    3_20_000,
    6_40_000,
    12_50_000,
    25_00_000,
    50_00_000,
    1_00_00_000,
    7_00_00_000
]

# Safety milestones
SAFETY_LEVELS = [5, 10]

# Subjects
SUBJECTS = {
    "1": "Biology",
    "2": "History",
    "3": "Mathematics",
    "4": "Science",
    "5": "Geography",
    "6": "General Knowledge"
}

# Temporary sample question bank.
# Later, AI will generate questions for the selected subject.
QUESTIONS = {
    "Biology": [
        {
            "question": "Which organ pumps blood around the human body?",
            "options": {
                "A": "Lungs",
                "B": "Heart",
                "C": "Kidneys",
                "D": "Stomach"
            },
            "answer": "B",
            "explanation": "The heart pumps blood around the body."
        },
        {
            "question": "Which part of a plant usually absorbs water?",
            "options": {
                "A": "Flower",
                "B": "Fruit",
                "C": "Root",
                "D": "Leaf"
            },
            "answer": "C",
            "explanation": "Roots absorb water and minerals from the soil."
        }
    ],

    "History": [
        {
            "question": "Who was the first Mughal emperor in India?",
            "options": {
                "A": "Akbar",
                "B": "Babur",
                "C": "Shah Jahan",
                "D": "Aurangzeb"
            },
            "answer": "B",
            "explanation": "Babur founded the Mughal Empire in India."
        },
        {
            "question": "In which year did India gain independence?",
            "options": {
                "A": "1942",
                "B": "1945",
                "C": "1947",
                "D": "1950"
            },
            "answer": "C",
            "explanation": "India became independent on 15 August 1947."
        }
    ],

    "Mathematics": [
        {
            "question": "What is 12 multiplied by 8?",
            "options": {
                "A": "86",
                "B": "96",
                "C": "108",
                "D": "88"
            },
            "answer": "B",
            "explanation": "12 multiplied by 8 equals 96."
        },
        {
            "question": "What is the square root of 144?",
            "options": {
                "A": "10",
                "B": "11",
                "C": "12",
                "D": "14"
            },
            "answer": "C",
            "explanation": "12 multiplied by 12 equals 144."
        }
    ],

    "Science": [
        {
            "question": "Which planet is known as the Red Planet?",
            "options": {
                "A": "Earth",
                "B": "Mars",
                "C": "Jupiter",
                "D": "Venus"
            },
            "answer": "B",
            "explanation": "Mars appears reddish because of iron-rich minerals."
        },
        {
            "question": "Which gas do plants absorb during photosynthesis?",
            "options": {
                "A": "Oxygen",
                "B": "Nitrogen",
                "C": "Hydrogen",
                "D": "Carbon dioxide"
            },
            "answer": "D",
            "explanation": "Plants use carbon dioxide during photosynthesis."
        }
    ],

    "Geography": [
        {
            "question": "Which is the largest ocean on Earth?",
            "options": {
                "A": "Indian Ocean",
                "B": "Arctic Ocean",
                "C": "Pacific Ocean",
                "D": "Atlantic Ocean"
            },
            "answer": "C",
            "explanation": "The Pacific Ocean is the largest ocean on Earth."
        },
        {
            "question": "Which is the highest mountain above sea level?",
            "options": {
                "A": "Mount Everest",
                "B": "K2",
                "C": "Kangchenjunga",
                "D": "Lhotse"
            },
            "answer": "A",
            "explanation": "Mount Everest is the highest mountain above sea level."
        }
    ],

    "General Knowledge": [
        {
            "question": "What is the capital of India?",
            "options": {
                "A": "Mumbai",
                "B": "Chennai",
                "C": "New Delhi",
                "D": "Kolkata"
            },
            "answer": "C",
            "explanation": "New Delhi is the capital of India."
        },
        {
            "question": "How many days are there in a leap year?",
            "options": {
                "A": "364",
                "B": "365",
                "C": "366",
                "D": "367"
            },
            "answer": "C",
            "explanation": "A leap year has 366 days."
        }
    ]
}


def format_rupees(amount):
    """Format numbers using the Indian numbering system."""

    amount = int(amount)

    if amount < 1000:
        return f"₹{amount}"

    number = str(amount)
    last_three = number[-3:]
    remaining = number[:-3]

    if remaining:
        parts = []

        while len(remaining) > 2:
            parts.insert(0, remaining[-2:])
            remaining = remaining[:-2]

        if remaining:
            parts.insert(0, remaining)

        return "₹" + ",".join(parts) + "," + last_three

    return "₹" + last_three


def display_prize_ladder(current_question):
    """Display all prize levels and highlight current progress."""

    print("\n" + "=" * 42)
    print("              PRIZE LADDER")
    print("=" * 42)

    for index in range(len(PRIZE_LADDER) - 1, -1, -1):
        question_number = index + 1
        prize = format_rupees(PRIZE_LADDER[index])

        marker = " <-- CURRENT" if question_number == current_question else ""

        if question_number in SAFETY_LEVELS:
            marker += " [SAFETY LEVEL]"

        print(
            f"Question {question_number:02d}: "
            f"{prize}{marker}"
        )

    print("=" * 42)


def choose_subject():
    """Ask the player to choose a subject."""

    print("\nChoose your subject:")

    for number, subject in SUBJECTS.items():
        print(f"{number}. {subject}")

    while True:
        choice = input("\nEnter your choice (1-6): ").strip()

        if choice in SUBJECTS:
            return SUBJECTS[choice]

        print("Invalid choice. Enter a number from 1 to 6.")


def prepare_questions(subject):
    """
    Prepare 16 questions for the game.

    This learning version uses a small temporary question bank.
    AI-generated questions will replace this later.
    """

    question_bank = QUESTIONS[subject].copy()

    random.shuffle(question_bank)

    # Repeat available sample questions to make a 16-question
    # game possible during early development.
    # This is temporary and does not guarantee unique questions.
    prepared = []

    while len(prepared) < 16:
        prepared.extend(question_bank)

    return prepared[:16]


def use_fifty_fifty(question):
    """Simulate the 50:50 lifeline."""

    correct_answer = question["answer"]

    wrong_answers = [
        option
        for option in question["options"]
        if option != correct_answer
    ]

    random.shuffle(wrong_answers)

    keep_options = [correct_answer, wrong_answers[0]]
    random.shuffle(keep_options)

    print("\n50:50 LIFELINE")

    for option in keep_options:
        print(f"{option}. {question['options'][option]}")


def use_audience_poll(question):
    """Simulate an audience poll."""

    correct_answer = question["answer"]

    other_options = [
        option
        for option in question["options"]
        if option != correct_answer
    ]

    percentages = {
        option: random.randint(5, 20)
        for option in other_options
    }

    remaining = 100 - sum(percentages.values())
    percentages[correct_answer] = remaining

    options = list(percentages.items())
    random.shuffle(options)

    print("\nAUDIENCE POLL")

    for option, percentage in options:
        print(f"{option}: {percentage}%")


def use_expert_lifeline(question):
    """Simulate Ask the Expert."""

    print("\nASK THE EXPERT")
    print("The expert offers a clue:")
    print(question["explanation"])


def use_phone_lifeline(question):
    """Simulate a phone-a-friend lifeline."""

    print("\nPHONE-A-FRIEND")

    possible_answers = [
        option
        for option in question["options"]
        if option != question["answer"]
    ]

    # A simulated friend may be right or wrong.
    if random.random() < 0.75:
        suggested_answer = question["answer"]
    else:
        suggested_answer = random.choice(possible_answers)

    print(
        "Your friend suggests option "
        f"{suggested_answer}: "
        f"{question['options'][suggested_answer]}"
    )


def display_lifelines(used_lifelines):
    """Show which lifelines remain available."""

    print("\nAvailable lifelines:")

    lifelines = {
        "1": "50:50",
        "2": "Audience Poll",
        "3": "Phone-a-Friend",
        "4": "Ask the Expert"
    }

    for number, name in lifelines.items():
        status = "USED" if number in used_lifelines else "AVAILABLE"
        print(f"{number}. {name} — {status}")

    print("Enter 0 to return to the question.")


def run_game():
    """Run the complete quiz game."""

    print("\n" + "=" * 42)
    print("          QUIZ CROREPATI")
    print("=" * 42)

    print("\nWelcome to Quiz Crorepati!")
    print("Educational KBC-style game.")
    print("All prize money is virtual.")

    subject = choose_subject()
    questions = prepare_questions(subject)

    used_lifelines = set()

    last_safety_prize = 0
    current_question = 0
    final_prize = 0

    print(f"\nSelected subject: {subject}")
    print("\nRules for this prototype:")
    print("- There are 16 question levels.")
    print("- You may quit before answering a question.")
    print("- Each lifeline can be used once.")
    print("- Safety levels are Questions 5 and 10.")

    input("\nPress Enter when you are ready to play...")

    for index, question in enumerate(questions):
        current_question = index + 1
        prize = PRIZE_LADDER[index]

        display_prize_ladder(current_question)

        print(f"\nQUESTION {current_question}")
        print(f"Prize for a correct answer: {format_rupees(prize)}")
        print(f"\n{question['question']}")

        for option, text in question["options"].items():
            print(f"{option}. {text}")

        while True:
            print("\nEnter A, B, C, or D to answer.")
            print("Enter L to use a lifeline.")
            print("Enter Q to quit the game.")

            answer = input("Your choice: ").strip().upper()

            if answer == "Q":
                final_prize = last_safety_prize
                print("\nYou chose to quit the game.")
                print(
                    "Your secured virtual winnings: "
                    f"{format_rupees(final_prize)}"
                )
                show_result(
                    subject,
                    current_question,
                    final_prize,
                    "QUIT"
                )
                return

            if answer == "L":
                display_lifelines(used_lifelines)

                lifeline = input(
                    "Choose a lifeline (1-4), or 0 to return: "
                ).strip()

                if lifeline == "0":
                    continue

                if lifeline not in ["1", "2", "3", "4"]:
                    print("Invalid lifeline choice.")
                    continue

                if lifeline in used_lifelines:
                    print("You have already used this lifeline.")
                    continue

                used_lifelines.add(lifeline)

                if lifeline == "1":
                    use_fifty_fifty(question)

                elif lifeline == "2":
                    use_audience_poll(question)

                elif lifeline == "3":
                    use_phone_lifeline(question)

                elif lifeline == "4":
                    use_expert_lifeline(question)

                continue

            if answer not in ["A", "B", "C", "D"]:
                print("Invalid choice. Enter A, B, C, D, L, or Q.")
                continue

            break

        if answer == question["answer"]:
            print("\nCORRECT ANSWER!")
            print(question["explanation"])

            final_prize = prize

            if current_question in SAFETY_LEVELS:
                last_safety_prize = prize

                print("\nSAFETY LEVEL REACHED!")
                print(
                    "Your secured milestone is now "
                    f"{format_rupees(last_safety_prize)}."
                )

        else:
            print("\nINCORRECT ANSWER!")
            print(
                f"The correct answer was {question['answer']}. "
                f"{question['options'][question['answer']]}"
            )

            final_prize = last_safety_prize

            show_result(
                subject,
                current_question,
                final_prize,
                "INCORRECT"
            )
            return

        print(
            "\nYour current virtual winnings: "
            f"{format_rupees(final_prize)}"
        )

    print("\nINCREDIBLE! YOU COMPLETED ALL 16 QUESTIONS!")

    final_prize = PRIZE_LADDER[-1]

    show_result(
        subject,
        current_question,
        final_prize,
        "COMPLETED"
    )


def show_result(subject, question_number, prize, status):
    """Display the final game result."""

    print("\n" + "=" * 42)
    print("               GAME OVER")
    print("=" * 42)

    print(f"Subject: {subject}")
    print(f"Questions reached: {question_number}")
    print(f"Game status: {status}")
    print(f"Virtual winnings: {format_rupees(prize)}")

    if status == "COMPLETED":
        print("Congratulations! You reached the top prize!")

    print("\nThank you for playing Quiz Crorepati!")


def main():
    """Start the game and optionally allow replay."""

    while True:
        run_game()

        play_again = input(
            "\nWould you like to play again? (Y/N): "
        ).strip().upper()

        if play_again != "Y":
            print("\nThank you for playing. Goodbye!")
            break


if __name__ == "__main__":
    main()