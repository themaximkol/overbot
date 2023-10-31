from functools import wraps
import sqlite3 as sql

with open("token.txt", 'r') as file:
    token = file.read()
