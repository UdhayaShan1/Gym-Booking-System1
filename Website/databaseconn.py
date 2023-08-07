import mysql.connector
pwd = None
with open("includes\database_pwd.txt") as f:
    pwd = f.read().strip()
db = mysql.connector.connect(
    host="gcp.connect.psdb.cloud",
    user='2m2rl8qq29djzzqvooet',
    passwd=pwd,
    database="fitbook",
    connect_timeout=30
)