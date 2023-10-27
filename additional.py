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


@with_cursor
def load_games_aliases(cursor):
    cursor.execute("SELECT * FROM roles")
    rows = cursor.fetchall()
    games = {row[0]: row[1] for row in rows}

    cursor.execute("SELECT * FROM aliases")
    rows = cursor.fetchall()
    aliases = {row[0]: row[1] for row in rows}

    return games, aliases


games, aliases = load_games_aliases()
