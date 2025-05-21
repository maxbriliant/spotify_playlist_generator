#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#©MxBit2025
#Enjoy

import os
import sys
import time
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import webbrowser

# Constants for the UI
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
        
        # Configure window
        self.title("Spotify Credentials Setup")
        self.geometry("650x500")
        self.resizable(True, True)
        self.minsize(650, 500)
        self.configure(bg="#121212")
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
                           "3. Copy your Client ID and Client Secret below\n"
                           "4. Set the Redirect URI exactly as shown below in your Spotify app settings")
        
        instructions_label = ttk.Label(instructions_frame, text=instructions_text,
                                    justify="left", wraplength=600)
        instructions_label.pack(anchor="w")
        
        # Dev portal link button
        portal_button = ttk.Button(instructions_frame, text="Open Spotify Developer Portal",
                                 command=self.open_spotify_dev)
        portal_button.pack(anchor="w", pady=(10, 5))
        
        # Form frame
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill=tk.X, pady=10)
        
        # Client ID
        client_id_label = ttk.Label(form_frame, text="Client ID:")
        client_id_label.grid(row=0, column=0, sticky="w", pady=5)
        
        self.client_id_var = tk.StringVar()
        self.client_id_entry = ttk.Entry(form_frame, textvariable=self.client_id_var, width=50)
        self.client_id_entry.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        # Client Secret
        client_secret_label = ttk.Label(form_frame, text="Client Secret:")
        client_secret_label.grid(row=1, column=0, sticky="w", pady=5)
        
        self.client_secret_var = tk.StringVar()
        self.client_secret_entry = ttk.Entry(form_frame, textvariable=self.client_secret_var, width=50, show="•")
        self.client_secret_entry.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        # Toggle visibility button for client secret
        self.show_secret_var = tk.BooleanVar(value=False)
        show_secret_check = ttk.Checkbutton(form_frame, text="Show Secret", 
                                         variable=self.show_secret_var, 
                                         command=self.toggle_secret_visibility)
        show_secret_check.grid(row=1, column=2, padx=5, pady=5)
        
        # Redirect URI
        redirect_uri_label = ttk.Label(form_frame, text="Redirect URI:")
        redirect_uri_label.grid(row=2, column=0, sticky="w", pady=5)
        
        self.redirect_uri_var = tk.StringVar(value="http://127.0.0.1:8888/callback")
        redirect_uri_entry = ttk.Entry(form_frame, textvariable=self.redirect_uri_var, width=50)
        redirect_uri_entry.grid(row=2, column=1, sticky="w", padx=5, pady=5)
        
        # Copy button for URI
        copy_uri_button = ttk.Button(form_frame, text="Copy", command=self.copy_redirect_uri)
        copy_uri_button.grid(row=2, column=2, padx=5, pady=5)
        
        # Note about redirect URI
        uri_note_label = ttk.Label(form_frame, text="Important: Use exactly this Redirect URI in your Spotify app settings", 
                                foreground="#1DB954")
        uri_note_label.grid(row=3, column=1, sticky="w", padx=5, pady=(0, 10))
        
        # Add a button to edit .env directly in a text editor
        edit_env_button = tk.Button(form_frame, text="Open .env in Text Editor", 
                                bg="#333333", fg="white",
                                activebackground="#555555", activeforeground="white",
                                font=("Helvetica", 10),
                                padx=10, pady=5,
                                command=self.open_env_in_editor)
        edit_env_button.grid(row=4, column=1, sticky="w", padx=5, pady=5)
        
        # Screenshots or extra help info could be added here
        help_frame = ttk.Frame(main_frame)
        help_frame.pack(fill=tk.X, pady=5)
        
        help_text = ("In your Spotify Developer Dashboard:\n"
                   "• Click 'Edit Settings' for your app\n"
                   "• Add the exact Redirect URI shown above\n"
                   "• Make sure to save your changes\n\n"
                   "The first time you create a playlist, you'll be redirected to authorize the app.")
                   
        help_label = ttk.Label(help_frame, text=help_text, justify="left", wraplength=600)
        help_label.pack(fill=tk.X)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Using custom buttons to ensure visibility with consistent styling
        save_button = tk.Button(button_frame, text="Save Credentials", 
                             bg="#1DB954", fg="white", 
                             activebackground="#169c46", activeforeground="white",
                             font=("Helvetica", 10, "bold"), 
                             padx=10, pady=5,
                             command=self.save_credentials)
        save_button.pack(side=tk.RIGHT, padx=5)
        
        cancel_button = tk.Button(button_frame, text="Cancel", 
                               bg="#444444", fg="white",
                               activebackground="#666666", activeforeground="white",
                               font=("Helvetica", 10), 
                               padx=10, pady=5,
                               command=self.cancel)
        cancel_button.pack(side=tk.RIGHT, padx=5)
    
    def open_env_in_editor(self):
        """Open the .env file in system's default text editor"""
        try:
            if os.path.exists(self.env_path):
                if sys.platform == 'win32':
                    os.startfile(self.env_path)
                elif sys.platform == 'darwin':  # macOS
                    subprocess.call(['open', self.env_path])
                else:  # Linux and other Unix-like
                    subprocess.call(['xdg-open', self.env_path])
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
        """Toggle between showing and hiding the client secret"""
        if self.show_secret_var.get():
            self.client_secret_entry.config(show="")
        else:
            self.client_secret_entry.config(show="•")
    
    def open_spotify_dev(self):
        """Open the Spotify Developer portal in a web browser"""
        webbrowser.open("https://developer.spotify.com/dashboard")
    
    def copy_redirect_uri(self):
        """Copy the redirect URI to the clipboard"""
        self.clipboard_clear()
        self.clipboard_append(self.redirect_uri_var.get())
        messagebox.showinfo("Copied", "Redirect URI copied to clipboard")
    
    def load_existing_credentials(self):
        """Load existing credentials from .env file if it exists"""
        try:
            if os.path.exists(self.env_path):
                with open(self.env_path, "r") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            if "SPOTIPY_CLIENT_ID=" in line:
                                client_id = line.replace("SPOTIPY_CLIENT_ID=", "", 1).strip()
                                if client_id and client_id != "your_client_id_here":
                                    self.client_id_var.set(client_id)
                            elif "SPOTIPY_CLIENT_SECRET=" in line:
                                client_secret = line.replace("SPOTIPY_CLIENT_SECRET=", "", 1).strip()
                                if client_secret and client_secret != "your_client_secret_here":
                                    self.client_secret_var.set(client_secret)
                            elif "SPOTIPY_REDIRECT_URI=" in line:
                                redirect_uri = line.replace("SPOTIPY_REDIRECT_URI=", "", 1).strip()
                                if redirect_uri:
                                    self.redirect_uri_var.set(redirect_uri)
        except Exception as e:
            print(f"Error loading credentials: {e}")
    
    def save_credentials(self):
        """Save credentials to .env file"""
        client_id = self.client_id_var.get().strip()
        client_secret = self.client_secret_var.get().strip()
        redirect_uri = self.redirect_uri_var.get().strip()
        
        if not client_id or not client_secret:
            messagebox.showwarning("Incomplete Information", 
                                "Please enter both Client ID and Client Secret")
            return
        
        try:
            with open(self.env_path, "w") as f:
                f.write("# Spotify API Credentials\n")
                f.write(f"SPOTIPY_CLIENT_ID={client_id}\n")
                f.write(f"SPOTIPY_CLIENT_SECRET={client_secret}\n")
                f.write(f"SPOTIPY_REDIRECT_URI={redirect_uri}\n")
            
            messagebox.showinfo("Success", "Credentials saved successfully!")
            self.result = True
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save credentials: {str(e)}")
    
    def cancel(self):
        """Cancel the dialog"""
        self.result = False
        self.destroy()

class SpotifyPlaylistGeneratorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Spotify Playlist Generator")
        
        # Set initial window size - smaller to ensure all elements are visible
        self.root.geometry(f"{INITIAL_WINDOW_WIDTH}x{INITIAL_WINDOW_HEIGHT}")
        self.root.minsize(INITIAL_WINDOW_WIDTH, INITIAL_WINDOW_HEIGHT)
        
        # Current directory
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Path to virtual environment
        self.venv_dir = os.path.join(self.current_dir, "venv_spotify")
        self.script_name = "main.py"
        self.python_path = os.path.join(self.venv_dir, "bin", "python3")
        
        # Environment file path
        self.env_path = os.path.join(self.current_dir, ".env")
        
        # Flag to track if the window is in expanded mode
        self.is_expanded = False
        
        # Set colors and style
        self.bg_color = "#121212"  # Spotify dark
        self.fg_color = "#FFFFFF"  # White text
        self.accent_color = "#1DB954"  # Spotify green
        self.dark_accent = "#169c46"  # Darker green for hover states
        self.button_bg = "#1DB954"  # Button background
        self.button_fg = "#FFFFFF"  # Button text
        self.button_active_bg = "#169c46"  # Button when clicked
        
        # Apply dark theme to the root window
        self.root.configure(bg=self.bg_color)
        
        # Create style for ttk widgets
        self.style = ttk.Style()
        self.style.theme_use('default')
        
        # Configure widget styles
        self.style.configure('TLabel', background=self.bg_color, foreground=self.fg_color, font=('Helvetica', 11))
        self.style.configure('TFrame', background=self.bg_color)
        self.style.configure('TEntry', fieldbackground="#333333", foreground=self.fg_color)
        self.style.configure('TCombobox', fieldbackground="#333333", foreground=self.fg_color)
        
        # Check environment before creating widgets
        if not os.path.exists(self.venv_dir):
            self.run_installation()
        
        # Now create the main UI
        self.create_widgets()
    
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
        """Create the main application UI"""
        # Main container with padding that will resize properly
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title label with Spotify logo-like styling
        title_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        title_frame.pack(fill=tk.X, pady=(0, 15))  # Reduced padding
        
        title_label = tk.Label(title_frame, text="SPOTIFY", 
                              font=('Helvetica', 18, 'bold'),  # Smaller font size
                              fg=self.accent_color, bg=self.bg_color)
        title_label.pack()
        
        subtitle_label = tk.Label(title_frame, text="Playlist Generator",
                                 font=('Helvetica', 14),  # Smaller font size
                                 fg=self.fg_color, bg=self.bg_color)
        subtitle_label.pack(pady=(0, 5))  # Reduced padding
        
        # Input frame
        input_frame = ttk.Frame(self.main_frame)
        input_frame.pack(fill=tk.X, pady=5)  # Reduced padding
        
        # Use grid layout for better alignment
        input_frame.columnconfigure(1, weight=1)  # Make second column expandable
        
        # Playlist name input
        playlist_label = ttk.Label(input_frame, text="Playlist Name:")
        playlist_label.grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.playlist_name = tk.StringVar()
        self.playlist_entry = ttk.Entry(input_frame, textvariable=self.playlist_name, width=30)  # Smaller width
        self.playlist_entry.grid(row=0, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Add focus out event to ensure the StringVar is updated
        self.playlist_entry.bind("<FocusOut>", lambda e: self.update_playlist_name())
        
        # Song file selection with combobox for recent files and browse button
        songs_label = ttk.Label(input_frame, text="Songs File:")
        songs_label.grid(row=1, column=0, sticky=tk.W, pady=5)
        
        self.songs_file_path = tk.StringVar()
        
        # File selection frame
        file_selection_frame = ttk.Frame(input_frame)
        file_selection_frame.grid(row=1, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        file_selection_frame.columnconfigure(0, weight=1)  # Make combobox expandable
        
        # Combobox for recent files
        self.file_combobox = ttk.Combobox(file_selection_frame, textvariable=self.songs_file_path)
        self.file_combobox.grid(row=0, column=0, sticky=tk.W+tk.E, padx=(0, 5))
        
        # Populate with recent song files if any
        self.populate_recent_files()
        
        # Browse button using native tk.Button for consistent appearance
        browse_button = tk.Button(file_selection_frame, text="Browse", 
                               bg=self.button_bg, fg=self.button_fg,
                               activebackground=self.button_active_bg, activeforeground=self.button_fg,
                               font=("Helvetica", 10),
                               command=self.browse_file)
        browse_button.grid(row=0, column=1)
        
        # Console output frame - initially smaller
        console_frame = ttk.Frame(self.main_frame)
        console_frame.pack(fill=tk.BOTH, expand=True, pady=5)  # Reduced padding
        
        console_label = ttk.Label(console_frame, text="Console Output:")
        console_label.pack(anchor=tk.W)
        
        # Create a frame to contain the console with controlled height
        console_container = ttk.Frame(console_frame)
        console_container.pack(fill=tk.BOTH, expand=True)
        
        # Make console text selectable and copyable
        self.console = scrolledtext.ScrolledText(console_container, bg="#333333", fg=self.fg_color,
                                              font=("Consolas", 10), height=5)  # Set initial height to smaller value
        self.console.pack(fill=tk.BOTH, expand=True)
        
        # Configure tags for the console text but allow selection
        self.console.tag_configure("readonly", background="#333333", foreground=self.fg_color)
        # Only prevent typing, but allow selection (Ctrl+A, Ctrl+C)
        def handle_key(event):
            # Allow copy/paste shortcuts
            if hasattr(event, 'state') and isinstance(event.state, int) and event.state & 0x4 and event.keysym in ("c", "C", "a", "A"):
                return None  # Allow the event
            return "break"  # Block typing
        
        self.console.bind("<Key>", handle_key)
        
        # Store reference to console container for resizing
        self.console_container = console_container
        
        # Button frame - ensures buttons are always visible
        button_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Using native tk buttons for consistent appearance and ensuring they're always visible
        self.create_button = tk.Button(button_frame, text="Create Playlist", 
                                   bg=self.accent_color, fg=self.button_fg,
                                   activebackground=self.button_active_bg, activeforeground=self.button_fg,
                                   font=("Helvetica", 12, "bold"),
                                   padx=15, pady=5,  # Reduced padding
                                   command=self.create_playlist)
        self.create_button.pack(side=tk.RIGHT, padx=5)
        
        clear_button = tk.Button(button_frame, text="Clear Console", 
                              bg="#444444", fg=self.fg_color,
                              activebackground="#666666", activeforeground=self.fg_color,
                              font=("Helvetica", 10),
                              padx=10, pady=5,
                              command=self.clear_console)
        clear_button.pack(side=tk.RIGHT, padx=5)
        
        # Add config button for credentials
        config_button = tk.Button(button_frame, text="Configure API Keys", 
                               bg="#333333", fg=self.fg_color,
                               activebackground="#555555", activeforeground=self.fg_color,
                               font=("Helvetica", 10),
                               padx=10, pady=5,
                               command=self.show_credentials_dialog)
        config_button.pack(side=tk.LEFT, padx=5)
        
        # Close button
        close_button = tk.Button(button_frame, text="Close", 
                              bg="#E74C3C", fg="white",
                              activebackground="#C0392B", activeforeground="white",
                              font=("Helvetica", 10),
                              padx=10, pady=5,
                              command=self.root.destroy)
        close_button.pack(side=tk.LEFT, padx=5)
        
        # Right-click context menu for copy operations in console
        self.console_menu = tk.Menu(self.console, tearoff=0)
        self.console_menu.add_command(label="Copy", command=self.copy_selected_text)
        self.console_menu.add_command(label="Copy All", command=self.copy_all_text)
        self.console_menu.add_separator()
        self.console_menu.add_command(label="Select All", command=self.select_all_text)
        
        # Bind right-click to open context menu
        self.console.bind("<Button-3>", self.show_context_menu)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = tk.Label(self.root, textvariable=self.status_var, 
                           bg="#333333", fg=self.fg_color,
                           relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Bind window resize event to update layout
        self.root.bind("<Configure>", self.on_resize)
        
        # Check environment on startup
        self.root.after(100, self.check_environment)
    
    def copy_selected_text(self):
        """Copy selected text to clipboard"""
        try:
            selected_text = self.console.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.root.clipboard_clear()
            self.root.clipboard_append(selected_text)
        except tk.TclError:  # No selection
            pass
    
    def copy_all_text(self):
        """Copy all console text to clipboard"""
        all_text = self.console.get(1.0, tk.END)
        self.root.clipboard_clear()
        self.root.clipboard_append(all_text)
    
    def select_all_text(self):
        """Select all console text"""
        self.console.tag_add(tk.SEL, "1.0", tk.END)
        self.console.mark_set(tk.INSERT, "1.0")
        self.console.see(tk.INSERT)
        return "break"
    
    def show_context_menu(self, event):
        """Show the context menu on right-click"""
        self.console_menu.tk_popup(event.x_root, event.y_root)
    
    def on_resize(self, event=None):
        """Handle window resize to ensure UI elements remain properly sized"""
        # Only handle if it's the root window being resized
        if event and event.widget != self.root:
            return
        
        # Update combobox width based on window size
        try:
            window_width = self.root.winfo_width()
            if window_width > 0:
                # Calculate appropriate combobox width
                combobox_width = max(20, int((window_width - 200) / 12))
                self.file_combobox.config(width=combobox_width)
        except Exception:
            pass  # Ignore any errors during resize
    
    def expand_window(self):
        """Expand the window when generating a playlist"""
        if not self.is_expanded:
            # Save current scroll position
            try:
                scroll_pos = self.console.yview()[0]
            except:
                scroll_pos = 0
                
            # Resize the window
            self.root.geometry(f"{INITIAL_WINDOW_WIDTH}x{EXPANDED_WINDOW_HEIGHT}")
            
            # Give console more height
            self.console.config(height=CONSOLE_EXPANDED_HEIGHT // 20)  # Approximate line count
            
            # Restore scroll position
            self.console.yview_moveto(scroll_pos)
            
            self.is_expanded = True
    
    def shrink_window(self):
        """Shrink the window back to normal size"""
        if self.is_expanded:
            # Save current scroll position
            try:
                scroll_pos = self.console.yview()[0]
            except:
                scroll_pos = 0
                
            # Resize the window
            self.root.geometry(f"{INITIAL_WINDOW_WIDTH}x{INITIAL_WINDOW_HEIGHT}")
            
            # Give console less height
            self.console.config(height=5)  # Smaller height
            
            # Restore scroll position
            self.console.yview_moveto(scroll_pos)
            
            self.is_expanded = False
    
    def update_playlist_name(self):
        """Ensures that the playlist_name StringVar is correctly updated when focus changes"""
        # Get the current content of the entry field
        current_value = self.playlist_entry.get().strip()
        # Force update the StringVar
        self.playlist_name.set(current_value)
        # Debug output if needed
        # print(f"Updated playlist name: '{current_value}'")
        return current_value
        
    def populate_recent_files(self):
        """Populate the combobox with recent song files"""
        # Current directory files
        current_dir = os.path.dirname(os.path.abspath(__file__))
        txt_files = [f for f in os.listdir(current_dir) if f.endswith('.txt')]
        
        # Default songs.txt if it exists
        if 'songs.txt' in txt_files:
            default_path = os.path.join(current_dir, 'songs.txt')
            self.songs_file_path.set(default_path)
            
        # Add all txt files to the dropdown
        file_paths = [os.path.join(current_dir, f) for f in txt_files]
        self.file_combobox['values'] = file_paths
        
        # Try to automatically select songs.txt
        if file_paths and 'songs.txt' in txt_files:
            self.file_combobox.current(txt_files.index('songs.txt'))
    
    def browse_file(self):
        """Open file browser to select a songs file"""
        filepath = filedialog.askopenfilename(
            title="Select Songs File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filepath:
            self.songs_file_path.set(filepath)
            
            # Add to recent files if not already there
            current_values = list(self.file_combobox['values'])
            if filepath not in current_values:
                current_values.append(filepath)
                self.file_combobox['values'] = current_values
    
    def check_environment(self):
        """Check if the virtual environment and dependencies are set up"""
        self.write_to_console("Checking environment...\n")
        
        # Check for virtual environment
        if not os.path.exists(self.venv_dir):
            self.write_to_console("Virtual environment not found. Please run install.py first.\n")
            if messagebox.askyesno("Setup Required", 
                                "Virtual environment not found. Would you like to run the installation now?"):
                self.run_installation()
            return False
        
        # Check for .env file
        if not os.path.exists(self.env_path):
            self.write_to_console("WARNING: .env file not found. API credentials are missing.\n")
            if messagebox.askyesno("Credentials Missing", 
                                "The .env file with Spotify API credentials is missing. Would you like to configure it now?"):
                self.show_credentials_dialog()
        else:
            # Check if credentials are blank/default
            try:
                with open(self.env_path, "r") as f:
                    content = f.read()
                    if "your_client_id_here" in content or "your_client_secret_here" in content:
                        self.write_to_console("WARNING: Spotify credentials appear to be using default values.\n")
                        if messagebox.askyesno("Credentials Missing", 
                                            "Your Spotify API credentials appear to be using default values. Would you like to configure them now?"):
                            self.show_credentials_dialog()
                    elif not self.has_valid_credentials():
                        self.write_to_console("WARNING: Spotify credentials appear to be incomplete.\n")
                        if messagebox.askyesno("Credentials Issue", 
                                            "Your Spotify API credentials appear to be incomplete. Would you like to configure them now?"):
                            self.show_credentials_dialog()
            except Exception:
                pass  # Ignore file read errors
        
        self.write_to_console("Environment check completed.\n")
        return True
    
    def has_valid_credentials(self):
        """Check if the .env file has valid credentials"""
        try:
            client_id = None
            client_secret = None
            redirect_uri = None
            
            with open(self.env_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        if "SPOTIPY_CLIENT_ID=" in line:
                            client_id = line.replace("SPOTIPY_CLIENT_ID=", "", 1).strip()
                        elif "SPOTIPY_CLIENT_SECRET=" in line:
                            client_secret = line.replace("SPOTIPY_CLIENT_SECRET=", "", 1).strip()
                        elif "SPOTIPY_REDIRECT_URI=" in line:
                            redirect_uri = line.replace("SPOTIPY_REDIRECT_URI=", "", 1).strip()
            
            return client_id and client_secret and redirect_uri
        except Exception:
            return False
    
    def show_credentials_dialog(self):
        """Show the credentials configuration dialog"""
        dialog = SpotifyCredentialsDialog(self.root, self.env_path)
        self.root.wait_window(dialog)
        if dialog.result:
            self.write_to_console("Spotify API credentials updated successfully.\n")
            return True
        return False
    
    def write_to_console(self, text):
        """Write text to the console widget"""
        # Don't disable the text widget, but make it read-only with key bindings
        self.console.insert(tk.END, text, "readonly")
        self.console.see(tk.END)
        self.root.update()
    
    def clear_console(self):
        """Clear the console output"""
        self.console.delete(1.0, tk.END)
        
        # Shrink the window when clearing console
        self.shrink_window()
    
    def create_playlist(self):
        """Create a Spotify playlist using Python directly"""
        # Important: Move focus away from any entry field to ensure the StringVar gets updated
        self.root.focus_set()
        
        # Force update root to ensure all StringVar values are current
        self.root.update_idletasks()
        
        # Now get the value from the StringVar
        playlist_name = self.playlist_name.get().strip()
        
        # Debug output for playlist name
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
            messagebox.showwarning("Input Error", "Please select a valid songs file.")
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
        
        # Execute the Python script directly (skip shell script)
        success = self._create_playlist_using_python(playlist_name, songs_file)
            
        # Reset UI state
        self.status_var.set("Ready")
        self.create_button.config(state=tk.NORMAL)
    
    def _create_playlist_using_python(self, playlist_name, songs_file):
        """Create playlist by directly calling Python (for Windows compatibility)"""
        # Get path to Python in the virtual environment
        if sys.platform == 'win32':
            python_exe = os.path.join(self.venv_dir, "Scripts", "python.exe")
        else:
            python_exe = os.path.join(self.venv_dir, "bin", "python3")
            
        if not os.path.exists(python_exe):
            # Try alternative path for Windows if the first one doesn't exist
            if sys.platform == 'win32':
                python_exe = os.path.join(self.venv_dir, "Scripts", "python")
                if not os.path.exists(python_exe):
                    messagebox.showerror("Error", "Python not found in virtual environment.")
                    return False
            else:
                messagebox.showerror("Error", "Python not found in virtual environment.")
                return False
                
        # Path to main script
        main_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), self.script_name)
        if not os.path.exists(main_script):
            messagebox.showerror("Error", f"Main script {self.script_name} not found.")
            return False
            
        # Create command - using list form ensures proper argument handling
        command = [python_exe, main_script, playlist_name, songs_file]
        
        # Debug output
        command_str = f"{python_exe} {main_script} \"{playlist_name}\" \"{songs_file}\""
        self.write_to_console(f"Executing command: {command_str}\n")
        
        return self._run_command_and_process_output(command, playlist_name, songs_file)
    
    def _run_command_and_process_output(self, command, playlist_name, songs_file):
        """Run the command and process its output"""
        self.write_to_console(f"Starting playlist creation: {playlist_name}\n")
        self.write_to_console(f"Using songs from: {songs_file}\n\n")
        
        # Run process
        try:
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
                while True:
                    line = process.stdout.readline()
                    if not line:  # End of stream
                        break
                        
                    # Process the line
                    self.write_to_console(line)
                    # Capture the playlist URL if it's in the output
                    if "Playlist-Link:" in line or "https://open.spotify.com/playlist/" in line:
                        # Extract the URL from the line
                        if "Playlist-Link:" in line:
                            playlist_url = line.strip().split("Playlist-Link:")[1].strip()
                        elif "https://open.spotify.com/playlist/" in line:
                            # Extract the URL using regex
                            import re
                            url_match = re.search(r'(https://open\.spotify\.com/playlist/[a-zA-Z0-9]+)', line)
                            if url_match:
                                playlist_url = url_match.group(1)
            else:
                self.write_to_console("Warning: Unable to capture output stream\n")
            
            # Wait for process to complete
            if process:
                process.wait()
                return_code = process.returncode
            else:
                self.write_to_console("Error: Process failed to start\n")
                return False
            
            # Display results
            if return_code == 0:
                success_msg = "Playlist created successfully!"
                self.write_to_console(f"\n✅ {success_msg}\n")
                if playlist_url:
                    self.write_to_console(f"Playlist URL: {playlist_url}\n")
                    # Show a dialog with the URL that can be clicked
                    if messagebox.askyesno("Success", f"{success_msg}\n\nDo you want to open the playlist in your browser?"):
                        webbrowser.open(playlist_url)
                else:
                    messagebox.showinfo("Success", success_msg)
                return True
            else:
                self.write_to_console("\n❌ Error creating playlist\n")
                messagebox.showerror("Error", "Failed to create playlist. See console for details.")
                return False
        
        except Exception as e:
            self.write_to_console(f"\n❌ Error: {str(e)}\n")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            return False

def create_splash_screen():
    """Create a splash screen while the app loads"""
    splash = tk.Tk()
    splash.overrideredirect(True)
    screen_width = splash.winfo_screenwidth()
    screen_height = splash.winfo_screenheight()
    
    width = 350  # Smaller splash screen
    height = 180
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    
    splash.geometry(f'{width}x{height}+{x}+{y}')
    splash.configure(bg="#121212")  # Spotify dark background
    
    # Spotify-like logo placeholder
    frame = tk.Frame(splash, bg="#121212", padx=20, pady=20)
    frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    
    label = tk.Label(frame, text="SPOTIFY", font=("Helvetica", 22, "bold"), fg="#1DB954", bg="#121212")
    label.pack()
    
    label2 = tk.Label(frame, text="Playlist Generator", font=("Helvetica", 14), fg="white", bg="#121212")
    label2.pack()
    
    # Custom progress bar
    progress_frame = tk.Frame(frame, bg="#121212", height=10, width=250)  # Smaller progress bar
    progress_frame.pack(pady=15)
    
    progress_bar = tk.Canvas(progress_frame, width=250, height=8, bg="#333333", 
                          highlightthickness=0)
    progress_bar.pack()
    
    # Create animated progress effect
    progress_value = 0
    bar_id = progress_bar.create_rectangle(0, 0, 0, 8, fill="#1DB954", width=0)
    
    def update_progress():
        nonlocal progress_value
        progress_value += 5
        if progress_value > 250:
            progress_value = 0
        progress_bar.coords(bar_id, 0, 0, progress_value, 8)
        splash.after(30, update_progress)
    
    update_progress()
    splash.update()
    return splash

def main():
    try:
        # Show splash screen
        splash = create_splash_screen()
        
        # Simulate loading time
        time.sleep(1.2)  # Shorter loading time
        
        # Initialize main app
        root = tk.Tk()
        app = SpotifyPlaylistGeneratorGUI(root)
        
        # Center the main window
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width - INITIAL_WINDOW_WIDTH) // 2
        y = (screen_height - INITIAL_WINDOW_HEIGHT) // 2
        root.geometry(f"+{x}+{y}")
        
        # Close splash and show main app
        splash.destroy()
        root.mainloop()
    
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()