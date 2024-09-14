import csv
import itertools
import time
import json
from fetch_train_schedule_module import fetch_train_schedule

# Function to read station ids from a CSV file
def read_station_ids_from_csv(file_path):
    stations = []
    with open(file_path, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            stations.append(row['station_id'])
    return stations

# Function to generate unique station combinations
def generate_unique_station_combinations(stations):
    return list(itertools.combinations(stations, 2))

# Function to run two requests synchronously and print the time gaps
def run_requests_for_two_combinations(combinations, ssl_verify=False):
    results = []
    for i, (start_station, end_station) in enumerate(combinations[:2]):  # Limit to 2 requests
        print(f"Fetching train schedule from station {start_station} to {end_station}...")

        start_time = time.time()  # Capture the start time of the request
        result = fetch_train_schedule(start_station, end_station, verify=ssl_verify)
        end_time = time.time()  # Capture the end time of the request
        
        duration = end_time - start_time  # Calculate the duration
        print(f"Fetched data between station {start_station} and {end_station}. Execution time: {duration:.2f} seconds.")

        results.append(result)
        
        # Small delay between requests (optional)
        time.sleep(1)
    
    return results

# Function to save results to a JSON file
def save_results_to_json(results, output_file):
    with open(output_file, 'w') as file:
        json.dump(results, file, indent=4)

if __name__ == "__main__":
    # Read station IDs from the CSV file
    station_ids = read_station_ids_from_csv("stations.csv")
    
    # Generate unique combinations of stations
    combinations = generate_unique_station_combinations(station_ids)
    
    # Run the requests for two combinations synchronously and measure the time gaps
    results = run_requests_for_two_combinations(combinations, ssl_verify=False)  # Set ssl_verify=False for now
    
    # Save the results to a JSON file
    save_results_to_json(results, "train_schedule_results.json")
    
    print("Completed fetching train schedules for 2 station combinations.")
