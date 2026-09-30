import os

os.environ[
    "DATABASE_URL"
] = "sqlite:///./test_fitbuddy.db"

os.environ[
    "GEMINI_API_KEY"
] = ""


from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, engine


client = TestClient(app)


def reset_database():

    Base.metadata.drop_all(
        bind=engine
    )

    Base.metadata.create_all(
        bind=engine
    )


def test_home():

    reset_database()

    response = client.get("/")

    assert response.status_code == 200

    assert "FitBuddy" in response.text


def test_health():

    reset_database()

    response = client.get(
        "/api/health"
    )

    assert response.status_code == 200

    assert response.json()["status"] == "ok"


def test_generate_workout():

    reset_database()

    response = client.post(
        "/generate-workout",
        data={
            "username": "Test User",
            "user_id": "TEST001",
            "age": "20",
            "weight": "60",
            "goal": "general wellness",
            "intensity": "medium"
        }
    )

    assert response.status_code == 200

    assert "7-Day Workout Plan" in response.text


def test_feedback():

    reset_database()

    client.post(
        "/generate-workout",
        data={
            "username": "Feedback User",
            "user_id": "TEST002",
            "age": "20",
            "weight": "60",
            "goal": "fitness",
            "intensity": "medium"
        }
    )

    response = client.post(
        "/submit-feedback",
        data={
            "user_id": "TEST002",
            "feedback":
                "Add more mobility and recovery."
        },
        follow_redirects=False
    )

    assert response.status_code == 303

    assert "/user/TEST002" in (
        response.headers["location"]
    )


def test_api_generation():

    reset_database()

    response = client.post(
        "/api/generate-workout",
        json={
            "username": "API User",
            "user_id": "API001",
            "age": 20,
            "weight": 65,
            "goal": "fitness",
            "intensity": "low"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["user_id"] == "API001"

    assert data["plan_id"] > 0

    assert "workout_plan" in data


def test_admin_page():

    reset_database()

    response = client.get(
        "/view-all-users"
    )

    assert response.status_code == 200

    assert "All Users" in response.text