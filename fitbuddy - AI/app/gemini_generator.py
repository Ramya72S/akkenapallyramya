from .config import settings
from .gemini_client import generate_text
from .prompts import workout_prompt


def generate_workout_gemini(
    username,
    age,
    weight,
    goal,
    intensity
):

    prompt = workout_prompt(
        username,
        age,
        weight,
        goal,
        intensity
    )

    if not settings.gemini_api_key:

        return mock_workout(
            username,
            goal,
            intensity
        )

    return generate_text(
        prompt,
        settings.ai_workout_model
    )


def mock_workout(
    username,
    goal,
    intensity
):

    return f"""
FitBuddy Demo Workout Plan

Name: {username}
Goal: {goal.title()}
Intensity: {intensity.title()}

Day 1 — Full Body

Focus:
Full body movement.

Warm-up:
5–10 minutes of easy walking and gentle mobility.

Main Workout:
• Bodyweight squats
• Incline push-ups
• Glute bridges
• Comfortable walking

Rest:
Take comfortable breaks between exercises.

Cool-down:
Gentle stretching.

Day 2 — Cardio & Mobility

Focus:
Light cardio and mobility.

Warm-up:
5 minutes easy walking.

Main Workout:
20–30 minutes of comfortable cardio such as walking,
cycling, or another enjoyable activity.

Cool-down:
Gentle mobility.

Day 3 — Upper Body & Core

Focus:
Upper body and core.

Warm-up:
5–10 minutes.

Main Workout:
• Incline push-ups
• Supported rows
• Bird-dog
• Dead-bug variation

Rest:
Rest whenever needed.

Cool-down:
Gentle stretching.

Day 4 — Recovery

Focus:
Recovery.

Activity:
Easy walking and gentle mobility.

Recovery:
Hydration, balanced meals, and adequate sleep.

Day 5 — Lower Body

Focus:
Lower body.

Warm-up:
5–10 minutes.

Main Workout:
• Bodyweight squats
• Step-ups
• Glute bridges
• Calf raises

Rest:
Use comfortable rest periods.

Cool-down:
Gentle stretching.

Day 6 — Fun Cardio

Focus:
Enjoyable movement.

Activity:
Walking, cycling, dancing, or another safe activity.

Keep the intensity comfortable and take breaks.

Day 7 — Rest & Reflection

Focus:
Recovery.

Activity:
Rest or gentle mobility.

Think about which activities felt comfortable and enjoyable.

DEMO MODE

Gemini API is not configured.

Add GEMINI_API_KEY to .env to activate real Gemini generation.
"""