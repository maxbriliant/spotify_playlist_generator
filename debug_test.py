#!/usr/bin/env python3

import os
import sys
import tkinter as tk
from tkinter import StringVar
import subprocess

def test_playlist_creation():
    # Create a simple test case
    root = tk.Tk()
    playlist_name_var = StringVar(value="Test Playlist")
    
    # Print initial value
    print(f"Initial StringVar value: '{playlist_name_var.get()}'")
    
    # Simulate focusing away from entry field
    root.update_idletasks()
    
    # Get the value that would be used
    playlist_name = playlist_name_var.get().strip()
    print(f"Retrieved value after update: '{playlist_name}'")
    
    # Test direct execution with this value
    songs_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "songs.txt")
    
    # Try both the shell script and Python script
    print("\nTesting shell script execution:")
    shell_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "spotylist_create.sh")
    try:
        # Use quotes around the playlist name to handle spaces properly
        shell_cmd = [shell_script, f'"{playlist_name}"', songs_file]
        print(f"Command: {' '.join(shell_cmd)}")
        result = subprocess.run(shell_cmd, capture_output=True, text=True)
        print(f"Return code: {result.returncode}")
        print(f"Output: {result.stdout[:200]}...") # Print only start of output
        print(f"Error: {result.stderr[:200]}..." if result.stderr else "No errors")
    except Exception as e:
        print(f"Shell script execution error: {e}")
    
    print("\nTesting Python script execution:")
    venv_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "venv_spotify")
    python_path = os.path.join(venv_dir, "bin", "python3")
    main_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "main.py")
    try:
        python_cmd = [python_path, main_script, playlist_name, songs_file]
        print(f"Command: {' '.join(python_cmd)}")
        result = subprocess.run(python_cmd, capture_output=True, text=True)
        print(f"Return code: {result.returncode}")
        print(f"Output: {result.stdout[:200]}...") # Print only start of output
        print(f"Error: {result.stderr[:200]}..." if result.stderr else "No errors")
    except Exception as e:
        print(f"Python script execution error: {e}")
    
    root.destroy()

if __name__ == "__main__":
    test_playlist_creation()