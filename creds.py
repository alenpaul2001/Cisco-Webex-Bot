import os

class Info():
    MAIL = "test@gmail.com"
    NAME = "testname"
    BOT_TOKEN = ""  # BOT_TOKEN
    API_ID = 12345  # API_ID
    API_HASH = ""  # API_HASH
    IS_HEROKU = False
    SUDO_USER = 1234567  # user_id
    GOOGLE_CHROME_BIN = os.environ.get("GOOGLE_CHROME_BIN", None)
