"""
OSS Pulse - Natural Language Query Interface
Chat with your GitHub data using Claude AI
"""

import streamlit as st
from text_to_sql import generate_sql, is_safe_query
from query_executor import execute_query, format_results
import pandas as pd
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="OSS Pulse - AI Query Interface",
    page_icon="🚀",
    layout="wide"
)

# Title
st.title("🚀 OSS Pulse - Natural Language Query Interface")
st.markdown("Ask questions about GitHub activity in plain English!")

# Sidebar with examples
with st.sidebar:
    st.header("📋 Example Questions")
    
    examples = [
        "What are the top 10 repositories by commit count?",
        "How many pull requests were merged?",
        "Show me the most active users",
        "What are the most common event types?",
        "Which repositories have the most pull requests?",
        "Show me commits by repository",
        "How many events happened in January 2024?",
    ]
    
    for example in examples:
        if st.button(example, key=example):
            st.session_state.user_question = example

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'last_results' not in st.session_state:
    st.session_state.last_results = None

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
user_question = st.chat_input("Ask a question about GitHub data...")

# Handle example button clicks
if 'user_question' in st.session_state:
    user_question = st.session_state.user_question
    del st.session_state.user_question

# Process user question
if user_question:
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": user_question})
    with st.chat_message("user"):
        st.markdown(user_question)
    
    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Generating SQL..."):
            try:
                # Step 1: Generate SQL
                sql = generate_sql(user_question)
                
                # Step 2: Safety check
                is_safe, reason = is_safe_query(sql)
                
                if not is_safe:
                    error_msg = f"❌ **Safety Error**: {reason}\n\nGenerated query was blocked for security."
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
                    st.stop()
                
                # Step 3: Show generated SQL
                st.markdown("**Generated SQL:**")
                st.code(sql, language="sql")
                
                # Step 4: Execute query
                with st.spinner("Executing query..."):
                    df = execute_query(sql)
                    
                    # Save results for CSV export
                    st.session_state.last_results = {
                        'dataframe': df,
                        'query': user_question,
                        'sql': sql,
                        'timestamp': datetime.now()
                    }
                    
                    # Display results
                    st.markdown(f"**Results:** ({len(df)} rows)")
                    
                    if len(df) == 0:
                        st.info("No results found.")
                    else:
                        # Show as table
                        st.dataframe(df, use_container_width=True)
                        
                        # CSV Download button
                        csv = df.to_csv(index=False)
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"oss_pulse_export_{timestamp}.csv"
                        
                        st.download_button(
                            label="📥 Download as CSV",
                            data=csv,
                            file_name=filename,
                            mime="text/csv",
                            key=f"download_{timestamp}"
                        )
                        
                        # Show summary stats if numeric columns
                        numeric_cols = df.select_dtypes(include=['number']).columns
                        if len(numeric_cols) > 0:
                            with st.expander("📊 Summary Statistics"):
                                st.write(df[numeric_cols].describe())
                
                # Save to message history
                response_content = f"**Generated SQL:**\n```sql\n{sql}\n```\n\n**Results:** {len(df)} rows returned"
                st.session_state.messages.append({"role": "assistant", "content": response_content})
                
            except Exception as e:
                error_msg = f"❌ **Error**: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

# Footer
st.markdown("---")
st.markdown("💡 **Tip**: Try asking specific questions about repositories, users, pull requests, or commits!")
