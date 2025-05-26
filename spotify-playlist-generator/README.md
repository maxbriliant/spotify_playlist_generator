# 🎵 Spotify Playlist Generator

![Spotify Playlist Generator](https://img.shields.io/badge/Spotify-Playlist%20Generator-1DB954?style=for-the-badge&logo=spotify&logoColor=white)

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

> Create Spotify playlists from simple text files. Perfect for AI-generated playlists!

---

## 🚀 Quick Start

### Installation

**Windows users:**
1. Download Python from [python.org](https://www.python.org/downloads/windows/)
2. Download this project as ZIP or clone:
   ```bash
   git clone https://github.com/maxbriliant/spotify_playlist_generator.git
   ```

**Linux/Mac users:**
```bash
git clone https://github.com/maxbriliant/spotify_playlist_generator.git
cd spotify_playlist_generator
```

### Setup
```bash
python install.py
```

This automatically:
- Creates a virtual environment
- Installs all dependencies
- Sets up configuration files

---

## 🔑 Spotify API Setup

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Create a new app
3. Copy your **Client ID** and **Client Secret**
4. Set **Redirect URI** to: `http://127.0.0.1:8888/callback`
5. Edit the `.env` file with your credentials:
   ```env
   SPOTIPY_CLIENT_ID=your_client_id_here
   SPOTIPY_CLIENT_SECRET=your_client_secret_here
   SPOTIPY_REDIRECT_URI=http://127.0.0.1:8888/callback
   ```

---

## 🎶 Usage

### GUI Mode (Recommended)
```bash
python Spotify_Playlist_Generator.py
```

![GUI Screenshot](demo1.png)

### Command Line
```bash
python main.py --cli --playlist "My Playlist" --songs playlist.txt
```

---

## 📝 Playlist File Format

Create a text file with your songs in any of these formats:

```text
# Artist - Title (Recommended for AI-generated playlists)
Timecop1983 - Tonight
FM‑84 feat. Ollie Wride - Running in the Night
The Midnight - Sunset
Kavinsky - Nightcall

# Spotify URLs
https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh

# Spotify Track IDs
4iV5W9uYEdYUVa79Axb7Rh
```

---

## 🤖 Perfect for ChatGPT

Ask ChatGPT to create playlists like this:

```
"Create a synthwave playlist with 15 tracks using this format:
Artist - Song Title

Include artists like The Midnight, Timecop1983, FM-84."
```

Save the response as a `.txt` file and use it with this tool!

---

## 🔧 Features

- **Smart Search**: Multiple strategies to find your tracks
- **Batch Processing**: Handle large playlists efficiently
- **Modern GUI**: Easy-to-use interface with dark/light themes
- **Multiple Formats**: Supports Spotify URLs, IDs, and Artist-Title format
- **AI-Friendly**: Perfect for ChatGPT-generated playlists

---

## 🐛 Troubleshooting

**Authentication Issues:**
- Check your Spotify credentials in `.env`
- Make sure redirect URI is exactly: `http://127.0.0.1:8888/callback`

**Tracks Not Found:**
- Check spelling in your playlist file
- Some tracks may not be available in your region

**GUI Won't Start:**
- Try: `python -m tkinter` to test tkinter
- Use CLI mode: `python main.py --cli`

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

**Made with ❤️ by MaxBriliant**  
Contact: mxbit(at)yahoo.com

*Transform your track lists into perfect Spotify playlists effortlessly.*