
# Plex-Tidal-DL

Plex supports Tidal integration. If you have a Tidal subscription and use Plex as your media server, this script automates the process of checking for newly favorited Tidal albums and downloading them using Tidal-DL. Once downloaded, the script updates your Plex library to include these new additions.

## Features
- **Automatic Syncing**: Regularly checks for new favorited albums on Tidal and downloads them.
- **Plex Library Updates**: Automatically refreshes your Plex library with newly downloaded content.
- **Flexible Scheduling**: Configure the frequency of checks to suit your needs.

## Prerequisites
- A Plex server setup with access to a Tidal subscription.
- Python 3.x installed on your system.
- Tidal-DL installed, which can be found [here](https://github.com/yaronzz/Tidal-Media-Downloader).


## Usage
To start the script with the default settings (checking every 30 minutes):
```bash
python plex-tidal-dl.py
```

### Changing the Check Interval
You can adjust the frequency of checks by using the command-line argument `--i` or `--interval`:
- To set the interval to 60 minutes:
  ```bash
  python plex-tidal-dl.py --i 60m
  ```
- To set the interval to 10 seconds:
  ```bash
  python plex-tidal-dl.py --i 10s
  ```

**Note**: Only minute (m) and second (s) intervals are supported.

### Settings Menu
Run the script without any arguments and type 'c' to access the interactive settings menu:
  ```bash
  Press 'c' to change settings, 's' to scan now, or 'q' to quit:
  c
  Options:
  1. Set Interval
  2. Set Schedule Start Time
  ```
In the settings menu, you can change the interval and schedule start times interactively.


## Acknowledgments
Special thanks to **dirty-jimm** for his original script. Check it out [here](https://github.com/dirty-jimm/Tidal_DL_Plus).


