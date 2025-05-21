#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ©MaxBriliant 2025
# Spotify Playlist Generator - GUI Version
# Release Candidate v1.0.0
# 
# Written as a hobby project during my IT studies
# Feel free to modify and share under GPL v3

import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import os
import sys
import time
import subprocess
import webbrowser
import re
import traceback  # For better error reporting

# Enable debug logging for final testing phase
# TODO: Set to False for production release
DEBUG = True

def debug_log(message):
    """Print debug messages when debug mode is enabled"""
    if DEBUG:
        print(f"DEBUG: {message}")

# UI layout constants - carefully tuned for best user experience
INITIAL_WINDOW_WIDTH = 600
INITIAL_WINDOW_HEIGHT = 450
EXPANDED_WINDOW_HEIGHT = 600
CONSOLE_MIN_HEIGHT = 100
CONSOLE_EXPANDED_HEIGHT = 300

class SpotifyCredentialsDialog(tk.Toplevel):
    def __init__(self, parent, env_path):
        super().__init__(parent)
        self.parent = parent
        self.env_path = env_path
        self.result = False
        
        # Track file modification time
        self.last_modified_time = os.path.getmtime(self.env_path) if os.path.exists(self.env_path) else 0
        
        # Configure window
        self.title("Spotify Credentials Setup")
        self.geometry("650x450")  # Reduced height since we're removing the preview section
        self.resizable(True, True)
        self.minsize(650, 450)
        
        # Use system default theme (light theme)
        # No explicit background color to maintain system look
        
        self.grab_set()  # Modal dialog
        self.transient(parent)  # Associate with parent window
        
        # Center on parent
        self.update_idletasks()
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        width = self.winfo_width()
        height = self.winfo_height()
        x = parent_x + (parent_width // 2) - (width // 2)
        y = parent_y + (parent_height // 2) - (height // 2)
        self.geometry(f"+{x}+{y}")
        
        # Create the UI
        self.create_widgets()
        
        # Load existing values if any
        self.load_existing_credentials()
        
        # Set focus on first entry
        self.client_id_entry.focus_set()
        
        # Set up file monitoring - check every 500ms for changes
        self.after(500, self.check_for_file_changes)
        
    def create_widgets(self):
        # Main frame with padding
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header
        header_label = ttk.Label(main_frame, text="Spotify API Credentials Setup", 
                               font=("Helvetica", 16, "bold"), foreground="#1DB954")
        header_label.pack(pady=(0, 5))
        
        # Instructions
        instructions_frame = ttk.Frame(main_frame)
        instructions_frame.pack(fill=tk.X, pady=10)
        
        instructions_text = ("To use this application, you need Spotify API credentials.\n"
                           "1. Create a Spotify Developer account at developer.spotify.com\n"
                           "2. Create a new application in the dashboard\n"
                           "3. Copy your Client ID and Client Secret into your .env file\n"
                           "4. Set the Redirect URI exactly as shown below in your Spotify app settings")
        
        instructions_label = ttk.Label(instructions_frame, text=instructions_text,
                                    justify="left", wraplength=600)
        instructions_label.pack(anchor="w")
        
        # Dev portal and edit .env buttons row
        buttons_row = ttk.Frame(instructions_frame)
        buttons_row.pack(anchor="w", pady=(10, 5))
        
        # Dev portal link button
        portal_button = ttk.Button(buttons_row, text="Open Spotify Developer Portal",
                                 command=self.open_spotify_dev)
        portal_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Open .env file button
        open_env_button = ttk.Button(buttons_row, text="Open .env File in Editor",
                                   command=self.open_env_in_editor)
        open_env_button.pack(side=tk.LEFT)
        
        # Form frame
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill=tk.X, pady=10)
        
        # Client ID - read-only but selectable
        client_id_label = ttk.Label(form_frame, text="Client ID:")
        client_id_label.grid(row=0, column=0, sticky="w", pady=5)
        
        self.client_id_var = tk.StringVar()
        self.client_id_entry = ttk.Entry(form_frame, textvariable=self.client_id_var, width=50, state="readonly")
        self.client_id_entry.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        copy_id_btn = ttk.Button(form_frame, text="Copy", width=5,
                              command=lambda: self.copy_to_clipboard(self.client_id_var.get()))
        copy_id_btn.grid(row=0, column=2, padx=5, pady=5)

        # Client Secret - read-only but selectable, now visible by default without show button
        client_secret_label = ttk.Label(form_frame, text="Client Secret:")
        client_secret_label.grid(row=1, column=0, sticky="w", pady=5)
        
        self.client_secret_var = tk.StringVar()
        # No longer using show="•" to make the secret visible by default
        self.client_secret_entry = ttk.Entry(form_frame, textvariable=self.client_secret_var, width=50, state="readonly")
        self.client_secret_entry.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        # Copy button directly in column 2 without the show checkbox frame
        copy_secret_btn = ttk.Button(form_frame, text="Copy", width=5,
                                  command=lambda: self.copy_to_clipboard(self.client_secret_var.get()))
        copy_secret_btn.grid(row=1, column=2, padx=5, pady=5)
        
        # Redirect URI - read-only but selectable
        redirect_uri_label = ttk.Label(form_frame, text="Redirect URI:")
        redirect_uri_label.grid(row=2, column=0, sticky="w", pady=5)
        
        self.redirect_uri_var = tk.StringVar(value="http://127.0.0.1:8888/callback")
        redirect_uri_entry = ttk.Entry(form_frame, textvariable=self.redirect_uri_var, width=50, state="readonly")
        redirect_uri_entry.grid(row=2, column=1, sticky="w", padx=5, pady=5)
        
        copy_uri_btn = ttk.Button(form_frame, text="Copy", width=5,
                               command=self.copy_redirect_uri)
        copy_uri_btn.grid(row=2, column=2, padx=5, pady=5)
        
        # Note about redirect URI
        note_label = ttk.Label(form_frame, text="* Must match exactly what's in your Spotify App settings",
                             font=("Helvetica", 9, "italic"))
        note_label.grid(row=3, column=1, sticky="w", padx=5, pady=(0, 10))
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=20)
        
        cancel_button = ttk.Button(buttons_frame, text="Cancel",
                                 command=self.cancel)
        cancel_button.pack(side=tk.RIGHT, padx=5)
        
        save_button = ttk.Button(buttons_frame, text="Edit Credentials",
                               command=self.open_env_in_editor)
        save_button.pack(side=tk.RIGHT, padx=5)

    def copy_to_clipboard(self, text):
        """Copy the provided text to clipboard and show a brief tooltip"""
        self.clipboard_clear()
        self.clipboard_append(text)
        messagebox.showinfo("Copied", "Value copied to clipboard!")
        
    def open_env_in_editor(self):
        """Open the .env file in system's default text editor"""
        try:
            if os.path.exists(self.env_path):
                if sys.platform == 'win32':
                    os.startfile(self.env_path)
                elif sys.platform == 'darwin':
                    subprocess.run(['open', self.env_path])                    
                else:
                    subprocess.run(['xdg-open', self.env_path])
                    
                messagebox.showinfo("Text Editor", "Opening .env file in your text editor.\nAfter editing, save the file and click 'Save Credentials' to apply changes.")
            else:
                with open(self.env_path, "w") as f:
                    f.write("# Spotify API Credentials\n")
                    f.write("SPOTIPY_CLIENT_ID=\n")
                    f.write("SPOTIPY_CLIENT_SECRET=\n")
                    f.write("SPOTIPY_REDIRECT_URI=http://127.0.0.1:8888/callback\n")
                    
                self.open_env_in_editor()  # Retry opening after creating
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open .env file: {str(e)}")
        
    def toggle_secret_visibility(self):
        """Toggle visibility of the client secret"""
        if self.show_secret_var.get():
            self.client_secret_entry.config(show="")
        else:
            self.client_secret_entry.config(show="•")
    
    def open_spotify_dev(self):
        """Open the Spotify Developer Portal in a browser"""
        webbrowser.open("https://developer.spotify.com/dashboard")
    
    def copy_redirect_uri(self):
        """Copy the redirect URI to clipboard"""
        self.clipboard_clear()
        self.clipboard_append(self.redirect_uri_var.get())
        messagebox.showinfo("Copied", "Redirect URI copied to clipboard.\n\nRemember to add this exact URI to your Spotify App settings.")
    
    def load_existing_credentials(self):
        """Load existing credentials from .env file if it exists"""
        try:
            if os.path.exists(self.env_path):
                with open(self.env_path, "r") as f:
                    for line in f:
                        if line.startswith("SPOTIPY_CLIENT_ID="):
                            _, value = line.strip().split("=", 1)
                            self.client_id_var.set(value)
                        elif line.startswith("SPOTIPY_CLIENT_SECRET="):
                            _, value = line.strip().split("=", 1)
                            self.client_secret_var.set(value)
                        elif line.startswith("SPOTIPY_REDIRECT_URI="):
                            _, value = line.strip().split("=", 1)
                            self.redirect_uri_var.set(value)
        except Exception as e:
            print(f"Error loading credentials: {e}")
    
    def save_credentials(self):
        """Save credentials to .env file"""
        client_id = self.client_id_var.get().strip()
        client_secret = self.client_secret_var.get().strip()
        redirect_uri = self.redirect_uri_var.get().strip()
        
        if not client_id or not client_secret:
            messagebox.showwarning("Missing Information", "Please enter both Client ID and Client Secret.")
            return
        
        if not redirect_uri:
            redirect_uri = "http://127.0.0.1:8888/callback"
            
        try:
            with open(self.env_path, "w") as f:
                f.write("# Spotify API Credentials - Fill these values!\n")
                f.write(f"SPOTIPY_CLIENT_ID={client_id}\n")
                f.write(f"SPOTIPY_CLIENT_SECRET={client_secret}\n")
                f.write(f"SPOTIPY_REDIRECT_URI={redirect_uri}\n")
                
            messagebox.showinfo("Success", "Credentials saved successfully!")
            self.result = True
            self.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save credentials: {str(e)}")
    
    def cancel(self):
        """Cancel and close the dialog"""
        self.result = False
        self.destroy()

    def update_preview(self, *args):
        """Update the preview text with current values"""
        client_id = self.client_id_var.get().strip()
        client_secret = self.client_secret_var.get().strip()
        redirect_uri = self.redirect_uri_var.get().strip()
        
        # Update preview text - ensuring it's visible and usable for copy/paste
        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.delete(1.0, tk.END)
        self.preview_text.insert(tk.END, f"SPOTIPY_CLIENT_ID={client_id}\n")
        self.preview_text.insert(tk.END, f"SPOTIPY_CLIENT_SECRET={client_secret}\n")
        self.preview_text.insert(tk.END, f"SPOTIPY_REDIRECT_URI={redirect_uri}\n")
        self.preview_text.config(state=tk.DISABLED)

    def check_for_file_changes(self):
        """Check if the .env file has been modified externally and reload if so"""
        try:
            if os.path.exists(self.env_path):
                current_modified_time = os.path.getmtime(self.env_path)
                
                if current_modified_time != self.last_modified_time:
                    # File has been modified, reload credentials
                    debug_log(f".env file changed. Last modified: {self.last_modified_time}, Current: {current_modified_time}")
                    self.last_modified_time = current_modified_time
                    self.load_existing_credentials()
                    debug_log("Reloaded credentials from modified .env file")
        except Exception as e:
            debug_log(f"Error checking .env file changes: {e}")
            
        # Schedule the next check if dialog is still open
        if self.winfo_exists():
            self.after(500, self.check_for_file_changes)

class SpotifyPlaylistGeneratorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Spotify Playlist Generator")
        self.root.geometry(f"{INITIAL_WINDOW_WIDTH}x{INITIAL_WINDOW_HEIGHT}")
        self.root.minsize(INITIAL_WINDOW_WIDTH, INITIAL_WINDOW_HEIGHT)
        
        # Use light theme colors
        self.accent_color = "#1DB954"  # Spotify green
        
        # Configure style
        self.style = ttk.Style()
        try:
            # Use the default theme (which is light on most systems)
            pass
        except:
            pass
        
        # Track window state
        self.expanded = False
        
        # Path variables
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.venv_dir = os.path.join(self.current_dir, "venv_spotify")
        self.env_path = os.path.join(self.current_dir, ".env")
        
        # UI variables
        self.playlist_name = tk.StringVar(value="")
        self.songs_file_path = tk.StringVar(value="")
        self.status_var = tk.StringVar(value="Ready")
        
        # Recent files history (could be loaded from config)
        self.recent_files = []
        
        # Create widgets
        self.create_widgets()
        
        # Check environment on startup
        self.root.after(500, self.check_environment)
        
        # Set up resize handling
        self.root.bind("<Configure>", self.on_resize)
        
        # Create right-click menu for console
        self.console_menu = tk.Menu(self.root, tearoff=0)
        self.console_menu.add_command(label="Copy Selected", command=self.copy_selected_text)
        self.console_menu.add_command(label="Copy All", command=self.copy_all_text)
        self.console_menu.add_separator()
        self.console_menu.add_command(label="Select All", command=self.select_all_text)
        self.console_menu.add_separator()
        self.console_menu.add_command(label="Clear Console", command=self.clear_console)
        
        # Bind right-click to console
        self.console.bind("<Button-3>", self.show_context_menu)
    
    def run_installation(self):
        """Run the installation script to set up the environment"""
        install_script = os.path.join(self.current_dir, "install.py")
        if not os.path.exists(install_script):
            messagebox.showerror("Error", "Installation script not found!")
            return False
        
        # Show a progress dialog
        progress_win = tk.Toplevel(self.root)
        progress_win.title("Installing...")
        progress_win.geometry("400x200")
        progress_win.resizable(False, False)
        progress_win.configure(bg=self.bg_color)
        progress_win.grab_set()  # Modal dialog
        
        # Center the progress window
        progress_win.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        width = progress_win.winfo_width()
        height = progress_win.winfo_height()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        progress_win.geometry(f"+{x}+{y}")
        
        # Progress info
        frame = ttk.Frame(progress_win)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        label = ttk.Label(frame, text="Setting up the environment...\nThis may take a moment.", 
                       font=("Helvetica", 12))
        label.pack(pady=(0, 20))
        
        progress = ttk.Progressbar(frame, mode="indeterminate", length=300)
        progress.pack(pady=10)
        progress.start()
        
        status_var = tk.StringVar(value="Installing dependencies...")
        status_label = ttk.Label(frame, textvariable=status_var)
        status_label.pack(pady=10)
        
        progress_win.update()
        
        try:
            # Run installation
            process = subprocess.Popen(
                [sys.executable, install_script],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Monitor output safely
            if process and process.stdout:
                while True:
                    line = process.stdout.readline()
                    if not line:
                        break
                    status_var.set(line.strip())
                    progress_win.update()
            
            if process:
                process.wait()
                return_code = process.returncode
            else:
                status_var.set("Error: Failed to start installation process")
                progress_win.update()
                time.sleep(2)
                progress.stop()
                progress_win.destroy()
                return False
            
            if return_code == 0:
                status_var.set("Installation completed successfully!")
                progress.stop()
                progress_win.update()
                time.sleep(1)
                progress_win.destroy()
                return True
            else:
                progress.stop()
                messagebox.showerror("Installation Failed", 
                                   "Failed to set up the environment. Please try again or run install.py manually.")
                progress_win.destroy()
                return False
                
        except Exception as e:
            progress.stop()
            messagebox.showerror("Installation Error", str(e))
            progress_win.destroy()
            return False
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header - Spotify Logo or Text
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=5)
        
        header_label = ttk.Label(header_frame, text="Spotify Playlist Generator", 
                              font=("Helvetica", 16, "bold"), foreground="#1DB954")
        header_label.pack(side=tk.LEFT)
        
        # Setup button for credentials
        creds_button = ttk.Button(header_frame, text="Setup Credentials", 
                               command=self.show_credentials_dialog)
        creds_button.pack(side=tk.RIGHT)
        
        # Form frame - for inputs
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill=tk.X, pady=10)
        
        # Playlist name
        playlist_label = ttk.Label(form_frame, text="Playlist Name:")
        playlist_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)
        
        self.playlist_entry = ttk.Entry(form_frame, textvariable=self.playlist_name, width=40)
        self.playlist_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self.playlist_entry.bind("<FocusOut>", self.update_playlist_name)
        
        # Playlist file
        songs_label = ttk.Label(form_frame, text="Playlist File:")
        songs_label.grid(row=1, column=0, sticky="w", padx=5, pady=5)
        
        songs_frame = ttk.Frame(form_frame)
        songs_frame.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        
        songs_entry = ttk.Entry(songs_frame, textvariable=self.songs_file_path, width=32)
        songs_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        browse_button = ttk.Button(songs_frame, text="Browse", width=8,
                                command=self.browse_file)
        browse_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Recent files section if we have any
        if self.recent_files:
            recent_label = ttk.Label(form_frame, text="Recent:")
            recent_label.grid(row=2, column=0, sticky="w", padx=5, pady=0)
            
            # Function to create a command with file path
            def make_select_command(file_path):
                return lambda: self.songs_file_path.set(file_path)
            
            recent_frame = ttk.Frame(form_frame)
            recent_frame.grid(row=2, column=1, sticky="ew", padx=5, pady=0)
            
            for i, file_path in enumerate(self.recent_files[:3]):
                file_name = os.path.basename(file_path)
                btn = ttk.Button(recent_frame, text=file_name, 
                              command=make_select_command(file_path),
                              style="Recent.TButton", width=10)
                btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Configure grid column weights
        form_frame.grid_columnconfigure(1, weight=1)
        
        # Action buttons frame
        actions_frame = ttk.Frame(main_frame)
        actions_frame.pack(fill=tk.X, pady=10)
        
        # Status label
        status_label = ttk.Label(actions_frame, textvariable=self.status_var)
        status_label.pack(side=tk.LEFT)
        
        # Create button
        self.create_button = ttk.Button(actions_frame, text="Generate Playlist", 
                                     style="Accent.TButton", width=15,
                                     command=self.create_playlist)
        self.create_button.pack(side=tk.RIGHT)
        
        # Console frame with output log
        console_frame = ttk.LabelFrame(main_frame, text="Console Output")
        console_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Console text widget with scrollbar - use light theme colors
        self.console = scrolledtext.ScrolledText(console_frame, wrap=tk.WORD, height=CONSOLE_MIN_HEIGHT,
                                             width=70, bg="#F8F8F8", fg="#333333", font=("Consolas", 9))
        self.console.pack(fill=tk.BOTH, expand=True, padx=2, pady=5)
        self.console.config(state=tk.DISABLED)
        
        # Resize handle
        resize_frame = ttk.Frame(main_frame, height=5, cursor="sb_v_double_arrow")
        resize_frame.pack(fill=tk.X, side=tk.BOTTOM)
        resize_frame.bind("<ButtonPress-1>", lambda e: self.expand_window() if not self.expanded else self.shrink_window())
    
    def copy_selected_text(self):
        """Copy selected text from console to clipboard"""
        try:
            selected_text = self.console.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.root.clipboard_clear()
            self.root.clipboard_append(selected_text)
        except tk.TclError:
            pass  # No selection
    
    def copy_all_text(self):
        """Copy all text from console to clipboard"""
        all_text = self.console.get(1.0, tk.END)
        self.root.clipboard_clear()
        self.root.clipboard_append(all_text)
    
    def select_all_text(self):
        """Select all text in the console"""
        self.console.tag_add(tk.SEL, "1.0", tk.END)
        self.console.mark_set(tk.INSERT, "1.0")
        self.console.see(tk.INSERT)
    
    def show_context_menu(self, event):
        """Show the right-click context menu"""
        self.console_menu.tk_popup(event.x_root, event.y_root)
    
    def on_resize(self, event=None):
        """Handle window resize events"""
        if event and event.widget == self.root:
            # Only respond when the entire window resizes, not when child widgets resize
            current_height = self.root.winfo_height()
            if current_height > INITIAL_WINDOW_HEIGHT + 50:  # Allow some buffer
                self.expanded = True
            else:
                self.expanded = False
    
    def expand_window(self):
        """Expand the window to show more console output"""
        if not self.expanded:
            self.root.geometry(f"{self.root.winfo_width()}x{EXPANDED_WINDOW_HEIGHT}")
            self.expanded = True
    
    def shrink_window(self):
        """Shrink the window back to normal size"""
        if self.expanded:
            self.root.geometry(f"{self.root.winfo_width()}x{INITIAL_WINDOW_HEIGHT}")
            self.expanded = False
    
    def update_playlist_name(self, event=None):
        """Update the playlist name variable when focus changes"""
        # This ensures the StringVar is updated even if Enter isn't pressed
        current_name = self.playlist_entry.get().strip()
        self.playlist_name.set(current_name)
        
    def load_recent_files(self):
        """Load recent song files from history"""
        try:
            # Start with the default playlist file
            default_playlist_file = os.path.join(self.current_dir, "playlist.txt")
            
            # If playlist.txt exists in the current directory, add it as the default
            if os.path.isfile(default_playlist_file):
                self.songs_file_path.set(default_playlist_file)
                
                # Preload the playlist file path in the UI
                self.recent_files = [default_playlist_file]
                
            # Look for other .txt files in the current directory to add to the dropdown
            for file in os.listdir(self.current_dir):
                if file.endswith(".txt") and file != "playlist.txt" and os.path.isfile(os.path.join(self.current_dir, file)):
                    file_path = os.path.join(self.current_dir, file)
                    if file_path not in self.recent_files:
                        self.recent_files.append(file_path)
        except Exception as e:
            debug_log(f"Error loading recent files: {e}")
            pass  # Ignore errors in populating recent files
            
    def start_file_monitoring(self, file_path):
        """Start monitoring a file for changes"""
        if hasattr(self, 'monitored_file'):
            # Cancel any existing monitoring
            if hasattr(self, 'monitoring_job') and self.monitoring_job:
                self.root.after_cancel(self.monitoring_job)
                self.monitoring_job = None
        
        self.monitored_file = file_path
        self.last_modified_time = os.path.getmtime(file_path) if os.path.exists(file_path) else 0
        
        # Start the monitoring job
        self.monitoring_job = self.root.after(1000, self.check_file_changes)
        
    def check_file_changes(self):
        """Check if the monitored file has changed"""
        try:
            if hasattr(self, 'monitored_file') and os.path.exists(self.monitored_file):
                current_modified_time = os.path.getmtime(self.monitored_file)
                
                if current_modified_time != self.last_modified_time:
                    # File has been modified
                    self.last_modified_time = current_modified_time
                    debug_log(f"Detected change in file: {self.monitored_file}")
                    
                    # If this is the currently selected file, update the UI to reflect changes
                    if self.monitored_file == self.songs_file_path.get():
                        self.status_var.set("File updated externally")
                        messagebox.showinfo("File Updated", 
                                          f"The file {os.path.basename(self.monitored_file)} has been updated externally.")
        except Exception as e:
            debug_log(f"Error checking file changes: {e}")
        
        # Reschedule the check
        self.monitoring_job = self.root.after(1000, self.check_file_changes)
    
    def browse_file(self):
        """Open file dialog to select a playlist file"""
        file_path = filedialog.askopenfilename(
            title="Select Playlist File",
            filetypes=[
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ],
            initialdir=self.current_dir
        )
        
        if file_path:
            self.songs_file_path.set(file_path)
            
            # Start monitoring the new file for changes
            self.start_file_monitoring(file_path)
            
            # Add to recent files if not already there
            if file_path not in self.recent_files:
                self.recent_files.insert(0, file_path)
                if len(self.recent_files) > 3:
                    self.recent_files.pop()
    
    def check_environment(self):
        """Check if the environment is set up correctly"""
        self.write_to_console("Checking environment...\n")
        
        # Check for virtual environment
        venv_exists = os.path.exists(self.venv_dir)
        
        # Check for .env file with credentials
        env_exists = os.path.exists(self.env_path)
        
        # Check for valid credentials
        has_credentials = self.has_valid_credentials() if env_exists else False
        
        # Log status
        env_status = []
        if not venv_exists:
            env_status.append("- Virtual environment not found")
        if not env_exists:
            env_status.append("- .env file with Spotify credentials not found")
        elif not has_credentials:
            env_status.append("- Spotify credentials need to be set up")
            
        if env_status:
            self.write_to_console("Environment issues:\n")
            for status in env_status:
                self.write_to_console(f"{status}\n")
                
            if not venv_exists:
                self.write_to_console("\nRecommended: Run setup by executing install.py\n")
                
            if not has_credentials:
                self.write_to_console("\nRecommended: Click 'Setup Credentials' button\n")
        else:
            self.write_to_console("Environment check completed.\n")
    
    def has_valid_credentials(self):
        """Check if the .env file has valid credentials"""
        try:
            client_id = None
            client_secret = None
            redirect_uri = None
            
            with open(self.env_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("SPOTIPY_CLIENT_ID="):
                        _, client_id = line.split("=", 1)
                    elif line.startswith("SPOTIPY_CLIENT_SECRET="):
                        _, client_secret = line.split("=", 1)
                    elif line.startswith("SPOTIPY_REDIRECT_URI="):
                        _, redirect_uri = line.split("=", 1)
            
            return client_id and client_secret and redirect_uri and \
                   client_id != "your_client_id_here" and \
                   client_secret != "your_client_secret_here"
        except Exception:
            return False
    
    def show_credentials_dialog(self):
        """Show dialog to set up Spotify API credentials"""
        dialog = SpotifyCredentialsDialog(self.root, self.env_path)
        self.root.wait_window(dialog)
        return dialog.result
    
    def write_to_console(self, text):
        """Write text to the console widget"""
        self.console.config(state=tk.NORMAL)
        self.console.insert(tk.END, text)
        self.console.see(tk.END)
        self.console.config(state=tk.DISABLED)
        self.root.update_idletasks()
    
    def clear_console(self):
        """Clear the console output"""
        self.console.config(state=tk.NORMAL)
        self.console.delete(1.0, tk.END)
        self.console.config(state=tk.DISABLED)
    
    def create_playlist(self):
        """Create a Spotify playlist using Python directly"""
        try:
            # Important: Move focus away from any entry field to ensure the StringVar gets updated
            self.root.focus_set()
            
            # Force update to ensure all StringVar values are current
            self.root.update_idletasks()
            
            # Directly get the value from the entry widget instead of the StringVar
            playlist_name = self.playlist_entry.get().strip()
            
            # Debug output for playlist name
            debug_log(f"Got playlist name from entry: '{playlist_name}'")
            self.write_to_console(f"Playlist name entered: '{playlist_name}'\n")
            
            # Expand window to show more console output
            self.expand_window()
            
            # Validate inputs
            songs_file = self.songs_file_path.get().strip()
            
            # Double check we have the current value
            if not playlist_name:
                messagebox.showwarning("Input Error", "Please enter a playlist name.")
                return
            
            if not songs_file or not os.path.exists(songs_file):
                messagebox.showwarning("Input Error", "Please select a valid playlist file.")
                return
            
            # Check environment
            if not os.path.exists(self.venv_dir):
                if messagebox.askyesno("Environment Error", 
                                    "Virtual environment not found. Would you like to run the installation now?"):
                    success = self.run_installation()
                    if not success:
                        return
                else:
                    return
            
            # Check for credentials
            if not os.path.exists(self.env_path) or not self.has_valid_credentials():
                if not self.show_credentials_dialog():
                    return
            
            # Clear console
            self.clear_console()
            
            # Expand window to show more console output
            self.expand_window()
            
            # Update status
            self.status_var.set("Creating playlist...")
            self.create_button.config(state=tk.DISABLED)
            
            # Try using the shell script first since it's known to work on Linux/Mac
            if sys.platform == 'linux' or sys.platform.startswith('darwin'):
                script_path = os.path.join(self.current_dir, "generate.sh")
                
                # Verify script permissions
                if not os.access(script_path, os.X_OK):
                    self.write_to_console("Warning: Shell script not executable, setting permissions...\n")
                    try:
                        os.chmod(script_path, 0o755)  # rwxr-xr-x
                    except Exception as e:
                        self.write_to_console(f"Error setting permissions: {e}\n")
                
                if os.path.exists(script_path) and os.access(script_path, os.X_OK):
                    self.write_to_console("Using shell script method\n")
                    
                    # Create a shell command with proper quoting for the arguments
                    command_str = f"{script_path} '{playlist_name}' '{songs_file}'"
                    debug_log(f"Shell command: {command_str}")
                    success = self._run_command_and_process_output(["/bin/bash", "-c", command_str], playlist_name, songs_file)
                else:
                    self.write_to_console("Shell script not executable, falling back to Python method\n")
                    success = self._create_playlist_using_python(playlist_name, songs_file)
            else:
                # For Windows and other platforms, use Python method directly
                success = self._create_playlist_using_python(playlist_name, songs_file)
                
            # Reset UI state
            self.status_var.set("Ready")
            self.create_button.config(state=tk.NORMAL)
        except Exception as e:
            debug_log(f"Exception in create_playlist: {e}")
            debug_log(traceback.format_exc())
            self.write_to_console(f"\n❌ Error: {str(e)}\n")
            self.status_var.set("Error")
            self.create_button.config(state=tk.NORMAL)
    
    def _create_playlist_using_python(self, playlist_name, songs_file):
        """Execute the Python script directly"""
        self.write_to_console("Using Python method\n")
        
        # Get Python path from virtual environment
        python_path = os.path.join(self.venv_dir, "bin", "python")
        if sys.platform == "win32":
            python_path = os.path.join(self.venv_dir, "Scripts", "python.exe")
        
        if not os.path.exists(python_path):
            # Try alternate locations
            if sys.platform == "win32":
                python_path = os.path.join(self.venv_dir, "Scripts", "python")
            else:
                python_path = os.path.join(self.venv_dir, "bin", "python3")
                if not os.path.exists(python_path):
                    python_path = sys.executable  # Fall back to system Python
        
        # Get path to main.py script
        script_path = os.path.join(self.current_dir, "main.py")
        if not os.path.exists(script_path):
            self.write_to_console("Error: main.py script not found!\n")
            return False
        
        # Build command
        command = [python_path, script_path, playlist_name, songs_file]
        
        # Execute command
        return self._run_command_and_process_output(command, playlist_name, songs_file)
    
    def _run_command_and_process_output(self, command, playlist_name, songs_file):
        """Run the command and process its output"""
        self.write_to_console(f"Starting playlist creation: {playlist_name}\n")
        self.write_to_console(f"Using songs from: {songs_file}\n\n")
        
        # Show exact command being executed (for debugging)
        if isinstance(command, list) and command[0] == "/bin/bash":
            self.write_to_console(f"Command: {command[2]}\n\n")
        else:
            self.write_to_console(f"Command: {' '.join(str(c) for c in command) if isinstance(command, list) else command}\n\n")
        
        # Run process
        try:
            debug_log(f"Executing command: {command}")
            
            # Use subprocess.Popen to capture output in real time
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Initialize playlist URL
            playlist_url = None
            
            # Process output in real time - safely check stdout exists
            if process and process.stdout:
                # Read line by line
                for line in iter(process.stdout.readline, ""):
                    if not line:
                        break
                    clean_line = line.strip()
                    
                    # Strip ANSI color codes from terminal output
                    # Matches color codes like [0;33m and [0m
                    clean_line = re.sub(r'\x1b\[\d+(;\d+)*m', '', clean_line)
                    
                    # Format the output to make it more readable
                    if "Prüfe Python-Umgebung" in clean_line:
                        self.write_to_console("\n━━━ Environment Check ━━━\n")
                        self.write_to_console(f"{clean_line}\n")
                    elif "Starte Playlist-Erstellung" in clean_line:
                        self.write_to_console("\n━━━ Creating Playlist ━━━\n")
                        self.write_to_console(f"{clean_line}\n")
                    elif "Playlist erstellt:" in clean_line or "Playlist-Link:" in clean_line:
                        self.write_to_console("\n━━━ Playlist Created ━━━\n")
                        self.write_to_console(f"✅ {clean_line}\n")
                        
                        # Extract URL
                        url_match = re.search(r'https://open\.spotify\.com/playlist/\w+', clean_line)
                        if url_match:
                            playlist_url = url_match.group(0)
                            debug_log(f"Found playlist URL: {playlist_url}")
                    elif "Gefunden via" in clean_line:
                        self.write_to_console(f"✓ {clean_line}\n")
                    elif "Batch hinzugefügt:" in clean_line or "Erfolgreich" in clean_line:
                        self.write_to_console("\n━━━ Summary ━━━\n")
                        self.write_to_console(f"✅ {clean_line}\n")
                    elif "Fehler:" in clean_line or "Error:" in clean_line:
                        self.write_to_console(f"❌ {clean_line}\n")
                    else:
                        self.write_to_console(f"{clean_line}\n")
            else:
                self.write_to_console("Error: Could not capture process output\n")
            
            # Wait for process to complete
            if process:
                return_code = process.wait()
                debug_log(f"Process completed with return code: {return_code}")
            else:
                self.write_to_console("Error: Process failed to start\n")
                return False
            
            # Display results
            if return_code == 0:
                self.write_to_console("\n✅ Playlist created successfully!\n")
                if playlist_url:
                    self.write_to_console(f"Playlist URL: {playlist_url}\n")
                    # Ask if user wants to open the playlist
                    if messagebox.askyesno("Success", f"Playlist '{playlist_name}' created successfully! Open in browser?"):
                        webbrowser.open(playlist_url)
                return True
            else:
                self.write_to_console(f"\n❌ Error: Process exited with code {return_code}\n")
                messagebox.showerror("Error", f"Failed to create playlist. Exit code: {return_code}")
                return False
        
        except Exception as e:
            debug_log(f"Exception in _run_command_and_process_output: {e}")
            debug_log(traceback.format_exc())
            self.write_to_console(f"\n❌ Error: {str(e)}\n")
            
            # If shell script fails, try Python method directly instead of showing error
            if sys.platform == 'linux' or sys.platform.startswith('darwin'):
                if isinstance(command, list) and len(command) > 0 and command[0] == "/bin/bash":
                    self.write_to_console("\nTrying alternative method with Python...\n")
                    return self._create_playlist_using_python(playlist_name, songs_file)
            
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            return False

def create_splash_screen():
    """Create a splash screen while the app loads"""
    splash = tk.Tk()
    
    # Configure the splash window
    splash.withdraw()  # Hide initially to prevent flicker
    splash.title("")
    splash.overrideredirect(True)  # No window decorations
    
    # Calculate position
    screen_width = splash.winfo_screenwidth()
    screen_height = splash.winfo_screenheight()
    width = 350  # Splash screen dimensions
    height = 180
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    
    # Set geometry and styling
    splash.geometry(f'{width}x{height}+{x}+{y}')
    splash.configure(bg="#121212")  # Spotify dark background
    
    # Create the content frame
    frame = tk.Frame(splash, bg="#121212", padx=20, pady=20)
    frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    
    # Add Spotify-like logo as text
    label = tk.Label(frame, text="SPOTIFY", font=("Helvetica", 22, "bold"), 
                   fg="#1DB954", bg="#121212")
    label.pack()
    
    label2 = tk.Label(frame, text="Playlist Generator", font=("Helvetica", 14), 
                    fg="white", bg="#121212")
    label2.pack()
    
    # Create progress bar
    progress_frame = tk.Frame(frame, bg="#121212", height=10, width=250)
    progress_frame.pack(pady=15)
    
    progress_bar = tk.Canvas(progress_frame, width=250, height=8, bg="#333333", 
                          highlightthickness=0)
    progress_bar.pack()
    
    # Draw progress bar and initialize variables for animation
    progress_position = [0]  # Use list for mutable reference
    bar = progress_bar.create_rectangle(0, 0, 0, 8, fill="#1DB954", width=0)
    
    # Safe animation function
    def animate_progress():
        # Only proceed if splash still exists and hasn't been destroyed
        if not splash.winfo_exists():
            return
            
        # Update progress position
        progress_position[0] = (progress_position[0] + 5) % 250
        try:
            progress_bar.coords(bar, 0, 0, progress_position[0], 8)
            # Store timer ID so it can be canceled
            if hasattr(splash, 'timer_id'):
                splash.timer_id = splash.after(30, animate_progress)
        except tk.TclError:
            # Canvas was already destroyed, do nothing
            pass
    
    # Create cleanup function
    def cleanup():
        """Safely cancel animation timer"""
        try:
            if hasattr(splash, 'timer_id') and splash.timer_id:
                splash.after_cancel(splash.timer_id)
                splash.timer_id = None
        except Exception:
            pass
    
    # Attach cleanup method to splash window
    splash.cleanup = cleanup
    
    # Initialize timer ID storage
    splash.timer_id = None
    
    # Show splash and start animation
    splash.deiconify()
    splash.update()
    splash.timer_id = splash.after(30, animate_progress)
    
    return splash

def main():
    splash = None
    root = None
    try:
        debug_log("Starting application...")
        
        # Create and show splash screen
        splash = create_splash_screen()
        
        # Simulate loading time
        time.sleep(1.2)
        
        # Initialize main app - make sure to destroy splash before creating root
        if splash and splash.winfo_exists():
            try:
                if hasattr(splash, 'cleanup'):
                    splash.cleanup()
                splash.destroy()
                splash = None
            except Exception as e:
                debug_log(f"Error during splash cleanup: {e}")
        
        # Now create the main application window
        root = tk.Tk()
        app = SpotifyPlaylistGeneratorGUI(root)
        
        # Make sure to load any recent files for the UI
        app.populate_recent_files()
        
        # Center the main window
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width - INITIAL_WINDOW_WIDTH) // 2
        y = (screen_height - INITIAL_WINDOW_HEIGHT) // 2
        root.geometry(f"+{x}+{y}")
        
        # Start the application main loop
        debug_log("Starting main application loop")
        root.mainloop()
        
    except Exception as e:
        debug_log(f"Error in main: {e}")
        debug_log(traceback.format_exc())
        if root and root.winfo_exists():
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
        else:
            print(f"Error: {str(e)}")
        
    finally:
        # Final cleanup for both windows
        for window in [splash, root]:
            if window and hasattr(window, 'winfo_exists') and window.winfo_exists():
                try:
                    debug_log(f"Cleaning up window in finally block")
                    if hasattr(window, 'cleanup'):
                        window.cleanup()
                    window.destroy()
                except Exception as e:
                    debug_log(f"Final cleanup error: {e}")
                    pass

if __name__ == "__main__":
    main()