#!/usr/bin/env python3

# ©MaxBriliant 2025
# Spotify Playlist Generator - Install Script
# Release Candidate v1.0.0
# 
# Written as a hobby project during my IT studies
# Feel free to modify and share under GPL v3

import os
import shutil
import sys
import subprocess
from pathlib import Path
import platform

def is_wine_or_windows_path(path):
    # Prüfe auf typische Windows/Wine-Pfade
    return (
        '\\' in path or
        (':' in path and (path[1:3] == ':/' or path[1:3] == ':\\')) or
        '/.wine/' in path or
        path.lower().startswith('c:/') or
        path.lower().startswith('c:\\')
    )

# Prüfe Python-Interpreter und Arbeitsverzeichnis
if (
    'wine' in sys.executable.lower() or
    is_wine_or_windows_path(sys.executable) or
    is_wine_or_windows_path(os.getcwd()) or
    platform.system().lower() == 'windows'
):
    print("\nERROR: Dieses Installationsskript darf NICHT unter Wine oder mit einem Windows-Python ausgeführt werden!\nBitte verwende einen nativen Linux-Python (z.B. /usr/bin/python3).\n")
    sys.exit(1)

# Normalisiere alle Pfade auf das aktuelle OS-Format
current_dir = os.path.normpath(os.path.dirname(os.path.abspath(__file__)))
venv_dir = os.path.normpath(os.path.join(current_dir, "venv_spotify"))

print("Setting up aiPlaylistGenerator Modern Edition...")

# Current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Set up Python virtual environment
venv_dir = os.path.join(current_dir, "venv_spotify")
print("Creating Python virtual environment...")
if not os.path.exists(venv_dir):
    try:
        subprocess.run([sys.executable, "-m", "venv", venv_dir], check=True)
        print("Virtual environment created successfully.")
    except Exception as e:
        print(f"Error creating virtual environment: {e}")
        sys.exit(1)
else:
    print("Virtual environment already exists.")

# Activate and install dependencies
print("Installing dependencies for Modern GUI...")
if sys.platform == "win32":
    pip_path = os.path.join(venv_dir, "Scripts", "pip")
    python_path = os.path.join(venv_dir, "Scripts", "python")
else:
    pip_path = os.path.join(venv_dir, "bin", "pip")
    python_path = os.path.join(venv_dir, "bin", "python")

# List all required packages
required_packages = [
    "spotipy",
    "python-dotenv",
    "pillow",
    "screeninfo",
    "python-xlib",
    "requests",
    "charset_normalizer",
    "idna",
    "urllib3"
]

try:
    subprocess.run([pip_path, "install", "--upgrade", "pip"], check=True)
    subprocess.run([pip_path, "install"] + required_packages, check=True)
    print("All dependencies installed successfully.")
except Exception as e:
    print(f"Error installing dependencies: {e}")
    sys.exit(1)

# Create a sample .env file if not present
env_path = os.path.join(current_dir, ".env")
if not os.path.exists(env_path):
    with open(env_path, "w") as f:
        f.write("# Spotify API Credentials - Fill these values!\n")
        f.write("SPOTIPY_CLIENT_ID=your_client_id_here\n")
        f.write("SPOTIPY_CLIENT_SECRET=your_client_secret_here\n")
        f.write("SPOTIPY_REDIRECT_URI=http://127.0.0.1:8888/callback\n")
    print(".env template created. You must edit this file with your Spotify credentials!")
else:
    print(".env file already exists.")

# Make executable files properly executable
print("Setting file permissions...")
executable_files = [
    os.path.join(current_dir, "Spotify_Playlist_Generator.py"),
    os.path.join(current_dir, "main.py"),
    os.path.join(current_dir, "generate.sh"),
    os.path.join(current_dir, "install.py"),
    os.path.join(current_dir, "debug_test.py")
]
for file_path in executable_files:
    if os.path.exists(file_path):
        try:
            current_mode = os.stat(file_path).st_mode
            new_mode = current_mode | ((current_mode & 0o444) >> 2)
            os.chmod(file_path, new_mode)
            print(f"Made {os.path.basename(file_path)} executable.")
        except Exception as e:
            print(f"Warning: Could not set permissions for {os.path.basename(file_path)}: {e}")
    else:
        print(f"Warning: File not found: {os.path.basename(file_path)}")

print("\n=== Installation Complete ===")
print("To use the Modern Spotify Playlist Generator GUI:")
print("1. Edit the .env file with your Spotify API credentials")
print("2. Create a playlist.txt file with songs in format 'Artist - Song Title'")
print("3. Run: ./venv_spotify/bin/python modern_spotify_gui.py")
print("\nEnjoy your music!")
