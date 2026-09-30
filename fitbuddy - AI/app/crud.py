from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import User, WorkoutPlan
from .schemas import UserInput


def get_user(
    db: Session,
    user_id: str
):

    return db.scalar(
        select(User)
        .where(User.user_id == user_id)
    )


def save_user(
    db: Session,
    data: UserInput
):

    user = get_user(
        db,
        data.user_id
    )

    if user:

        user.username = data.username
        user.age = data.age
        user.weight = data.weight
        user.goal = data.goal
        user.intensity = data.intensity

    else:

        user = User(
            user_id=data.user_id,
            username=data.username,
            age=data.age,
            weight=data.weight,
            goal=data.goal,
            intensity=data.intensity
        )

        db.add(user)

    db.commit()
    db.refresh(user)

    return user


def save_plan(
    db: Session,
    user: User,
    workout_plan: str,
    nutrition_tip: str
):

    plan = WorkoutPlan(
        user_id=user.id,
        original_plan=workout_plan,
        nutrition_tip=nutrition_tip
    )

    db.add(plan)

    db.commit()
    db.refresh(plan)

    return plan


def get_latest_plan(
    db: Session,
    user_id: str
):

    user = get_user(
        db,
        user_id
    )

    if not user:
        return None, None

    plan = db.scalar(
        select(WorkoutPlan)
        .where(
            WorkoutPlan.user_id == user.id
        )
        .order_by(
            WorkoutPlan.id.desc()
        )
    )

    return user, plan


def update_plan(
    db: Session,
    plan: WorkoutPlan,
    updated_plan: str,
    feedback: str
):

    plan.updated_plan = updated_plan
    plan.feedback = feedback

    plan.updated_at = datetime.now(
        timezone.utc
    )

    db.commit()
    db.refresh(plan)

    return plan


def get_all_users(db: Session):

    return db.scalars(
        select(User)
        .order_by(User.id.desc())
    ).all()


def get_all_plans(db: Session):

    return db.scalars(
        select(WorkoutPlan)
        .order_by(WorkoutPlan.id.desc())
    ).all()


def delete_user(
    db: Session,
    user_id: str
):

    user = get_user(
        db,
        user_id
    )

    if not user:
        return False

    db.delete(user)
    db.commit()

    return True