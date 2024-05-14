import threading
import time
import datetime
import msvcrt  
from plexapi.server import PlexServer
import tidalapi
import subprocess
import os
import json
import logging
import argparse
from logging.handlers import TimedRotatingFileHandler

os.environ['PYTHONIOENCODING'] = 'utf-8'

baseurl = 'http://localhost:32400'
token = '<YOUR TOKEN HERE>'
plex = PlexServer(baseurl, token)

session = tidalapi.Session()
current_directory = os.path.dirname(__file__)
cred_file = current_directory + "/.credentials"

scan_event = threading.Event()
reset_interval_event = threading.Event()

logging.basicConfig(level=logging.INFO, filename='application.log',
                    format='%(asctime)s - %(levelname)s - %(message)s')

def load_config():
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.warning("Config file not found. Using default settings.")
        return {"interval": 1800}  

def save_config(config):
    with open('config.json', 'w') as f:
        json.dump(config, f)
    logging.info("Configuration saved.")

def read_creds():
    with open(cred_file, "r") as f:
        lines = f.readlines()
        typ = lines[0][4:].strip()
        tok = lines[1][4:].strip()
        ref = lines[2][4:].strip()
        exp = lines[3][4:].strip()
    return typ, tok, ref, exp

def write_creds(typ, tok, ref, exp):
    with open(cred_file, "w+") as f:
        f.write("typ=" + typ + "\n")
        f.write("tok=" + tok + "\n")
        f.write("ref=" + ref + "\n")
        f.write("exp=" + exp.strftime("%Y-%m-%d %H:%M:%S.%f"))
    logging.info(f"New credentials saved to: {cred_file}")

def login(): 
    session.login_oauth_simple()
    token_type = session.token_type
    access_token = session.access_token
    refresh_token = session.refresh_token
    expiry_time = session.expiry_time
    write_creds(token_type, access_token, refresh_token, expiry_time)
    logging.info(f"New token expires: {expiry_time.strftime('%Y-%m-%d %H:%M:%S.%f')}")
    return session.check_login()

def connect(session):
    try:  
        creds = read_creds()
    except Exception as e:  
        logging.error("API credentials could not be read", exc_info=True)
        return login()

    try:  
        if session.load_oauth_session(*creds):  
            logging.info("Session Connected")
    except Exception as e:  
        logging.error("Connection Failed, try getting new API credentials", exc_info=True)
        if login():  
            logging.info("Successfully logged in")
        else:  
            logging.error("Log in failed, exiting")
            exit(0)
    return session.check_login()  

def settings_menu():
    global next_scan_time, scan_event, reset_interval_event
    config = load_config()
    print("Options: \n1. Set Interval \n2. Set Schedule Start Time")
    choice = input("Enter choice: ")

    if choice == '1':
        interval_input = input("Enter new interval (e.g., '30m' for 30 minutes or '45s' for 45 seconds): ")
        valid_input = False
        if interval_input.endswith('m'):
            minutes = int(interval_input[:-1])
            new_interval = minutes * 60
            valid_input = True
        elif interval_input.endswith('s'):
            new_interval = int(interval_input[:-1])
            valid_input = True

        if valid_input:
            config['interval'] = new_interval
            save_config(config)
            logging.info(f"Interval updated to {new_interval} seconds.")
            print(f"Please restart the application for the schedule changes to be applied.")

            last_scan_time = time.time()
            with open('last_scan_time.txt', 'w') as file:
                file.write(str(last_scan_time))

            next_scan_time = last_scan_time + new_interval
            next_scan_time_str = datetime.datetime.fromtimestamp(next_scan_time).strftime('%Y-%m-%d %H:%M:%S')
            logging.info(f"Next scan now scheduled for: {next_scan_time_str}")

            reset_interval_event.set()
            reset_interval_event.clear()
        else:
            logging.warning("Invalid input for interval change.")

    elif choice == '2':
        schedule_input = input("Enter schedule start time (e.g., 2024-05-11 19:00:00): ")
        try:
            scheduled_time = datetime.datetime.strptime(schedule_input, '%Y-%m-%d %H:%M:%S')
            current_time = datetime.datetime.now()
            if scheduled_time < current_time:
                raise ValueError("Scheduled time must be in the future.")
            initial_wait = (scheduled_time - current_time).total_seconds()
            with open('scheduled_time.txt', 'w') as file:
                file.write(schedule_input)
            logging.info(f"Scan scheduled to start at: {scheduled_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Please restart the application for the schedule changes to be applied.")
        except ValueError as e:
            print(f"Invalid date format or date in the past: {e}")

