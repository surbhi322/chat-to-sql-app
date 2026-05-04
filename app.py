__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import streamlit as st
from langchain_community.utilities import SQLDatabase

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

# 2. Setup a Dummy Database (So you don't get stuck without data)


def create_sample_db():
    conn = sqlite3.connect("example.db")
    cursor = conn.cursor()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS Employees (id INTEGER, name TEXT, dept TEXT, salary INTEGER)")
    # Insert some data if empty
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
    # Connect to the SQLite database
    db = SQLDatabase.from_uri("sqlite:///example.db")

    # Initialize the LLM (GPT-3.5 or GPT-4)
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0,
                     openai_api_key=api_key)

    # Create the SQL Toolkit and Agent
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    agent_executor = create_sql_agent(
        llm=llm,
        toolkit=toolkit,
        verbose=True,
        agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    )

    # 4. Chat Interface
    user_query = st.chat_input(
        "Ask a question about your data (e.g., 'Who has the highest salary?')")

    if user_query:
        with st.chat_message("user"):
            st.write(user_query)

        with st.chat_message("assistant"):
            with st.spinner("Analyzing database..."):
                # The agent decides which SQL query to run and returns the answer
                response = agent_executor.run(user_query)
                st.write(response)
else:
    st.info("Please enter your OpenAI API Key in the sidebar to start.")
