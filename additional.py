from functools import wraps
import sqlite3 as sql

with open("token.txt", 'r') as file:
    token = file.read()


def with_cursor(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        conn = sql.connect('bot.db')
        cursor = conn.cursor()
        result = func(cursor, *args, **kwargs)
        conn.commit()
        cursor.close()
        conn.close()
        return result

    return wrapper
