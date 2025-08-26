"""
Test file with intentional violations for governance demonstration
"""

# Magic variable violation
API_URL = "http://localhost:3000/api"  # This is a magic variable
SECRET_KEY = "hardcoded_secret_123"  # This is a credential violation

def process_data(data):
    # Assumption violation
    # TODO: This should probably work with the new API
    result = data * 2  # I think this will handle all cases
    
    # Missing error handling
    connection = connect_to_database("127.0.0.1", 5432)  # Magic host and port
    
    # Undocumented complex logic
    if result > 100:
        result = result / 2
        for i in range(10):  # Magic number
            if i % 2 == 0:
                result += i
            else:
                result -= i
    
    return result

def connect_to_database(host, port):
    # This function assumes the database is always available
    pass  # Not implemented

class DataProcessor:
    # Missing docstring
    def __init__(self):
        self.threshold = 1000  # Magic number
    
    def process(self, items):
        # This should work for most cases
        # FIXME: Need to handle edge cases
        return [item * 2 for item in items if item > 10]  # Magic number