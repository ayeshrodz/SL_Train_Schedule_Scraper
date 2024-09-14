import sqlite3
import logging
import os
import json
import time

# Function to log the result in SQLite database
def log_train_schedule_to_db(result, db_connection):
    cursor = db_connection.cursor()
    for train in result["data"]:
        cursor.execute("""
            INSERT INTO train_schedules (station, arrival_time, departure_time, destination, destination_time, 
                                         end_station, end_station_time, frequency, train_name, train_no, 
                                         available_classes, other_info)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            train["station"], train["arrival_time"], train["departure_time"], train["destination"],
            train["destination_time"], train["end_station"], train["end_station_time"], train["frequency"],
            train["train_name"], train["train_no"], ','.join(train["additional_info"]["available_classes"]),
            train["additional_info"]["other_info"]
        ))
    db_connection.commit()

# Function to log the execution details to SQLite
def log_execution_to_db(db_connection, start_station, end_station, search_date, result):
    cursor = db_connection.cursor()

    # Extract meta information from result
    meta = result.get("meta", {})
    request_time = meta.get("request_time")
    response_time = meta.get("response_time")
    request_duration = meta.get("request_duration_seconds", 0)
    http_status = meta.get("http_status", None)
    response_message = result.get("message", "")
    data_count = result.get("data_count", 0)

    # Insert execution log into the database
    cursor.execute("""
        INSERT INTO execution_logs (start_station_id, end_station_id, search_date, 
                                    request_time, response_time, request_duration_seconds, 
                                    http_status, response_message, data_count)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (start_station, end_station, search_date, request_time, response_time, request_duration, 
          http_status, response_message, data_count))

    db_connection.commit()

# Function to log response data into the regular debug log
def log_response_to_file(start_station, end_station, search_date, result, log_responses=False):
    if log_responses:
        log_message = {
            "start_station": start_station,
            "end_station": end_station,
            "search_date": search_date,
            "response_time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),  # Using the time module here
            "result": result
        }

        # Log the JSON response as a debug message in the log file
        logging.debug(f"Train schedule response: {json.dumps(log_message, indent=4)}")
