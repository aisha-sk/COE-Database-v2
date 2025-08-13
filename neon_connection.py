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

def configure_schema_version_1(connection_string:str)->None:
    """
    Configure the database according to Schema Version 14
    
    ### Parameters:
    1. connection_string : ``str``
        - The connection string passed into psycopg2 to connect to the database.
    
    ### Returns:
    None
    
    ### Effects:
    Creates the inital configuration of the relations in the hosted database.
    """
    connection = psycopg2.connect(connection_string)
    cursor = connection.cursor()
    
    cursor.execute("""
                   DROP TABLE IF EXISTS Studies CASCADE;
                   """)

    cursor.execute("""
                   DROP TABLE IF EXISTS StudiesLocationData CASCADE;
                   """)
    
    cursor.execute("""
                   DROP TABLE IF EXISTS StudiesDirections CASCADE;
                   """)
    
    cursor.execute("""
                   DROP TABLE IF EXISTS DirectionsMovements CASCADE;
                   """)
    
    cursor.execute("""
                   DROP TABLE IF EXISTS MovementVehicleClasses CASCADE;
                   """)

    connection.commit()
    
    cursor.execute("""
                   CREATE TABLE Studies(
                       miovision_id INT,
                       study_name VARCHAR(255),
                       study_duration DECIMAL,
                       study_date DATE,
                       PRIMARY KEY (miovision_id)
                   );
                   """)

    cursor.execute("""
                   CREATE TABLE StudiesLocationData(
                       miovision_id INT,
                       location_name VARCHAR(250),
                       latitude DECIMAL,
                       longitude DECIMAL,
                       study_type VARCHAR(20),
                       segment_type VARCHAR(10),
                       PRIMARY KEY(miovision_id),
                       CONSTRAINT miovision_location
                            FOREIGN KEY(miovision_id)
                                REFERENCES Studies(miovision_id)
                   );
                   """)

    cursor.execute("""
                   CREATE TABLE StudiesDirections(
                       study_direction_id INT GENERATED ALWAYS AS IDENTITY,
                       miovision_id INT,
                       direction_name VARCHAR(20),
                       PRIMARY KEY(study_direction_id),
                       CONSTRAINT miovision_directions
                            FOREIGN KEY(miovision_id)
                                REFERENCES Studies(miovision_id)
                   );
                   """)
    
    cursor.execute("""
                   CREATE TABLE DirectionsMovements(
                       movement_id INT GENERATED ALWAYS AS IDENTITY,
                       direction_id INT,
                       movement_name VARCHAR(10),
                       PRIMARY KEY(movement_id),
                       CONSTRAINT directions_movements
                            FOREIGN KEY(direction_id)
                                REFERENCES StudiesDirections(study_direction_id)
                   );
                   """)
    
    cursor.execute("""
                   CREATE TABLE MovementVehicleClasses(
                       vehicle_class_id INT GENERATED ALWAYS AS IDENTITY,
                       movement_id INT,
                       vehicle_class_name VARCHAR(10),
                       vehicle_count INT,
                       PRIMARY KEY(vehicle_class_id),
                       CONSTRAINT movements_classes
                            FOREIGN KEY(movement_id)
                                REFERENCES DirectionsMovements(movement_id)
                   );
                   """)
    
    connection.commit()
    
    

if __name__ == "__main__":
    load_dotenv()
    database_connection_string = os.getenv("DATABASE_URL")
    configure_schema_version_1(database_connection_string)