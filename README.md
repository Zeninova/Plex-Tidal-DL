# Plex-Tidal-DL
Plex supports Tidal integration, and this is a simple script that checks for favorited Tidal albums. If any albums have been favorited, then this script will start another program called Tidal-DL to download them. After downloading the albums, the Plex library will be updated automatically.

This script is designed to run continuously, and it checks for recently added albums every 30 minutes by default. If no albums are found, the script will simply continue without updating your Plex library.

To change the interval, you can enter ``python plex-tidal-dl.py --i 60m`` or ``python plex-tidal-dl.py --interval 60m`` to make it scan every 60 minutes, for example. Only minutes (m) and seconds(s) can be entered. There is a settings menu in the program that lets you change the interval as well.

Note: The Tidal app is *not* needed for this. All you need is a Plex server with a Tidal subscription, Python 3, and [Tidal-DL](https://github.com/yaronzz/Tidal-Media-Downloader)

![image](https://github.com/Zeninova/Plex-Tidal-DL/assets/21183791/f3f6e6f7-d3eb-40a2-8fcd-a12982e2166a)




Special thanks to dirty-jimm for his [script](https://github.com/dirty-jimm/Tidal_DL_Plus)
