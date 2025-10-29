# Import the QueryBase class
from .query_base import QueryBase

# Import dependencies needed for sql execution
# from the `sql_execution` module
from .sql_execution import query, QueryMixin

# Define a subclass of QueryBase
# called Employee
class Employee(QueryBase, QueryMixin):
    
    # Set the class attribute `name`
    # to the string "employee"
    name = "employee"

    @query
    def names(self):
        # Query 3
        return """
            SELECT first_name || ' ' || last_name AS full_name,
                   employee_id
            FROM employee
        """

    @query
    def username(self, id):
        # Query 4
        return f"""
            SELECT first_name || ' ' || last_name AS full_name
            FROM employee
            WHERE employee_id = {id}
        """

    def model_data(self, id):
        sql = f"""
            SELECT SUM(positive_events) positive_events,
                   SUM(negative_events) negative_events
            FROM {self.name}
            JOIN employee_events
                USING({self.name}_id)
            WHERE {self.name}.{self.name}_id = {id}
        """
        return self.pandas_query(sql)
