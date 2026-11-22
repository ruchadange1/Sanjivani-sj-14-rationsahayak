import logging
import os
import time
import uuid
from pathlib import Path

import requests
from dotenv import load_dotenv

# Loading .env file
base_path = Path(__file__).resolve().parent.parent
load_dotenv(base_path / ".env")

# Getting provider name
provider = os.getenv("LLM_PROVIDER", "gemini")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ration_sahayak")


def generate_answer(system_prompt, user_prompt):

    request_id = str(uuid.uuid4())[:8]
    start_time = time.perf_counter()

    input_tokens = 0
    output_tokens = 0
    status = "success"

    try:

        if provider == "gemini":

            api_key = os.getenv("GEMINI_API_KEY")
            model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

            if not api_key:
                raise ValueError("Gemini API key is missing")

            url = (
                f"https://generativelanguage.googleapis.com/v1beta/"
                f"models/{model}:generateContent?key={api_key}"
            )

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

            response = requests.post(url, json=data, timeout=120)

        elif provider == "groq":

            api_key = os.getenv("GROQ_API_KEY")
            model = os.getenv(
                "GROQ_MODEL",
                "llama-3.3-70b-versatile"
            )

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
                timeout=120
            )

        else:
            raise ValueError("Invalid LLM provider")

        if response.status_code != 200:
            raise ValueError(
                f"API Error {response.status_code}: {response.text}"
            )

        result = response.json()

        # Extract token usage
        usage = result.get("usageMetadata", {}) if provider == "gemini" else result.get("usage", {})

        if provider == "gemini":
            input_tokens = usage.get("promptTokenCount", 0)
            output_tokens = usage.get("candidatesTokenCount", 0)

            answer = result["candidates"][0]["content"]["parts"][0]["text"]

        else:
            input_tokens = usage.get("prompt_tokens", 0)
            output_tokens = usage.get("completion_tokens", 0)

            answer = result["choices"][0]["message"]["content"]

        return answer

    except Exception:
        status = "failed"
        raise

    finally:

        latency = time.perf_counter() - start_time

        logger.info(
            "[LLM METRICS] request_id=%s provider=%s "
            "latency_seconds=%.3f input_tokens=%s "
            "output_tokens=%s total_tokens=%s status=%s",
            request_id,
            provider,
            latency,
            input_tokens,
            output_tokens,
            input_tokens + output_tokens,
            status
        )