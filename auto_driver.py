from selenium.webdriver.support import expected_conditions as EC
from pyrogram import InlineKeyboardButton, InlineKeyboardMarkup
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium import webdriver
from datetime import datetime
from sql_backend import Database
import json, os, asyncio
from creds import Info
import re, sqlite3

time_to_wait = 40

async def recv(client, message):
    if os.path.exists("temp_time.json"):
        with open("temp_time.json", "r") as read_file:
            data = json.load(read_file)
        if message.chat.id !=  data["user"]:
            return 
        if len(data) == 1:
            date = re.search("[0-3]{1}\d{1}-[0-1]{1}\d{1}-\d{4}", message.text)
            if date is not None:
                data["date"] = date.group()
                await message.reply_text(quote=True, text="Now send the name of the lecture")
            else:
                await message.reply_text(quote=True, text="<b>Invalid Date/Format</b>")
                return 
        elif len(data) == 2:
            data["name"] = message.text
            await message.reply_text(quote=True, text="Now send the start and end time in 24HR format\n\n <code>Example : 8.30-9.30</code>")
        elif len(data) == 3:
            y = message.text.split("-", 1)
            start = str(y[0]).split('.')
            end = str(y[1]).split('.')
            p = (("{0}|{1:02}-{2:02}".format(data["date"], int(start[0]),int(start[1]))), ("{0}|{1:02}-{2:02}".format(data["date"], int(end[0]),int(end[1]))))
            print(p)
            data["start"] = p[0]
            data["end"] = p[1]
            await message.reply_text(quote=True, text="Now send me the lecture link")
        elif len(data) == 5:
            data["link"] = message.text
        with open("temp_time.json", "w") as writer:
            writer.writelines(json.dumps(data, indent=4))
        if len(data) == 6:
            db = Database()
            db.create_table(data["date"])
            try:
                db.insert(
                    data["date"],data["name"],
                    data["start"],data["end"],
                    data["link"]
                )
                db.commit()
                await message.reply_text(quote=True, text="Table successfully added !!")
            except sqlite3.IntegrityError:
                await message.reply_text("The lecture name should be unique :/ \n\n<i>Table Creation Failed😒</i>")
            os.remove("temp_time.json")
    # Filters incoming link adn joins the lecture
    elif("webex.com" in message.text):
        if os.path.isfile("session_handler.json"):
            await message.reply_text("Another Session Instance Found!!\n\nPlease close the instance using <code>/close</code> command")
            return False
        random_message = await message.reply_text(
            quote=True,
            text="Launching chrome..."
        )
        await auto_join(
            message.text,
            random_message
        )


async def json_writer(exec_url, session_id):
    with open("session_handler.json", "w") as writer:
        data = {"Date": datetime.now().strftime("%d/%m/%Y %H:%M:%S")}
        data["session_id"] = session_id; data["exec_url"] = exec_url
        writer.writelines(json.dumps(data, indent=2))


async def auto_join(meeting_link, message):
    if Info.GOOGLE_CHROME_BIN is None:
        await message.edit("need to install Google Chrome. Module Stopping.")
        return
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument("--test-type")
    options.add_argument("--headless")
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('window-size=1200x600')
    options.add_argument("--use-fake-ui-for-media-stream")
    options.binary_location = Info.GOOGLE_CHROME_BIN
    browser = webdriver.Chrome(chrome_options=options)
    await json_writer(browser.command_executor._url, browser.session_id)
    await message.edit("Chrome Launched, Fetching Link...")
    browser.get(meeting_link)
    # tried and failed :| StackOverFlow rescued 
    #https://stackoverflow.com/questions/61104794/how-to-login-to-webex-platform-with-selenium
    await message.edit("Now Working, Progress 20%")
    try:
        clickable = WebDriverWait(browser, time_to_wait).until(EC.element_to_be_clickable((By.ID, "smartJoinButton")))
        clickable.click()
        await message.edit("Now Working, Progress 40%")
        WebDriverWait(browser,time_to_wait).until(EC.frame_to_be_available_and_switch_to_it((By.ID,"pbui_iframe")))
        await message.edit("Now Working, Progress 60%")
        username = WebDriverWait(browser, time_to_wait).until(EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='Your full name']")))
        username.send_keys(Info.NAME)
        password = WebDriverWait(browser, time_to_wait).until(EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='Email address']")))
        password.send_keys(Info.MAIL)
        signin = browser.find_element_by_css_selector(".style-rest-1IrDU.style-theme-primary-2Khdp.style-size-large-1-1tY.style-botton-outline-none-1M0ur")
        signin.click()
        await message.edit("Now Working, Progress 80%")
        join_meeting = WebDriverWait(browser, time_to_wait).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".style-rest-1IrDU.style-theme-green-22KBC.style-join-button-yqbh_.style-size-huge-3dFcq.style-botton-outline-none-1M0ur")))
        join_meeting.click()
        await message.edit("Now Working, Progress 100%")
        await asyncio.sleep(1)
        await message.edit("<b>Successfully Joined</b>")
        while True:
            try:
                WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".style-room-info-1bmd5")))
                try:
                    WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".style-rest-1IrDU.style-theme-primary-2Khdp.style-size-large-1-1tY.style-botton-outline-none-1M0ur")))
                    print("waiting /////")
                    await asyncio.sleep(10)
                except:
                    pass
                    #browser.save_screenshot("meetingnotstarted.png")
                print("waiting \\\\")
                await asyncio.sleep(5)
            except TimeoutException:
                #browser.save_screenshot("notapproved.png")
                await message.reply_text("<b>The Meeting is either started or you been approved to join the meeting 😎👍</b>")
                break
        try:
            mic = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".menu-item.item-mute.btn-52.icon-unMute")))
            mic.click() # to mute urself
        except:
            await message.reply_text("<b>automatic mic disabling failed please make sure you are in the right page using <code>/screenshot</code> command and use <code>/mute</code> command</b>")
    except Exception:
        pass


