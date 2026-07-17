from database.connect import connect
import mysql.connector

def save(nom:str)->int:
    cnx = connect()
    cursor = cnx.cursor()
    query = "INSERT INTO artiste(nom) VALUES (%s)"
    cursor.execute(query, (nom,))
    lastrowid = cursor.lastrowid
    cnx.commit()
    cursor.close()
    cnx.close()
    return int(lastrowid) if lastrowid is not None else 0

def link_album(id_artiste:int, id_album:int):
    cnx = connect()
    cursor = cnx.cursor()
    query = "INSERT IGNORE INTO artiste_album(id_artiste, id_album) VALUES (%s, %s)"
    cursor.execute(query, (id_artiste, id_album))
    cnx.commit()
    cursor.close()
    cnx.close()

def findByName(nom:str)->list:
    cnx = connect()
    cursor = cnx.cursor()
    query = "SELECT * FROM artiste WHERE nom=%s"
    cursor.execute(query, (nom,))
    resultat = cursor.fetchall()
    cursor.close()
    cnx.close()
    return resultat

def link_morceau(id_artiste:int, id_morceau:int):
    cnx = connect()
    cursor = cnx.cursor()
    query = "INSERT IGNORE INTO artiste_morceau(id_artiste, id_morceau) VALUES (%s, %s)"
    cursor.execute(query, (id_artiste, id_morceau))
    cnx.commit()
    cursor.close()
    cnx.close()
