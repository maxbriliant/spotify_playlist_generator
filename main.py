#!/usr/bin/env python3
"""
Spotify Playlist Generator - Core Script
----------------------------------------
Version: 1.0.0 (Release Candidate)
Author: MaxBriliant
Date: May 2025

This script is the heart of my Spotify Playlist Generator - honestly, my first 
serious coding project that I worked on while learning Python. I started it because 
I was tired of manually creating playlists song by song!
So i created something you can input an AI generated Song List.

What it does:
- Creates Spotify playlists from text files with minimal effort
- Handles artist-title formats, URLs, or Spotify IDs - whatever you throw at it
- Tries really hard to find the right songs with multiple search strategies
- Processes songs in batches so large playlists don't crash

For the easy way, just use the GUI: ./Spotify_Playlist_Generator.py
"""

from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth
import spotipy
import sys
import os
import time
import re

# --- VENV CHECK ---
venv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "venv_spotify")
if not sys.prefix.startswith(venv_path):
    print("\nERROR: Please run this script using the virtual environment Python!\n" \
          "On Linux:   ./venv_spotify/bin/python main.py\n" \
          "On Windows: venv_spotify\\Scripts\\python.exe main.py\n")
    sys.exit(1)

# Logging stuff - because I like to know what's happening
def log(message: str) -> None:
    """
    Adds timestamps to messages and saves them to a log file.
    I might be a bit obsessive about logging, but it's saved me many times!
    """
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    entry = f"{timestamp} - {message}"
    print(entry, flush=True)
    with open("spotify_playlist.log", "a", encoding="utf-8") as f:
        f.write(entry + "\n")

# The search magic - this took me forever to get right!
def search_track_id(sp: spotipy.Spotify, query: str) -> str:
    """
    My not-so-secret sauce for finding tracks. If one method fails, try another!
    
    I learned the hard way that the Spotify API can be picky, so I built this
    with three fallback strategies:
    1. The precise approach: Try artist and title separately for exact matches 
    2. The straightforward approach: Just search the whole string
    3. The desperate approach: Strip special characters and try again
    
    # TODO: Maybe add some fuzzy matching? Sometimes the titles have typos...
    """
    track_id = None
    
    try:
        # First attempt - the proper way
        if " - " in query:
            track_name, artist = query.split(" - ", 1)
            result = sp.search(q=f'track:"{track_name}" artist:"{artist}"', type="track", limit=1)
            if result and "tracks" in result and "items" in result["tracks"] and result["tracks"]["items"]:
                track_id = result["tracks"]["items"][0]["id"]
                log(f"Found with precise search: {query}")
        
        # Second attempt - just throw the whole thing at Spotify
        if not track_id:
            result = sp.search(q=query, type="track", limit=1)
            if result and "tracks" in result and "items" in result["tracks"] and result["tracks"]["items"]:
                track_id = result["tracks"]["items"][0]["id"]
                log(f"Found with general search: {query}")
        
        # Last resort - clean up the text and try again
        if not track_id and " - " in query:
            track_name, artist = query.split(" - ", 1)
            # Strip those pesky special characters 
            clean_track = re.sub(r'[^\w\s]', '', track_name)
            clean_artist = re.sub(r'[^\w\s]', '', artist)
            result = sp.search(q=f'{clean_track} {clean_artist}', type="track", limit=1)
            if result and "tracks" in result and "items" in result["tracks"] and result["tracks"]["items"]:
                track_id = result["tracks"]["items"][0]["id"]
                log(f"Found with sanitized search: {query}")
        
        # If we still found nothing, admit defeat
        if not track_id:
            log(f"Couldn't find: {query} - maybe check the spelling?")
            return ""
            
        return track_id
        
    except Exception as e:
        log(f"Search error for '{query}': {e}")
        return ""

