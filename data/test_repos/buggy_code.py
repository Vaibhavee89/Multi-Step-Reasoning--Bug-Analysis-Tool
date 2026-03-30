"""Sample buggy code for testing the analysis agent.

This file contains intentional bugs for demonstration purposes.
"""


def divide_numbers(a, b):
    """Divide two numbers - BUG: No zero division check."""
    return a / b  # BUG: ZeroDivisionError possible


def process_user_input(user_input):
    """Process user input - BUG: SQL Injection vulnerability."""
    import sqlite3

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # BUG: SQL Injection - never concatenate user input
    query = f"SELECT * FROM users WHERE username = '{user_input}'"
    cursor.execute(query)

    return cursor.fetchall()


def calculate_average(numbers=[]):
    """Calculate average - BUG: Mutable default argument."""
    if not numbers:
        numbers.append(0)  # BUG: Modifies shared default list

    return sum(numbers) / len(numbers)


class DataProcessor:
    """Data processor class."""

    def __init__(self, data):
        self.data = data

    def process(self):
        """Process data - BUG: Bare except clause."""
        try:
            result = []
            for item in self.data:
                result.append(item * 2)
            return result
        except:  # BUG: Catches all exceptions including KeyboardInterrupt
            pass


def fetch_user_data(user_id):
    """Fetch user data - BUG: Unused variable."""
    _temp_data = "temporary"  # BUG: Unused variable

    # Simulate fetching data
    user_data = {"id": user_id, "name": "User"}

    return user_data


def complex_calculation(x, y, z, a, b, c, d):
    """Complex function - BUG: Too many parameters."""
    # BUG: Cyclomatic complexity too high
    if x > 0:
        if y > 0:
            if z > 0:
                if a > 0:
                    if b > 0:
                        if c > 0:
                            if d > 0:
                                return x + y + z + a + b + c + d
    return 0


def get_config():
    """Get configuration - BUG: Hardcoded credentials."""
    config = {
        "api_key": "sk_test_123456789",  # BUG: Hardcoded secret
        "password": "admin123",  # BUG: Hardcoded password
        "database_url": "postgresql://user:pass@localhost/db"
    }
    return config


def unsafe_eval(user_code):
    """Execute user code - BUG: Code injection vulnerability."""
    # BUG: Never use eval with user input
    result = eval(user_code)
    return result


def find_item(items, target):
    """Find item in list - BUG: Inefficient algorithm."""
    # BUG: O(n²) when could be O(n) with set
    for i in range(len(items)):
        for j in range(len(items)):
            if items[i] == target:
                return i
    return -1


def read_file(filename):
    """Read file - BUG: Resource leak."""
    # BUG: File not closed properly
    f = open(filename, 'r')
    data = f.read()
    return data  # File never closed


def parse_json(json_string):
    """Parse JSON - BUG: No error handling."""
    import json
    # BUG: No try-except for JSON parsing
    return json.loads(json_string)  # Could raise ValueError


class Singleton:
    """Singleton pattern - BUG: Not thread-safe."""
    _instance = None

    def __new__(cls):
        # BUG: Not thread-safe singleton
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance


def format_string(name, age):
    """Format string - BUG: XSS vulnerability in web context."""
    # BUG: No HTML escaping
    return f"<div>Welcome {name}, age {age}</div>"


# BUG: Global mutable state
GLOBAL_COUNTER = []

def increment_counter():
    """Increment counter - BUG: Global mutable state."""
    GLOBAL_COUNTER.append(1)
    return len(GLOBAL_COUNTER)


if __name__ == "__main__":
    # Test some buggy functions
    print(divide_numbers(10, 0))  # Will crash
    print(calculate_average())
    print(unsafe_eval("__import__('os').system('ls')"))  # Security risk
