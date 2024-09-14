import logging
import os

def setup_logging(log_file="logs/train_schedule.log", debug_mode=False):
    log_directory = os.path.dirname(log_file)
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    log_level = logging.DEBUG if debug_mode else logging.INFO  # Toggle debug_mode to switch between DEBUG and INFO

    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    logging.info(f"Logging is set up. Log file: {log_file}. Debug mode: {debug_mode}")

def log_response_to_file(start_station, end_station, search_date, result, log_responses):
    if log_responses:
        # Logging the response as a DEBUG log message
        logging.debug(f"Train schedule response for {start_station} to {end_station}: {{"
                      f"start_station: {start_station}, "
                      f"end_station: {end_station}, "
                      f"search_date: {search_date}, "
                      f"result: {result}}}")
