"""
Query Executor - Safely runs SQL queries against Snowflake.
"""

import os
import snowflake.connector
from dotenv import load_dotenv
import pandas as pd

# Load environment variables
load_dotenv()

def get_snowflake_connection():
    """Create a Snowflake connection."""
    return snowflake.connector.connect(
        user=os.getenv('SNOWFLAKE_USER'),
        password=os.getenv('SNOWFLAKE_PASSWORD'),
        account=os.getenv('SNOWFLAKE_ACCOUNT'),
        warehouse='WH_REPORTING',
        database='OSS_PULSE',
        schema='STAGING',
        role='REPORTER'
    )

def execute_query(sql: str) -> pd.DataFrame:
    """
    Execute a SQL query and return results as a pandas DataFrame.
    
    Args:
        sql: SQL query string
        
    Returns:
        pandas DataFrame with query results
    """
    conn = None
    try:
        conn = get_snowflake_connection()
        
        # Execute query
        cursor = conn.cursor()
        cursor.execute(sql)
        
        # Fetch results
        columns = [desc[0] for desc in cursor.description]
        results = cursor.fetchall()
        
        # Convert to DataFrame
        df = pd.DataFrame(results, columns=columns)
        
        cursor.close()
        return df
        
    except Exception as e:
        raise Exception(f"Error executing query: {str(e)}")
        
    finally:
        if conn:
            conn.close()


def format_results(df: pd.DataFrame, max_rows: int = 100) -> str:
    """
    Format DataFrame results as a nice string for display.
    
    Args:
        df: pandas DataFrame
        max_rows: Maximum rows to display
        
    Returns:
        Formatted string
    """
    if df.empty:
        return "No results found."
    
    # Limit rows
    if len(df) > max_rows:
        df_display = df.head(max_rows)
        truncated = f"\n... (showing {max_rows} of {len(df)} rows)"
    else:
        df_display = df
        truncated = ""
    
    # Format as string
    result = df_display.to_string(index=False)
    result += truncated
    
    return result


if __name__ == "__main__":
    # Test the executor
    test_query = """
    SELECT event_type, COUNT(*) as count
    FROM OSS_PULSE.STAGING.STG_EVENTS
    GROUP BY event_type
    ORDER BY count DESC
    LIMIT 5;
    """
    
    print("Testing Query Executor...\n")
    print(f"Query:\n{test_query}\n")
    
    try:
        df = execute_query(test_query)
        print("Results:")
        print(format_results(df))
        print(f"\nReturned {len(df)} rows")
        
    except Exception as e:
        print(f"Error: {e}")
