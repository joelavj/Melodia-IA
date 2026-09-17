from database.connect import connect
from pathlib import Path
from typing import cast, Literal
from models.directory_model import Directory

class DirectoryRepository :

    def save(self, path:Path)->Literal[False] | int:
        cnx = connect()
        cursor = cnx.cursor()
        query = """
            INSERT IGNORE INTO repertoire(chemin) 
            VALUES (%s)
        """
        cursor.execute(query, (str(path),))
        lastrowid = cursor.lastrowid
        cnx.commit()
        resultat = int(lastrowid) if lastrowid is not None else False
        cursor.close()
        cnx.close()
        return resultat


    def delete(self, id:int)->bool:
        cnx = connect()
        cursor = cnx.cursor()
        query = """
            DELETE FROM repertoire 
            WHERE id_repertoire=%s
        """
        cursor.execute(query, (str(id),))
        cnx.commit()
        resultat = True
        cursor.close()
        cnx.close()
        return resultat


    def find_all(self)->list:
        cnx = connect()
        cursor = cnx.cursor()
        query = """
            SELECT id_repertoire, chemin 
            FROM repertoire;
        """
        cursor.execute(query)
        directories = cursor.fetchall()
        if directories:
            directories = [ Directory(directory[0],directory[1]) for directory in cast(list[tuple[int,str]],directories)]
        cursor.close()
        cnx.close()
        return directories

    
    def find_by_id(self, id:int)->Directory|None:
        cnx = connect()
        cursor = cnx.cursor()
        query = """
            SELECT id_repertoire, chemin 
            FROM repertoire 
            WHERE id_repertoire=%s
        """
        cursor.execute(query, (id,))
        directory = cursor.fetchone()
        if directory is not None:
            directory = cast(tuple[int,str], directory)
            directory = Directory(directory[0], directory[1])
        cursor.close()
        cnx.close()
        return directory

    
    def find_by_path(self, path:Path)->Directory|None:
        cnx = connect()
        cursor = cnx.cursor()
        query = """
            SELECT id_repertoire, chemin 
            FROM repertoire 
            WHERE chemin=%s
        """
        cursor.execute(query, (str(path),))
        directory = cursor.fetchone()
        if directory is not None:
            directory = cast(tuple[int,str], directory)
            directory = Directory(id=directory[0], path=directory[1])
        cursor.close()
        cnx.close()
        return directory


    def find_path_songs(self, id_directory:int)->list:
        cnx = connect()
        cursor = cnx.cursor()
        query = """
            SELECT id_morceau, chemin
            FROM morceau
            WHERE id_repertoire = %s;
        """
        cursor.execute(query,(id_directory,))
        songs = cursor.fetchall()
        if songs:
            songs = [(id,Path(path)) for id,path in cast(list[tuple[int,str]],songs)]
        cursor.close()
        cnx.close()
        return songs

directory_repository = DirectoryRepository()
