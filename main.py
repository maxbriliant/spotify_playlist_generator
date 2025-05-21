# filepath: /aiPlaylistGenerator/aiPlaylistGenerator/main.py
#!/usr/bin/env python3
import os
import sys
import time
import re
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Logging-Funktion
def log(message: str) -> None:
    """
    Loggt Nachrichten mit Zeitstempel in stdout und in 'spotify_playlist.log'.
    """
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    entry = f"{timestamp} - {message}"
    print(entry)
    with open("spotify_playlist.log", "a", encoding="utf-8") as f:
        f.write(entry + "\n")

# Verbesserte Funktion: Flexiblere Suche nach Track-ID
def search_track_id(sp: spotipy.Spotify, query: str) -> str:
    """
    Sucht einen Track mit verschiedenen Suchstrategien:
    1. Erst versuchen, nach Titel und Künstler getrennt zu suchen
    2. Falls nicht erfolgreich, versuchen mit allgemeiner Suche
    3. Falls nicht erfolgreich, versuchen mit teilweiser Übereinstimmung
    
    Gibt die erste gefundene ID zurück oder None.
    """
    track_id = None
    
    try:
        # Strategie 1: Suche mit track und artist Parametern getrennt
        if " - " in query:
            track_name, artist = query.split(" - ", 1)
            result = sp.search(q=f'track:"{track_name}" artist:"{artist}"', type="track", limit=1)
            if result and "tracks" in result and "items" in result["tracks"] and result["tracks"]["items"]:
                track_id = result["tracks"]["items"][0]["id"]
                log(f"Gefunden via präzise Suche: {query}")
                return track_id
        
        # Strategie 2: Allgemeine Suche mit vollständiger Query
        if not track_id:
            result = sp.search(q=query, type="track", limit=1)
            if result and "tracks" in result and "items" in result["tracks"] and result["tracks"]["items"]:
                track_id = result["tracks"]["items"][0]["id"]
                log(f"Gefunden via allgemeine Suche: {query}")
                return track_id
        
        # Strategie 3: Weniger präzise Suche für Titel mit Spezialzeichen
        if not track_id and " - " in query:
            track_name, artist = query.split(" - ", 1)
            # Entferne Sonderzeichen und Klammern
            clean_track = re.sub(r'[^\w\s]', '', track_name)
            clean_artist = re.sub(r'[^\w\s]', '', artist)
            result = sp.search(q=f'{clean_track} {clean_artist}', type="track", limit=1)
            if result and "tracks" in result and "items" in result["tracks"] and result["tracks"]["items"]:
                track_id = result["tracks"]["items"][0]["id"]
                track_info = f"{result['tracks']['items'][0]['name']} - {result['tracks']['items'][0]['artists'][0]['name']}"
                log(f"Gefunden via flexible Suche: {query} → {track_info}")
                return track_id
        
        # Wenn immer noch nichts gefunden wurde
        log(f"Nicht gefunden: {query}")
        return ""  # Return empty string instead of None
        
    except Exception as e:
        log(f"Fehler bei der Suche nach '{query}': {e}")
        return ""  # Return empty string instead of None

# Hauptfunktion
def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <Playlist-Name> <Eingabe-Datei>")
        sys.exit(1)

    playlist_name = sys.argv[1]
    input_file = sys.argv[2]

    log("Script gestartet")

    # Lade Umgebungsvariablen
    load_dotenv()
    CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
    CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
    REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI")
    if not all([CLIENT_ID, CLIENT_SECRET, REDIRECT_URI]):
        log("Fehler: Spotify-Credentials fehlen in .env")
        sys.exit(1)

    # Authentifizierung
    try:
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            redirect_uri=REDIRECT_URI,
            scope="playlist-modify-private playlist-modify-public",
            cache_path=".spotify_cache"
        ))
        
        # Get user ID safely with None check
        me_info = sp.me()
        if me_info is None:
            log("Fehler: Konnte keine Benutzerinformation abrufen")
            sys.exit(1)
            
        user_id = me_info.get("id")
        if not user_id:
            log("Fehler: Keine Benutzer-ID erhalten")
            sys.exit(1)
            
        log(f"Authentifiziert als {user_id}")
    except Exception as e:
        log(f"Authentifizierungsfehler: {e}")
        sys.exit(1)

    # Playlist erstellen
    try:
        playlist = sp.user_playlist_create(
            user=user_id,
            name=playlist_name,
            public=False,
            description=f"Erstellt am {time.strftime('%d.%m.%Y %H:%M')}"
        )
        
        # Make sure playlist was created successfully
        if playlist is None:
            log("Fehler: Playlist konnte nicht erstellt werden (keine Rückgabe)")
            sys.exit(1)
            
        playlist_id = playlist.get("id")
        if not playlist_id:
            log("Fehler: Keine Playlist-ID erhalten")
            sys.exit(1)
            
        # Get Spotify URL safely
        external_urls = playlist.get("external_urls", {})
        playlist_url = external_urls.get("spotify")
        
        if not playlist_url:
            log("Warnung: Kein Playlist-URL erhalten")
            playlist_url = f"https://open.spotify.com/playlist/{playlist_id}"
            
        log(f"Playlist erstellt: {playlist_url}")
    except Exception as e:
        log(f"Fehler beim Erstellen der Playlist: {e}")
        sys.exit(1)

    # Einlesen der Eingabedatei
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            lines = [l.strip() for l in f if l.strip()]
    except Exception as e:
        log(f"Fehler beim Lesen der Datei '{input_file}': {e}")
        sys.exit(1)

    # Extrahieren oder Suchen von Track-IDs
    track_ids = []
    for line in lines:
        # Prüfen auf bereits vorhandene ID
        id_match = re.fullmatch(r"[A-Za-z0-9]{22}", line)
        if id_match:
            track_ids.append(line)
            log(f"Direkte ID genutzt: {line}")
            continue
        # Prüfen URI
        uri_match = re.search(r"spotify:track:([A-Za-z0-9]{22})", line)
        if uri_match:
            track_ids.append(uri_match.group(1))
            log(f"URI-ID genutzt: {uri_match.group(1)}")
            continue
        # Prüfen HTTP-Link
        http_match = re.search(r"open\.spotify\.com/track/([A-Za-z0-9]{22})", line)
        if http_match:
            track_ids.append(http_match.group(1))
            log(f"HTTP-Link-ID genutzt: {http_match.group(1)}")
            continue
        # Andernfalls interpretiere als "Song - Künstler" mit verbesserter Suche
        tid = search_track_id(sp, line)
        if tid:
            track_ids.append(tid)
        else:
            log(f"Nicht gefunden: {line}")

    # Duplikate entfernen
    unique_ids = list(dict.fromkeys(track_ids))
    if not unique_ids:
        log("Keine valide Track-IDs ermittelt.")
        sys.exit(1)
    log(f"Insgesamt {len(unique_ids)} eindeutige Track-IDs")

    # Tracks in Batches zur Playlist hinzufügen
    for i in range(0, len(unique_ids), 100):
        batch = unique_ids[i:i+100]
        try:
            sp.playlist_add_items(playlist_id, batch)
            log(f"Batch hinzugefügt: {len(batch)} Tracks")
        except Exception as e:
            log(f"Fehler beim Hinzufügen der Batch: {e}")

    log(f"Erfolgreich {len(unique_ids)} Tracks hinzugefügt.")
    
    # Ausgabe des Playlist-Links in einem konsistenten Format für die GUI
    print(f"Playlist-Link: {playlist_url}")

if __name__ == "__main__":
    main()
