import sqlite3

conn = sqlite3.connect('books.db')

cursor = conn.cursor()

try:
    # sql запрос для создания таблицы
    user = "CREATE TABLE \"books\" (\"ID\" INTEGER UNIQUE, \"user_id\" INTEGER, \"book\" TEXT, \"ReadUnread\" TEXT, \"IMPRESSION\", PRIMARY KEY (\"ID\"))"
    cursor.execute(user)
except:
    pass
