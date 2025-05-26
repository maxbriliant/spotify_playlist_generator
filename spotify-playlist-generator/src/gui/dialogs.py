"""
GUI Dialogs - Modern dialog windows for the application
=====================================================
Version: 2.0.0
Author: MaxBriliant

Contains various dialog windows used throughout the application.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import webbrowser
import subprocess
import sys
import os
from pathlib import Path
from typing import Optional, Callable, Dict, Any

class ModernDialog(tk.Toplevel):
    """Base class for modern dialog windows."""
    
    def __init__(self, parent, title: str = "Dialog", width: int = 400, height: int = 300):
        super().__init__(parent)
        self.parent = parent
        self.result = None
        
        # Configure window
        self.title(title)
        self.geometry(f"{width}x{height}")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        # Center on parent
        self.center_on_parent()
        
        # Configure colors (basic styling)
        self.configure(bg='#2b2b2b')
        
        # Bind escape to close
        self.bind('<Escape>', lambda e: self.destroy())
    
    def center_on_parent(self):
        """Center dialog on parent window."""
        self.update_idletasks()
        
        # Get parent position and size
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        # Calculate center position
        my_width = self.winfo_width()
        my_height = self.winfo_height()
        
        x = parent_x + (parent_width - my_width) // 2
        y = parent_y + (parent_height - my_height) // 2
        
        self.geometry(f"+{x}+{y}")

class CredentialsDialog(ModernDialog):
    """Dialog for setting up Spotify API credentials."""
    
    def __init__(self, parent, config_manager):
        super().__init__(parent, "Spotify API Setup", 600, 500)
        self.config_manager = config_manager
        self.create_widgets()
        self.load_existing_credentials()
    
    def create_widgets(self):
        """Create the dialog widgets."""
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header
        header_label = ttk.Label(
            main_frame, 
            text="🔑 Spotify API Credentials", 
            font=('Helvetica', 16, 'bold')
        )
        header_label.pack(pady=(0, 10))
        
        # Instructions
        instructions = """To use this application, you need Spotify API credentials:

1. Go to Spotify Developer Dashboard
2. Create a new application
3. Copy your Client ID and Client Secret
4. Set the Redirect URI exactly as shown below"""
        
        instructions_label = ttk.Label(
            main_frame, 
            text=instructions, 
            justify=tk.LEFT,
            wraplength=550
        )
        instructions_label.pack(pady=(0, 15))
        
        # Buttons row
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(0, 15))
        
        dev_button = ttk.Button(
            buttons_frame, 
            text="🌐 Open Developer Dashboard",
            command=self.open_developer_dashboard
        )
        dev_button.pack(side=tk.LEFT, padx=(0, 10))
        
        env_button = ttk.Button(
            buttons_frame,
            text="📝 Edit .env File", 
            command=self.open_env_file
        )
        env_button.pack(side=tk.LEFT)
        
        # Form fields
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill=tk.X, pady=10)
        
        # Client ID
        ttk.Label(form_frame, text="Client ID:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.client_id_var = tk.StringVar()
        client_id_entry = ttk.Entry(form_frame, textvariable=self.client_id_var, width=50)
        client_id_entry.grid(row=0, column=1, padx=(10, 0), pady=5)
        
        # Client Secret
        ttk.Label(form_frame, text="Client Secret:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.client_secret_var = tk.StringVar()
        client_secret_entry = ttk.Entry(form_frame, textvariable=self.client_secret_var, width=50, show="*")
        client_secret_entry.grid(row=1, column=1, padx=(10, 0), pady=5)
        
        # Redirect URI
        ttk.Label(form_frame, text="Redirect URI:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.redirect_uri_var = tk.StringVar(value="http://127.0.0.1:8888/callback")
        redirect_uri_entry = ttk.Entry(form_frame, textvariable=self.redirect_uri_var, width=50)
        redirect_uri_entry.grid(row=2, column=1, padx=(10, 0), pady=5)
        
        # Note
        note_label = ttk.Label(
            form_frame,
            text="* The Redirect URI must match exactly what's in your Spotify app settings",
            font=('Helvetica', 9, 'italic')
        )
        note_label.grid(row=3, column=0, columnspan=2, pady=(5, 0), sticky=tk.W)
        
        # Action buttons
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X, pady=(20, 0))
        
        cancel_button = ttk.Button(action_frame, text="Cancel", command=self.destroy)
        cancel_button.pack(side=tk.RIGHT, padx=(10, 0))
        
        save_button = ttk.Button(action_frame, text="💾 Save Credentials", command=self.save_credentials)
        save_button.pack(side=tk.RIGHT)
        
        test_button = ttk.Button(action_frame, text="🧪 Test Connection", command=self.test_credentials)
        test_button.pack(side=tk.RIGHT, padx=(0, 10))
    
    def open_developer_dashboard(self):
        """Open Spotify Developer Dashboard in browser."""
        webbrowser.open("https://developer.spotify.com/dashboard")
    
    def open_env_file(self):
        """Open .env file in system editor."""
        env_path = Path.cwd() / ".env"
        
        try:
            if not env_path.exists():
                # Create template .env file
                self.config_manager.create_env_template()
            
            if sys.platform == 'win32':
                os.startfile(env_path)
            elif sys.platform == 'darwin':
                subprocess.run(['open', env_path])
            else:
                subprocess.run(['xdg-open', env_path])
                
        except Exception as e:
            messagebox.showerror("Error", f"Could not open .env file: {e}")
    
    def load_existing_credentials(self):
        """Load existing credentials if available."""
        try:
            spotify_config = self.config_manager.get_spotify_config()
            self.client_id_var.set(spotify_config.client_id)
            self.client_secret_var.set(spotify_config.client_secret)
            self.redirect_uri_var.set(spotify_config.redirect_uri)
        except Exception:
            pass  # No existing credentials
    
    def save_credentials(self):
        """Save credentials to .env file."""
        client_id = self.client_id_var.get().strip()
        client_secret = self.client_secret_var.get().strip()
        redirect_uri = self.redirect_uri_var.get().strip()
        
        if not client_id or not client_secret:
            messagebox.showerror("Error", "Please enter both Client ID and Client Secret.")
            return
        
        if not redirect_uri:
            redirect_uri = "http://127.0.0.1:8888/callback"
        
        try:
            env_path = Path.cwd() / ".env"
            env_content = f"""# Spotify API Credentials
