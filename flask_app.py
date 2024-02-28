import os
from flask import Flask, render_template
import psycopg2
from psycopg2 import errors

app = Flask(__name__)

# PostgreSQL database configuration using environment variables
db_config = {
    'host': os.environ.get('DB_HOST', ''),
    'port': int(os.environ.get('DB_PORT', 5432)),
    'user': os.environ.get('DB_USER', ''),
    'password': os.environ.get('DB_PASSWORD', ''),
    'database': os.environ.get('DB_NAME', ''),
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

# Additional code for local development and production deployment
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Optional startup command for your Flask app.')
    parser.add_argument('--debug', action='store_true', help='Run the app in debug mode')
    args = parser.parse_args()

    if args.debug:
        app.run(host='0.0.0.0', port=8000, debug=True)
    else:
        # Use Gunicorn for production
        from gunicorn.app.base import Application

        class StandaloneApplication(Application):
            def __init__(self, app, options=None):
                self.options = options or {}
                self.application = app
                super().__init__()

            def load_config(self):
                for key, value in self.options.items():
                    if key in self.cfg.settings and value is not None:
                        self.cfg.set(key.lower(), value)

            def load(self):
                return self.application

        options = {
            'bind': '0.0.0.0:8000',
            'workers': 4
        }

        StandaloneApplication(app, options).run()
