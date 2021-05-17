import sqlite3

from src.paths import DATABASE_PATH

DB = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
DB_CURSOR = DB.cursor()
DB_CURSOR.execute(
    """CREATE TABLE IF NOT EXISTS auth_data (email TEXT, password TEXT)"""
)
DB_CURSOR.execute(
    """CREATE TABLE IF NOT EXISTS devices (device_id TEXT)"""
)
DB_CURSOR.execute(
    """CREATE TABLE IF NOT EXISTS bots (email TEXT, password TEXT, sid TEXT, is_valid INTEGER, valid_time INTEGER)"""
)
DB.commit()


class DatabaseController:
    def set_auth_data(self, email: str, password: str):
        DB_CURSOR.execute("""SELECT email FROM auth_data WHERE email=?""", (email,))
        if DB_CURSOR.fetchone() is None:
            DB_CURSOR.execute("""INSERT INTO auth_data VALUES (?, ?)""", (email, password))
            DB.commit()

    def get_auth_data(self):
        DB_CURSOR.execute("""SELECT * FROM auth_data""")
        return DB_CURSOR.fetchall()

    def get_device_ids(self):
        DB_CURSOR.execute("""SELECT * FROM devices""")
        return DB_CURSOR.fetchall()

    def get_bots(self):
        DB_CURSOR.execute("""SELECT * FROM bots""")
        return DB_CURSOR.fetchall()

    def set_device_id(self, device_id: str):
        DB_CURSOR.execute("""INSERT INTO devices VALUES (?)""", (device_id,))
        DB.commit()

    def set_bots(self, accounts: list):
        for i in accounts:
            email = i.get("email")
            password = i.get("password")
            sid = i.get("sid")
            is_valid = i.get("isValid")
            valid_time = i.get("validTime")
            DB_CURSOR.execute("""INSERT INTO bots VALUES (?, ?, ?, ?, ?)""", (email, password, sid, is_valid, valid_time))
        DB.commit()

    def remove_account(self, email: str):
        DB_CURSOR.execute("""DELETE FROM auth_data WHERE email=?""", (email,))
        DB.commit()

    def remove_bot(self, email: str):
        DB_CURSOR.execute("""DELETE FROM bots WHERE email=?""", (email,))
        DB.commit()

    def clear_table(self, table_name: str):
        DB_CURSOR.execute(f"""DELETE FROM {table_name}""")
        DB.commit()
