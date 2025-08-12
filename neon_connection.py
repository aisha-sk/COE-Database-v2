import os
import psycopg2
from dotenv import load_dotenv

def create_dummy_table(connection_string:str)->None:
    """
    Create a dummy table called books in the database, and prints the results. 
    Used as a **sanity check** to ensure that connection to the hosted database is established.
    
    ### Parameters:
    1. connection_string : ``str`` 
        - The string passed into the psycopg2 modules to connection to the database.
    
    ### Returns 
    None
    
    ### Effects
    Creation of a database called **books** in the database. 
    """
    connection = psycopg2.connect(connection_string)
    cursor = connection.cursor()
    
    cursor.execute("""
                   DROP TABLE IF EXISTS books;
                   """)
    
    cursor.execute("""
                   CREATE TABLE books(
                       id SERIAL PRIMARY KEY,
                       title VARCHAR(255) NOT NULL,
                       pages SMALLINT NOT NULL
                   );
                   """)
    
    cursor.execute("""
                   INSERT INTO books (title,pages)
                   VALUES
                   ('Harry Potter and the Chamber of Secrets',750),
                   ('The US Constitution',20000)
                   RETURNING id
                   ;
                   """)
    connection.commit()
    cursor.execute("""
                             SELECT *
                             FROM books;
                             """)
    
    results = cursor.fetchall()
    print(results)

if __name__ == "__main__":
    load_dotenv()
    database_connection_string = os.getenv("DATABASE_URL")
    create_dummy_table(database_connection_string)