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

print("Setting up aiPlaylistGenerator...")

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

# Activate and install dependencies
print("Installing dependencies...")
pip_path = os.path.join(venv_dir, "bin", "pip")
try:
    subprocess.run([pip_path, "install", "--upgrade", "pip"], check=True, capture_output=True)
    subprocess.run([pip_path, "install", "python-dotenv", "spotipy", "shutils"], check=True)
    print("Dependencies installed successfully.")
    
    # Install tkinter if not available in standard library (for the GUI)
    print("Checking for GUI dependencies...")
    try:
        import tkinter
        print("Tkinter is already available.")
    except ImportError:
        print("Tkinter not found in standard library. Please install it using your package manager.")
        print("For Ubuntu/Debian: sudo apt-get install python3-tk")
        print("For Fedora: sudo dnf install python3-tkinter")
        print("For Arch Linux: sudo pacman -S tk")
        
except Exception as e:
    print(f"Error installing dependencies: {e}")
    sys.exit(1)

# Create a sample .env file
env_path = os.path.join(current_dir, ".env")
env_example_path = os.path.join(current_dir, ".env.example")
print("Creating environment file template...")
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
    os.path.join(current_dir, "spotylist_create.sh"),
    os.path.join(current_dir, "install.py"),
    os.path.join(current_dir, "debug_test.py")
]

for file_path in executable_files:
    if os.path.exists(file_path):
        try:
            current_mode = os.stat(file_path).st_mode
            # Add executable bit for user, group and others (if readable)
            new_mode = current_mode | ((current_mode & 0o444) >> 2)
            os.chmod(file_path, new_mode)
            print(f"Made {os.path.basename(file_path)} executable.")
        except Exception as e:
            print(f"Warning: Could not set permissions for {os.path.basename(file_path)}: {e}")
    else:
        print(f"Warning: File not found: {os.path.basename(file_path)}")

print("\n=== Installation Complete ===")
print("To use the Spotify Playlist Generator:")
print("1. Edit the .env file with your Spotify API credentials")
print("2. Create a playlist.txt file with songs in format 'Artist - Song Title'")
print("3. Run: ./spotylist_create.sh 'My Playlist Name' playlist.txt")
print("   OR")
print("4. Use the GUI version: ./Spotify_Playlist_Generator.py")
print("\nEnjoy your music!")
