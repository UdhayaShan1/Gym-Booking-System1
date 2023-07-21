import mysql.connector
pwd = None
with open("includes\database_pwd.txt") as f:
    pwd = f.read().strip()
db = mysql.connector.connect(
    host="sql6.freemysqlhosting.net",
    user='sql6634220',
    passwd=pwd,
    database="sql6634220",
    connect_timeout=30
)