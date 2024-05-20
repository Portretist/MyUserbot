from typing import List

from sqlalchemy import select
import asyncio

from ..database import session
from ..models import User, StageOne, StageTwo, StageThree


async def get_user(user_id: int) -> str:
    try:
        result = asyncio.create_task(session.execute(select(User.status).where(User.id == user_id)))
        status = await result
        status = status.fetchone()[0]
        return status
    except Exception:
        return "No data"


async def get_users_by_group(group_type: str) -> List or str:
    if group_type == "group_1":
        result = asyncio.create_task(session.execute(select(StageOne.user, StageOne.created_at)))

    elif group_type == "group_2":
        result = asyncio.create_task(session.execute(select(StageTwo.user, StageTwo.created_at)))

    elif group_type == "group_3":
        result = asyncio.create_task(session.execute(select(StageThree.user, StageThree.created_at)))

    users = await result
    users = users.fetchall()
    if not users:
        return "No data"
    return users


