import sqlite3

connection = sqlite3.connect("users.db")
cursor = connection.cursor()

command = """CREATE TABLE IF NOT EXISTS users(id int NOT NULL, name varchar(200), email varchar(120), date_added datetime)"""

cursor.execute(command)
