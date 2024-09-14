# log_module.py
import sqlite3

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
    cursor.execute("""
        INSERT INTO execution_logs (start_station_id, end_station_id, search_date, status, message, request_time, 
                                    response_time, request_duration_seconds, data_count)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        start_station, end_station, search_date, result["status"], result["message"],
        result["meta"]["request_time"], result["meta"]["response_time"], 
        result["meta"]["request_duration_seconds"], result["data_count"]
    ))
    db_connection.commit()
