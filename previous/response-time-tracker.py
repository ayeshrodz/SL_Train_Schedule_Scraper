import requests
import time
import datetime
import csv
import urllib3

# Disable InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# List of time gaps to test (in seconds)
time_gaps = [180, 150, 120, 90, 60, 45, 30]

# Number of iterations per time gap
iterations = 5

# URL and form data
url = "https://eservices.railway.gov.lk/schedule/searchTrain.action"
form_data = {
    "searchCriteria.startStationID": "107",
    "searchCriteria.endStationID": "160",
    "searchDate": "14/09/2024",
    "selectedLocale": "en"
}

# File to save the results
output_file = "server_response_times.csv"

# Open the CSV file for writing
with open(output_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow([
        "Time Gap (s)", "Iteration", "Request Time", "Response Time",
        "Response Delay (s)", "Status Code", "Error Message"
    ])

    for gap in time_gaps:
        print(f"\nTesting with a time gap of {gap} seconds...\n")
        for i in range(iterations):
            request_time = datetime.datetime.now()
            try:
                # Make the POST request
                response = requests.post(url, data=form_data, verify=False, timeout=300)
                response_time = datetime.datetime.now()
                response_delay = (response_time - request_time).total_seconds()
                status_code = response.status_code
                error_message = ""
                print(f"Iteration {i+1}:")
                print(f"Request Time: {request_time.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"Response Time: {response_time.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"Response Delay: {response_delay:.2f} seconds")
                print(f"Status Code: {status_code}\n")

                # Write the data to the CSV file
                writer.writerow([
                    gap, i+1, request_time.strftime('%Y-%m-%d %H:%M:%S'),
                    response_time.strftime('%Y-%m-%d %H:%M:%S'),
                    f"{response_delay:.2f}", status_code, error_message
                ])

            except Exception as e:
                response_time = datetime.datetime.now()
                response_delay = (response_time - request_time).total_seconds()
                status_code = "N/A"
                error_message = str(e)
                print(f"Iteration {i+1}: Error during request: {e}\n")

                # Write the error to the CSV file
                writer.writerow([
                    gap, i+1, request_time.strftime('%Y-%m-%d %H:%M:%S'),
                    response_time.strftime('%Y-%m-%d %H:%M:%S'),
                    f"{response_delay:.2f}", status_code, error_message
                ])

            # Wait for the specified time gap before the next request
            time.sleep(gap)

print(f"\nTesting complete. Results saved to {output_file}.")
