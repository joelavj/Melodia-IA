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
    id_repertoire = cursor.lastrowid
    cnx.commit()
    cursor.close()
    cnx.close()
    return id_repertoire

def delete(id:int)->None:
    cnx = connect()
    cursor = cnx.cursor()
    query = "DELETE FROM repertoire WHERE id_repertoire=%s"
    cursor.execute(query, (str(id),))
    cnx.commit()
    cursor.close()
    cnx.close()