def background_scanning():
    logging.info("Background scanning thread started.")
    next_scan_time = None

    while True:
        try:
            current_time = time.time()
            if next_scan_time is None or current_time >= next_scan_time:

                logging.info("Performing interval-based scan.")
                check_albums(session)

                config = load_config()
                interval = config['interval']
                next_scan_time = current_time + interval

            time.sleep(1)

        except Exception as e:
            logging.error(f"Error during background scanning: {str(e)}")
            time.sleep(10)  

def check_albums(session):
    config = load_config()
    interval = config['interval']
    favorite_albums = session.user.favorites.albums() if session.user.favorites.albums() else []

    last_scan_time = time.time()
    with open('last_scan_time.txt', 'w') as file:
        file.write(str(last_scan_time))

    if not favorite_albums:
        logging.info("No favorited albums to process.", extra={"interval": interval})
        return

    for album in favorite_albums:
        command = f"tidal-dl -l {album.id}"
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        if stderr:
            logging.error(f"Error executing command for album {album.id}: {stderr.decode('utf-8', errors='replace')}", extra={"interval": interval})
        else:

            output = stdout.decode('utf-8', errors='ignore')
            logging.info(output, extra={"interval": interval})

            session.user.favorites.remove_album(album.id)
            update_library()

def display_next_scan_time():
    try:

        with open('scheduled_time.txt', 'r') as file:
            scheduled_time_str = file.read().strip()
        scheduled_time = datetime.datetime.strptime(scheduled_time_str, '%Y-%m-%d %H:%M:%S')
        current_time = datetime.datetime.now()

        if scheduled_time > current_time:
            next_scan_time_str = scheduled_time.strftime('%Y-%m-%d %H:%M:%S')
            logging.info(f"Next scan scheduled to start at: {next_scan_time_str}")
        else:

            raise ValueError("Scheduled time is in the past")
    except (FileNotFoundError, ValueError):

        config = load_config()
        interval = config['interval']
        next_scan_time = time.time() + interval
        next_scan_time_str = datetime.datetime.fromtimestamp(next_scan_time).strftime('%Y-%m-%d %H:%M:%S')
        logging.info(f"Next scan scheduled for: {next_scan_time_str}")

def update_library():
    for library in plex.library.sections():
        library.update()
        logging.info(f"Updating library: {library.title}")

def setup_logging():

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    file_handler = TimedRotatingFileHandler('application.log', when='midnight', interval=1, backupCount=30)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    file_handler.backupCount = 30

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.INFO)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

def parse_arguments():
    parser = argparse.ArgumentParser(description="Control the media scanning script.")
    parser.add_argument('-i', '--interval', type=str, help='Set the interval for scans, e.g., 30m or 45s')
    parser.add_argument('-s', '--schedule', type=str, help='Schedule a start time for the scan, e.g., "2024-05-12 15:00:00"')
    return parser.parse_args()

def main_loop():
    global next_scan_time, scan_event
    next_scan_time = time.time()

    background_scan_thread = threading.Thread(target=background_scanning)
    background_scan_thread.daemon = True
    background_scan_thread.start()

    while True:
        user_input = input("\nPress 'c' to change settings, 's' to scan now, or 'q' to quit: \n")
        if user_input == 'c':
            settings_menu()
        elif user_input == 's':
            logging.info("Manual scan triggered.")
            check_albums(session)
        elif user_input == 'q':
            logging.info("Exiting program.")
            break

import sys
import datetime

if __name__ == "__main__":
    args = parse_arguments()
    setup_logging()

    if args.interval:
        try:
            value = int(args.interval[:-1])
            if args.interval.endswith('m'):
                new_interval = value * 60
            elif args.interval.endswith('s'):
                new_interval = value
            else:
                raise ValueError("Invalid interval format.")

            config = load_config()
            config['interval'] = new_interval
            save_config(config)
            logging.info(f"Interval set via command line to {new_interval} seconds.")
        except ValueError as e:
            logging.error(f"Error setting interval from command line: {e}")
            sys.exit(1)  

    if args.schedule:
        try:
            scheduled_time = datetime.datetime.strptime(args.schedule, '%Y-%m-%d %H:%M:%S')
            current_time = datetime.datetime.now()
            if scheduled_time < current_time:
                raise ValueError("Scheduled time must be in the future.")
            with open('scheduled_time.txt', 'w') as file:
                file.write(args.schedule)
            logging.info(f"Scanning scheduled to start at: {args.schedule}")
        except ValueError as e:
            logging.error(f"Error setting scheduled time from command line: {e}")
            sys.exit(1)  

    if connect(session):
        display_next_scan_time()  
        main_loop()
    else:
        logging.error("Connection has failed.")
