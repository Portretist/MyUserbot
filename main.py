import asyncio
from pyrogram import Client, filters
from pyrogram.errors import UserDeactivated, UserBlocked

from database.database import session, engine
from database import CRUD
from database import models

api_id = 12345
api_hash = "some api hash"
chat_id = -6789
app = Client("my_account", api_id=api_id, api_hash=api_hash)

message_for_group_1 = "Текст1"
message_for_group_2 = "Текст2"
message_for_group_3 = "Текст3"


@app.on_message(filters.text & filters.chat(chat_id))
async def message_handler(client, message):
    """
    Обработчик сообщения.
    Отлавливает сообщения и передаёт их в работу функции 'check_message'.
    :param client:
    :param message:
    """
    await asyncio.create_task(CRUD.check_message(message))


async def main():
    """
    Main.
    При запуске ждёт у минуту, после чего запускает бесконечный цикл проверки пользователей на готовность
    получить сообщение, соответствующие уровню воронки. При наличии готовых к получению сообщения пользователей
    отправляет им соответствующее сообщение.
    """
    await asyncio.sleep(60)
    while True:
        groups = await asyncio.create_task(CRUD.check_users_for_sending_message())
        for group_type, group in groups.items():
            if group != "No data":
                if group_type == "group_1":
                    message = message_for_group_1
                elif group_type == "group_1":
                    message = message_for_group_2
                elif group_type == "group_1":
                    message = message_for_group_3
                for group_member in group:
                    try:
                        await app.send_message(group_member, message)

                    except (UserDeactivated, UserBlocked):
                        await asyncio.create_task(CRUD.update_data.update_status("dead", group_member))
                        await asyncio.create_task(CRUD.delete_data.force_delete_records(group_member))
                        await session.commit()
                        new_group_list = list(groups[group_type])
                        new_group_list.remove(group_member)
                        groups[group_type] = tuple(new_group_list)

                    await asyncio.sleep(0.005)

        await asyncio.create_task(CRUD.change_group_and_status(groups))
        await session.commit()
        await asyncio.sleep(60)


async def run():
    """
    Run.
    Инициализация таблиц баз данных. Запуск работы приложения. Остановка работы приложения.
    """
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    await asyncio.gather(app.start(), main())
    await app.stop()


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(run())
