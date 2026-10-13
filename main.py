print("===================================")
print("       QUIZ CROREPATI")
print("===================================")

print("\nWelcome to Quiz Crorepati!")
print("\nChoose your favourite subject:")

print("1. Biology")
print("2. History")
print("3. Mathematics")
print("4. Science")
print("5. Geography")
print("6. General Knowledge")

choice = input("\nEnter your choice (1-6): ")

subjects = {
    "1": "Biology",
    "2": "History",
    "3": "Mathematics",
    "4": "Science",
    "5": "Geography",
    "6": "General Knowledge"
}

if choice not in subjects:
    print("Invalid choice! Please run the program again.")
else:
    selected_subject = subjects[choice]

    print("\nYou selected:", selected_subject)
    print("\nLet's start your quiz!")

    print("\nQuestion 1")
    print("Which planet is known as the Red Planet?")

    print("A. Earth")
    print("B. Mars")
    print("C. Jupiter")
    print("D. Venus")

    answer = input("\nEnter your answer (A/B/C/D): ")
    answer = answer.strip().upper()

    if answer == "B":
        print("\nCorrect answer!")
    elif answer in ["A", "C", "D"]:
        print("\nSorry! The correct answer is B. Mars.")
    else:
        print("\nInvalid answer! Please enter A, B, C, or D.")