import requests
from bs4 import BeautifulSoup
import re
import time

# Define a regex pattern to match time in HH:MM:SS format
time_pattern = re.compile(r"\d{2}:\d{2}:\d{2}")

def extract_destination_and_time(text):
    """Function to separate destination and time intelligently."""
    parts = text.split()
    destination_parts = []
    time_part = ""

    # Loop through the parts and separate destination and time
    for part in parts:
        if time_pattern.match(part):
            time_part = part
        else:
            destination_parts.append(part)

    # Join destination parts to form the full destination
    destination = " ".join(destination_parts)
    return destination, time_part

def clean_text(text):
    """Utility function to clean up unwanted characters from the text."""
    return text.replace("\r", "").replace("\n", "").replace("\t", "").replace("\u00a0", "").strip()

def fetch_train_schedule(start_station, end_station, search_date, verify=True):
    url = "https://eservices.railway.gov.lk/schedule/searchTrain.action"
    data = {
        "searchCriteria.startStationID": start_station,
        "searchCriteria.endStationID": end_station,
        "searchDate": search_date,
        "selectedLocale": "en"
    }

    # Capture request start time in epoch
    request_time = time.time()

    try:
        # Make the POST request with or without SSL verification based on the flag
        response = requests.post(url, data=data, verify=verify)
        
        # Capture response time in epoch
        response_time = time.time()

        # Check if the response was successful
        if response.status_code == 200:
            # Parse the HTML content
            soup = BeautifulSoup(response.content, "html.parser")
            
            # Initialize a list to store train details
            train_schedule = []

            # Extracting the train details from the table rows
            table = soup.find("table", class_="table")

            if table:
                for row in table.find_all("tr"):
                    cells = row.find_all("td")
                    
                    # Process only the main train data rows (ignoring those that don't have 8 cells)
                    if len(cells) == 8:
                        destination_info_raw = clean_text(cells[3].get_text(strip=True))
                        end_station_info_raw = clean_text(cells[4].get_text(strip=True))

                        # Extract destination and time separately
                        destination, destination_time = extract_destination_and_time(destination_info_raw)
                        end_station, end_station_time = extract_destination_and_time(end_station_info_raw)

                        # Extract available classes and other information from the "additional info" row
                        additional_row = row.find_next_sibling("tr")
                        additional_info_cells = additional_row.find_all("td")
                        if len(additional_info_cells) > 1:
                            # Extract available classes
                            available_classes_info = clean_text(additional_info_cells[0].get_text(strip=True).replace("Available Classes:", "")).split(',')
                            # Extract other info
                            other_info = clean_text(additional_info_cells[1].get_text(strip=True))

                        train_data = {
                            "station": clean_text(cells[0].get_text(strip=True)),
                            "arrival_time": clean_text(cells[1].get_text(strip=True)),
                            "departure_time": clean_text(cells[2].get_text(strip=True)),
                            "destination": destination,
                            "destination_time": destination_time,
                            "end_station": end_station,
                            "end_station_time": end_station_time,
                            "frequency": clean_text(cells[5].get_text(strip=True)),
                            "train_name": clean_text(cells[7].get_text(strip=True)),
                            "train_no": clean_text(cells[6].get_text(strip=True)),
                            "additional_info": {
                                "available_classes": [clean_text(cls) for cls in available_classes_info],
                                "other_info": other_info
                            }
                        }
                        train_schedule.append(train_data)

                # Metadata section with epoch timestamps
                metadata = {
                    "http_status": response.status_code,
                    "request_time": int(request_time),
                    "response_time": int(response_time),
                    "request_duration_seconds": int(response_time - request_time),
                    "request_parameters": data
                }

                # Final output JSON structure
                output_data = {
                    "status": "success",
                    "message": "Train schedule data retrieved successfully",
                    "data_count": len(train_schedule),
                    "data": train_schedule,
                    "meta": metadata
                }

            else:
                # If no table is found, handle it as an error (empty data)
                output_data = {
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
            # If the response status code is not 200, handle the error
            output_data = {
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
        # Handle any exceptions that occur during the request
        response_time = time.time()  # Capture the response time even if there's an error
        output_data = {
            "status": "error",
            "message": f"An error occurred: {str(e)}",
            "data_count": 0,
            "data": [],
            "meta": {
                "http_status": None,  # No HTTP status since the request failed
                "request_time": int(request_time),
                "response_time": int(response_time),
                "request_duration_seconds": int(response_time - request_time),
                "request_parameters": data
            }
        }

    return output_data
