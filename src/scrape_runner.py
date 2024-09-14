import time
import urllib3
from fetch_train_schedule_module import fetch_train_schedule
from log_module import log_train_schedule_to_db, log_execution_to_db
from db_module import connect_db, fetch_station_combinations

# Suppress InsecureRequestWarning if ssl_verify is False
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Function to execute requests for combinations sequentially
def run_requests_for_combinations(combinations, search_date, db_connection, ssl_verify=True):
    for start_station, end_station in combinations:
        print(f"Fetching train schedule from station {start_station} to {end_station}...")
        start_time = time.time()

        result = fetch_train_schedule(start_station, end_station, search_date, verify=ssl_verify)

        end_time = time.time()
        print(f"Received response for {start_station} to {end_station}. Time taken: {end_time - start_time} seconds.")

        log_execution_to_db(db_connection, start_station, end_station, search_date, result)

        if result["status"] == "success":
            log_train_schedule_to_db(result, db_connection)

        time.sleep(1)  # Simulate delay between requests

# Runner function
if __name__ == "__main__":
    db_path = "train_schedule.db"
    search_date = "14/09/2024"

    with connect_db(db_path) as conn:
        combinations = fetch_station_combinations(conn)
        run_requests_for_combinations(combinations[:2], search_date, conn, ssl_verify=False)
