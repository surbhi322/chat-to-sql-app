__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import streamlit as st
import sqlite3
from langchain_community.utilities import SQLDatabase
from langchain_openai import ChatOpenAI
from langchain_community.agent_toolkits import create_sql_agent

# 1. Page Config
st.set_page_config(page_title="Data Engineer AI")
st.title("📊 Chat with SQL Database")

# 2. Database Creation (Automatic)
def init_db():
    conn = sqlite3.connect("example.db")
    curr = conn.cursor()
    curr.execute("CREATE TABLE IF NOT EXISTS Data (id INTEGER, name TEXT, role TEXT)")
    curr.execute("SELECT COUNT(*) FROM Data")
    if curr.fetchone()[0] == 0:
        curr.execute("INSERT INTO Data VALUES (1, 'Surbhi', 'Data Engineer')")
        conn.commit()
    conn.close()

init_db()

# 3. Sidebar for Key
key = st.sidebar.text_input("OpenAI API Key", type="password")

if key:
    try:
        db = SQLDatabase.from_uri("sqlite:///example.db")
        llm = ChatOpenAI(model="gpt-3.5-turbo", api_key=key, temperature=0)
        
        # Agent setup
        agent = create_sql_agent(llm, db=db, verbose=True, agent_type="openai-tools")
        
        user_input = st.chat_input("Ask about the database...")
        if user_input:
            st.chat_message("user").write(user_input)
            with st.chat_message("assistant"):
                res = agent.run(user_input)
                st.write(res)
    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.warning("Please enter your API Key to start.")
