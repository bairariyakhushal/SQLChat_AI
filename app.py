import os
import sqlite3
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv
from urllib.parse import quote_plus  # Fix: to handle special chars in password
load_dotenv()

from langchain_groq import ChatGroq
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_community.utilities import SQLDatabase
from langchain_community.callbacks import StreamlitCallbackHandler
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from sqlalchemy import create_engine

st.title("Chat with SQL DB")

LOCALDB = "USE_LOCALDB"
MYSQL = "USE_MYSQL"

radio_opt = ["Use SQLLite 3 Database- Student.db", "Connect to you MySQL Database"]

selected_opt = st.sidebar.radio(label="Choose the DB which you want to chat", options=radio_opt)

if radio_opt.index(selected_opt) == 1:
    db_uri = MYSQL
    mysql_host = st.sidebar.text_input("Provide MySQL Host")
    mysql_user = st.sidebar.text_input("MYSQL_User")
    mysql_password = st.sidebar.text_input("MYSQL password", type="password")
    mysql_db = st.sidebar.text_input("MySQL database")
else:
    db_uri = LOCALDB

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

llm = ChatGroq(groq_api_key=GROQ_API_KEY, model_name="llama-3.3-70b-versatile")

@st.cache_resource(ttl="2h")
def configure_db(db_uri, mysql_host=None, mysql_user=None, mysql_password=None, mysql_db=None):
    if db_uri == LOCALDB:
        dbfilepath = (Path(__file__).parent / "student.db").absolute()
        if not dbfilepath.exists():
            st.error(f"student.db not found at: {dbfilepath}. Please run sqlite.py first.")
            st.stop()
        dbfilepath_str = str(dbfilepath).replace("\\", "/")
        creator = lambda: sqlite3.connect(f"file:{dbfilepath_str}?mode=ro", uri=True)
        return SQLDatabase(create_engine("sqlite:///", creator=creator))

    elif db_uri == MYSQL:
        if not (mysql_host and mysql_user and mysql_password and mysql_db):
            st.error("Please provide all MySQL connection details.")
            st.stop()
        encoded_password = quote_plus(mysql_password)  # Fix: @ # etc. handle ho jayenge
        return SQLDatabase(create_engine(
            f"mysql+mysqlconnector://{mysql_user}:{encoded_password}@{mysql_host}/{mysql_db}"
        ))

if db_uri == MYSQL:
    db = configure_db(db_uri, mysql_host, mysql_user, mysql_password, mysql_db)
else:
    db = configure_db(db_uri)

# toolkit
toolkit = SQLDatabaseToolkit(db=db, llm=llm)

agent = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    verbose=True
)

if "messages" not in st.session_state or st.sidebar.button("Clear message history"):
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

user_query = st.chat_input(placeholder="Ask anything from the database")

if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    st.chat_message("user").write(user_query)

    with st.chat_message("assistant"):
        streamlit_callback = StreamlitCallbackHandler(st.container(), expand_new_thoughts=False)
        response = agent.run(user_query, callbacks=[streamlit_callback])
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.write(response)