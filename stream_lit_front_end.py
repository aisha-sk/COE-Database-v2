import streamlit as st
import requests

# Set up variables

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    

st.title("City of Edmonton Traffic Volume Chat")
prompt = st.chat_input(placeholder="Ask me anything about the Traffic Volume Database",key="chat_input")
system_agent = st.chat_message("assistant")
system_agent.write(placeholder)