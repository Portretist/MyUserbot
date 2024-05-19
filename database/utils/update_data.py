import asyncio
from sqlalchemy import update
from datetime import datetime

from ..database import session
from ..models import User


async def update_status(new_status: str, message) -> None:
    cur_time = datetime.now()
    task = asyncio.create_task(
        session.execute(
            update(User).where(User.id == message.from_user.id).values(status=new_status, status_updated_at=cur_time)
        )
    )
    await task
