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
                async_tasks.cancel()

# print(datetime.now() - current_time)
# j = [tuples for table_list in all_entries for tuples in table_list]
# sorted_time = sorted(j, key=cmp_to_key(sort_func))
# print(sorted_time)
# for items in sorted_time:
#     if str(today) == items[1].split("|")[0]:
#         print("hmm")

    # print(items[1].split("|")[0])
# print(str(today))

# a = time.strptime("30-10-2001-09-30", "%d-%m-%Y-%H-%M")
# b = time.strptime("30-09-2001-09-41", "%d-%m-%Y-%H-%M")


async def scheduler(seconds, link, client):
    await asyncio.sleep(seconds)
    message = await client.send_message(Info.SUDO_USER, "starting func")
    await dummy(link, message)
