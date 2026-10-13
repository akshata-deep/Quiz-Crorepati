
print("===================================")
print("       QUIZ CROREPATI")
print("===================================")

print("\nWelcome to Quiz Crorepati!")
print("\nChoose your favourite subject:")

subjects = {
    "1": "Biology",
    "2": "History",
    "3": "Mathematics",
    "4": "Science",
    "5": "Geography",
    "6": "General Knowledge"
}

for number, subject in subjects.items():
    print(f"{number}. {subject}")

choice = input("\nEnter your choice (1-6): ").strip()

if choice not in subjects:
    print("Invalid choice! Please run the program again.")

else:
    selected_subject = subjects[choice]

    print(f"\nYou selected: {selected_subject}")
    print("\nLet's start your quiz!")

    questions = [
        {
            "question": "Which planet is known as the Red Planet?",
            "options": ["A. Earth", "B. Mars", "C. Jupiter", "D. Venus"],
            "answer": "B"
        },
        {
            "question": "How many sides does a triangle have?",
            "options": ["A. Two", "B. Four", "C. Three", "D. Five"],
            "answer": "C"
        },
        {
            "question": "Which gas do plants absorb during photosynthesis?",
            "options": [
                "A. Oxygen",
                "B. Nitrogen",
                "C. Hydrogen",
                "D. Carbon dioxide"
            ],
            "answer": "D"
        },
        {
            "question": "What is 8 multiplied by 7?",
            "options": ["A. 54", "B. 56", "C. 64", "D. 48"],
            "answer": "B"
        },
        {
            "question": "Which is the largest ocean on Earth?",
            "options": [
                "A. Indian Ocean",
                "B. Arctic Ocean",
                "C. Pacific Ocean",
                "D. Atlantic Ocean"
            ],
            "answer": "C"
        }
    ]

    score = 0

    for number, question_data in enumerate(questions, start=1):
        print(f"\nQuestion {number}:")
        print(question_data["question"])

        for option in question_data["options"]:
            print(option)

        answer = input("Enter your answer (A/B/C/D): ").strip().upper()

        if answer not in ["A", "B", "C", "D"]:
            print("Invalid option! This question will not earn a point.")

        elif answer == question_data["answer"]:
            print("Correct answer!")
            score += 1

        else:
            print(
                f"Incorrect! The correct answer is "
                f"{question_data['answer']}."
            )

    print("\n===================================")
    print("           QUIZ RESULT")
    print("===================================")
    print(f"Subject selected: {selected_subject}")
    print(f"Your score: {score}/{len(questions)}")
    print(f"Percentage: {score / len(questions) * 100:.0f}%")
    print("Thank you for playing Quiz Crorepati!")
