from fastapi import (
    APIRouter,
    Depends,
    Form,
    HTTPException,
    Request
)

from fastapi.responses import (
    HTMLResponse,
    RedirectResponse
)

from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session

from .crud import (
    delete_user,
    get_all_plans,
    get_all_users,
    get_latest_plan,
    save_plan,
    save_user,
    update_plan
)

from .database import get_db

from .gemini_flash_generator import (
    generate_nutrition_tip_with_flash
)

from .gemini_generator import (
    generate_workout_gemini
)

from .schemas import (
    FeedbackRequest,
    UserInput
)

from .updated_plan import (
    update_workout_plan
)


router = APIRouter()


templates = Jinja2Templates(
    directory="app/templates"
)


@router.get(
    "/",
    response_class=HTMLResponse
)
def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "error": None
        }
    )


@router.post(
    "/generate-workout",
    response_class=HTMLResponse
)
def generate_workout(

    request: Request,

    username: str = Form(...),

    user_id: str = Form(...),

    age: int = Form(...),

    weight: float = Form(...),

    goal: str = Form(...),

    intensity: str = Form(...),

    db: Session = Depends(get_db)
):

    try:

        data = UserInput(
            username=username,
            user_id=user_id,
            age=age,
            weight=weight,
            goal=goal,
            intensity=intensity
        )

        user = save_user(
            db,
            data
        )

        workout_plan = generate_workout_gemini(
            data.username,
            data.age,
            data.weight,
            data.goal,
            data.intensity
        )

        nutrition_tip = (
            generate_nutrition_tip_with_flash(
                data.goal
            )
        )

        plan = save_plan(
            db,
            user,
            workout_plan,
            nutrition_tip
        )

        return templates.TemplateResponse(
            request=request,
            name="result.html",
            context={
                "user": user,
                "plan": plan,
                "workout_plan": workout_plan,
                "nutrition_tip": nutrition_tip,
                "message": None,
                "error": None
            }
        )

    except Exception as exc:

        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "error": str(exc)
            },
            status_code=400
        )


@router.post(
    "/submit-feedback",
    response_class=HTMLResponse
)
def submit_feedback(

    request: Request,

    user_id: str = Form(...),

    feedback: str = Form(...),

    db: Session = Depends(get_db)
):

    user, plan = get_latest_plan(
        db,
        user_id
    )

    if not user or not plan:

        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "error":
                    "User ID was not found. "
                    "Generate a plan first."
            },
            status_code=404
        )

    if len(feedback.strip()) < 3:

        return templates.TemplateResponse(
            request=request,
            name="result.html",
            context={
                "user": user,
                "plan": plan,
                "workout_plan":
                    plan.updated_plan
                    or plan.original_plan,
                "nutrition_tip":
                    plan.nutrition_tip,
                "message": None,
                "error":
                    "Please provide more specific feedback."
            },
            status_code=400
        )

    try:

        revised_plan = update_workout_plan(
            plan.original_plan,
            feedback,
            user.goal,
            user.intensity
        )

        update_plan(
            db,
            plan,
            revised_plan,
            feedback
        )

        return RedirectResponse(
            url=f"/user/{user.user_id}?updated=1",
            status_code=303
        )

    except Exception as exc:

        return templates.TemplateResponse(
            request=request,
            name="result.html",
            context={
                "user": user,
                "plan": plan,
                "workout_plan":
                    plan.updated_plan
                    or plan.original_plan,
                "nutrition_tip":
                    plan.nutrition_tip,
                "message": None,
                "error":
                    f"Could not update plan: {exc}"
            },
            status_code=500
        )


@router.get(
    "/user/{user_id}",
    response_class=HTMLResponse
)
def user_result(

    request: Request,

    user_id: str,

    updated: int = 0,

    db: Session = Depends(get_db)
):

    user, plan = get_latest_plan(
        db,
        user_id
    )

    if not user or not plan:

        raise HTTPException(
            status_code=404,
            detail="User or plan not found"
        )

    return templates.TemplateResponse(
        request=request,
        name="result.html",
        context={
            "user": user,
            "plan": plan,
            "workout_plan":
                plan.updated_plan
                or plan.original_plan,
            "nutrition_tip":
                plan.nutrition_tip,
            "message":
                "Plan updated successfully."
                if updated
                else None,
            "error": None
        }
    )


@router.get(
    "/view-all-users",
    response_class=HTMLResponse
)
def view_all_users(

    request: Request,

    db: Session = Depends(get_db)
):

    users = get_all_users(db)

    plans = get_all_plans(db)

    plan_map = {
        plan.user_id: plan
        for plan in plans
    }

    return templates.TemplateResponse(
        request=request,
        name="all_users.html",
        context={
            "users": users,
            "plan_map": plan_map
        }
    )


@router.post(
    "/delete-user/{user_id}"
)
def remove_user(

    user_id: str,

    db: Session = Depends(get_db)
):

    delete_user(
        db,
        user_id
    )

    return RedirectResponse(
        url="/view-all-users",
        status_code=303
    )


# =====================================================
# REST API
# =====================================================


@router.get(
    "/api/health"
)
def api_health():

    return {
        "status": "ok",
        "service": "FitBuddy API"
    }


@router.post(
    "/api/generate-workout"
)
def api_generate_workout(

    data: UserInput,

    db: Session = Depends(get_db)
):

    user = save_user(
        db,
        data
    )

    workout = generate_workout_gemini(
        data.username,
        data.age,
        data.weight,
        data.goal,
        data.intensity
    )

    tip = generate_nutrition_tip_with_flash(
        data.goal
    )

    plan = save_plan(
        db,
        user,
        workout,
        tip
    )

    return {
        "user_id": user.user_id,
        "plan_id": plan.id,
        "workout_plan": workout,
        "nutrition_tip": tip
    }


@router.post(
    "/api/feedback"
)
def api_feedback(

    data: FeedbackRequest,

    db: Session = Depends(get_db)
):

    user, plan = get_latest_plan(
        db,
        data.user_id
    )

    if not user or not plan:

        raise HTTPException(
            status_code=404,
            detail="User or plan not found"
        )

    revised = update_workout_plan(
        plan.original_plan,
        data.feedback,
        user.goal,
        user.intensity
    )

    update_plan(
        db,
        plan,
        revised,
        data.feedback
    )

    return {
        "user_id": user.user_id,
        "plan_id": plan.id,
        "updated_plan": revised,
        "feedback": data.feedback
    }