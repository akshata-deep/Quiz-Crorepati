
from google import genai
from google.genai import types
import os

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("API key is missing. Set it in this terminal.")
else:
    try:
        print("Connecting to Gemini...")

        client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(timeout=120000)
        )

        print("Sending test question...")

        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=(
                "Create one easy Biology multiple-choice question "
                "with four options and identify the correct answer."
            )
        )

        print("\nGemini response:")
        print(response.text)

    except Exception as error:
        print("\nGemini test failed:")
        print(type(error).__name__)
        print(error)
