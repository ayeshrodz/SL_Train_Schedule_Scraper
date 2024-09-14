import logging
import time
import os
import sqlite3
import urllib3
from fetch_train_schedule_module import fetch_train_schedule
from log_module import log_train_schedule_to_db, log_execution_to_db, log_response_to_file
from db_module import connect_db, fetch_station_combinations
from logging_module import setup_logging

# Function to execute requests for combinations sequentially
def run_requests_for_combinations(combinations, search_date, db_connection, ssl_verify=True, log_responses=False):
    for start_station, end_station in combinations:
        try:
            logging.info(f"Fetching train schedule from station {start_station} to {end_station}...")
            start_time = time.time()

            # Fetch the result
            result = fetch_train_schedule(start_station, end_station, search_date, verify=ssl_verify)

            end_time = time.time()
            logging.info(f"Received response for {start_station} to {end_station}. Time taken: {end_time - start_time:.6f} seconds.")

            # Log response to the debug log file if needed
            log_response_to_file(start_station, end_station, search_date, result, log_responses)

            # Check the result status
            if result["status"] == "success":
                if result["data_count"] > 0:
                    log_train_schedule_to_db(result, db_connection)
                    logging.info(f"Data fetched and logged for {start_station} to {end_station}.")
                else:
                    logging.info(f"No train schedule data found for {start_station} to {end_station}.")
            else:
                logging.warning(f"Failed to fetch data for {start_station} to {end_station}: {result['message']}")
            
            # Ensure the execution log is always saved regardless of status
            log_execution_to_db(db_connection, start_station, end_station, search_date, result)

            time.sleep(2)  # Simulate delay between requests
        except Exception as e:
            logging.error(f"An error occurred while processing {start_station} to {end_station}: {str(e)}", exc_info=True)
            # Log the failed attempt to the execution log even if there's an error
            log_execution_to_db(db_connection, start_station, end_station, search_date, {
                "status": "error",
                "message": str(e),
                "data_count": 0,
                "meta": {
                    "http_status": None,  # No HTTP status in case of exception
                    "request_time": int(start_time),
                    "response_time": int(time.time()),
                    "request_duration_seconds": int(time.time() - start_time),
                    "request_parameters": {
                        "start_station": start_station,
                        "end_station": end_station,
                        "search_date": search_date
                    }
                }
            })

# Function to check if the database file exists, and if not, initialize it
def ensure_database_initialized(db_path):
    if not os.path.exists(db_path):
        logging.info(f"Database file '{db_path}' not found. Initializing database...")
        # Run the initialization script
        os.system('python initialize_db.py')
        logging.info("Database initialized.")
        # Insert stations into the database
        os.system('python insert_stations.py')
        logging.info("Stations inserted into the database.")
    else:
        logging.info(f"Database file '{db_path}' already exists.")

# Runner function
if __name__ == "__main__":
    # Set debug_mode=True to enable DEBUG logs, False to disable
    debug_mode = False

    # Set up logging with the debug_mode flag
    setup_logging(debug_mode=debug_mode)

    # Suppress InsecureRequestWarning if debug_mode is False
    if not debug_mode:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    db_path = "train_schedule.db"
    search_date = "14/09/2024"

    # Ensure the database is initialized and the stations are inserted
    ensure_database_initialized(db_path)

    # Enable response logging only when in debug mode
    log_responses = debug_mode  # Automatically ties response logging to the debug mode

    try:
        with connect_db(db_path) as conn:
            combinations = fetch_station_combinations(conn)
            run_requests_for_combinations(combinations[:5], search_date, conn, ssl_verify=False, log_responses=log_responses)
    except Exception as e:
        logging.critical(f"Fatal error occurred: {str(e)}", exc_info=True)
