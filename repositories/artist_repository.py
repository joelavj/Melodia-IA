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

def delete(id:int)->None:
    cnx = connect()
    cursor = cnx.cursor()
    query = "DELETE FROM artiste WHERE id_artiste=%s"
    cursor.execute(query, (id,))
    cnx.commit()
    cursor.close()
    cnx.close()

def get_songs(id)->list:
    cnx = connect()
    cursor = cnx.cursor()
    query = "SELECT id_morceau FROM artiste_morceau WHERE id_artiste=%s"
    cursor.execute(query, (id,))
    resultat = cursor.fetchall()
    cursor.close()
    cnx.close()
    return resultat

def get_albums(id)->list:
    cnx = connect()
    cursor = cnx.cursor()
    query = "SELECT id_album FROM artiste_album WHERE id_artiste=%s"
    cursor.execute(query, (id,))
    resultat = cursor.fetchall()
    cursor.close()
    cnx.close()
    return resultat

def find_all()->list:
    cnx = connect()
    cursor = cnx.cursor()
    query = "SELECT * FROM artiste"
    cursor.execute(query)
    resultat = cursor.fetchall()
    cursor.close()
    cnx.close()
    return resultat