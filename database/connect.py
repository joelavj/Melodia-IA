import mysql.connector

def connect(config = {
    "user": "root",
    "password": "",
    "host":"127.0.0.1",
    "database": "melodia_ia",
}):
    try:
        cnx = mysql.connector.connect(**config)
    except mysql.connector.Error as error:
        print(error)
    else:
        return cnx
