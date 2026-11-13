import os
import requests
from pathlib import Path
from dotenv import load_dotenv


# Loading .env file
base_path = Path(__file__).resolve().parent.parent
load_dotenv(base_path / ".env")


# Getting provider name
provider = os.getenv("LLM_PROVIDER", "gemini")


# Function to generate answer
def generate_answer(system_prompt, user_prompt):

    if provider == "gemini":

        api_key = os.getenv("GEMINI_API_KEY")
        model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

        if not api_key:
            raise ValueError("Gemini API key is missing")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

        data = {
            "system_instruction": {
                "parts": [{"text": system_prompt}]
            },
            "contents": [
                {
                    "parts": [{"text": user_prompt}]
                }
            ]
        }

        response = requests.post(url, json=data, timeout=60)

    elif provider == "groq":

        api_key = os.getenv("GROQ_API_KEY")
        model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

        if not api_key:
            raise ValueError("Groq API key is missing")

        url = "https://api.groq.com/openai/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {api_key}"
        }

        data = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        }

        response = requests.post(
            url,
            headers=headers,
            json=data,
            timeout=60
        )

    else:
        raise ValueError("Invalid LLM provider")

    # Checking API response
    if response.status_code != 200:
        raise ValueError(
            f"API Error {response.status_code}: {response.text}"
        )

    result = response.json()

    # Getting generated answer
    if provider == "gemini":
        return result["candidates"][0]["content"]["parts"][0]["text"]

    return result["choices"][0]["message"]["content"]