import sqlite3


class Database(object):

    db_path = "timetable.db"

    def __init__(self):
        self.connection = sqlite3.connect(Database.db_path)
        self.cursor = self.connection.cursor()

    def create_table(self, name):
        """create a database table if it does not exist already"""
        self.cursor.execute(f'''CREATE TABLE IF NOT EXISTS [{name}](lecture_name text UNIQUE, \
                                                            start real,
                                                            end real,
                                                            link text)''')

    def delete_table(self, name):
        self.cursor.execute(f"DROP TABLE IF EXISTS '{name}'")

    def __del__(self):
        self.connection.close()

    def print_all(self):
        return self.cursor.execute("SELECT * FROM sqlite_master WHERE type='table'").fetchall()

    def insert(self, tabname, lecture_name, start, end, link):
        self.cursor.execute(f"INSERT INTO [{tabname}] VALUES (:name, :start, :end, :link)",
                            {"name": lecture_name, "start": start, "end": end, "link": link})

    def print(self, name):
        return self.cursor.execute(f"SELECT * FROM [{name}]").fetchall()

    def commit(self):
        self.connection.commit()

    def find_one(self, tabname, lecture_name):
        return self.cursor.execute(f"""SELECT lecture_name, start, end, link
        FROM [{tabname}] WHERE lecture_name='{lecture_name}'""").fetchone()

    def delete_one(self, tabname, lecture_name):
        return self.cursor.execute(f"""DELETE
        FROM [{tabname}] WHERE lecture_name='{lecture_name}'""")