async def toolkit(client, message):
    try: 
        _, session_id, exec_url = await json_reader()
        browser = attach_to_session(exec_url, session_id)
        await asyncio.sleep(1)
        if message.command[0] == "screenshot":
            browser.save_screenshot("screenshot.png")
            await client.send_photo(photo="screenshot.png", chat_id=message.chat.id)
            os.remove("screenshot.png")
        elif message.command[0] == "mute":
            msg = await message.reply_text("<b>processing...</b>")
            try:
                WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".menu-item.item-mute.btn-52.icon-unMute"))).click()
                await msg.edit("<b>mic muted</b>")
            except:
                await msg.edit("<b>Mic is either mute or element cannot be found</b>")
    except ValueError:
        await message.reply_text(text=await json_reader())


async def close_session(_, message):
    try: 
        date, _, _ = await json_reader()
        await message.reply_text(
            text=f"<b>Do you really want to close the session which was created at {date}?</b>",
            reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(text='Yes', callback_data='yes')],
                    [InlineKeyboardButton(text='No', callback_data='exit')],
                    [InlineKeyboardButton(text='Generate Screenshot and close', callback_data='ss')]])
        )
    except ValueError:
        await message.reply_text(text=await json_reader())


async def callback_handler(client, callback_query):
    cb_data = callback_query.data
    msg = callback_query.message
    await msg.delete()    
    if cb_data == 'yes' or cb_data == 'ss':
        if cb_data == "ss":
            await asyncio.sleep(5)
        try:
            _, session_id, exec_url = await json_reader()
            browser = attach_to_session(exec_url, session_id)
            browser.quit() ; os.remove("session_handler.json")
            await client.send_message(text="Session Closed", chat_id=msg.chat.id)
        except ValueError:
            await msg.reply_text(text=await json_reader())  
        except Exception:
            os.remove("session_handler.json") 
    # below code read the timetable.json file and list every date :) 
    elif cb_data == "list":
        list_message = await msg.reply_text("calculating")
        db = Database()
        data = db.print_all()
        # spend 1.30hr making the below list comp
        # below code generates InlineKeyboardButton list with date buttons ending with an exit button
        if len(data) == 0:
            await list_message.edit("No TimeTable Found 😎")
            return 
        list_comp = [[InlineKeyboardButton(text=x, callback_data=y)] for x,y in [("Exit", "exit") if x >= len(data) else (data[x][2], f"fetch={x}") for x in range(len(data) + 1)]]
        await list_message.edit(
            text="Please Select A Date",
            reply_markup=InlineKeyboardMarkup(list_comp)
        )
    # add creates a temporary json file - which triggers recv function
    elif cb_data == "add":
        with open("temp_time.json", "w") as writer:
            data = {'user': msg.chat.id} ; writer.writelines(json.dumps(data))
        await msg.reply_text("Send me the date in dd-mm-yyyy format")
    # fetches lecture list with the given key, in this case date
    elif "fetch" in cb_data:
        pos = int(cb_data.split("=", 1)[1])
        db_name = msg["reply_markup"]["inline_keyboard"][pos][0]["text"]
        db = Database()
        data = db.print(db_name)
        #  :/ same as above list comp instead of date this comp gen* lecture buttons
        markup = [[InlineKeyboardButton(text=x, callback_data=y)] for x,y in [("Exit", "exit") if x >= len(data) else (data[x][0], f"data={x}={db_name}") for x in range(len(data) + 1)]]
        await msg.reply_text(
            text="Please Select A Lecture",
            reply_markup=InlineKeyboardMarkup(markup)
        )
    # options for each lecture
    elif "data" in cb_data:
        pos, tabname = cb_data.split("=")[1:]
        lecture_name = msg["reply_markup"]["inline_keyboard"][int(pos)][0]["text"]
        db = Database()
        data = db.find_one(tabname, lecture_name)
        await msg.reply_text(
            text=f"Lecture name : {data[0]}\n\nstart time : {data[1]}\nend time : {data[2]}\nlink : {data[3]}",
            reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(text='load lecture', callback_data='load')],
                    [InlineKeyboardButton(text='delete lecture', callback_data=f'delete={tabname}={lecture_name}')],
                    [InlineKeyboardButton(text='Exit ', callback_data='exit')]])
        )
    # delete a lecture - using key {date} and index {position}
    elif "delete" in cb_data:
        tabname, lecture_name = cb_data.split("=")[1:]
        db = Database()
        db.delete_one(tabname, lecture_name)
        # if the last item of a key then delete the key :)
        if len(db.print(tabname)) == 0:
            db.delete_table(tabname)
        db.commit()
        await msg.reply_text(quote=True, text="Lecture deleted 😜")
    
    # LOAD LINK -- >
    elif cb_data == "load":
        print("Initiated Auto Join Link --> " + str(l := msg.text.split("\n")[-1].split(" ")[-1]))
        m = await client.send_message(msg.chat.id,"Loading Lecture")
        await auto_join(l, m)
    # °º¤ø,¸¸,ø¤º°`°º¤ø,¸,ø¤°º¤ø,¸¸,ø¤º°`°º¤ø,¸
    elif cb_data == 'exit':
        await msg.reply_text("understandable have a great day")

