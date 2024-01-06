import random
import os

with open("token.txt", 'r') as file:
    token = file.read()


def select_random_file(folder_path):
    files = os.listdir(folder_path)
    files = [f for f in files if os.path.isfile(os.path.join(folder_path, f))]
    random_file = random.choice(files)

    return os.path.join(folder_path, random_file)
