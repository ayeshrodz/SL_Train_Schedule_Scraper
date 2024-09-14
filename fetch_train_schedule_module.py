import requests
from bs4 import BeautifulSoup
import json
import time
import sqlite3

def fetch_train_schedule(start_station_id, end_station_id, search_date, selected_locale, db_conn, verify=True):
    url = "https://eservices.railway.gov.lk/schedule/searchTrain.action"
    data = {
        "searchCriteria.startStationID": start_station_id,
        "searchCriteria.endStationID": end_station_id,
        "searchDate": search_date,
        "selectedLocale": selected_locale
    }

    request_time = time.time()

    try:
        response = requests.post(url, data=data, verify=verify)
        response_time = time.time()

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            table = soup.find("table", class_="table")

            if table:
                train_schedule = []
                for row in table.find_all("tr"):
                    cells = row.find_all("td")
                    if len(cells) == 8:
                        destination_info = clean_text(cells[3].get_text(strip=True)).split()
                        end_station_info = clean_text(cells[4].get_text(strip=True)).split()
                        additional_row = row.find_next_sibling("tr")
                        additional_info_cells = additional_row.find_all("td")
                        available_classes_info = clean_text(additional_info_cells[0].get_text(strip=True).replace("Available Classes:", "")).split(',')
                        other_info = clean_text(additional_info_cells[1].get_text(strip=True))

                        train_data = {
                            "station": clean_text(cells[0].get_text(strip=True)),
                            "arrival_time": clean_text(cells[1].get_text(strip=True)),
                            "departure_time": clean_text(cells[2].get_text(strip=True)),
                            "destination": destination_info[0],
                            "destination_time": destination_info[1] if len(destination_info) > 1 else "",
                            "end_station": end_station_info[0],
                            "end_station_time": end_station_info[1] if len(end_station_info) > 1 else "",
                            "frequency": clean_text(cells[5].get_text(strip=True)),
                            "train_name": clean_text(cells[7].get_text(strip=True)),
                            "train_no": clean_text(cells[6].get_text(strip=True)),
                            "available_classes": ','.join(available_classes_info),
                            "other_info": other_info
                        }

                        train_schedule.append(train_data)
                        save_train_schedule_to_db(train_data, db_conn, start_station_id, end_station_id, search_date, selected_locale)

                save_execution_log(db_conn, start_station_id, end_station_id, search_date, selected_locale, request_time, response_time, response.status_code, 'success', 'Train schedule data retrieved successfully')
            else:
                save_execution_log(db_conn, start_station_id, end_station_id, search_date, selected_locale, request_time, response_time, response.status_code, 'error', 'No train schedule data found in the response')

        else:
            save_execution_log(db_conn, start_station_id, end_station_id, search_date, selected_locale, request_time, response_time, response.status_code, 'error', f"HTTP Status Code: {response.status_code}")

    except requests.exceptions.RequestException as e:
        response_time = time.time()
        save_execution_log(db_conn, start_station_id, end_station_id, search_date, selected_locale, request_time, response_time, None, 'error', f"An error occurred: {str(e)}")


def clean_text(text):
    return text.replace("\r", "").replace("\n", "").replace("\t", "").replace("\u00a0", "").strip()

def save_train_schedule_to_db(data, db_conn, start_station_id, end_station_id, search_date, selected_locale):
    cursor = db_conn.cursor()
    cursor.execute("""
        INSERT INTO train_schedules (start_station_id, end_station_id, search_date, selected_locale, station, arrival_time, departure_time, destination, destination_time, end_station, end_station_time, frequency, train_name, train_no, available_classes, other_info)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        start_station_id, end_station_id, search_date, selected_locale,
        data["station"], data["arrival_time"], data["departure_time"], data["destination"], data["destination_time"],
        data["end_station"], data["end_station_time"], data["frequency"], data["train_name"], data["train_no"],
        data["available_classes"], data["other_info"]
    ))
    db_conn.commit()

def save_execution_log(db_conn, start_station_id, end_station_id, search_date, selected_locale, request_time, response_time, http_status, status, message):
    cursor = db_conn.cursor()
    cursor.execute("""
        INSERT INTO execution_logs (start_station_id, end_station_id, search_date, selected_locale, request_time, response_time, request_duration_seconds, http_status, status, message)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        start_station_id, end_station_id, search_date, selected_locale, int(request_time), int(response_time),
        int(response_time - request_time), http_status, status, message
    ))
    db_conn.commit()
