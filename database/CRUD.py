import asyncio
import re
from datetime import datetime
from typing import Tuple, Dict

from .database import session
from .utils import create_data, read_data, update_data, delete_data


async def ready_to_send(user_data: Tuple, group_type: str) -> bool:
    cur_time = datetime.now()
    timedelta = cur_time - user_data[1]
    if group_type == "group_1":
        if (timedelta.seconds % 3600) // 60 >= 6:
            return True
    elif group_type == "group_2":
        if (timedelta.seconds % 3600) // 60 >= 39:
            return True
    elif group_type == "group_3":
        if timedelta.day >= 1:
            if timedelta // 3600 >= 2:
                return True

    return False


async def check_group_member_to_send_message(group: Tuple, group_type: str) -> Tuple:
    members_to_send = []
    for group_member in group:
        check_result = await ready_to_send(group_member, group_type)
        if check_result is True:
            members_to_send.append(group_member[0])
    return tuple(members_to_send)


async def check_chat_member(message) -> str:
    user_id = message.from_user.id
    get_user_status = asyncio.create_task(read_data.get_user(user_id))
    user = await get_user_status
    if user == "No data":
        add_user_in_db = asyncio.create_task(create_data.add_user(user_id))
        await add_user_in_db
        await session.commit()
        add_record_s_one = asyncio.create_task(create_data.add_record("group_1", user_id))
        await add_record_s_one
        await session.commit()
        return await asyncio.create_task(check_chat_member(message))
    return user


async def check_word(word: str) -> bool:
    if word.lower() in ("прекрасно", "ожидать"):
        return False
    return True


async def check_message(message) -> None:
    check_status = asyncio.create_task(check_chat_member(message))
    status = await check_status
    if status == "alive":
        words = re.findall(r"\w+", message.text)
        if not all([await check_word(word) for word in words]):
            await update_data.update_status(new_status="dead", message=message)
            await delete_data.force_delete_records(message.from_user.id)
            await session.commit()
        else:
            await asyncio.create_task(check_member_group_2(message))
            await session.commit()


async def check_member_group_2(message) -> None:
    members = await read_data.get_users_by_group("group_2")
    user_id = message.from_user.id
    for member in members:
        if user_id == member[0]:
            data = {"group_1": "No data", "group_2": (user_id,), "group_3": "No data"}
            await asyncio.create_task(change_group_and_status(data))


async def check_users_for_sending_message() -> Dict:
    to_send_message_list = []
    group_1 = asyncio.create_task(read_data.get_users_by_group("group_1"))
    group_2 = asyncio.create_task(read_data.get_users_by_group("group_2"))
    group_3 = asyncio.create_task(read_data.get_users_by_group("group_3"))

    group_1, group_2, group_3 = [await func for func in (group_1, group_2, group_3)]

    for group in ((group_1, "group_1"), (group_2, "group_2"), (group_3, "group_3")):
        if group[0] != "No data":
            to_send = asyncio.create_task(
                check_group_member_to_send_message(group[0], group[1])
            )
        else:
            to_send = group[0]
        to_send_message_list.append(to_send)

    group_1, group_2, group_3 = [await task if task != "No data" else task for task in to_send_message_list]
    return {"group_1": group_1, "group_2": group_2, "group_3": group_3}


async def change_group_and_status(groups) -> None:
    change_group_list = []
    change_status_list = []
    for group_name, group_members in groups.items():
        if group_members != "No data":
            for group_member in group_members:
                delete_task = asyncio.create_task(
                    delete_data.delete_record(group_name, group_member)
                )
                change_group_list.append(delete_task)
                if group_name != "group_3":
                    if group_name == "group_1":
                        to_group = "group_2"
                    else:
                        to_group = "group_3"

                    create_task = asyncio.create_task(
                        create_data.add_record(to_group, group_member)
                    )
                    change_group_list.append(create_task)
                else:
                    update_task = update_data.update_status("finished", group_member)
                    change_status_list.append(update_task)

    [await task for task in change_group_list]
    [await tsk for tsk in change_status_list]
