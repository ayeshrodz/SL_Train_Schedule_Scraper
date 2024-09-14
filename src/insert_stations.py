import sqlite3
import csv

# Database connection
db_file = "train_schedule.db"  # Make sure to match the file name with your database
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# Path to the CSV file
csv_file_path = "stations.csv"  # Path to your CSV file

# Insert stations into the database
def insert_stations_from_csv(csv_file_path):
    try:
        with open(csv_file_path, mode='r') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)  # Skip the header row if present

            for row in csv_reader:
                station_id = row[0]
                station_name = row[1]

                # Insert each station into the stations table
                cursor.execute("""
                    INSERT INTO stations (station_id, station_name)
                    VALUES (?, ?)
                """, (station_id, station_name))

        # Commit the transaction
        conn.commit()
        print(f"Stations inserted successfully from {csv_file_path}")

    except Exception as e:
        print(f"An error occurred while inserting stations: {e}")
    finally:
        # Close the database connection
        conn.close()

# Call the function to insert data
insert_stations_from_csv(csv_file_path)
