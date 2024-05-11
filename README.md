
# Plex-Tidal-DL

**Plex-Tidal-DL** is a Python script designed to enhance your music experience by integrating Plex with Tidal. If you have a Tidal subscription and use Plex as your media server, this script automates the process of checking for newly favorited Tidal albums and downloading them using Tidal-DL. Once downloaded, the script updates your Plex library to include these new additions.

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

## Contribution
Contributions are welcome! Please feel free to submit pull requests or open issues to improve the functionality or fix problems with the script.

## Acknowledgments
Special thanks to **dirty-jimm** for his contributions to the Tidal-DL community, which inspired this script. Check out his project [here](https://github.com/dirty-jimm/Tidal_DL_Plus).

![Plex-Tidal-DL in action](https://github.com/Zeninova/Plex-Tidal-DL/assets/21183791/f3f6e6f7-d3eb-40a2-8fcd-a12982e2166a)

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE.md) file for details.
