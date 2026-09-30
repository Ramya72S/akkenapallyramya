import time

from google import genai

from .config import settings


_client = None


def get_client():

    global _client

    if not settings.gemini_api_key:
        return None

    if _client is None:

        _client = genai.Client(
            api_key=settings.gemini_api_key
        )

    return _client


def generate_text(
    prompt: str,
    model: str
):

    client = get_client()

    if client is None:

        raise RuntimeError(
            "Gemini API key is not configured. "
            "Please check GEMINI_API_KEY in your .env file."
        )

    if not model:

        raise RuntimeError(
            "Gemini model is not configured. "
            "Please check AI_WORKOUT_MODEL in your .env file."
        )

    last_error = None

    # Retry temporary Gemini 503/429/server errors.
    for attempt in range(4):

        try:

            response = client.models.generate_content(
                model=model,
                contents=prompt
            )

            text = getattr(
                response,
                "text",
                None
            )

            if not text:

                raise RuntimeError(
                    "Gemini returned an empty response."
                )

            return text.strip()

        except Exception as exc:

            last_error = exc

            error_text = str(exc)

            # Retry temporary server/rate-limit errors.
            is_temporary_error = (
                "503" in error_text
                or "UNAVAILABLE" in error_text.upper()
                or "429" in error_text
                or "RESOURCE_EXHAUSTED" in error_text.upper()
                or "500" in error_text
                or "INTERNAL" in error_text.upper()
            )

            if not is_temporary_error:

                raise RuntimeError(
                    f"Gemini API error: {error_text}"
                ) from exc

            # Do not retry forever.
            if attempt == 3:
                break

            wait_seconds = 2 ** attempt

            time.sleep(wait_seconds)

    raise RuntimeError(
        "Gemini is temporarily unavailable after "
        "multiple attempts. "
        f"Model: {model}. "
        f"Last error: {last_error}"
    ) from last_error
