from sql_backend import Database
from datetime import date, datetime
from creds import Info
import asyncio

form = "%d-%m-%Y|%H-%M"


async def dump():
    while True:
        print("hello")
        await asyncio.sleep(5)


async def dummy(link, message):
    await message.edit(link)


async def from_db():
    db = Database()
    today = date.today().strftime("%d-%m-%Y")
    return [db.print(table_name) for table_name in [schema[2] for schema in db.print_all() if schema[2] == today]][0]


async def sync(client, _):
    todays_schedules = await from_db()
    for lectures in todays_schedules:
        lecture_time = datetime.strptime(lectures[1], form)
        current_time = datetime.now()
        time_delta = lecture_time - current_time
        asyncio.create_task(scheduler(time_delta.seconds, lectures[-1], client), name=lectures[0])


async def sync_cancel(c, m):
    tasks = [x[0] for x in await from_db()]
    for task in tasks:
        for async_tasks in asyncio.all_tasks():
            print(task)
            print(async_tasks.get_name())
            if async_tasks.get_name() == task:


async def scheduler(seconds, link, client):
    await asyncio.sleep(seconds)
    message = await client.send_message(Info.SUDO_USER, "starting func")
    await dummy(link, message)