SPOTIPY_CLIENT_ID={client_id}
SPOTIPY_CLIENT_SECRET={client_secret}
SPOTIPY_REDIRECT_URI={redirect_uri}
"""
            
            with open(env_path, 'w') as f:
                f.write(env_content)
            
            self.result = True
            messagebox.showinfo("Success", "Credentials saved successfully!")
            self.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save credentials: {e}")
    
    def test_credentials(self):
        """Test the entered credentials."""
        client_id = self.client_id_var.get().strip()
        client_secret = self.client_secret_var.get().strip()
        redirect_uri = self.redirect_uri_var.get().strip() or "http://127.0.0.1:8888/callback"
        
        if not client_id or not client_secret:
            messagebox.showerror("Error", "Please enter credentials first.")
            return
        
        try:
            # Test by creating a temporary Spotify client
            from core.spotify_client import SpotifyClient
            
            test_client = SpotifyClient(
                client_id=client_id,
                client_secret=client_secret,
                redirect_uri=redirect_uri
            )
            
            # Try to get user info
            user_info = test_client.user_info
            
            messagebox.showinfo(
                "Success", 
                f"✅ Connection successful!\nLogged in as: {user_info.get('display_name', user_info.get('id', 'Unknown'))}"
            )
            
        except Exception as e:
            messagebox.showerror("Connection Failed", f"Could not connect to Spotify:\n\n{str(e)}")

class AboutDialog(ModernDialog):
    """About dialog with application information."""
    
    def __init__(self, parent):
        super().__init__(parent, "About Spotify Playlist Generator", 500, 400)
        self.create_widgets()
    
    def create_widgets(self):
        """Create about dialog widgets."""
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        # Logo/Icon
        logo_label = ttk.Label(main_frame, text="🎵", font=('Helvetica', 48))
        logo_label.pack(pady=(0, 10))
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text="Spotify Playlist Generator",
            font=('Helvetica', 18, 'bold')
        )
        title_label.pack()
        
        # Version
        version_label = ttk.Label(main_frame, text="Version 2.0.0 - Refactored Edition")
        version_label.pack(pady=(5, 20))
        
        # Description
        description = """A modern, intelligent tool for creating Spotify playlists from simple text files.

Features:
• Smart track search with multiple strategies
• Support for various input formats
• Modern GUI with dark/light themes
• Command-line interface
• Perfect for AI-generated playlists

Created by MaxBriliant
Contact: mxbit@yahoo.com"""
        
        desc_label = ttk.Label(
            main_frame, 
            text=description, 
            justify=tk.CENTER,
            wraplength=400
        )
        desc_label.pack(pady=(0, 20))
        
        # Links frame
        links_frame = ttk.Frame(main_frame)
        links_frame.pack(pady=10)
        
        github_button = ttk.Button(
            links_frame,
            text="🐙 GitHub Repository",
            command=lambda: webbrowser.open("https://github.com/maxbriliant/spotify_playlist_generator")
        )
        github_button.pack(side=tk.LEFT, padx=5)
        
        spotify_button = ttk.Button(
            links_frame,
            text="🎵 Spotify Developer",
            command=lambda: webbrowser.open("https://developer.spotify.com/dashboard")
        )
        spotify_button.pack(side=tk.LEFT, padx=5)
        
        # Close button
        close_button = ttk.Button(main_frame, text="Close", command=self.destroy)
        close_button.pack(pady=(20, 0))

class ProgressDialog(ModernDialog):
    """Progress dialog for long-running operations."""
    
    def __init__(self, parent, title: str = "Processing...", message: str = "Please wait..."):
        super().__init__(parent, title, 400, 150)
        self.message = message
        self.cancelled = False
        self.create_widgets()
    
    def create_widgets(self):
        """Create progress dialog widgets."""
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        # Message
        self.message_var = tk.StringVar(value=self.message)
        message_label = ttk.Label(main_frame, textvariable=self.message_var)
        message_label.pack(pady=(0, 15))
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=(0, 15))
        self.progress.start()
        
        # Cancel button
        cancel_button = ttk.Button(main_frame, text="Cancel", command=self.cancel)
        cancel_button.pack()
    
    def update_message(self, message: str):
        """Update the progress message."""
        self.message_var.set(message)
        self.update()
    
    def cancel(self):
        """Cancel the operation."""
        self.cancelled = True
        self.destroy()
    
    def is_cancelled(self) -> bool:
        """Check if operation was cancelled."""
        return self.cancelled

class FilePreviewDialog(ModernDialog):
    """Dialog for previewing playlist files before creation."""
    
    def __init__(self, parent, file_path: str):
        super().__init__(parent, f"Preview: {Path(file_path).name}", 600, 500)
        self.file_path = file_path
        self.approved = False
        self.create_widgets()
        self.load_file_content()
    
    def create_widgets(self):
        """Create file preview widgets."""
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header
        header_label = ttk.Label(
            main_frame,
            text=f"📁 Preview: {Path(self.file_path).name}",
            font=('Helvetica', 14, 'bold')
        )
        header_label