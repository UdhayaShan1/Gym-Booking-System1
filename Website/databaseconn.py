import mysql.connector
pwd = None
with open("includes\database_pwd.txt") as f:
    pwd = f.read().strip()
db = mysql.connector.connect(
    host="gcp.connect.psdb.cloud",
    user='dmcurece3iqorlzf3qz1',
    passwd=pwd,
    database="fitbook",
    connect_timeout=30
)

def dbcreator():
    pwd1 = pwd
    db = mysql.connector.connect(
        host="gcp.connect.psdb.cloud",
        user='dmcurece3iqorlzf3qz1',
        passwd=pwd,
        database="fitbook",
        connect_timeout=30
    )
    return db