from langchain_deepseek import ChatDeepSeek
from dotenv import load_dotenv
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langgraph.prebuilt import create_react_agent
import os
import psycopg2
from psycopg2.extras import RealDictCursor
import pandas as pd

class SQLAgent:
    """
    Used to access various capabilities across the SQL agent. 
    """
    def __init__(self):
        load_dotenv()
        
        api_key = os.getenv("LLM_API_KEY")
        base_url = os.getenv("LLM_BASE_URL")
        self.database_connection_string = os.getenv("LOCAL_DATABASE_URL")
        
        self.llm = ChatDeepSeek(
            model="deepseek-chat",
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
            base_url=base_url,
            api_key=api_key
        )
    
    def validate_prompt_adequacy(self,prompt:str)->bool:
        """
        Given the prompt, internally validate it's adequacy.
        
        ### Parameters
        1. prompt : ``str``
            - Prompt to be tested against.
            
        ### Returns
        ``True|False`` depending on validity.
        """
        return self.__validate_information_needed_for_prompt(
            llm=self.llm,
            database_connection_string=self.database_connection_string,
            prompt=prompt
        )
    
    def generate_prompt_suggestions(self,prompt:str)->str:
        """
        Generate and return prompt suggestions based on the prompt.
        
        ### Parameters
        1. prompt : ``str``
            - Prompt used for generating suggestions
        
        ### Returns
        A ``str`` object containing suggestions. 
        """
        return self.__generate_additional_information(
            llm=self.llm,
            database_connection_string=self.database_connection_string,
            prompt=prompt
        )
    
    def return_dataframe(self,prompt:str)->pd.DataFrame:
        """
        Given the prompt, internally, generate a query internally, access the database, and return a DataFrame.
        
        ### Parameters
        1. prompt : ``str``
            - Prompt to be used generating the query.
        ### Returns
        A ``pd.DataFrame`` object
        """
        query = self.__generate_query(
            llm=self.llm,
            database_connection_string=self.database_connection_string,
            prompt=prompt
        )
        
        return self.__retrieve_dataframe(
            query=query,
            database_connection_string=self.database_connection_string
        )
    
    def __generate_query(self,llm:ChatDeepSeek,database_connection_string:str,prompt:str)->str:
        """
        Generate a DML query based on the prompt for the database referenced by the connection string.
        
        ### Parameters
        1. llm: ``ChatDeepSeek``
            - Deepseek client
        2. database_connection_string : ``str``
            - Connection string used to obtain schema for context for the LLM
        3. prompt: ``str``
            - Prompt used for sql generation
        
        ### Effects
        Depletes tokens from DeepSeek account
        
        ### Returns 
        DML query in string format
        """
        db = SQLDatabase.from_uri(database_uri=database_connection_string)
        toolkit = SQLDatabaseToolkit(db=db,llm=llm)
        schema_info = db.get_table_info(db.get_usable_table_names())
        
        system_prompt = """
        You are an agent designed to interact with a SQL database.
        Given an input question, create a syntactically correct {dialect} query to run.

        Query all revelant columns to the prompt even if the user may not have explicity asked for it.
    
        You MUST double check your query before returning it by executing it. When checking the query, always limit
        the number of rows returned to a maximum of 5 to boost efficieny. However, remove this row limit from the final
        query that you output unless the uses asked for one. If you get an error while
        executing a query, rewrite the query and try again.

        DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the
        database. ALWAYS REMEMBER TO LIMIT QUERIES TO A MAXIMUM OF FIVE RETURNED TUPLES WHEN CHECKING THE QUERY.
        HOWEVER, REMOVE THIS FROM THE FINAL QUERY UNLESS THE USER SPECIFIED A LIMIT.

        To start you should ALWAYS look at the tables in the database to see what you
        can query. Do NOT skip this step.

        After testing the query you have written and fixing any issues, return simply the {dialect} query as the final output.
        
        THIS IS IMPORTANT. FOR THE FINAL MESSAGE, ONLY RETURN THE QUERY TEXT NOTHING ELSE, NO ADDED REMARKS. DO NOT FORGET THE
        SEMICOLON AT THE END OF QUERIES.
        """.format(
            dialect=db.dialect,
        )

        
        agent = create_react_agent(
            model=llm,
            tools=toolkit.get_tools(),
            prompt=system_prompt
        )
        
        response_itr = agent.stream(
            {"messages": [{"role": "user", "content": prompt}]},
            stream_mode='values'
        )
        
        list_response = list(response_itr)
        response_content = list_response[-1]['messages'][-1].content
        return response_content
        

    def __generate_additional_information(self,llm:ChatDeepSeek,database_connection_string:str,prompt:str)->str:
        """
        Given the prompt, use an LLM agent to provide the minimum additional information that would be needed to generate
        a query from the database.
        
        ### Parameters
        1. llm:``langchain_deepseek.ChatDeepSeek``
            - Used to send the request
        2. database_connection: ``str``
            - Connection string needed to connect to the database.
        3. prompt: ``str``
            - The prompt to be tested
        
        ### Effects
        Internally makes a call to the LLM and depletes tokens
        
        ### Returns
        ``str`` message that contains the minimum additional information needed to generate information from the database. 
        """
        db = SQLDatabase.from_uri(database_connection_string)
        schema_info = db.get_table_info(db.get_usable_table_names())
        
        system_prompt = """You are an agent designed to interact with a SQL database.
            The database information is this:
            
            {db_info}

            Given an input prompt, output the minimum additional information that would be needed to generate a {dialect} query for the given schema.
            
            After examining the schema, respond with the information.
            """.format(
                db_info=schema_info,
                dialect=db.dialect
            )
        
        messages = [
            (
                'system',
                system_prompt
            ),
            (
                'human',
                prompt
            )
        ]
        
        response = llm.invoke(messages)
        
        return response.content

    def __retrieve_dataframe(self,query:str,database_connection_string:str)->pd.DataFrame:
        """
        Given the query and connection string, return a pandas Dataframe for the resulting output
        
        ### Parameters
        1. query: ``str``
            - Query to be passed into the database
        2. database_connection_string: ``str``
            - Used to connect to the database
        
        ### Returns
        A ``pd.DataFrame`` object
        """
        
        return_dict = None
        
        # Clean query just in case extra text was left in by the LLM
        expected_first_clause = "SELECT"
        
        expected_start_index = query.index(expected_first_clause)
        
        query = query[expected_start_index:]
        
        with psycopg2.connect(database_connection_string) as connection:
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query=query)
                result_dict = cursor.fetchall()
                return_dict = result_dict
                
        return pd.DataFrame(data=return_dict)
        

    def __validate_information_needed_for_prompt(self,llm:ChatDeepSeek,database_connection_string:str,prompt:str)->bool:
        """
        Given the prompt, use an LLM agent to check if the prompt aligns with a request for a SQL query from 
        the database schema. 
        
        ### Parameters
        1. llm:``langchain_deepseek.ChatDeepSeek``
            - Used to send the request
        2. database_connection: ``str``
            - Connection string needed to connect to the database.
        3. prompt: ``str``
            - The prompt to be tested
        
        ### Effects
        Internally makes a call to the LLM and depletes tokens
        
        ### Returns
        ``True | False`` depending on closeness to a SQL query. 
        """
        db = SQLDatabase.from_uri(database_connection_string)
        
        schema_info = db.get_table_info(db.get_usable_table_names())
        
        system_message = """You are an agent designed to interact with a SQL database.
            The database information is this:
            
            {db_info}

            Given an input question, check to see if the prompt can be converted into a {dialect} query based on
            the schema and information in the database.


            After examining the schema, analyze if the input question can be answered with the available data.
            Simply respond with 'True' if enough information is present to answer the question, or 'False' if not enough information is available.
            respond with anything else.
            """.format(
                db_info=schema_info,
                dialect=db.dialect
            )
        
        messages = [
            (
                "system",
                system_message
            ),
            (
                "human",
                prompt
            )
        ]
        
        
        response = llm.invoke(messages)

        if response.content.lower() == 'true':
            return True
        elif response.content.lower() == 'false':
            return False
        else:
            raise Exception('Validation LLM did not return True or False')


if __name__ == "__main__":
    print("Logic for ")