__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import streamlit as st
import sqlite3
from langchain_community.utilities import SQLDatabase
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.agent_toolkits import create_sql_agent

# 1. Page Config
st.set_page_config(page_title="Data Engineer AI (Gemini)")
st.title("📊 Chat with SQL (Free via Gemini)")

# 2. Database Creation
def init_db():
    conn = sqlite3.connect("example.db")
    curr = conn.cursor()
    curr.execute("CREATE TABLE IF NOT EXISTS Employees (id INTEGER, name TEXT, dept TEXT, salary INTEGER)")
    curr.execute("SELECT COUNT(*) FROM Employees")
    if curr.fetchone()[0] == 0:
        curr.executemany("INSERT INTO Employees VALUES (?, ?, ?, ?)", 
                         [(1, 'Surbhi', 'Data', 95000), (2, 'Rahul', 'DevOps', 85000), (3, 'Amit', 'HR', 70000)])
        conn.commit()
    conn.close()

init_db()

# 3. Sidebar for Gemini Key
api_key = st.sidebar.text_input("Enter Google Gemini API Key", type="password")

if api_key:
    try:
        db = SQLDatabase.from_uri("sqlite:///example.db")
        
        # Using Gemini instead of OpenAI
        llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=api_key, temperature=0)
        
        agent = create_sql_agent(llm, db=db, verbose=True, agent_type="zero-shot-react-description")
        
        user_input = st.chat_input("Ask about employees or salaries...")
        if user_input:
            st.chat_message("user").write(user_input)
            with st.chat_message("assistant"):
                res = agent.run(user_input)
                st.write(res)
    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.info("Please enter your Google API Key from AI Studio to start.")