# https://stackoverflow.com/a/48194907/13033981
def attach_to_session(executor_url, session_id):
    original_execute = WebDriver.execute
    def new_command_execute(self, command, params=None):
        if command == "newSession":
            # Mock the response
            return {'success': 0, 'value': None, 'sessionId': session_id}
        else:
            return original_execute(self, command, params)
    # Patch the function before creating the driver object
    WebDriver.execute = new_command_execute
    driver = webdriver.Remote(command_executor=executor_url, desired_capabilities={})
    driver.session_id = session_id
    # Replace the patched function with original function
    WebDriver.execute = original_execute
    return driver


async def json_reader():
    if os.path.isfile("session_handler.json"):
        with open("session_handler.json", "r") as read_file:
            data = json.load(read_file)
            if len(data) != 3:
                return "Session data either corrupted or invalid"
            else:
                try:
                    return (data["Date"], data["session_id"], data["exec_url"])
                except KeyError:
                    return "Session data either corrupted or invalid"
    else:
        return "Soory No Active Session Found"

async def disconnect_handler(_):
    print("Initiated Disconnect Sequence")
    #os.remove("session_handler.json")

async def send_message(_, message):
    if len(message.command) == 1:
        await message.reply_text("Please give message input")
        return
    # Creating a lock object that blocks incoming multiple messages.
    # The below while loop keep the loop waiting untill previous message is finished sending.
    while os.path.exists("message.lock"):
        await asyncio.sleep(2)
    # Lock file is created for this instance
    else:
        with open("message.lock", "w") as _:
            pass
        try: 
            _, session_id, exec_url = await json_reader()
            browser = attach_to_session(exec_url, session_id)
            await asyncio.sleep(1)
            # Webdrive Stuffs :)
            chat_all = WebDriverWait(browser, time_to_wait).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".menu-item.icon-chat.item-chat.btn-52")))
            chat_all.click()
            text_space = WebDriverWait(browser, time_to_wait).until(EC.element_to_be_clickable((By.XPATH, "//textarea[@title='Enter your message for everyone']")))
            text_space.send_keys(" ".join(message.command[1:]))
            text_space.send_keys(Keys.ENTER)
            text_space.send_keys(Keys.ESCAPE)
            # Removing the lock
            os.remove("message.lock")
            print(f'send message : {" ".join(message.command[1:])}')
            await message.reply_text("Message Successfully Send", quote=True,)
        except ValueError:
            await message.reply_text(text=await json_reader())
        except Exception:
            os.remove("message.lock")


async def timetable(client, message):
    await client.send_message(
        text="Please select a option",
        chat_id=message.chat.id,
        reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(text='Add TimeTable', callback_data='add')],
                    [InlineKeyboardButton(text='List TimeTables', callback_data='list')],
                    [InlineKeyboardButton(text='Exit ', callback_data='exit')]])
        )