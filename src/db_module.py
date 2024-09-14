import sqlite3

# Function to fetch station combinations from the database
def fetch_station_combinations(db_connection):
    cursor = db_connection.cursor()
    cursor.execute("SELECT station_id FROM stations")
    stations = [row[0] for row in cursor.fetchall()]

    # Generate unique combinations
    combinations = [(stations[i], stations[j]) for i in range(len(stations)) for j in range(i + 1, len(stations))]
    return combinations

# Initialize database connection
def connect_db(db_path="train_schedule.db"):
    return sqlite3.connect(db_path)
