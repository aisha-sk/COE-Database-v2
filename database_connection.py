import os
import psycopg2
from dotenv import load_dotenv
from gather_names import ColumnNames

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
    
    relation_names = ['STUDIES','STUDIES_DIRECTIONS','DIRECTION_TYPES','DIRECTIONS_MOVEMENTS','movement_types','movement_vehicle_classes','vehicle_types']
    
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
                       study_date DATE NOT NULL,
                       PRIMARY KEY(miovision_id)
                   );
                   """)

    cursor.execute("""
                   CREATE TABLE direction_types(
                       id INTEGER GENERATED ALWAYS AS IDENTITY,
                       direction_name VARCHAR(20) NOT NULL,
                       PRIMARY KEY(id)
                   );
                   """)

    cursor.execute("""
                   CREATE TABLE movement_types(
                       id INTEGER GENERATED ALWAYS AS IDENTITY,
                       movement_name VARCHAR(10) NOT NULL,
                       PRIMARY KEY(id)
                   );
                   """)

    
    cursor.execute("""
                   CREATE TABLE vehicle_types(
                       id INTEGER GENERATED ALWAYS AS IDENTITY,
                       vehicle_type_name VARCHAR(100) NOT NULL,
                       PRIMARY KEY(id)
                    );
                   """)
    
    cursor.execute("""
                   CREATE TABLE studies_directions(
                       id INTEGER GENERATED ALWAYS AS IDENTITY,
                       miovision_id INTEGER,
                       direction_type_id INTEGER,
                       PRIMARY KEY(id),
                       CONSTRAINT fk_studies
                       FOREIGN KEY(miovision_id)
                       REFERENCES studies(miovision_id),
                       CONSTRAINT fk_direction_types
                       FOREIGN KEY(direction_type_id)
                       REFERENCES direction_types(id)
                   );
                   """)
    
    cursor.execute("""
                   CREATE TABLE directions_movements(
                       id INTEGER GENERATED ALWAYS AS IDENTITY,
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
                       id INTEGER GENERATED ALWAYS AS IDENTITY,
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
    connection.commit()

def input_directions(connection_string:str)->None:
    """
    Populates the directions data from the provided Miovision datasets. 
    
    ### Parameters
    1. connection_string: ``str``
        - Used to connect to the database
    
    ### Returns
    None
    
    ### Effects
    Creation of tuples in the relations configured for Schema Version 2. 
    """
    connection = psycopg2.connect(connection_string)
    cursors = connection.cursor()
    
    directions = ['Northeastbound', 'Westbound', 'Eastbound', 'Southeastbound', 'Northbound', 'Northwestbound', 'Southbound', 'Southwestbound']
    
    for direction in directions:
        cursors.execute(f"""
                        INSERT INTO direction_types (direction_name)
                        VALUES ('{direction}');
                        """)
        
        connection.commit()
        
def input_vehicle_types(connection_string:str)->None:
    """
    Populates the vehicle class tables with the information on all possible types of vehicles. 
    
    ### Parameters
    1. connection_string: ``str``
        - Used to connect to the database
    
    ### Returns
    Nothing
    
    ### Effects
    Creates corrsponding tuples in the vehicle_types table in the database.
    """
    connection = psycopg2.connect(connection_string)
    cursor = connection.cursor()
    
    vehicle_classes = ['Cars', 'Articulated Trucks and Single-Unit Trucks', 
                        'Buses', 'Pedestrians', 'Light Goods Vehicles', 'Heavy', 
                        'Bicycles on Road', 'Bicycles on Crosswalk', 'Motorcycles',
                        'Lights', 'Articulated Trucks', 'Buses and Single-Unit Trucks',
                        'Bicycles', 'Single-Unit Trucks', 'Lights and Motorcycles', 'Vehicles', 
                        'Trams and Road Trains', 'Heavy and Lights', 'E-Scooters', 'e-Scooters (Road)']
    
    for veh_class in vehicle_classes:
        cursor.execute(f"""
                        INSERT INTO vehicle_types (vehicle_type_name)
                        VALUES ('{veh_class}');
                        """)
    
    connection.commit()

def input_movement_types(connection_string:str)->None:
    """
    Input the various movement types in the movement_types table in the database.
    
    ### Parameters:
    1. connection_string: ``str``
        - The string used for connecting to the database.
    
    ### Returns
    Nothing
    
    ### Effects
    Creates the corresponding utples in the movement_types table in the database.
    """
    connection = psycopg2.connect(connection_string)
    cursor = connection.cursor()
    
    movement_types = ['Peds', 'Right', 'Peds CW', 'Hard right',
                      'Peds CCW', 'Bear right', 'Bear left', 
                      'Hard left', 'U-Turn', 'Left', 'Thru']
    
    for mov_type in movement_types:
        cursor.execute(f"""
                       INSERT INTO movement_types (movement_name)
                       VALUES ('{mov_type}');
                       """)
    connection.commit()
    
def populate_main_data(connection_string:str)->None:
    """
    Internally called the ColumnNames class to populate the studies, studies_directions, directions_movements, and
    movement_vehicle_classes tables for each study.
    
    ### Parameters:
    1. connection_string: ``str``
        - String used to connnec to the database
    
    ### Returns:
    Nothing
    
    ### Effects:
    Creates corresponding tuple in the studies, studies_directions, directions_movements, and
    movement_vehicle_classes tables in the database. 
    """
    connection = psycopg2.connect(database_connection_string)
    cursor = connection.commit()
    
    column_names = ColumnNames(start_year=2010,end_year=2024)
    
if __name__ == "__main__":
    load_dotenv()
    database_connection_string = os.getenv("LOCAL_DATABASE_URL")
    configure_schema(connection_string=database_connection_string)
    input_directions(database_connection_string)
    input_vehicle_types(database_connection_string)
    input_movement_types(database_connection_string)