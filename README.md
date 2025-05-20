spotyListCreator
Bild anzeigen

A simple tool to create Spotify playlists from a text file of song names.

📋 Overview
spotyListCreator allows you to effortlessly generate Spotify playlists from text files. Simply list your favorite tracks in a text file, and this tool handles the rest - finding the songs on Spotify and creating a playlist for you.
⚙️ Installation
bashpython3 install.py
This will automatically:

Create a Python virtual environment
Install required dependencies (spotipy, python-dotenv, etc.)
Create a template .env file for your Spotify credentials
Update the script files

🔑 Configuration
Before using spotyListCreator, you need to set up your Spotify Developer credentials:

Create a Spotify Developer account at developer.spotify.com
Create a new application to get your client ID and secret
Edit the .env file with your credentials:
SPOTIPY_CLIENT_ID=your_client_id
SPOTIPY_CLIENT_SECRET=your_client_secret
SPOTIPY_REDIRECT_URI=http://localhost:8888/callback


🚀 Usage
Create a playlist with:
bash./spotylist_create.sh "My Playlist Name" songs.txt
Where songs.txt contains one song per line in any of these formats:

Artist - Song Title (e.g., "Kavinsky - Nightcall")
Spotify Track ID (22-character code)
Spotify URI (spotify:track:xxxx)
Spotify URL (open.spotify.com/track/xxxx)

📝 Example Playlist Format
Timecop1983 – Tonight
FM‑84 feat. Ollie Wride – Running in the Night
The Midnight – Sunset
Magic Sword – In The Face Of Evil
Kavinsky – Nightcall
Dance With The Dead – That House
❓ Troubleshooting

Check your .env file has correct credentials
Make sure your playlist text file has one track per line
For browser authentication issues, try using a private/incognito window
Logs are saved to spotify_playlist.log for debugging

📄 License
This project is maintained by MxBit © 2025.
Contact: mxbit(at)yahoo.com
