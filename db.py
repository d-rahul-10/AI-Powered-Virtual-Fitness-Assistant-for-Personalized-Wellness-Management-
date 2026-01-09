import sqlite3
import os
import threading
import logging

# Configure logging (optional, but helpful for debugging)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Path to the SQLite database file
DB_PATH = "Fitness Assistant.db"

# Thread-local storage for database connections (for multi-threading safety in Streamlit)
local_storage = threading.local()

def get_db_connection():
    """
    Gets a thread-local SQLite connection, creating one if it doesn't exist.
    Ensures row_factory is set for accessing columns by name.
    """
    if not hasattr(local_storage, 'connection'):
        try:
            local_storage.connection = sqlite3.connect(DB_PATH)
            local_storage.connection.row_factory = sqlite3.Row # Enables accessing columns by name
            logger.info(f"Connected to SQLite database: {DB_PATH}")
        except sqlite3.Error as e:
            logger.error(f"Failed to connect to database {DB_PATH}: {e}")
            raise # Re-raise to be handled by the calling function
    return local_storage.connection

def close_db_connection():
    """
    Closes the thread-local SQLite connection if it exists.
    """
    if hasattr(local_storage, 'connection'):
        try:
            local_storage.connection.close()
            logger.info("Database connection closed.")
        except sqlite3.Error as e:
            logger.error(f"Error closing database connection: {e}")
        finally:
            # Remove the connection attribute after closing
            delattr(local_storage, 'connection')

def query_db(query, params=(), fetchone=False):
    """
    Executes a SELECT query and returns the results.
    """
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        logger.debug(f"Executing query: {query} with params: {params}")
        cursor.execute(query, params)

        if fetchone:
            result = cursor.fetchone()
            logger.debug(f"Fetched one row: {result}")
        else:
            result = cursor.fetchall()
            logger.debug(f"Fetched {len(result)} rows")

        return result

    except sqlite3.Error as e:
        logger.error(f"Database Query Error: Query: {query}, Params: {params}, Error: {e}")
        if fetchone:
            return None
        else:
            return []
    except Exception as e: # Catch other potential errors
        logger.error(f"Unexpected error in query_db: {e}")
        if fetchone:
            return None
        else:
            return []
    finally:
        # Close cursor explicitly (good practice)
        if cursor:
            try:
                cursor.close()
            except sqlite3.Error as e:
                logger.warning(f"Error closing cursor: {e}")
        # Note: Connection is managed per thread and not closed here.

def execute_db(query, params=()):
    """
    Executes an INSERT, UPDATE, or DELETE query.
    """
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        logger.debug(f"Executing update query: {query} with params: {params}")
        cursor.execute(query, params)
        conn.commit() # Commit the transaction
        last_row_id = cursor.lastrowid
        row_count = cursor.rowcount
        logger.debug(f"Query executed successfully. Last row ID: {last_row_id}, Rows affected: {row_count}")
        # Return last inserted row id for INSERT statements, or affected rows count for UPDATE/DELETE
        return last_row_id if last_row_id is not None else row_count

    except sqlite3.Error as e:
        logger.error(f"Database Execution Error: Query: {query}, Params: {params}, Error: {e}")
        if conn: # Rollback only if connection object exists
            try:
                conn.rollback()
                logger.info("Transaction rolled back due to error.")
            except sqlite3.Error as rollback_e:
                logger.error(f"Error rolling back transaction: {rollback_e}")
        return -1 # Indicate failure
    except Exception as e: # Catch other potential errors
        logger.error(f"Unexpected error in execute_db: {e}")
        if conn:
            try:
                conn.rollback()
                logger.info("Transaction rolled back due to unexpected error.")
            except sqlite3.Error as rollback_e:
                logger.error(f"Error rolling back transaction: {rollback_e}")
        return -1
    finally:
        # Close cursor explicitly (good practice)
        if cursor:
            try:
                cursor.close()
            except sqlite3.Error as e:
                logger.warning(f"Error closing cursor: {e}")
        # Note: Connection is managed per thread and not closed here.

def init_db():
    """
    Creates the necessary tables if they don't exist.
    This function should be called once when setting up the application.
    """
    create_users = """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            password TEXT, -- Consider storing hash as BLOB if possible, or TEXT as string
            age INTEGER,
            gender TEXT,
            height REAL,
            weight REAL
        );
    """
    create_workouts = """
        CREATE TABLE IF NOT EXISTS workouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            date DATE,
            exercise TEXT,
            duration INTEGER,
            calories_burned REAL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
    """
    create_goals = """
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            goal_type TEXT,
            target_value REAL,
            current_value REAL,
            start_date DATE,
            end_date DATE,
            status TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
    """
    create_chat_logs = """
        CREATE TABLE IF NOT EXISTS chat_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            user_message TEXT,
            bot_reply TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
    """
    execute_db(create_users)
    execute_db(create_workouts)
    execute_db(create_goals)
    execute_db(create_chat_logs)
    logger.info("Database tables created successfully (or already existed).")

# --- Call init_db() here to ensure tables exist ---
init_db()
