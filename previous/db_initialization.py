import sqlite3

def create_tables():
    db_conn = sqlite3.connect('train_schedule.db')
    cursor = db_conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stations (
            station_id INTEGER PRIMARY KEY,
            station_name TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS train_schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            start_station_id INTEGER,
            end_station_id INTEGER,
            search_date TEXT,
            selected_locale TEXT,
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

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS execution_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            start_station_id INTEGER,
            end_station_id INTEGER,
            search_date TEXT,
            selected_locale TEXT,
            request_time INTEGER,
            response_time INTEGER,
            request_duration_seconds INTEGER,
            http_status INTEGER,
            status TEXT,
            message TEXT
        )
    """)

    db_conn.commit()
    db_conn.close()

# Run this to initialize the database
create_tables()
