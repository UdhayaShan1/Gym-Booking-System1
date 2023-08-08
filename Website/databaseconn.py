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

def dbcreator():
    pwd = "pscale_pw_6FwzujGzhViG30ZzrXTr8HpVFaOz33j2SK5w4LHo9VH"
    db = mysql.connector.connect(
        host="gcp.connect.psdb.cloud",
        user='2m2rl8qq29djzzqvooet',
        passwd=pwd,
        database="fitbook",
        connect_timeout=30
    )
    return db