from database.connect import connect
import mysql.connector
from pathlib import Path

def findAll()->list:
    cnx = connect()
    cursor = cnx.cursor()
    query = "SELECT id_repertoire, chemin FROM repertoire"
    cursor.execute(query)
    resultat = cursor.fetchall()
    cursor.close()
    cnx.close()
    return resultat

def save(path:Path)->int:
    cnx = connect()
    cursor = cnx.cursor()
    query = "INSERT INTO repertoire(chemin) VALUES (%s)"
    cursor.execute(query, (str(path),))
    lastrowid = cursor.lastrowid
    cnx.commit()
    cursor.close()
    cnx.close()
    return int(lastrowid) if lastrowid is not None else 0

def delete(id:int)->None:
    cnx = connect()
    cursor = cnx.cursor()
    query = "DELETE FROM repertoire WHERE id_repertoire=%s"
    cursor.execute(query, (str(id),))
    cnx.commit()
    cursor.close()
    cnx.close()

def findByPath(path:Path)->list:
    cnx = connect()
    cursor = cnx.cursor()
    query = "SELECT * FROM repertoire WHERE chemin=%s"
    cursor.execute(query, (str(path),))
    resultat = cursor.fetchall()
    cursor.close()
    cnx.close()
    return resultat