from langchain_deepseek import ChatDeepSeek
from dotenv import load_dotenv
from langchain_community.utilities import SQLDatabase
from langgraph.prebuilt import create_react_agent
from langgraph.graph.state import CompiledStateGraph
from langchain_community.agent_toolkits import SQLDatabaseToolkit
import os

def validate_prompt_topic(llm:ChatDeepSeek,prompt:str)->bool:
    """
    Given the prompt, use an LLM agent to check if the prompt aligns with a request for a SQL query for
    a postgress database. 
    
    ### Parameters
    1. llm:``langchain_deepseek.ChatDeepSeek``
        - Used to send the request
     
    ### Effects
    Internally makes a call to the LLM and depletes tokens
    
    ### Returns
    ``True | False`` depending on closeness to a SQL query. 
    """
    
    system_content = """
    You are an expert in writing SQL queries for a postgresql database. Your only job is to determine whether
    the user prompt is asking for information that can returned by writing a SQL query to a database containing
    information about traffic volume studies. Respond with 'true' if it is related and 'false' if it is not.
    """
    messages = [
        (
            "system",
            system_content
        ),
        (
            "human",
            prompt
        )
    ]
    response = llm.invoke(messages)
    
    if response.content.lower() == "false":
        return False
    elif response.content.lower() == "true":
        return True
    else:
        raise Exception("Response from Validation LLM was not true or false")

def query_from_database(llm:ChatDeepSeek,database_connection_string:str)->CompiledStateGraph:
    db = SQLDatabase.from_uri(database_connection_string)
    tools = SQLDatabaseToolkit(llm=llm,db=db)
    
    agent = create_react_agent(
        model=llm,
        tools=tools,
        
    )
    
    print(db.dialect)


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
    
    query_from_database(llm=llm,database_connection_string=database_connection_string)