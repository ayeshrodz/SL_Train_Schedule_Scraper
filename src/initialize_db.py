# initialize_db.py
import sqlite3

def initialize_db(db_path="train_schedule.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create the stations table if not exists
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS stations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        station_id INTEGER UNIQUE,
        station_name TEXT
    )
    """)

    # Create the train_schedules table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS train_schedules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        station TEXT,
        arrival_time TEXT,
        departure_time TEXT,
        destination TEXT,
        destination_time TEXT,
        end_station TEXT,
        end_station_time TEXT,
        frequency TEXT,
        train_name TEXT,
        train_no TEXT,
        available_classes TEXT,
        other_info TEXT
    )
    """)

    # Create the execution_logs table (added data_count column)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS execution_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        start_station_id INTEGER,
        end_station_id INTEGER,
        search_date TEXT,
        request_time INTEGER,
        response_time INTEGER,
        request_duration_seconds INTEGER,
        http_status INTEGER,
        response_message TEXT, 
        data_count INTEGER  
    )
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    initialize_db()
