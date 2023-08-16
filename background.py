from flask import Flask
from threading import Thread

file_path_main = "token_main.txt"
with open(file_path_main, "r") as file:
    token_main = file.read()

file_path_test = "token_main.txt"
with open(file_path_test, "r") as file:
    token_test = file.read()

app = Flask('')


@app.route('/')
def home():
    return "I'm alive"


def run():
    app.run(host='0.0.0.0', port=80)


def keep_alive():
    t = Thread(target=run)
    t.start()
