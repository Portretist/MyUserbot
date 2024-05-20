from ..database import session
from ..models import User, StageOne, StageTwo, StageThree


async def add_user(user_id) -> None:
    user = User(id=user_id)
    session.add(user)


async def add_record(group_type, user_id) -> None:
    if group_type == "group_1":
        record = StageOne(user=user_id)
    elif group_type == "group_2":
        record = StageTwo(user=user_id)
    elif group_type == "group_3":
        record = StageThree(user=user_id)

    session.add(record)

