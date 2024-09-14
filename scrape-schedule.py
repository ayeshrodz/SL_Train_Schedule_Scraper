import requests
from bs4 import BeautifulSoup
import json
import time

# URL and form data
url = "https://eservices.railway.gov.lk/schedule/searchTrain.action"
data = {
    "searchCriteria.startStationID": "3",
    "searchCriteria.endStationID": "410",
    "searchDate": "14/09/2024",
    "selectedLocale": "en"
}

# Capture request start time in epoch
request_time = time.time()

try:
    # Make the POST request with SSL verification disabled
    response = requests.post(url, data=data, verify=False)

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

        def clean_text(text):
            """Utility function to clean up unwanted characters from the text."""
            return text.replace("\r", "").replace("\n", "").replace("\t", "").replace("\u00a0", "").strip()

        if table:
            for row in table.find_all("tr"):
                cells = row.find_all("td")
                
                # Process only the main train data rows (ignoring those that don't have 8 cells)
                if len(cells) == 8:
                    # Extract the main train details
                    destination_info = clean_text(cells[3].get_text(strip=True)).split()
                    end_station_info = clean_text(cells[4].get_text(strip=True)).split()

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

# Save the cleaned data to a JSON file
with open("train_schedule_cleaned.json", "w") as json_file:
    json.dump(output_data, json_file, indent=4)

print("Train schedule saved to train_schedule_cleaned.json")
