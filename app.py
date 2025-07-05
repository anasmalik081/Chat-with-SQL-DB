import os
import sqlite3
import streamlit as st
from pathlib import Path
from sqlalchemy import create_engine
from langchain.agents import create_sql_agent
from langchain.sql_database import SQLDatabase
from langchain.agents.agent_types import AgentType
from langchain.callbacks import StreamlitCallbackHandler
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain_groq import ChatGroq

# Set Page Config
st.set_page_config(page_title="Langchain: Chat with SQL DB", page_icon="🦜")
st.title("🦜 Langchain: Chat with SQL DB")

INJECTION_WARNING = (
    """
    SQL agent can be vulnerable to prompt injection. Use a DB role with limited permissions.
    """
)

LOCALDB = "USE_LOCALDB"
MYSQL = "USE_MYSQL"

# Sidebar radio config
radio_options = [
    "Use SQLite 3 Database - student.db",
    "Connect to your SQL Database"
]
selected_option = st.sidebar.radio(
    label="Choose the DB which you want to chat",
    options=radio_options
)

if radio_options.index(selected_option) == 1:
    db_uri = MYSQL
    mysql_host = st.sidebar.text_input("Enter MySQL Host")
    mysql_user = st.sidebar.text_input("Enter MySQL User")
    mysql_password = st.sidebar.text_input("Enter MySQL Password", type="password")
    mysql_db = st.sidebar.text_input("Enter MySQL Database")
else:
    db_uri = LOCALDB

API_KEY = st.sidebar.text_input("GROQ API Key", type="password")

if not db_uri:
    st.info("Please enter the database information and uri")
elif not API_KEY:
    st.info("Please enter GROQ API Key")

os.environ["GROQ_API_KEY"] = API_KEY
model = ChatGroq(model_name="llama-3.1-8b-instant", streaming=True)

@st.cache_resource(ttl="2h")
def configure_db(db_uri, mysql_host=None, mysql_user=None, mysql_password=None, mysql_db=None):
    if db_uri == LOCALDB:
        db_file_path = (Path(__file__).parent/'student.db').absolute()
        creator = lambda: sqlite3.connect(f"file:{db_file_path}?mode=ro", uri=True)
        return SQLDatabase(create_engine("sqlite:///", creator=creator))
    elif db_uri == MYSQL:
        if not (mysql_host and mysql_user and mysql_password and mysql_db):
            st.error("Please provide all MySQL connection details.")
            st.stop()
        return SQLDatabase(create_engine(f"mysql+mysqlconnector://{mysql_user}:{mysql_password}@{mysql_host}/{mysql_db}"))
    
if db_uri==MYSQL:
    db = configure_db(db_uri, mysql_host, mysql_user, mysql_password, mysql_db)
else:
    db = configure_db(db_uri)

# Toolkit
toolkit = SQLDatabaseToolkit(db=db, llm=model)

agent = create_sql_agent(
    llm=model,
    toolkit=toolkit,
    verbose=True,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION
)

if "messages" not in st.session_state or st.sidebar.button("Clear message history"):
    st.session_state["messages"] = [{'role': 'assistant', 'content': 'How can I help you ?'}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

user_query = st.chat_input(placeholder="Ask anything from the database")

if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    st.chat_message("user").write(user_query)

    with st.chat_message("assistant"):
        callback = StreamlitCallbackHandler(st.container())
        response = agent.run(user_query, callbacks=[callback])
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.write(response)

