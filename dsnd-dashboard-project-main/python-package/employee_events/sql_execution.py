from sqlite3 import connect
from pathlib import Path
from functools import wraps
import pandas as pd
def execute_sql(query, params=None):
    print(f"[DEBUG] Executing SQL: {query}")
    return []

def execute_sql_df(query, params=None):
    import pandas as pd
    print(f"[DEBUG] Executing SQL (returning df): {query}")
    return pd.DataFrame()

# Using pathlib, create a `db_path` variable
# that points to the absolute path for the `employee_events.db` file
db_path = Path(__file__).resolve().parent / "employee_events.db"


# OPTION 1: MIXIN
# Define a class called `QueryMixin`
class QueryMixin:
    
    def pandas_query(self, sql_query: str):
        """Execute an SQL query and return a pandas DataFrame"""
        connection = connect(db_path)
        df = pd.read_sql_query(sql_query, connection)
        connection.close()
        return df

    def query(self, sql_query: str):
        """Execute an SQL query and return a list of tuples"""
        connection = connect(db_path)
        cursor = connection.cursor()
        result = cursor.execute(sql_query).fetchall()
        connection.close()
        return result


# Leave this code unchanged
def query(func):
    """
    Decorator that runs a standard sql execution
    and returns a list of tuples
    """

    @wraps(func)
    def run_query(*args, **kwargs):
        query_string = func(*args, **kwargs)
        connection = connect(db_path)
        cursor = connection.cursor()
        result = cursor.execute(query_string).fetchall()
        connection.close()
        return result
    
    return run_query
