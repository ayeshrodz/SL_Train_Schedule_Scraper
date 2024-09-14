import requests
from bs4 import BeautifulSoup
import time

# Utility function for cleaning text
def clean_text(text):
    return text.replace("\r", "").replace("\n", "").replace("\t", "").replace("\u00a0", "").strip()

# Function to fetch train schedule between two stations
def fetch_train_schedule(start_station, end_station, search_date, locale="en", verify=True):
    url = "https://eservices.railway.gov.lk/schedule/searchTrain.action"
    data = {
        "searchCriteria.startStationID": start_station,
        "searchCriteria.endStationID": end_station,
        "searchDate": search_date,
        "selectedLocale": locale
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
                        available_classes_info = []
                        other_info = ""

                        if len(additional_info_cells) > 1:
                            available_classes_info = clean_text(
                                additional_info_cells[0].get_text(strip=True).replace("Available Classes:", "")
                            ).split(',')
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
                            "additional_info": {
                                "available_classes": [clean_text(cls) for cls in available_classes_info],
                                "other_info": other_info
                            }
                        }
                        train_schedule.append(train_data)

                metadata = {
                    "http_status": response.status_code,
                    "request_time": int(request_time),
                    "response_time": int(response_time),
                    "request_duration_seconds": int(response_time - request_time),
                    "request_parameters": data
                }

                return {
                    "status": "success",
                    "message": "Train schedule data retrieved successfully",
                    "data_count": len(train_schedule),
                    "data": train_schedule,
                    "meta": metadata
                }
            else:
                return {
                    "status": "error",
                    "message": "No train schedule data found in the response",
                    "data_count": 0,
                    "data": [],
                    "meta": {
                        "http_status": response.status_code,
                        "request_time": int(request_time),
                        "response_time": int(response_time),
                        "request_duration_seconds": int(response_time - request_time),
                        "request_parameters": data
                    }
                }
        else:
            return {
                "status": "error",
                "message": f"Failed to retrieve train schedule data. HTTP Status Code: {response.status_code}",
                "data_count": 0,
                "data": [],
                "meta": {
                    "http_status": response.status_code,
                    "request_time": int(request_time),
                    "response_time": int(response_time),
                    "request_duration_seconds": int(response_time - request_time),
                    "request_parameters": data
                }
            }
    except requests.exceptions.RequestException as e:
        response_time = time.time()
        return {
            "status": "error",
            "message": f"An error occurred: {str(e)}",
            "data_count": 0,
            "data": [],
            "meta": {
                "http_status": None,
                "request_time": int(request_time),
                "response_time": int(response_time),
                "request_duration_seconds": int(response_time - request_time),
                "request_parameters": data
            }
        }
