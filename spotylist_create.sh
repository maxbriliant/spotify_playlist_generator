# filepath: /aiPlaylistGenerator/create_spotify_playlist.sh
#!/usr/bin/env bash
set -euo pipefail

#©MxBit2020
#Enjoy

# ---- KONFIG ----
VENV_DIR="venv_spotify"
SCRIPT_NAME="main.py"
LOG_FILE="spotify_playlist.log"

# Farben
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m'

# ---- USAGE ----
if [[ "$#" -lt 2 ]]; then
  echo -e "${YELLOW}Usage: $0 <Playlist-Name> <Track-Datei>${NC}"
  echo -e "${YELLOW}Hinweis: Track-Datei kann Spotify-Track-IDs, URLs, oder Songname-Artist Paare enthalten.${NC}"
  exit 1
fi

PLAYLIST_NAME="$1"
TRACKS_FILE="$2"

# ---- CHECKS ----
if [[ ! -f "$TRACKS_FILE" ]]; then
  echo -e "${RED}Fehler: Datei '$TRACKS_FILE' nicht gefunden.${NC}"
  exit 1
fi

if [[ ! -f ".env" ]]; then
  echo -e "${RED}Fehler: .env-Datei mit SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET und SPOTIPY_REDIRECT_URI fehlt.${NC}"
  exit 1
fi

# ---- VENV ----
echo -e "${YELLOW}Prüfe Python-Umgebung...${NC}"
if [[ ! -d "$VENV_DIR" ]]; then
  python3 -m venv "$VENV_DIR"
  source "$VENV_DIR/bin/activate"
  pip install --upgrade pip >/dev/null
  pip install spotipy python-dotenv >/dev/null
else
  source "$VENV_DIR/bin/activate"
fi

# ---- GENERATE & RUN PYTHON ----
echo -e "${YELLOW}Starte Playlist-Erstellung für '$PLAYLIST_NAME'...${NC}"
python3 "$SCRIPT_NAME" "$PLAYLIST_NAME" "$TRACKS_FILE"
EXIT_CODE=$?

# ---- CLEANUP ----
deactivate

if [[ $EXIT_CODE -eq 0 ]]; then
  echo -e "${GREEN}Playlist erfolgreich erstellt! Details in $LOG_FILE.${NC}"
else
  echo -e "${RED}Fehler bei der Erstellung. Siehe $LOG_FILE.${NC}"
  exit $EXIT_CODE
fi