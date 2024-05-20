from sqlalchemy import delete
import asyncio

from ..database import session
from ..models import StageOne, StageTwo, StageThree


async def delete_record(group_type, user_id) -> None:
    if group_type == "group_1":
        task = asyncio.create_task(
            session.execute(delete(StageOne).where(StageOne.user == user_id))
        )
    elif group_type == "group_2":
        task = asyncio.create_task(
            session.execute(delete(StageTwo).where(StageTwo.user == user_id))
        )
    elif group_type == "group_3":
        task = asyncio.create_task(
            session.execute(delete(StageThree).where(StageThree.user == user_id))
        )
    await task


async def force_delete_records(user_id) -> None:
    g_1 = asyncio.create_task(session.execute(delete(StageOne).where(StageOne.user == user_id)))
    g_2 = asyncio.create_task(session.execute(delete(StageTwo).where(StageTwo.user == user_id)))
    g_3 = asyncio.create_task(session.execute(delete(StageThree).where(StageThree.user == user_id)))

    [await task for task in (g_1, g_2, g_3)]
