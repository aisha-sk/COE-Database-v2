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


    """
    Configure the database according to Schema Version 2
    
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
                       study_name VARCHAR(255) NOT NULL,
                       study_duration DECIMAL NOT NULL,
                       segment_type VARCHAR(15) NOT NULL,
                       study_type VARCHAR(20) NOT NULL,
                       location_name VARCHAR(30) NOT NULL,
                       latitude DECIMAL NOT NULL,
                       longitude DECIMAL NOT NULL,
                       project_name VARCHAR(30),
                       study_date DATE NOT NULL,
                       PRIMARY KEY (miovision_id)
                   );
                   """)

    cursor.execute("""
                   CREATE TABLE StudiesDirections(
                       study_direction_id INT GENERATED ALWAYS AS IDENTITY,
                       miovision_id INT,
                       direction_name VARCHAR(20) NOT NULL,
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
                       movement_name VARCHAR(10) NOT NULL,
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
                       vehicle_class_name VARCHAR(10) NOT NULL,
                       vehicle_count INT NOT NULL,
                       PRIMARY KEY(vehicle_class_id),
                       CONSTRAINT movements_classes
                            FOREIGN KEY(movement_id)
                                REFERENCES DirectionsMovements(movement_id)
                   );
                   """)

def configure_schema(connection_string:str)->None:
    """
    Configure the database according to Schema Version 3
    
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
    
    relation_names = ['STUDIES','STUDIES_DIRECTIONS','DIRECTION_TYPES','DIRECTIONS_MOVEMENTS','MOVEMENTS_TYPES','MOVEMENT_VE','VehicleTypes']
    
    for relation in relation_names:
        cursor.execute(f"DROP TABLE IF EXISTS {relation} CASCADE;")
    
    connection.commit()
    
    cursor.execute("""
                   CREATE TABLE studies(
                       miovision_id INTEGER,
                       study_name VARCHAR(50) NOT NULL,
                       study_duration DECIMAL NOT NULL,
                       segment_type VARCHAR(10) NOT NULL,
                       study_type VARCHAR(20) NOT NULL,
                       location_name VARCHAR(50) NOT NULL,
                       latitude DECIMAL NOT NULL,
                       longitude DECIMAL NOT NULL,
                       project_name VARCHAR(20),
                       study_date DATETIME NOT NULL,
                       PRIMARY KEY(miovision_id)
                   );
                   """)

    cursor.execute("""
                   CREATE TABLE direction_types(
                       id GENERATED ALWAYS AS IDENTITY,
                       direction_name VARCHAR(20) NOT NULL,
                       PRIMARY KEY(id)
                   );
                   """)

    cursor.execute("""
                   CREATE TABLE movement_types(
                       id GENERATED ALWAYS AS IDENTITY,
                       movement_name VARCHAR(10) NOT NULL,
                       PRIMARY KEY(id)
                   );
                   """)

    
    cursor.execute("""
                   CREATE TABLE vehicle_types(
                       id GENERATED ALWAYS AS IDENTITY,
                       vehicle_type_name VARCHAR(20) NOT NULL,
                       PRIMARY KEY(id)
                    );
                   """)
    
    cursor.execute("""
                   CREATE TABLE studies_directions(
                       id GENERATED ALWAYS AS IDENTITY,
                       miovision_id INTEGER,
                       direction_type_id INTEGER,
                       PRIMARY KEY(id),
                       CONSTRAINT fk_studies
                       FORERIGN KEY(miovision_id)
                       REFERENCES studies(miovision_id),
                       CONSTRAINT fk_direction_types
                       FOREIGN KEY(direction_type_id)
                       REFERENCES direction_types(id)
                   );
                   """)
    
    cursor.execute("""
                   CREATE TABLE directions_movements(
                       id GENERATED ALWAYS AS IDENTITY,
                       study_direction_id INTEGER,
                       movement_type_id INTEGER,
                       PRIMARY KEY(id),
                       CONSTRAINT fk_studies_directions
                       FOREIGN KEY(study_direction_id)
                       REFERENCES studies_directions(id),
                       CONSTRAINT fk_movement_type
                       FOREIGN KEY(movement_type_id)
                       REFERENCES movement_types(id)
                   );
                   """)
    
    cursor.execute("""
                   CREATE TABLE movement_vehicle_classes(
                       id GENERATED ALWAYS AS IDENTITY,
                       direction_movement_id INTEGER,
                       vehicle_type_id INTEGER,
                       vehicle_count INTEGER,
                       PRIMARY KEY(id),
                       CONSTRAINT fk_direction_movement
                       FOREIGN KEY(direction_movement_id)
                       REFERENCES directions_movements(id),
                       CONSTRAINT fk_vehicle_types
                       FOREIGN KEY(vehicle_type_id)
                       REFERENCES vehicle_types(id)
                   );
                   """)



    

def input_data(connection_string:str)->None:
    """
    Populates the data in accordance with Schema Version 3. Internally inputs data from the provided Miovision datasets. 
    
    ### Parameters
    1. connection_string: ``str``
        - Used to connect to the neon database
    
    ### Returns
    None
    
    ### Effects
    Creation of tuples in the relations configured for Schema Version 2. 
    """
    connection = psycopg2.connect(connection_string)
    cursors = connection.cursor()

if __name__ == "__main__":
    load_dotenv()
    database_connection_string = os.getenv("DATABASE_URL")
    configure_schema(database_connection_string)