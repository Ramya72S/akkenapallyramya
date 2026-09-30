from .config import settings
from .gemini_client import generate_text
from .prompts import update_prompt


def update_workout_plan(
    original_plan,
    feedback,
    goal,
    intensity
):

    prompt = update_prompt(
        original_plan,
        feedback,
        goal,
        intensity
    )

    if not settings.gemini_api_key:

        return (
            original_plan
            + "\n\n"
            + "------------------------------\n"
            + "DEMO UPDATE\n"
            + "------------------------------\n"
            + f"User feedback received: {feedback}\n\n"
            + "Gemini is not configured, so the original plan "
              "is preserved in demo mode."
        )

    return generate_text(
        prompt,
        settings.ai_workout_model
    )