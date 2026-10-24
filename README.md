# Quiz Crorepati — AI-Powered Quiz Website

Quiz Crorepati is a web-based quiz game inspired by the format of Indian television quiz shows. Players can select a subject, answer multiple-choice questions, use lifelines, track their scores, and view their game history.

This project is developed as a student project using Python and Flask, with a simple web interface and a database for user accounts and game history.

## Features

- User registration, login, and logout
- Six quiz subjects:
  - Biology
  - History
  - Mathematics
  - Science
  - Geography
  - General Knowledge
- Multiple-choice questions with four options
- Correct-answer feedback and explanations
- 16-question game format
- Virtual prize ladder with safe-prize milestones
- Three lifelines:
  - 50:50
  - Audience Poll
  - Phone-a-Friend
- Game history showing subject, score, prize, and result
- SQLite database for storing users and game records
- Gemini API integration for AI-generated questions
- Built-in question bank as a fallback when the AI service is unavailable or its free quota is exhausted
- Responsive website styling

## Technologies Used

- Python
- Flask
- HTML
- CSS
- JavaScript
- SQLite
- Google Gemini API
- Git and GitHub

## Project Structure

```text
Quiz-Crorepati/
├── app.py
├── main.py
├── question_bank.py
├── gemini_quiz.py
├── test_gemini.py
├── README.md
├── step-tracker.md
├── templates/
│   ├── index.html
│   ├── auth.html
│   └── history.html
└── static/
    ├── style.css
    └── script.js
```

*Note: The file list may vary depending on the latest version of the project.*

## Installation and Setup

### 1. Install Python

Install Python 3 if it is not already installed.

### 2. Open the project folder

Open the project folder in VS Code and open a terminal inside the folder containing `app.py`.

### 3. Install dependencies

```bash
pip install flask google-genai
```

### 4. Configure the Gemini API key (optional)

To enable AI-generated questions, obtain an API key through Google AI Studio and configure it as an environment variable.

In Windows PowerShell:

```powershell
$env:GEMINI_API_KEY = Read-Host "Enter your Gemini API key"
```

Enter the key when prompted. Do not publish your API key in GitHub or commit it to source files.

AI generation depends on the availability and quota of the selected Gemini model. The application can use its built-in question bank when AI generation is unavailable.

### 5. Run the application

```bash
python app.py
```

Open the local address shown in the terminal, usually:

http://127.0.0.1:5000

## How to Play

1. Register for an account or log in.
2. Select a quiz subject.
3. Start the game and answer the questions.
4. Use available lifelines when needed.
5. Earn virtual prizes for correct answers.
6. View completed games in Game History.

## Database

SQLite is used to store user account information, game state, and game history.

Passwords are stored as password hashes rather than plain text.

## Important Notes

- This is an educational student project and is not affiliated with or endorsed by Kaun Banega Crorepati or its owners.
- All prizes are virtual and have no monetary value.
- AI-generated questions depend on the external API's availability and usage limits.
- Never commit API keys, passwords, or other secrets to GitHub.

## Future Improvements

- Improve question variety and validation
- Add more detailed game statistics
- Improve mobile responsiveness and accessibility
- Add automated tests for game rules and database operations
- Improve error handling for AI-generated questions

## Author

Developed as a student project to practice Python, Flask, web development, database management, and API integration.
