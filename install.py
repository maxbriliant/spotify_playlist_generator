#!/usr/bin/env python3

#©MxBit2025
#Enjoy

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
    subprocess.run([pip_path, "install", "python-dotenv", "spotipy", "os", "shutils", "subprocess", "sys"], check=True)
    print("Dependencies installed successfully.")
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
        f.write("SPOTIPY_REDIRECT_URI=http://localhost:8888/callback\n")
    
    # Also create .env.example as a visible reference
    with open(env_example_path, "w") as f:
        f.write("# Spotify API Credentials - EXAMPLE FILE\n")
        f.write("SPOTIPY_CLIENT_ID=your_client_id_here\n")
        f.write("SPOTIPY_CLIENT_SECRET=your_client_secret_here\n")
        f.write("SPOTIPY_REDIRECT_URI=http://localhost:8888/callback\n")
    
    print(".env template created. You must edit this file with your Spotify credentials!")
else:
    print(".env file already exists.")

# Update script files
main_py_path = os.path.join(current_dir, "main.py")
main2_py_path = os.path.join(current_dir, "main2.py")
parent_dir = os.path.dirname(current_dir)
parent_main2_py_path = os.path.join(parent_dir, "main2.py")

# Handle main.py and main2.py
print("Updating script files...")
if os.path.exists(main_py_path):
    try:
        os.remove(main_py_path)
        print("Removed existing main.py")
    except Exception as e:
        print(f"Error removing main.py: {e}")

# Check if main2.py exists in current dir or parent dir
if os.path.exists(main2_py_path):
    source_path = main2_py_path
elif os.path.exists(parent_main2_py_path):
    source_path = parent_main2_py_path
else:
    print("Error: main2.py not found in expected locations")
    sys.exit(1)

try:
    shutil.copy(source_path, main_py_path)
    print(f"Copied {source_path} to main.py")
except Exception as e:
    print(f"Error copying main2.py to main.py: {e}")
    sys.exit(1)

# Update the shell script
sh_path = os.path.join(current_dir, "create_spotify_playlist.sh")
parent_sh_path = os.path.join(parent_dir, "create_spotify_playlist.sh")

# Determine which script to update
if os.path.exists(sh_path):
    script_to_update = sh_path
elif os.path.exists(parent_sh_path):
    script_to_update = parent_sh_path
else:
    print("Warning: create_spotify_playlist.sh not found")
    script_to_update = None

if script_to_update:
    try:
        with open(script_to_update, "r") as f:
            content = f.read()
        
        # Replace main2.py references with main.py
        updated_content = content.replace("main2.py", "main.py")
        
        with open(script_to_update, "w") as f:
            f.write(updated_content)
        
        print(f"Updated {script_to_update} to reference main.py")
    except Exception as e:
        print(f"Error updating shell script: {e}")

print("\n=== Installation Complete ===")
print("To use the Spotify Playlist Generator:")
print("1. Edit the .env file with your Spotify API credentials")
print("2. Create a playlist.txt file with songs in format 'Artist - Song Title'")
print("3. Run: ./create_spotify_playlist.sh 'My Playlist Name' playlist.txt")
print("\nEnjoy your music!")
