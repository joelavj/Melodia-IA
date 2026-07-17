from database.connect import connect

def save(titre:str, annee_sortie:str)->int:
    titre = titre.strip() if titre else ""
    if not titre:
        titre = "inconnu"

    cnx = connect()
    cursor = cnx.cursor()
    query = "INSERT INTO album(titre, annee_sortie) VALUES (%s,%s)"
    cursor.execute(query, (titre, annee_sortie))
    lastrowid = cursor.lastrowid
    cnx.commit()
    cursor.close()
    cnx.close()
    return int(lastrowid) if lastrowid is not None else 0

def link_artiste(id_artiste:int, id_album:int):
    cnx = connect()
    cursor = cnx.cursor()
    query = "INSERT INTO artiste_album(id_artiste, id_album) VALUES (%s, %s)"
    cursor.execute(query, (id_artiste, id_album))
    cnx.commit()
    cursor.close()
    cnx.close()
   
def findByName(titre:str)->list:
    cnx = connect()
    cursor = cnx.cursor()
    query = "SELECT * FROM album WHERE titre=%s"
    cursor.execute(query, (titre,))
    resultat = cursor.fetchall()
    cursor.close()
    cnx.close()
    return resultat