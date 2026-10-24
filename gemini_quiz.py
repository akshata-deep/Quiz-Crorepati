
import json
import os
from google import genai
from google.genai import types


def generate_quiz_questions(subject):
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError("Gemini API key is not set.")

    client = genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(timeout=120000)
    )

    prompt = f"""
Create exactly 16 multiple-choice questions for the subject: {subject}.

Requirements:
- Suitable for a general educational quiz.
- Four options per question.
- Exactly one correct option.
- Include a short explanation.
- Vary the difficulty from easy to medium.
- Avoid duplicate questions.
- Return ONLY a valid JSON array, without Markdown.

Use this exact structure for every question:
{{
  "question": "Question text",
  "options": ["Option A", "Option B", "Option C", "Option D"],
  "answer": "The exact text of the correct option",
  "explanation": "Short explanation"
}}
"""

    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json"
        )
    )

    questions = json.loads(response.text)

    if not isinstance(questions, list) or len(questions) != 16:
        raise ValueError("Gemini did not return exactly 16 questions.")

    for question in questions:
        if not all(
            key in question
            for key in ("question", "options", "answer", "explanation")
        ):
            raise ValueError("A generated question is missing required fields.")

        if len(question["options"]) != 4:
            raise ValueError("Every question must have four options.")

        if question["answer"] not in question["options"]:
            raise ValueError("The correct answer must match an option.")

    return questions
