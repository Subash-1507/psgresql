import os
from flask import Flask, render_template
import psycopg2
from psycopg2 import errors

app = Flask(__name__)

# PostgreSQL database configuration using environment variables
db_config = {
    'host': os.environ.get('PGHOST', ''),
    'port': int(os.environ.get('PGPORT', 5432)),
    'user': os.environ.get('PGUSER', ''),
    'password': os.environ.get('PGPASSWORD', ''),
    'database': os.environ.get('PGDATABASE', ''),
    'sslmode': 'require'  # Use 'require' for Azure Database for PostgreSQL
}

def get_users():
    """Retrieve users from the database."""
    try:
        # Use the connection string here
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()

        cursor.execute("SELECT id, name FROM users;")
        users = cursor.fetchall()

        cursor.close()
        conn.close()

        return users

    except errors.OperationalError as e:
        # Handle connection errors
        print(f"Error connecting to the database: {e}")
        return []

    except errors.Error as e:
        # Handle other PostgreSQL errors
        print(f"PostgreSQL error: {e}")
        return []

@app.route('/')
def index():
    """Render a simple web page with user data."""
    users = get_users()
    return render_template('index.html', users=users)

# Add the following lines at the end of your script
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

