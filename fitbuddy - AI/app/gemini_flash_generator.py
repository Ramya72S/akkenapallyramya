from .config import settings
from .gemini_client import generate_text
from .prompts import nutrition_prompt


def generate_nutrition_tip_with_flash(goal):

    prompt = nutrition_prompt(goal)

    if not settings.gemini_api_key:

        return (
            f"For a {goal} goal, focus on regular balanced meals, "
            "include nutritious protein and plant foods, drink water "
            "regularly, and prioritize sleep and recovery."
        )

    return generate_text(
        prompt,
        settings.ai_tip_model
    )
