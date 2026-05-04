__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import streamlit as st
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_openai import ChatOpenAI
from langchain.agents import create_sql_agent
from langchain.agents.agent_types import AgentType
import sqlite3

# 1. UI Configuration
st.set_page_config(page_title="Chat with SQL DB", page_icon="📊")
st.title("📊 Chat with your SQL Database")

# 2. Setup a Dummy Database
def create_sample_db():
    conn = sqlite3.connect("example.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS Employees (id INTEGER, name TEXT, dept TEXT, salary INTEGER)")
    cursor.execute("SELECT count(*) FROM Employees")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO Employees VALUES (?, ?, ?, ?)", 
                           [(1, 'Surbhi', 'Data', 90000), (2, 'Rahul', 'DevOps', 80000)])
        conn.commit()
    conn.close()

create_sample_db()

# 3. Connection & API Key
api_key = st.sidebar.text_input("Enter OpenAI API Key", type="password")

if api_key:
    try:
        db = SQLDatabase.from_uri("sqlite:///example.db")
        llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0, openai_api_key=api_key)
        toolkit = SQLDatabaseToolkit(db=db, llm=llm)
        agent_executor = create_sql_agent(
            llm=llm,
            toolkit=toolkit,
            verbose=True,
            agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            handle_parsing_errors=True
        )

        user_query = st.chat_input("Ask a question about your data")
        
        if user_query:
            with st.chat_message("user"):
                st.write(user_query)
            
            with st.chat_message("assistant"):
                response = agent_executor.run(user_query)
                st.write(response)
    except Exception as e:
        st.error(f"An error occurred: {e}")
else:
    st.info("Please enter your OpenAI API Key in the sidebar to start.")
