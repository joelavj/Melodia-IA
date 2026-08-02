from database.connect import connect
import mysql.connector
from pathlib import Path
from typing import cast
from models.directory_model import Directory

class DirectoryRepository :
        
    def find_all(self)->list:
        cnx = connect()
        cursor = cnx.cursor()
        query = """
            SELECT id_repertoire, chemin 
            FROM repertoire
        """
        cursor.execute(query)
        directories = cursor.fetchall()
        if directories != []:
            directories_tmp = []
            for directory in cast(list[tuple[int,str]], directories):
                directories_tmp.append(Directory(id=directory[0], path=Path(directory[1])))
            directories = directories_tmp
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
        if directory is None:
            directory = None
        else:
            directory = cast(tuple[int,Path], directory)
            directory = Directory(id=directory[0], path=Path(directory[1]))
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
        if directory is None:
            directory = None
        else:
            directory = cast(tuple[int,Path], directory)
            directory = Directory(id=directory[0], path=Path(directory[1]))
        cursor.close()
        cnx.close()
        return directory

        
    def save(self, path:Path)->int:
        cnx = connect()
        cursor = cnx.cursor()
        query = """
            INSERT INTO repertoire(chemin) 
            VALUES (%s)
        """
        cursor.execute(query, (str(path),))
        lastrowid = cursor.lastrowid
        cnx.commit()
        cursor.close()
        cnx.close()
        return int(lastrowid) if lastrowid is not None else 0

    
    def delete(self, id:int)->None:
        cnx = connect()
        cursor = cnx.cursor()
        query = """
            DELETE FROM repertoire 
            WHERE id_repertoire=%s
        """
        cursor.execute(query, (str(id),))
        cnx.commit()
        cursor.close()
        cnx.close()


directory_repository = DirectoryRepository()