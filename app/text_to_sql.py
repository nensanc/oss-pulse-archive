"""
Text-to-SQL Agent using Claude API.
Converts natural language questions into SQL queries.
"""

import os
import re
from anthropic import Anthropic
from schema_context import get_schema_context
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Anthropic client
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = f"""You are an expert SQL query generator for the OSS Pulse data warehouse.

Your job is to convert natural language questions into valid Snowflake SQL queries.

# Database Schema:
{get_schema_context()}

# Rules:
1. ONLY generate SELECT queries (no INSERT, UPDATE, DELETE, DROP, CREATE)
2. Always use fully qualified table names: OSS_PULSE.STAGING.TABLE_NAME
3. Include LIMIT clause for safety (default LIMIT 100 unless user specifies)
4. Use proper JOINs when querying star schema (fact_events with dimensions)
5. Add comments to explain complex queries
6. Return ONLY the SQL query, no explanations before or after
7. Use appropriate date filters and aggregations
8. Validate that column names exist in the schema

# Output Format:
Return ONLY the SQL query as plain text. No markdown code blocks, no explanations.

# Examples:

User: "Show me the top 10 most active repositories"
Assistant: SELECT repo_name, COUNT(*) as event_count FROM OSS_PULSE.STAGING.STG_EVENTS GROUP BY repo_name ORDER BY event_count DESC LIMIT 10;

User: "How many pull requests were merged in January 2024?"
Assistant: SELECT COUNT(*) as merged_prs FROM OSS_PULSE.STAGING.STG_PULL_REQUESTS WHERE pr_merged = true AND DATE_TRUNC('month', pr_created_at) = '2024-01-01' LIMIT 1;

User: "What are the most common event types?"
Assistant: SELECT event_type, COUNT(*) as count FROM OSS_PULSE.STAGING.STG_EVENTS GROUP BY event_type ORDER BY count DESC LIMIT 10;
"""

def generate_sql(user_question: str) -> str:
    """
    Convert a natural language question into a SQL query using Claude.
    
    Args:
        user_question: Natural language question from user
        
    Returns:
        SQL query string
    """
    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",  # Latest Sonnet model
            max_tokens=2000,
            temperature=0,  # Deterministic output for SQL
            system=SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": user_question
                }
            ]
        )
        
        # Extract the SQL query from response
        sql_query = message.content[0].text.strip()
        
        # Remove markdown code blocks if present
        if sql_query.startswith("```sql"):
            sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
        elif sql_query.startswith("```"):
            sql_query = sql_query.replace("```", "").strip()
            
        return sql_query
        
    except Exception as e:
        raise Exception(f"Error generating SQL: {str(e)}")


def is_safe_query(sql: str) -> tuple[bool, str]:
    """
    Validate that the SQL query is safe to execute.
    
    Args:
        sql: SQL query string
        
    Returns:
        (is_safe: bool, reason: str)
    """
    sql_upper = sql.upper()
    
    # Block dangerous operations (using word boundaries to avoid false positives)
    dangerous_patterns = [
        r'\bDROP\b', r'\bDELETE\b', r'\bTRUNCATE\b', r'\bINSERT\b', 
        r'\bUPDATE\b', r'\bALTER\b', r'\bGRANT\b', r'\bREVOKE\b',
        r'\bEXEC\b', r'\bEXECUTE\b', r'\bMERGE\b', r'\bREPLACE\b'
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, sql_upper):
            keyword = pattern.replace(r'\b', '')
            return False, f"Query contains dangerous keyword: {keyword}"
    
    # Special check for CREATE (but allow CURRENT_DATE, etc.)
    if re.search(r'\bCREATE\s+(TABLE|VIEW|DATABASE|SCHEMA|USER|ROLE)', sql_upper):
        return False, "Query contains dangerous keyword: CREATE"
    
    # Ensure it's a SELECT query
    if not sql_upper.strip().startswith('SELECT'):
        return False, "Query must be a SELECT statement"
    
    # Check for semicolons (could indicate multiple statements)
    if sql.count(';') > 1:
        return False, "Multiple statements not allowed"
    
    return True, "Query is safe"


if __name__ == "__main__":
    # Test the agent
    test_questions = [
        "What are the top 5 repositories by commit count?",
        "How many pull requests were opened yesterday?",
        "Show me user activity by event type"
    ]
    
    print("Testing Text-to-SQL Agent...\n")
    
    for question in test_questions:
        print(f"Question: {question}")
        try:
            sql = generate_sql(question)
            is_safe, reason = is_safe_query(sql)
            
            print(f"Generated SQL:\n{sql}\n")
            print(f"Safety Check: {'✅ SAFE' if is_safe else '❌ UNSAFE - ' + reason}\n")
            print("-" * 80 + "\n")
        except Exception as e:
            print(f"Error: {e}\n")
