from langchain_deepseek import ChatDeepSeek
from dotenv import load_dotenv
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
import os


def generate_additional_information(llm:ChatDeepSeek,database_connection_string:str,prompt:str)->str:
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

def validate_information_needed_for_prompt(llm:ChatDeepSeek,database_connection_string:str,prompt:str)->bool:
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
    load_dotenv()
    
    api_key = os.getenv("LLM_API_KEY")
    base_url = os.getenv("LLM_BASE_URL")
    database_connection_string = os.getenv("LOCAL_DATABASE_URL")
    
    llm = ChatDeepSeek(
        model="deepseek-chat",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
        base_url=base_url,
        api_key=api_key
    )
    
    print("Prompt:")
    prompt = input()
    
    
    
    if not validate_information_needed_for_prompt(llm=llm,database_connection_string=database_connection_string,prompt=prompt):
        print('Prompt deemed inadequate for query generation. Generating suggestions for improvement..')
        response = generate_additional_information(llm=llm,database_connection_string=database_connection_string,prompt=prompt)
        print("Response: ",response)