import threading
import time
import datetime
from plexapi.server import PlexServer
import tidalapi
import subprocess
import os
import json

# Configuration and log setup
baseurl = 'http://localhost:32400'
token = '--L5DmQR3T_coBnzu3PW'
plex = PlexServer(baseurl, token)

session = tidalapi.Session()
current_directory = os.path.dirname(__file__)
cred_file = current_directory + "/.credentials"

print_lock = threading.Lock()
scan_event = threading.Event()

# Load or initialize configuration
def load_config():
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"interval": 1800}  # Default interval of 30 minutes in seconds

# Save configuration
def save_config(config):
    with open('config.json', 'w') as f:
        json.dump(config, f)


def log(message, interval=None):
    """ Helper function to add timestamp to log messages with thread synchronization. """
    with print_lock:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if interval is not None:
            message += f" (Interval: {interval} seconds)"
        print(f"\n{timestamp} - {message}")




# Read credentials
def read_creds():
    with open(cred_file, "r") as f:
        lines = f.readlines()
        typ = lines[0][4:].strip()
        tok = lines[1][4:].strip()
        ref = lines[2][4:].strip()
        exp = lines[3][4:].strip()
    return typ, tok, ref, exp

# Write credentials
def write_creds(typ, tok, ref, exp):
    with open(cred_file, "w+") as f:
        f.write("typ=" + typ + "\n")
        f.write("tok=" + tok + "\n")
        f.write("ref=" + ref + "\n")
        f.write("exp=" + exp.strftime("%Y-%m-%d %H:%M:%S.%f"))
        f.close()
        log("New credentials saved to: " + cred_file)

def login(): 
    session.login_oauth_simple()
    token_type = session.token_type
    access_token = session.access_token
    refresh_token = session.refresh_token
    expiry_time = session.expiry_time
    write_creds(token_type, access_token, refresh_token, expiry_time)
    log("New token expires:" + expiry_time.strftime("%Y-%m-%d %H:%M:%S.%f"))
    return session.check_login()

def connect(session):
    try:  
        creds = read_creds()
    except:  
        log("API credentials could not be read")
        login()  
        return session.check_login()

    try:  
        if session.load_oauth_session(
            creds[0], creds[1], creds[2], creds[3]
        ):  
            log("Session Connected")
    except:  
        log("Connection Failed, try getting new API credentials")
        if login():  
            log("Successfully logged in")
        else:  
            log("Log in failed, exiting")
            exit(0)
    return session.check_login()  

# Enhanced log function to ensure thread-safe prints
def thread_safe_log(message):
    with threading.Lock():
        print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}")

# Settings menu
def settings_menu():
    global next_scan_time, scan_event
    with print_lock:
        config = load_config()
        print(f"\nCurrent scan interval is {config['interval']} seconds.")
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
        log(f"Interval updated to {new_interval} seconds.")
        next_scan_time = time.time() + new_interval  # Reset the next scan time immediately to the new interval
        scan_event.set()  # Wake up the scan thread immediately
    else:
        with print_lock:
            log("Invalid input. Please specify 'm' for minutes or 's' for seconds.")




# Background scanning function
def background_scanning():
    while True:
        check_albums()
        time.sleep(load_config()['interval'])  # Load the interval from the configuration


# Check and process albums
def check_albums():
    while True:
        config = load_config()  # Move this inside the loop to always get the latest interval
        interval = config['interval']
        favorite_albums = session.user.favorites.albums() if session.user.favorites.albums() else []
        if not favorite_albums:
            log("No favorited albums to process.", interval=interval)
            time.sleep(interval)  # Sleep based on the updated interval
            continue

        for album in favorite_albums:
            log(f"{album.id} - {album.name} by {album.artist.name}", interval=interval)
            command = f"tidal-dl -l {album.id}"
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            if stderr:
                log(f"Error executing command for album {album.id}: {stderr.decode('utf-8')}", interval=interval)
            else:
                log(stdout.decode("utf-8"), interval=interval)
                session.user.favorites.remove_album(album.id)
                update_library()




def main_loop():
    global scan_event
    next_scan_time = time.time()

    def start_scanning():
        global scan_event
        nonlocal next_scan_time
        while True:
            time_to_wait = next_scan_time - time.time()
            scan_event.wait(timeout=max(0, time_to_wait))
            scan_event.clear()

            if time.time() >= next_scan_time:
                check_albums()
                config = load_config()
                next_scan_time = time.time() + config['interval']

    scan_thread = threading.Thread(target=start_scanning)
    scan_thread.daemon = True
    scan_thread.start()

    while True:
        user_input = input("\nPress 'c' to change settings, 's' to scan now, or 'q' to quit: \n")
        if user_input == 'c':
            settings_menu()
        elif user_input == 's':
            log("Manual scan triggered.")
            check_albums()
            next_scan_time = time.time() + load_config()['interval']
            scan_event.set()
        elif user_input == 'q':
            print("Exiting program.")
            break

if __name__ == "__main__":
    if connect(session):
        main_loop()
    else:
        log("Connection has failed.")