# Where the magic happens
def main():
    """
    The main workflow that ties everything together:
    
    1. Check that the user isn't missing anything important
    2. Log in to Spotify (the OAuth dance)
    3. Create a shiny new playlist
    4. Hunt down all the tracks from the input file
    5. Add everything to the playlist in batches
    """
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <Playlist-Name> <Input-File>", flush=True)
        sys.exit(1)

    playlist_name = sys.argv[1]
    input_file = sys.argv[2]

    log("Script started - let's make a playlist!")

    # Get our credentials from the .env file
    load_dotenv()
    CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
    CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
    REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI")
    if not all([CLIENT_ID, CLIENT_SECRET, REDIRECT_URI]):
        log("Error: Missing Spotify credentials in .env file - did you set them up?")
        sys.exit(1)

    # Connect to Spotify - fingers crossed!
    try:
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            redirect_uri=REDIRECT_URI,
            scope="playlist-modify-private playlist-modify-public",
            cache_path=".spotify_cache"
        ))
        
        # Make sure we're actually logged in
        me_info = sp.me()
        if me_info is None:
            log("Error: Couldn't get user info - authentication might have failed")
            sys.exit(1)
            
        user_id = me_info.get("id")
        if not user_id:
            log("Error: No user ID received - weird API response?")
            sys.exit(1)
            
        log(f"Logged in as {user_id} - we're good to go!")
    except Exception as e:
        log(f"Authentication failed: {e}")
        sys.exit(1)

    # Create the playlist with today's date
    try:
        playlist = sp.user_playlist_create(
            user=user_id,
            name=playlist_name,
            public=False,
            description=f"Created on {time.strftime('%d.%m.%Y %H:%M')} with my Spotify Playlist Generator"
        )
        
        # Make sure the playlist was actually created
        if playlist is None:
            log("Error: Couldn't create playlist - no response from Spotify")
            sys.exit(1)
            
        playlist_id = playlist.get("id")
        if not playlist_id:
            log("Error: No playlist ID received - something's wrong")
            sys.exit(1)
            
        # Get the URL so we can open it later
        external_urls = playlist.get("external_urls", {})
        playlist_url = external_urls.get("spotify")
        
        if not playlist_url:
            log("Warning: No playlist URL received - that's strange")
            
        log(f"Playlist created: {playlist_url}")
    except Exception as e:
        log(f"Error creating playlist: {e}")
        sys.exit(1)

    # Read the songs from the file
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
    except Exception as e:
        log(f"Error reading file '{input_file}': {e}")
        sys.exit(1)

    # Find all the track IDs
    track_ids = []
    for line in lines:
        # Look for different formats:
        
        # Direct Spotify IDs - easy mode
        id_match = re.fullmatch(r"[A-Za-z0-9]{22}", line)
        if id_match:
            track_ids.append(line)
            continue
            
        # Spotify URIs like spotify:track:xxxx
        uri_match = re.search(r"spotify:track:([A-Za-z0-9]{22})", line)
        if uri_match:
            track_ids.append(uri_match.group(1))
            continue
            
        # Spotify URLs from the website/app
        http_match = re.search(r"open\.spotify\.com/track/([A-Za-z0-9]{22})", line)
        if http_match:
            track_ids.append(http_match.group(1))
            continue
            
        # The hard way - just "Artist - Song" format
        tid = search_track_id(sp, line)
        if tid:
            track_ids.append(tid)
        else:
            log(f"Couldn't find '{line}' - skipping this one")

    # Remove duplicates so we don't add the same song twice
    unique_ids = list(dict.fromkeys(track_ids))
    if not unique_ids:
        log("No valid tracks found - check your input file")
        sys.exit(1)
    log(f"Found {len(unique_ids)} unique tracks - adding to playlist!")

    # Add songs in batches (Spotify limit is 100 per request)
    for i in range(0, len(unique_ids), 100):
        batch = unique_ids[i:i+100]
        try:
            sp.playlist_add_items(playlist_id, batch)
            log(f"Added batch of {len(batch)} tracks")
        except Exception as e:
            log(f"Error adding tracks: {e}")
            sys.exit(1)

    log(f"Success! Added {len(unique_ids)} tracks to your playlist.")
    
    # Print the playlist link so the GUI can grab it
    print(f"Playlist-Link: {playlist_url}", flush=True)

if __name__ == "__main__":
    main()
