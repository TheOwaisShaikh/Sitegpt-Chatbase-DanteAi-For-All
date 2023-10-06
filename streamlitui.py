import os
import tempfile
import streamlit as st
from streamlit_chat import message
from webquery import WebQuery

st.set_page_config(page_title="Website to Chatbot")

def display_messages():
    st.subheader("Chat")
    for i, (msg, is_user) in enumerate(st.session_state["messages"]):
        message(msg, is_user=is_user, key=str(i))
    st.session_state["thinking_spinner"] = st.empty()

def process_input():
    if st.session_state["user_input"] and len(st.session_state["user_input"].strip()) > 0:
        user_text = st.session_state["user_input"].strip()
        with st.session_state["thinking_spinner"], st.spinner(f"Thinking"):
            query_text = st.session_state["webquery"].ask(user_text)

        st.session_state["messages"].append((user_text, True))
        st.session_state["messages"].append((query_text, False))
        
def ingest_input():
    if st.session_state["input_url"] and len(st.session_state["input_url"].strip()) > 0:
        url = st.session_state["input_url"].strip()
        with st.session_state["thinking_spinner"], st.spinner(f"Thinking"):
            ingest_text = st.session_state["webquery"].ingest(url)

def is_openai_api_key_set() -> bool:
    # Always return True since the key is hard-coded
    return True

def main():
    if len(st.session_state) == 0:
        st.session_state["messages"] = []
        st.session_state["url"] = ""
        
        # Hardcoded API key
        st.session_state["OPENAI_API_KEY"] = "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"
        st.session_state["webquery"] = WebQuery(st.session_state["OPENAI_API_KEY"])

    st.header("Website to Chatbot")
    
    # The input field for the API key has been commented out since it's hardcoded.
    # st.text_input("OpenAI API Key", value=st.session_state["OPENAI_API_KEY"], key="input_OPENAI_API_KEY", type="password")

    st.subheader("Add a url")
    st.text_input("Input url", value=st.session_state["url"], key="input_url", disabled=not is_openai_api_key_set(), on_change=ingest_input)
    st.session_state["ingestion_spinner"] = st.empty()

    display_messages()
    st.text_input("Message", key="user_input", disabled=not is_openai_api_key_set(), on_change=process_input)

    st.divider()
    st.markdown("Source code: [Github](https://github.com/Anil-matcha/Website-to-Chatbot)")

if __name__ == "__main__":
    main()
