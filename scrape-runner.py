import sqlite3
import itertools
from fetch_train_schedule_module import fetch_train_schedule

def get_station_combinations(stations):
    return list(itertools.combinations(stations, 2))

def run_requests_for_two_combinations(combinations, db_conn):
    for start_station_id, end_station_id in combinations[:2]:
        print(f"Fetching train schedule from station {start_station_id} to {end_station_id}...")
        fetch_train_schedule(start_station_id, end_station_id, '14/09/2024', 'en', db_conn, verify=False)

# Setup database connection
db_conn = sqlite3.connect('train_schedule.db')

# Assuming stations table is already populated
cursor = db_conn.cursor()
cursor.execute("SELECT station_id FROM stations")
stations = [row[0] for row in cursor.fetchall()]

combinations = get_station_combinations(stations)
run_requests_for_two_combinations(combinations, db_conn)

# Close the database connection
db_conn.close()
