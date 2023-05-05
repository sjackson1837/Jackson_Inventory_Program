import mysql.connector

mydb = mysql.connector.connect(host="localhost", user="root", passwd = "ert33MNB",)

my_cursor = mydb.cursor()

#This is the line that creates the database....comment it out after the databse is created!!!!
# my_cursor.execute("CREATE DATABASE our_users")

my_cursor.execute("SHOW DATABASES")
for db in my_cursor:
    print(db)