import sqlite3
from main import games, aliases

conn = sqlite3.connect('bot.db')
cursor = conn.cursor()

users_roles = [
    ("335762220", "@themaximkol",
     ["Last of Us", "Deep Rock", "Persona", "Better Call Saul", "Breaking Bad", "Cyberpunk 2077", "Counter Strike",
      "Yakuza"]),
    ("428717189", "@lukasobaka",
     ["Last of Us", "Breaking Bad", "Анімедібылы общий сбор", "Resident Evil", "Deep Rock", "Cyberpunk 2077",
      "Counter Strike", "Yakuza", "Tyler, the Creator"]),
    ("694949879", "@maosttra",
     ["Over", "Deep Rock", "Bleach", "Persona", "Better Call Saul", "Breaking Bad", "Resident Evil", "Last of Us",
      "Yakuza", "Анімедібылы общий сбор"]),
    ("160274125", "@KnowNoth1ng",
     ["Over", "Dota", "Deep Rock", "Baldur's gate 3", "Bleach", "Persona", "KEVIN", "One Piece", "Better Call Saul",
      "Breaking Bad", "Анімедібылы общий сбор", "Resident Evil", "Cyberpunk 2077",
      "Counter Strike", "Last of Us", "Yakuza", "Jujutsu Kaisen", "Ретроёбы"]),
    ("146943636", "@pink_wild_cherry",
     ["Bleach", "One Piece", "Better Call Saul", "Breaking Bad", "Анімедібылы общий сбор", "Jujutsu Kaisen", "Persona",
      "Tyler, the Creator"]),
    ("744197313", "@shidler_nm",
     ["Over", "Bleach", "KEVIN", "One Piece", "Анімедібылы общий сбор", "Resident Evil", "Yakuza", "Jujutsu Kaisen",
      "Ретроёбы", "Tyler, the Creator"]),
    ("761982075", "@Doomfisting2004",
     ["Over", "Dota", "Bleach", "One Piece", "Baldur's gate 3", "Deep Rock", "Counter Strike", "Вахоёбы",
      "Анімедібылы общий сбор"]),
    ("87600842", "@MedvedNikki",
     ["Baldur's gate 3", "KEVIN", "One Piece", "Breaking Bad", "Cyberpunk 2077", "Вахоёбы", "Bleach",
      "Jujutsu Kaisen"]),
    ("628793236", "@Pavlo_D_A", ["Persona", "Breaking Bad", "Анімедібылы общий сбор", "Yakuza", "Вахоёбы", "Ретроёбы"]),
    ("552126018", "@TerribleRick132", ["Better Call Saul", "Breaking Bad", "Resident Evil", "Last of Us", "Ретроёбы"]),
    ("539017344", "@smillims_0",
     ["Last of Us", "Over", "Dota", "Deep Rock", "Bleach", "Persona", "KEVIN", "One Piece", "Better Call Saul",
      "Breaking Bad", "Resident Evil", "Counter Strike", "Jujutsu Kaisen",
      "Анімедібылы общий сбор"]),
    ("741280840", "@emprerorr", ["Over", "Dota", "Tyler, the Creator"]),
    ("287196610", "@plushabest", ["Persona", "One Piece"]),
    ("306758056", "@phiIemon", ["Persona"]),
    ("377260960", "@limbonchik", ["Cyberpunk 2077"]),
    ("1239375296", "@Smou_Gee90", ["Tyler, the Creator"]),
]

for user_id, username, roles in users_roles:

    for role in roles:

        cursor.execute("SELECT id FROM roles WHERE name=?", (role,))
        role_id = cursor.fetchone()

        if role_id is not None:
            cursor.execute("INSERT INTO user_roles (user_id, role_id) VALUES (?, ?)", (user_id, role_id[0]))

conn.commit()
conn.close()
