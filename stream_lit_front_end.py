import streamlit as st
import requests
import time
from io import BytesIO
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()
api_endpoint = os.getenv('SERVER_ENDPOINT')

# Set up variables
st.title(":blue[City of Edmonton] Traffic Volume Chat")


if "processing_request" not in st.session_state:
    st.session_state.processing_request = False

if "saved_prompt" not in st.session_state:
    st.session_state.saved_prompt = None


def stream_data(text:str):
    for word in text.split(" "):
        yield word + " "
        time.sleep(0.05)

def reset_chat():
    st.session_state.saved_prompt = None
    st.session_state.processing_request = False
    
prompt = st.chat_input(placeholder="Ask me anything about the Traffic Volume Database",key="chat_input",disabled=st.session_state.processing_request)

if prompt:
    st.session_state.saved_prompt = prompt
    st.session_state.processing_request = True
    st.rerun()

if st.session_state.saved_prompt and st.session_state.processing_request:

    with st.chat_message("user"):
        st.markdown(st.session_state.saved_prompt)
    
    with st.chat_message("ai"):
        with st.spinner("Validating Prompt...",show_time=True):
            response = requests.post(
                url=f"{api_endpoint}/validate",
                json={
                    "prompt":st.session_state.saved_prompt
                }
            )
        is_valid = response.json()['is_valid']
        
        if is_valid:
            st.success("Prompt is adequate for query generation.")
        else:
            st.error("Prompt is NOT adequate for query generation.")
    
    if not is_valid:
        with st.chat_message("assistant"):
            with st.spinner("Generating suggestions for improvement...",show_time=True):
                response = requests.post(
                    url=f"{api_endpoint}/suggestion",
                    json={
                        "prompt":st.session_state.saved_prompt
                    }
                )
            suggestion = response.json()['suggestion']
            generator = stream_data(suggestion)
            st.write_stream(generator)
        c1, c2, c3 = st.columns(3)
        c2.button("Write Another Prompt",on_click=reset_chat)
    else:
        with st.chat_message("assistant"):
            with st.spinner(text="Generating SQL Query... (Exp. Time ~ 80-140s)",show_time=True):
                start_time = time.time()
                response = requests.post(
                    url=f"{api_endpoint}/query",
                    json={
                        "prompt":st.session_state.saved_prompt
                    }
                )
                query = response.json()['query']
                end_time = time.time()
            st.success(f"Successfully qenerated query. Time taken: {round(end_time-start_time,1)}s")
            description_generator = stream_data("The following query will be used to aggregate data from the database:")
            st.write_stream(description_generator)
            st.code(body=query,language='sql')
        
        with st.chat_message("assistant"):
            with st.spinner(text="Aggregating data into Excel format...",show_time=True):
                response = requests.post(
                    url=f"{api_endpoint}/excel_file",
                    json={
                        "prompt":query
                    }
                )
                file_bytes = response.content
            st.success("Successfully Recieved Data.")
        
        df = pd.read_excel(BytesIO(file_bytes))
        
        with st.chat_message("assistant"):
            df_description_generator = stream_data("Preview of the data stored in the Excel file:")
            st.write_stream(df_description_generator)
            st.dataframe(df,hide_index=True,)
        
        columns = st.columns(4)
        columns[1].download_button(
            label="Download Excel File",
            data=file_bytes,
            file_name="Generated Data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            icon=":material/download:",
            on_click=reset_chat,
            type='primary'
        )
        columns[2].button(
            label="Write Another Prompt",
            on_click=reset_chat
        )
            

            
    

 
    