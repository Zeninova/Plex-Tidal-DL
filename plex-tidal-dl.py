import tidalapi
import subprocess
import os
import time
from plexapi.server import PlexServer
import datetime

baseurl = 'http://localhost:32400'
token = '<YOUR TOKEN HERE>'
plex = PlexServer(baseurl, token)

session = tidalapi.Session()
current_directory = os.path.dirname(__file__)
cred_file = current_directory+"/.credentials" 

def log(message):
    """ Helper function to add timestamp to log messages. """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{timestamp} - {message}")

def read_creds(): 
    f = open(cred_file, "r")
    Lines = f.readlines()
    type = Lines[0][4:].strip()
    token = Lines[1][4:].strip()
    refresh = Lines[2][4:].strip()
    expiry = Lines[3][4:].strip()
    return type, token, refresh, expiry

def write_creds(typ, tok, ref, exp): 
    f = open(cred_file, "w+")
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

def check_albums(session):
    while True:
        try:
            favorite_albums = session.user.favorites.albums()
        except AttributeError:
            log("No favorited albums found.")
            favorite_albums = []  
        
        if not favorite_albums:
            log("No favorited albums to process.")
            time.sleep(1800)
            continue

        log("Favorited Albums:")
        for album in favorite_albums:
            log(f"{album.id} - {album.name} by {album.artist.name}")
            command = (r"<TIDAL-DL.EXE DIRECTORY HERE>"
            try:
                process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, stderr = process.communicate()
                if stderr:
                    log(f"Error executing command for album {album.id}: {stderr.decode('utf-8', errors='ignore')}")
                else:
                    log(stdout.decode("utf-8", errors='ignore'))
                    session.user.favorites.remove_album(album.id)
                    update_library()
            except Exception as e:
                log(f"Error executing command for album {album.id}: {e}")


def update_library():
    for library in plex.library.sections():
        log(f"Updating library: {library.title}")
        library.update()

if __name__ == "__main__":
    if connect(session):
        check_albums(session)
    else:
        log("Connection has failed somewhere")
