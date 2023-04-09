from datetime import datetime
from datetime import date
from flask import Flask, jsonify, request
import sqlite3

app = Flask(__name__)
DATABASE = 'hello.db'

def init_db():
    """
    This function initializes the database by creating a table 'users' with two columns 'username' and 'dob'.
    'username' is the primary key and 'dob' stores the date of birth in the format 'YYYY-MM-DD'. 
    If the table already exists, it will not create a new one.
      Args:
        None
    Returns:
        None
    """
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (username text primary key, dob text)''')
    conn.commit()
    conn.close()

def add_user(username, dob):
    """
    This function adds or updates a user to the 'users' table in the database.
    It opens a connection to the database, executes the insert or replace command with the given parameters, and then closes the connection.
    Args:
        username (string) 
        dob (string in YYYY-MM-DD format)
    Returns:
        None
    """
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO users VALUES (?, ?)", (username, dob))
    conn.commit()
    conn.close()

def get_user(username):
    """
    This function gets a user record from the database based on their username. It establishes a connection to the database,
    executes an SQL query to fetch the record, and returns the result as a tuple. If the user is not found in the database, 
    the function returns None.
    Args:
        username (string) 
    Returns:
        None
    """
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    user = c.fetchone()
    conn.close()
    return user

def calculate_days_diff(dob):
    """
    Calculates the number of days between the provided date of birth (dob) and today's date.
    Args:
        dob (str): The date of birth in the format 'YYYY-MM-DD'.
    Returns:
        int: The number of days between the provided date of birth and today's date.
    """
    today = date.today()
    today_str = today.strftime('%Y-%m-%d')
    print(today_str)  # Output: '2023-04-09'
    dob_date = datetime.strptime(dob, '%Y-%m-%d').date()
    dob_date = dob_date.replace(year=today.year)
    if dob_date < today:
        dob_date = dob_date.replace(year=today.year + 1)
    today = datetime.strptime(today_str, '%Y-%m-%d').date() # convert today back to date object
    if dob_date == today:
        days_diff = 0
    else:
        days_diff = (dob_date - today).days
    return days_diff


@app.route('/hello/<username>', methods=['PUT'])
def update_user(username):
    """
    Function to update user's date of birth based on the given username
    """
    dob = request.json['dateOfBirth'] # Extract date of birth from the request body
    try:
        datetime.strptime(dob, '%Y-%m-%d')  # Check if the date is in the correct format
    except ValueError:
        return jsonify(error="Invalid date format. Please use YYYY-MM-DD"), 400 # Return an error message if the date format is invalid
    if not username.isalpha(): # Check if the username contains only letters
        return jsonify(error="Invalid username. Please use letters only"), 400
    if datetime.strptime(dob, '%Y-%m-%d') >= datetime.today(): # Check if the date of birth is before today
        return jsonify(error="Invalid date of birth. Please provide a date before today"), 400
    add_user(username, dob) # Add or replace the user's data in the database
    return '', 204 # Return a success message

@app.route('/hello/<username>', methods=['GET'])
def hello_user(username):
    """
    This function takes a username as input, fetches the user's date of birth from the database, 
    calculates the days difference between the current date and the user's date of birth, and returns a JSON message.
    If the user is not found in the database, it returns a 404 error message. 
    If the user's date of birth is today's date, it returns a happy birthday message. 
    Otherwise, it returns a message with the number of days remaining until the user's birthday.
    """
    user = get_user(username)
    print(user)
    if not user:
        return jsonify(error= f"Sorry!, {username} not found in database"), 404
    days_diff = calculate_days_diff(user[1])
    if days_diff == 0:
        message = f"Hello, {username}! Happy birthday!"
    else:
        message = f"Hello, {username}! Your birthday is in {days_diff} day(s)"
    return jsonify(message=message)

# The following block of code initializes the Flask app and starts it on a local server. 
# The debug mode is set to True to help with development and troubleshooting. The database is 
# also initialized. Once everything is set up, the app is run by calling the run method.
if __name__ == '__main__':
    app.debug = True
    init_db()
    app.run()