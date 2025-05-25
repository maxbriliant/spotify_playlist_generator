#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Modern Spotify Playlist Generator - Beautiful UI
================================================
Version: 2.0.0 - Modern Edition
Author: MaxBriliant (Enhanced by AI)
Date: May 2025

A completely redesigned, modern UI following Material Design 3 principles
with glassmorphism effects, smooth animations, and contemporary styling.
"""

import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import os
import sys
import time
import subprocess
import webbrowser
import re
import traceback
import threading
from datetime import datetime

# Remove all [DEBUG] output and suppress PIL warning for end users
# Only print PIL warning if running in a dev/debug mode
PIL_AVAILABLE = False
try:
    from PIL import Image, ImageTk, ImageDraw, ImageFilter
    PIL_AVAILABLE = True
except ImportError:
    if os.environ.get('SPOTIFY_DEV_MODE') == '1':
        print("Note: PIL not available, using basic icons")

# Fix: Only import screeninfo if available, and handle missing import gracefully
try:
    from screeninfo import get_monitors
except ImportError:
    get_monitors = None

# Modern UI Configuration
class ModernConfig:
    # Color Schemes - Material Design 3 inspired
    COLORS = {
        'dark': {
            'primary': '#1DB954',           # Spotify Green
            'primary_variant': '#1ed760',    # Lighter green
            'secondary': '#191414',          # Spotify Black
            'surface': '#121212',            # Dark surface
            'surface_variant': '#1e1e1e',    # Lighter dark surface
            'surface_container': '#2a2a2a',  # Container surface
            'on_surface': '#ffffff',         # Text on dark
            'on_surface_variant': '#b3b3b3', # Secondary text
            'outline': '#535353',            # Borders
            'background': '#0d1117',         # Background
            'error': '#ff6b6b',             # Error color
            'warning': '#ffa726',           # Warning color
            'success': '#4caf50',           # Success color
            'glass_bg': '#1a1a1a80',       # Glassmorphism background
        },
        'light': {
            'primary': '#1DB954',
            'primary_variant': '#1ed760',
            'secondary': '#ffffff',
            'surface': '#ffffff',
            'surface_variant': '#f5f5f5',
            'surface_container': '#fafafa',
            'on_surface': '#000000',
            'on_surface_variant': '#666666',
            'outline': '#e0e0e0',
            'background': '#fafafa',
            'error': '#d32f2f',
            'warning': '#f57c00',
            'success': '#388e3c',
            'glass_bg': '#ffffff80',
        }
    }
    
    # Typography - fallback to system fonts
    FONTS = {
        'heading': ('Helvetica', 24, 'bold'),
        'title': ('Helvetica', 18, 'bold'),
        'body': ('Helvetica', 11),
        'body_medium': ('Helvetica', 12),
        'caption': ('Helvetica', 10),
        'button': ('Helvetica', 11, 'bold'),
        'monospace': ('Courier', 10),
    }
    
    # Spacing
    SPACING = {
        'xs': 4,
        'sm': 8, 
        'md': 16,
        'lg': 24,
        'xl': 32,
        'xxl': 48,
    }

class ModernStyleManager:
    def __init__(self, root):
        self.root = root
        self.current_theme = 'dark'
        self.colors = ModernConfig.COLORS[self.current_theme]
        self.setup_styles()
    
    def setup_styles(self):
        """Setup modern ttk styles"""
        self.style = ttk.Style()
        
        # Try to use a modern theme
        try:
            self.style.theme_use('clam')
        except:
            pass
    
    def toggle_theme(self):
        """Toggle between dark and light themes"""
        self.current_theme = 'light' if self.current_theme == 'dark' else 'dark'
        self.colors = ModernConfig.COLORS[self.current_theme]
        self.apply_theme()
    
    def apply_theme(self):
        """Apply the current theme to all widgets"""
        # Update root window
        self.root.configure(bg=self.colors['background'])
        
        # Update all widgets recursively
        for widget in self.root.winfo_children():
            self._apply_theme_recursive(widget)
    
    def _apply_theme_recursive(self, widget):
        """Recursively apply theme to all widgets"""
        try:
            widget_class = widget.winfo_class()
            
            if widget_class == 'Frame':
                widget.configure(bg=self.colors['surface'])
            elif widget_class == 'Label':
                widget.configure(
                    bg=self.colors['surface'],
                    fg=self.colors['on_surface']
                )
            elif widget_class == 'Canvas':
                widget.configure(bg=self.colors['surface'])
            
            # Recursively apply to children
            for child in widget.winfo_children():
                self._apply_theme_recursive(child)
        except:
            pass

class ModernWidget:
    """Base class for creating modern, styled widgets"""
    
    @staticmethod
    def create_modern_button(parent, text, command=None, style='primary', width=None, **kwargs):
        """Create a modern styled button with hover effects"""
        style_manager = getattr(parent, 'style_manager', None) or getattr(parent.master, 'style_manager', None)
        colors = style_manager.colors if style_manager else ModernConfig.COLORS['dark']
        
        # Create frame for button to handle styling
        button_frame = tk.Frame(parent, bg=colors.get('surface', '#121212'))
        
        if style == 'primary':
            bg_color = colors['primary']
            fg_color = '#ffffff'
            hover_color = colors['primary_variant']
        elif style == 'secondary':
            bg_color = colors['surface_variant']
            fg_color = colors['on_surface']
            hover_color = colors['surface_container']
        else:
            bg_color = colors['surface_container']
            fg_color = colors['on_surface']
            hover_color = colors['surface_variant']
        
        button = tk.Button(
            button_frame,
            text=text,
            command=command if command is not None else (lambda: None),
            bg=bg_color,
            fg=fg_color,
            font=ModernConfig.FONTS['button'],
            relief='flat',
            borderwidth=0,
            cursor='hand2',
            padx=20,
            pady=12,
            width=width if width is not None else 0,
            **kwargs
        )
        
        # Add hover effects
        def on_enter(e):
            button.configure(bg=hover_color)
        
        def on_leave(e):
            button.configure(bg=bg_color)
        
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
        button.pack(fill='both', expand=True)
        
        return button_frame
    
    @staticmethod
    def create_modern_entry(parent, textvariable=None, placeholder="", **kwargs):
        """Create a modern styled entry with placeholder support"""
        style_manager = getattr(parent, 'style_manager', None) or getattr(parent.master, 'style_manager', None)
        colors = style_manager.colors if style_manager else ModernConfig.COLORS['dark']
        
        entry_frame = tk.Frame(parent, bg=colors.get('surface', '#121212'))
        
        entry = tk.Entry(
            entry_frame,
            textvariable=textvariable if textvariable is not None else tk.StringVar(),
            font=ModernConfig.FONTS['body_medium'],
            bg=colors['surface_variant'],
            fg=colors['on_surface'],
            relief='flat',
            borderwidth=0,
            insertbackground=colors['primary'],
            **kwargs
        )
        
        # Add padding effect
        entry.pack(padx=2, pady=2, fill='both', expand=True)
        
        # Placeholder functionality
        if placeholder:
            def on_focus_in(event):
                if entry.get() == placeholder:
                    entry.delete(0, 'end')
                    entry.configure(fg=colors['on_surface'])
            
            def on_focus_out(event):
                if not entry.get():
                    entry.insert(0, placeholder)
                    entry.configure(fg=colors['on_surface_variant'])
            
            entry.bind('<FocusIn>', on_focus_in)
            entry.bind('<FocusOut>', on_focus_out)
            
            # Set initial placeholder
            entry.insert(0, placeholder)
            entry.configure(fg=colors['on_surface_variant'])
        
        return entry_frame, entry
    
    @staticmethod
    def create_modern_card(parent, **kwargs):
        """Create a modern card-style container"""
        style_manager = getattr(parent, 'style_manager', None) or getattr(parent.master, 'style_manager', None)
        colors = style_manager.colors if style_manager else ModernConfig.COLORS['dark']
        
        card = tk.Frame(
            parent,
            bg=colors['surface_container'],
            relief='flat',
            borderwidth=0,
            **kwargs
        )
        
        return card

class ModernSpotifyGUI:
    def __init__(self, root):
        self.root = root
        self.style_manager = ModernStyleManager(root)
        # Starte im Light-Mode
        self.style_manager.current_theme = 'light'
        self.style_manager.colors = ModernConfig.COLORS['light']
        root.style_manager = self.style_manager  # Make accessible to child widgets
        
        # Configure main window
        self.setup_window()
        
        # Initialize variables
        self.playlist_name = tk.StringVar(value="")
        self.songs_file_path = tk.StringVar(value="")
        self.status_var = tk.StringVar(value="Ready to create amazing playlists ✨")
        
        # Animation variables
        self.animation_running = False
        self.animation_after_id = None
        self.status_animation_id = None
        
        # Paths
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.venv_dir = os.path.join(self.current_dir, "venv_spotify")
        self.env_path = os.path.join(self.current_dir, ".env")
        
        # Create the beautiful UI
        self.create_modern_ui()
        
        # Apply initial theme
        self.style_manager.apply_theme()
        
        # Start periodic updates
        self.start_status_animation()
    
    def setup_window(self):
        """Configure the main window with modern styling"""
        # Window properties
        self.root.title("Spotify Playlist Generator - Modern Edition")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        # Modern window styling
        self.root.configure(bg=self.style_manager.colors['background'])
        
        # Center window
        self.center_window()
        
        # Configure window icon (if PIL available)
        if PIL_AVAILABLE:
            try:
                self.create_window_icon()
            except:
                pass
    
    def center_window(self):
        try:
            # Versuche mit screeninfo und Xlib
            try:
                import Xlib.display
                dsp = Xlib.display.Display()
                root = dsp.screen().root
                pointer = root.query_pointer()
                mouse_x, mouse_y = pointer.root_x, pointer.root_y
                if get_monitors:
                    monitors = get_monitors()
                    for m in monitors:
                        if m.x <= mouse_x < m.x + m.width and m.y <= mouse_y < m.y + m.height:
                            screen_x, screen_y, screen_w, screen_h = m.x, m.y, m.width, m.height
                            break
                    else:
                        m = monitors[0]
                        screen_x, screen_y, screen_w, screen_h = m.x, m.y, m.width, m.height
                else:
                    raise Exception('screeninfo not available')
            except Exception:
                screen_x, screen_y = 0, 0
                screen_w = self.root.winfo_screenwidth()
                screen_h = self.root.winfo_screenheight()
            self.root.update_idletasks()
            width = self.root.winfo_width()
            height = self.root.winfo_height()
            x = screen_x + (screen_w - width) // 2
            y = screen_y + (screen_h - height) // 2
            self.root.geometry(f'+{x}+{y}')
        except Exception:
            self.root.update_idletasks()
            width = self.root.winfo_width()
            height = self.root.winfo_height()
            x = (self.root.winfo_screenwidth() // 2) - (width // 2)
            y = (self.root.winfo_screenheight() // 2) - (height // 2)
            self.root.geometry(f'+{x}+{y}')
    
    def create_window_icon(self):
        if not PIL_AVAILABLE:
            return
        from PIL import Image, ImageTk, ImageDraw
        icon_size = 32
        icon = Image.new('RGBA', (icon_size, icon_size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(icon)
        draw.ellipse([4, 4, 28, 28], fill='#1DB954')
        icon_tk = ImageTk.PhotoImage(icon)
        self.root.iconphoto(False, icon_tk)
    
    def create_modern_ui(self):
        """Create the main modern UI"""
        # Main container with padding
        main_container = tk.Frame(
            self.root,
            bg=self.style_manager.colors['background'],
            padx=ModernConfig.SPACING['xl'],
            pady=ModernConfig.SPACING['lg']
        )
        main_container.pack(fill='both', expand=True)
        
        # Header section
        self.create_header(main_container)
        
        # Main content area
        content_frame = tk.Frame(main_container, bg=self.style_manager.colors['background'])
        content_frame.pack(fill='both', expand=True, pady=(ModernConfig.SPACING['lg'], 0))
        
        # Left panel - Input form
        self.create_input_panel(content_frame)
        
        # Right panel - Console and controls
        self.create_output_panel(content_frame)
        
        # Bottom status bar
        self.create_status_bar(main_container)
    
    def create_header(self, parent):
        """Create beautiful header with branding"""
        header_frame = tk.Frame(parent, bg=self.style_manager.colors['background'])
        header_frame.pack(fill='x', pady=(0, ModernConfig.SPACING['lg']))
        
        # Left side - Logo and title
        left_header = tk.Frame(header_frame, bg=self.style_manager.colors['background'])
        left_header.pack(side='left', fill='y')
        
        # App title
        title_label = tk.Label(
            left_header,
            text="🎵 Spotify Playlist Generator",
            font=ModernConfig.FONTS['heading'],
            fg=self.style_manager.colors['primary'],
            bg=self.style_manager.colors['background']
        )
        title_label.pack(anchor='w')
        
        # Subtitle
        subtitle_label = tk.Label(
            left_header,
            text="Create beautiful playlists effortlessly",
            font=ModernConfig.FONTS['body'],
            fg=self.style_manager.colors['on_surface_variant'],
            bg=self.style_manager.colors['background']
        )
        subtitle_label.pack(anchor='w', pady=(4, 0))
        
        # Right side - Controls
        right_header = tk.Frame(header_frame, bg=self.style_manager.colors['background'])
        right_header.pack(side='right', fill='y')
        
        # Theme toggle button
        self.theme_btn = ModernWidget.create_modern_button(
            right_header,
            text="🌙" if self.style_manager.current_theme == 'dark' else "☀️",
            command=self.toggle_theme,
            style='secondary',
            width=3
        )
        self.theme_btn.pack(side='right', padx=(ModernConfig.SPACING['sm'], 0))
        
        # Settings button
        settings_btn = ModernWidget.create_modern_button(
            right_header,
            text="⚙️ Setup",
            command=self.show_credentials_dialog,
            style='secondary'
        )
        settings_btn.pack(side='right', padx=(ModernConfig.SPACING['sm'], 0))
    
    def create_input_panel(self, parent):
        """Create the left input panel"""
        # Create main input card
        input_card = ModernWidget.create_modern_card(parent)
        input_card.pack(side='left', fill='both', expand=True, padx=(0, ModernConfig.SPACING['md']))
        
        # Card header
        card_header = tk.Label(
            input_card,
            text="📝 Playlist Details",
            font=ModernConfig.FONTS['title'],
            fg=self.style_manager.colors['on_surface'],
            bg=self.style_manager.colors['surface_container'],
            anchor='w'
        )
        card_header.pack(fill='x', padx=ModernConfig.SPACING['md'], pady=(ModernConfig.SPACING['md'], ModernConfig.SPACING['sm']))
        
        # Playlist name section
        name_section = tk.Frame(input_card, bg=self.style_manager.colors['surface_container'])
        name_section.pack(fill='x', padx=ModernConfig.SPACING['md'], pady=ModernConfig.SPACING['sm'])
        
        name_label = tk.Label(
            name_section,
            text="Playlist Name",
            font=ModernConfig.FONTS['body_medium'],
            fg=self.style_manager.colors['on_surface'],
            bg=self.style_manager.colors['surface_container'],
            anchor='w'
        )
        name_label.pack(fill='x', pady=(0, ModernConfig.SPACING['xs']))
        
        name_entry_frame, self.name_entry = ModernWidget.create_modern_entry(
            name_section,
            textvariable=self.playlist_name,
            placeholder="Enter your playlist name..."
        )
        name_entry_frame.pack(fill='x', ipady=8)
        
        # File selection section
        file_section = tk.Frame(input_card, bg=self.style_manager.colors['surface_container'])
        file_section.pack(fill='x', padx=ModernConfig.SPACING['md'], pady=ModernConfig.SPACING['md'])
        
        file_label = tk.Label(
            file_section,
            text="Songs File",
            font=ModernConfig.FONTS['body_medium'],
            fg=self.style_manager.colors['on_surface'],
            bg=self.style_manager.colors['surface_container'],
            anchor='w'
        )
        file_label.pack(fill='x', pady=(0, ModernConfig.SPACING['xs']))
        
        # File input row
        file_input_frame = tk.Frame(file_section, bg=self.style_manager.colors['surface_container'])
        file_input_frame.pack(fill='x')
        
        file_entry_frame, self.file_entry = ModernWidget.create_modern_entry(
            file_input_frame,
            textvariable=self.songs_file_path,
            placeholder="Select a .txt file with songs..."
        )
        file_entry_frame.pack(side='left', fill='both', expand=True, ipady=8)
        
        browse_btn = ModernWidget.create_modern_button(
            file_input_frame,
            text="📁 Browse",
            command=self.browse_file,
            style='secondary'
        )
        browse_btn.pack(side='right', padx=(ModernConfig.SPACING['sm'], 0), fill='y')
        
        # Quick actions section
        actions_section = tk.Frame(input_card, bg=self.style_manager.colors['surface_container'])
        actions_section.pack(fill='x', padx=ModernConfig.SPACING['md'], pady=ModernConfig.SPACING['md'])
        
        actions_label = tk.Label(
            actions_section,
            text="Quick Actions",
            font=ModernConfig.FONTS['body_medium'],
            fg=self.style_manager.colors['on_surface'],
            bg=self.style_manager.colors['surface_container'],
            anchor='w'
        )
        actions_label.pack(fill='x', pady=(0, ModernConfig.SPACING['sm']))
        
        # Action buttons row
        actions_row = tk.Frame(actions_section, bg=self.style_manager.colors['surface_container'])
        actions_row.pack(fill='x')
        
        sample_btn = ModernWidget.create_modern_button(
            actions_row,
            text="📄 Use Sample",
            command=self.use_sample_file,
            style='tertiary'
        )
        sample_btn.pack(side='left', fill='x', expand=True, padx=(0, ModernConfig.SPACING['xs']))
        
        help_btn = ModernWidget.create_modern_button(
            actions_row,
            text="❓ Help",
            command=self.show_help,
            style='tertiary'
        )
        help_btn.pack(side='right', fill='x', expand=True, padx=(ModernConfig.SPACING['xs'], 0))
        
        # Main action button
        create_btn_frame = tk.Frame(input_card, bg=self.style_manager.colors['surface_container'])
        create_btn_frame.pack(fill='x', padx=ModernConfig.SPACING['md'], pady=ModernConfig.SPACING['lg'])
        
        self.create_button = ModernWidget.create_modern_button(
            create_btn_frame,
            text="🚀 Generate Playlist",
            command=self.create_playlist,
            style='primary'
        )
        self.create_button.pack(fill='x', ipady=8)
    
    def create_output_panel(self, parent):
        """Create the right output panel with console"""
        # Create output card
        output_card = ModernWidget.create_modern_card(parent)
        output_card.pack(side='right', fill='both', expand=True)
        
        # Card header
        console_header_frame = tk.Frame(output_card, bg=self.style_manager.colors['surface_container'])
        console_header_frame.pack(fill='x', padx=ModernConfig.SPACING['md'], pady=(ModernConfig.SPACING['md'], ModernConfig.SPACING['sm']))
        
        console_label = tk.Label(
            console_header_frame,
            text="📟 Console Output",
            font=ModernConfig.FONTS['title'],
            fg=self.style_manager.colors['on_surface'],
            bg=self.style_manager.colors['surface_container'],
            anchor='w'
        )
        console_label.pack(side='left')
        
        # Console controls
        clear_btn = ModernWidget.create_modern_button(
            console_header_frame,
            text="🗑️",
            command=self.clear_console,
            style='tertiary',
            width=3
        )
        clear_btn.pack(side='right')
        
        # Console area
        console_frame = tk.Frame(output_card, bg=self.style_manager.colors['surface_container'])
        console_frame.pack(fill='both', expand=True, padx=ModernConfig.SPACING['md'], pady=(0, ModernConfig.SPACING['md']))
        
        self.console = scrolledtext.ScrolledText(
            console_frame,
            wrap=tk.WORD,
            font=ModernConfig.FONTS['monospace'],
            bg=self.style_manager.colors['surface'],
            fg=self.style_manager.colors['on_surface'],
            insertbackground=self.style_manager.colors['primary'],
            relief='flat',
            borderwidth=0,
            padx=ModernConfig.SPACING['sm'],
            pady=ModernConfig.SPACING['sm']
        )
        self.console.pack(fill='both', expand=True)
        self.console.config(state=tk.DISABLED)
        
        # Welcome message
        self.write_to_console("🎵 Welcome to Spotify Playlist Generator!\n")
        self.write_to_console("Modern Edition v2.0.0 - Ready to create amazing playlists...\n\n")
    
    def create_status_bar(self, parent):
        """Create modern status bar"""
        status_frame = tk.Frame(parent, bg=self.style_manager.colors['background'])
        status_frame.pack(fill='x', pady=(ModernConfig.SPACING['lg'], 0))
        
        # Status indicator
        self.status_indicator = tk.Label(
            status_frame,
            text="●",
            font=('Arial', 16),
            fg=self.style_manager.colors['success'],
            bg=self.style_manager.colors['background']
        )
        self.status_indicator.pack(side='left')
        
        # Status text
        status_label = tk.Label(
            status_frame,
            textvariable=self.status_var,
            font=ModernConfig.FONTS['body'],
            fg=self.style_manager.colors['on_surface_variant'],
            bg=self.style_manager.colors['background']
        )
        status_label.pack(side='left', padx=(ModernConfig.SPACING['sm'], 0))
        
        # Version info
        version_label = tk.Label(
            status_frame,
            text="v1.2 Modern Edition",
            font=ModernConfig.FONTS['caption'],
            fg=self.style_manager.colors['on_surface_variant'],
            bg=self.style_manager.colors['background']
        )
        version_label.pack(side='right')
    
    def toggle_theme(self):
        """Toggle between dark and light themes with smooth transition"""
        self.style_manager.toggle_theme()
        try:
            theme_button = self.theme_btn.winfo_children()[0]
            new_text = '☀️' if self.style_manager.current_theme == 'dark' else '🌙'
            theme_button.config(text=new_text)
        except:
            pass
    
    def start_status_animation(self):
        """Start the status indicator animation"""
        if self.status_animation_id:
            self.root.after_cancel(self.status_animation_id)
        self.update_status_animation()
    
    def update_status_animation(self):
        """Animate status indicator"""
        if not self.animation_running:
            colors = ['#4caf50', '#2196f3', '#ff9800', '#e91e63']
            current_color = colors[int(time.time()) % len(colors)]
            try:
                self.status_indicator.configure(fg=current_color)
            except:
                pass
        
        self.status_animation_id = self.root.after(1000, self.update_status_animation)
    
    def write_to_console(self, text, tag=None):
        """Write text to console with optional styling"""
        try:
            self.console.config(state=tk.NORMAL)
            
            if tag == 'success':
                self.console.insert(tk.END, text, 'success')
                self.console.tag_configure('success', foreground=self.style_manager.colors['success'])
            elif tag == 'error':
                self.console.insert(tk.END, text, 'error')
                self.console.tag_configure('error', foreground=self.style_manager.colors['error'])
            elif tag == 'warning':
                self.console.insert(tk.END, text, 'warning')
                self.console.tag_configure('warning', foreground=self.style_manager.colors['warning'])
            else:
                self.console.insert(tk.END, text)
            
            self.console.see(tk.END)
            self.console.config(state=tk.DISABLED)
            self.root.update_idletasks()
        except:
            pass
    
    def clear_console(self):
        """Clear console output"""
        try:
            self.console.config(state=tk.NORMAL)
            self.console.delete(1.0, tk.END)
            self.console.config(state=tk.DISABLED)
            self.write_to_console("🎵 Console cleared!\n\n")
        except:
            pass
    
    def browse_file(self):
        """Open file dialog to select playlist file"""
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
            self.write_to_console(f"📁 Selected file: {os.path.basename(file_path)}\n", 'success')
    
    def use_sample_file(self):
        """Use the sample playlist.txt file"""
        sample_file = os.path.join(self.current_dir, "playlist.txt")
        if os.path.exists(sample_file):
            self.songs_file_path.set(sample_file)
            self.write_to_console("📄 Using sample playlist file\n", 'success')
        else:
            self.write_to_console("❌ Sample file not found\n", 'error')
    
    def show_help(self):
        """Show help dialog as modern styled dialog"""
        try:
            from modern_dialogs import ModernHelpDialog
            dialog = ModernHelpDialog(self.root)
            self.root.wait_window(dialog)
        except Exception as e:
            messagebox.showinfo("Help", f"Fehler beim Öffnen des Hilfedialogs: {e}")

    def show_credentials_dialog(self):
        """Zeige modernen Credentials-Dialog im neuen Design mit Dev-Portal-Button"""
        try:
            from modern_dialogs import ModernCredentialsDialog
            dialog = ModernCredentialsDialog(self.root, self.env_path)
            self.root.wait_window(dialog)
            if getattr(dialog, 'result', False):
                self.write_to_console("✅ Credentials updated successfully!\n", 'success')
        except Exception as e:
            from tkinter import messagebox
            messagebox.showinfo(
                "Setup Credentials", 
                f"Bitte .env-Datei mit deinen Spotify API Credentials bearbeiten.\n\nFehler: {e}"
            )
    
    def create_playlist(self):
        """Create the Spotify playlist"""
        # Get values from entries
        playlist_name = self.name_entry.get().strip()
        songs_file = self.file_entry.get().strip()
        
        # Remove placeholder text if present
        if playlist_name == "Enter your playlist name...":
            playlist_name = ""
        if songs_file == "Select a .txt file with songs...":
            songs_file = ""
        
        # Validate inputs
        if not playlist_name:
            self.write_to_console("❌ Please enter a playlist name\n", 'error')
            messagebox.showwarning("Input Error", "Please enter a playlist name.")
            return
        
        if not songs_file or not os.path.exists(songs_file):
            self.write_to_console("❌ Please select a valid song file\n", 'error')
            messagebox.showwarning("Input Error", "Please select a valid playlist file.")
            return
        
        # Sofortiges Feedback
        self.animation_running = True
        self.status_var.set("⏳ Generating playlist...")
        try:
            self.status_indicator.configure(fg=self.style_manager.colors['warning'])
        except:
            pass
        try:
            create_button = self.create_button.winfo_children()[0]
            create_button.config(state=tk.DISABLED)
        except:
            pass
        self.clear_console()
        self.write_to_console(f"🚀 Starting playlist creation: {playlist_name}\n")
        self.write_to_console(f"📁 Using songs from: {os.path.basename(songs_file)}\n\n")
        thread = threading.Thread(
            target=self._create_playlist_thread,
            args=(playlist_name, songs_file),
            daemon=True
        )
        thread.start()

    def _finish_playlist_creation(self, success, playlist_url, playlist_name):
        """Finish playlist creation (called in main thread)"""
        self.animation_running = False
        # Re-enable create button und Text zurücksetzen
        try:
            create_button = self.create_button.winfo_children()[0]
            create_button.config(state=tk.NORMAL)
        except:
            pass
        if success:
            self.status_var.set("✅ Playlist created successfully!")
            try:
                self.status_indicator.configure(fg=self.style_manager.colors['success'])
            except:
                pass
            self.write_to_console("\n🎉 Playlist created successfully!\n", 'success')
            if playlist_url:
                if messagebox.askyesno("Success!", f"Playlist '{playlist_name}' created successfully!\n\nWould you like to open it in Spotify?"):
                    webbrowser.open(playlist_url)
        else:
            self.status_var.set("❌ Failed to create playlist")
            try:
                self.status_indicator.configure(fg=self.style_manager.colors['error'])
            except:
                pass
            self.write_to_console("\n❌ Failed to create playlist\n", 'error')
    
    def _handle_playlist_error(self, error_msg):
        """Handle playlist creation error (called in main thread)"""
        self.animation_running = False
        try:
            create_button = self.create_button.winfo_children()[0]
            create_button.config(state=tk.NORMAL)
        except:
            pass
            
        self.status_var.set("❌ Error occurred")
        try:
            self.status_indicator.configure(fg=self.style_manager.colors['error'])
        except:
            pass
        self.write_to_console(f"\n❌ Error: {error_msg}\n", 'error')

    def _run_command_and_process_output(self, command, playlist_name, songs_file):
        self.write_to_console(f"Starting playlist creation: {playlist_name}\n")
        self.write_to_console(f"Using songs from: {songs_file}\n\n")
        if isinstance(command, list) and command[0] == "/bin/bash":
            self.write_to_console(f"Command: {command[2]}\n\n")
        else:
            self.write_to_console(f"Command: {' '.join(str(c) for c in command) if isinstance(command, list) else command}\n\n")
        try:
            import select
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            playlist_url = None
            if process and process.stdout:
                for line in iter(process.stdout.readline, ""):
                    if not line:
                        break
                    clean_line = line.strip()
                    clean_line = re.sub(r'\x1b\[\d+(;\d+)*m', '', clean_line)
                    self.write_to_console(f"{clean_line}\n")
                    self.console.update_idletasks()  # Sofort flushen
                    # Playlist-URL extrahieren
                    url_match = re.search(r'https://open\.spotify\.com/playlist/\w+', clean_line)
                    if url_match:
                        playlist_url = url_match.group(0)
            if process:
                return_code = process.wait()
            else:
                self.write_to_console("Error: Process failed to start\n")
                return False
            if return_code == 0:
                self.write_to_console("\n✅ Playlist created successfully!\n")
                if playlist_url:
                    self.write_to_console(f"Playlist URL: {playlist_url}\n")
                    if messagebox.askyesno("Success", f"Playlist '{playlist_name}' created successfully! Open in browser?"):
                        webbrowser.open(playlist_url)
                return True
            else:
                self.write_to_console(f"\n❌ Error: Process exited with code {return_code}\n")
                messagebox.showerror("Error", f"Failed to create playlist. Exit code: {return_code}")
                return False
        except Exception as e:
            self.write_to_console(f"\n❌ Error: {str(e)}\n")
            if sys.platform == 'linux' or sys.platform.startswith('darwin'):
                if isinstance(command, list) and len(command) > 0 and command[0] == "/bin/bash":
                    self.write_to_console("\nTrying alternative method with Python...\n")
                    if hasattr(self, '_create_playlist_using_python'):
                        return self._create_playlist_using_python(playlist_name, songs_file)
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            return False

    def _create_playlist_thread(self, playlist_name, songs_file):
        try:
            # Robust venv Python selection for all platforms
            venv_python = os.path.join(self.current_dir, "venv_spotify", "bin", "python")
            if sys.platform == "win32":
                venv_python = os.path.join(self.current_dir, "venv_spotify", "Scripts", "python.exe")
                # Use pythonw.exe to suppress command window
                pythonw = os.path.join(self.current_dir, "venv_spotify", "Scripts", "pythonw.exe")
                if os.path.exists(pythonw):
                    venv_python = pythonw
            if not os.path.exists(venv_python):
                # Only fallback if both venv paths are missing
                venv_python = sys.executable
                # Use pythonw.exe if available and on Windows
                if sys.platform == "win32":
                    pythonw = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
                    if os.path.exists(pythonw):
                        venv_python = pythonw
            script_path = os.path.join(self.current_dir, "main.py")
            command = [venv_python, script_path, playlist_name, songs_file]
            success = self._run_command_and_process_output(command, playlist_name, songs_file)
            if not success:
                self.write_to_console("\n❌ Playlist generation failed. See above for details.\n", 'error')
            self.root.after(0, lambda: self._finish_playlist_creation(success, None, playlist_name))
        except Exception as e:
            import traceback
            self.write_to_console(f"\n❌ Exception: {e}\n{traceback.format_exc()}\n", 'error')
            self.root.after(0, lambda: self._finish_playlist_creation(False, None, playlist_name))

def create_modern_splash():
    """Create a beautiful modern splash screen"""
    splash = tk.Tk()
    splash.title("")
    splash.overrideredirect(True)
    
    # Splash dimensions and positioning
    width, height = 480, 320
    screen_width = splash.winfo_screenwidth()
    screen_height = splash.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    splash.geometry(f'{width}x{height}+{x}+{y}')
    
    # Modern dark background
    splash.configure(bg='#0d1117')
    
    # Main container
    container = tk.Frame(splash, bg='#0d1117')
    container.place(relx=0.5, rely=0.5, anchor='center')
    
    # App icon/logo
    logo_label = tk.Label(
        container,
        text="🎵",
        font=('Arial', 48),
        fg='#1DB954',
        bg='#0d1117'
    )
    logo_label.pack(pady=(0, 16))
    
    # App title
    title_label = tk.Label(
        container,
        text="Spotify Playlist Generator",
        font=('Helvetica', 24, 'bold'),
        fg='#ffffff',
        bg='#0d1117'
    )
    title_label.pack()
    
    # Subtitle
    subtitle_label = tk.Label(
        container,
        text="Spotify Playlist Gen. v1.2",
        font=('Helvetica', 12),
        fg='#1DB954',
        bg='#0d1117'
    )
    subtitle_label.pack(pady=(4, 32))
    
    # Loading animation
    loading_frame = tk.Frame(container, bg='#0d1117')
    loading_frame.pack()
    
    loading_label = tk.Label(
        loading_frame,
        text="Loading amazing features...",
        font=('Helvetica', 10),
        fg='#8b949e',
        bg='#0d1117'
    )
    loading_label.pack()
    
    # Simple loading indicator
    dots_label = tk.Label(
        loading_frame,
        text="",
        font=('Helvetica', 10),
        fg='#1DB954',
        bg='#0d1117'
    )
    dots_label.pack()
    
    splash_state = {"animation_id": None}
    animate_state = [0]
    def animate_loading():
        dots = ['', '.', '..', '...', '....', '.....']
        animate_state[0] = (animate_state[0] + 1) % len(dots)
        try:
            dots_label.configure(text=dots[animate_state[0]])
            if splash_state["animation_id"]:
                splash.after_cancel(splash_state["animation_id"])
            splash_state["animation_id"] = splash.after(200, animate_loading)
        except Exception:
            pass
    def cleanup():
        try:
            if splash_state["animation_id"]:
                splash.after_cancel(splash_state["animation_id"])
                splash_state["animation_id"] = None
        except Exception:
            pass
    splash_state["cleanup"] = cleanup
    animate_loading()
    splash.update()
    return splash, splash_state

def main():
    """Main application entry point"""
    # Create and show splash screen
    try:
        splash, splash_state = create_modern_splash()
        # Show splash for 2.5 seconds
        splash.after(2500, lambda: (splash_state["cleanup"](), splash.destroy()))
        splash.mainloop()
    except Exception:
        pass  # Skip splash if there are issues
    
    # Create main application
    root = tk.Tk()
    app = ModernSpotifyGUI(root)
    
    # Handle window closing
    def on_closing():
        if app.status_animation_id:
            root.after_cancel(app.status_animation_id)
        if app.animation_after_id:
            root.after_cancel(app.animation_after_id)
        root.destroy()
        sys.exit(0)
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Start the application
    root.mainloop()

if __name__ == "__main__":
    main()

# Provide a stub for _create_playlist_using_python if not defined
if not hasattr(ModernSpotifyGUI, '_create_playlist_using_python'):
    def _create_playlist_using_python(self, playlist_name, songs_file):
        self.write_to_console("Python playlist creation not implemented in Modern UI.\n", 'error')
        return False
    ModernSpotifyGUI._create_playlist_using_python = _create_playlist_using_python