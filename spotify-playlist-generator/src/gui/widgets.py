"""
Custom GUI Widgets - Reusable UI components
==========================================
Version: 2.0.0
Author: MaxBriliant

Contains custom widgets and components used throughout the application.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable, Any, List
import threading
import time

class ModernButton(ttk.Frame):
    """Modern styled button with hover effects."""
    
    def __init__(self, parent, text: str = "", command: Optional[Callable] = None, 
                 style: str = "primary", width: int = 0, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.command = command
        self.text = text
        self.style_type = style
        
        # Color schemes
        self.colors = {
            'primary': {'bg': '#1DB954', 'fg': 'white', 'hover': '#1ed760'},
            'secondary': {'bg': '#535353', 'fg': 'white', 'hover': '#666666'},
            'danger': {'bg': '#dc3545', 'fg': 'white', 'hover': '#c82333'},
            'success': {'bg': '#28a745', 'fg': 'white', 'hover': '#218838'},
        }
        
        self.create_button()
    
    def create_button(self):
        """Create the button widget."""
        colors = self.colors.get(self.style_type, self.colors['primary'])
        
        self.button = tk.Button(
            self,
            text=self.text,
            command=self.command,
            bg=colors['bg'],
            fg=colors['fg'],
            relief='flat',
            borderwidth=0,
            font=('Helvetica', 10, 'bold'),
            cursor='hand2',
            padx=20,
            pady=8
        )
        self.button.pack(fill='both', expand=True)
        
        # Bind hover effects
        self.button.bind('<Enter>', self.on_enter)
        self.button.bind('<Leave>', self.on_leave)
    
    def on_enter(self, event):
        """Handle mouse enter."""
        colors = self.colors.get(self.style_type, self.colors['primary'])
        self.button.configure(bg=colors['hover'])
    
    def on_leave(self, event):
        """Handle mouse leave."""
        colors = self.colors.get(self.style_type, self.colors['primary'])
        self.button.configure(bg=colors['bg'])
    
    def configure_text(self, text: str):
        """Update button text."""
        self.text = text
        self.button.configure(text=text)
    
    def configure_command(self, command: Callable):
        """Update button command."""
        self.command = command
        self.button.configure(command=command)

class StatusBar(ttk.Frame):
    """Status bar with text and optional progress indicator."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.status_var = tk.StringVar(value="Ready")
        self.create_widgets()
    
    def create_widgets(self):
        """Create status bar widgets."""
        # Status indicator dot
        self.indicator = tk.Label(
            self,
            text="●",
            font=('Arial', 12),
            fg='#28a745'  # Green for ready
        )
        self.indicator.pack(side=tk.LEFT, padx=(5, 10))
        
        # Status text
        self.status_label = ttk.Label(self, textvariable=self.status_var)
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Progress bar (hidden by default)
        self.progress = ttk.Progressbar(self, mode='indeterminate')
        
        # Version/info on the right
        self.info_label = ttk.Label(self, text="v2.0.0")
        self.info_label.pack(side=tk.RIGHT, padx=5)
    
    def set_status(self, message: str, status_type: str = "info"):
        """Set status message with optional type indicator."""
        self.status_var.set(message)
        
        # Update indicator color based on status type
        colors = {
            'info': '#007bff',
            'success': '#28a745', 
            'warning': '#ffc107',
            'error': '#dc3545',
            'ready': '#28a745'
        }
        
        self.indicator.configure(fg=colors.get(status_type, '#007bff'))
    
    def show_progress(self, show: bool = True):
        """Show or hide progress indicator."""
        if show:
            self.progress.pack(side=tk.RIGHT, padx=(5, 10), before=self.info_label)
            self.progress.start()
        else:
            self.progress.stop()
            self.progress.pack_forget()
    
    def clear(self):
        """Clear status and hide progress."""
        self.set_status("Ready", "ready")
        self.show_progress(False)

class ConsoleWidget(ttk.Frame):
    """Console output widget with logging capabilities."""
    
    def __init__(self, parent, height: int = 10, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.max_lines = 1000  # Limit console lines to prevent memory issues
        self.create_widgets(height)
        self.setup_tags()
    
    def create_widgets(self, height: int):
        """Create console widgets."""
        # Header with title and controls
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X, padx=5, pady=(5, 0))
        
        ttk.Label(header_frame, text="📟 Console", font=('Helvetica', 10, 'bold')).pack(side=tk.LEFT)
        
        # Control buttons
        controls_frame = ttk.Frame(header_frame)
        controls_frame.pack(side=tk.RIGHT)
        
        ttk.Button(controls_frame, text="Clear", command=self.clear, width=6).pack(side=tk.RIGHT, padx=2)
        ttk.Button(controls_frame, text="Copy", command=self.copy_all, width=6).pack(side=tk.RIGHT, padx=2)
        
        # Console text area
        text_frame = ttk.Frame(self)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.text_widget = tk.Text(
            text_frame,
            height=height,
            wrap=tk.WORD,
            font=('Consolas', 9),
            bg='#1e1e1e',
            fg='white',
            insertbackground='white',
            selectbackground='#404040'
        )
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.text_widget.yview)
        self.text_widget.configure(yscrollcommand=scrollbar.set)
        
        self.text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Make read-only
        self.text_widget.configure(state=tk.DISABLED)
        
        # Context menu
        self.create_context_menu()
    
    def setup_tags(self):
        """Setup text tags for different log levels."""
        self.text_widget.tag_configure('INFO', foreground='white')
        self.text_widget.tag_configure('SUCCESS', foreground='#28a745')
        self.text_widget.tag_configure('WARNING', foreground='#ffc107')
        self.text_widget.tag_configure('ERROR', foreground='#dc3545')
        self.text_widget.tag_configure('DEBUG', foreground='#6c757d')
    
    def create_context_menu(self):
        """Create right-click context menu."""
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Copy Selected", command=self.copy_selected)
        self.context_menu.add_command(label="Copy All", command=self.copy_all)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Select All", command=self.select_all)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Clear", command=self.clear)
        
        self.text_widget.bind('<Button-3>', self.show_context_menu)
    
    def show_context_menu(self, event):
        """Show context menu."""
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()
    
    def write_line(self, message: str, level: str = "INFO"):
        """Write a line to the console."""
        self.text_widget.configure(state=tk.NORMAL)
        
        # Add timestamp
        timestamp = time.strftime("%H:%M:%S")
        full_message = f"[{timestamp}] {message}\n"
        
        # Insert with appropriate tag
        self.text_widget.insert(tk.END, full_message, level)
        
        # Limit lines to prevent memory issues
        lines = int(self.text_widget.index(tk.END).split('.')[0])
        if lines > self.max_lines:
            self.text_widget.delete(1.0, f"{lines - self.max_lines}.0")
        
        # Auto-scroll to bottom
        self.text_widget.see(tk.END)
        self.text_widget.configure(state=tk.DISABLED)
        
        # Update display
        self.update_idletasks()
    
    def clear(self):
        """Clear console output."""
        self.text_widget.configure(state=tk.NORMAL)
        self.text_widget.delete(1.0, tk.END)
        self.text_widget.configure(state=tk.DISABLED)
        self.write_line("Console cleared", "INFO")
    
    def copy_selected(self):
        """Copy selected text to clipboard."""
        try:
            selected_text = self.text_widget.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.clipboard_clear()
            self.clipboard_append(selected_text)
        except tk.TclError:
            pass  # No selection
    
    def copy_all(self):
        """Copy all text to clipboard."""
        all_text = self.text_widget.get(1.0, tk.END)
        self.clipboard_clear()
        self.clipboard_append(all_text)
    
    def select_all(self):
        """Select all text."""
        self.text_widget.tag_add(tk.SEL, "1.0", tk.END)

class FileDropWidget(ttk.Frame):
    """Widget that accepts drag & drop files."""
    
    def __init__(self, parent, on_file_drop: Optional[Callable[[str], None]] = None, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.on_file_drop = on_file_drop
        self.create_widgets()
        self.setup_drag_drop()
    
    def create_widgets(self):
        """Create file drop widgets."""
        # Drop area
        self.drop_area = tk.Frame(
            self,
            bg='#f8f9fa',
            relief='dashed',
            bd=2,
            height=100
        )
        self.drop_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Drop message
        self.drop_label = tk.Label(
            self.drop_area,
            text="📁 Drop playlist file here\nor click to browse",
            bg='#f8f9fa',
            fg='#6c757d',
            font=('Helvetica', 12),
            cursor='hand2'
        )
        self.drop_label.pack(expand=True)
        
        # Bind click to browse
        self.drop_label.bind('<Button-1>', self.browse_file)
        self.drop_area.bind('<Button-1>', self.browse_file)
    
    def setup_drag_drop(self):
        """Setup drag and drop functionality."""
        # Note: Full drag & drop would require tkinterdnd2 library
        # For now, we'll just handle the browse functionality
        pass
    
    def browse_file(self, event=None):
        """Open file browser."""
        from tkinter import filedialog
        
        file_path = filedialog.askopenfilename(
            title="Select Playlist File",
            filetypes=[
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ]
        )
        
        if file_path and self.on_file_drop:
            self.on_file_drop(file_path)
    
    def set_file(self, file_path: str):
        """Set the current file and update display."""
        from pathlib import Path
        
        file_name = Path(file_path).name
        self.drop_label.configure(text=f"📄 {file_name}")

class ProgressWidget(ttk.Frame):
    """Progress widget with percentage and status text."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.create_widgets()
        self.reset()
    
    def create_widgets(self):
        """Create progress widgets."""
        # Status text
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(self, textvariable=self.status_var)
        self.status_label.pack(fill=tk.X, pady=(0, 5))
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self,
            variable=self.progress_var,
            maximum=100,
            mode='determinate'
        )
        self.progress_bar.pack(fill=tk.X, pady=(0, 5))
        
        # Percentage label
        self.percent_var = tk.StringVar(value="0%")
        self.percent_label = ttk.Label(self, textvariable=self.percent_var)
        self.percent_label.pack()
    
    def update_progress(self, current: int, total: int, status: str = ""):
        """Update progress display."""
        if total > 0:
            percentage = (current / total) * 100
            self.progress_var.set(percentage)
            self.percent_var.set(f"{percentage:.1f}%")
        
        if status:
            self.status_var.set(status)
        
        self.update_idletasks()
    
    def set_indeterminate(self, active: bool = True):
        """Set progress bar to indeterminate mode."""
        if active:
            self.progress_bar.configure(mode='indeterminate')
            self.progress_bar.start()
            self.percent_var.set("Working...")
        else:
            self.progress_bar.stop()
            self.progress_bar.configure(mode='determinate')
    
    def reset(self):
        """Reset progress to initial state."""
        self.progress_var.set(0)
        self.percent_var.set("0%")
        self.status_var.set("Ready")
        self.progress_bar.stop()
        self.progress_bar.configure(mode='determinate')

class SearchableListbox(ttk.Frame):
    """Listbox with built-in search functionality."""
    
    def __init__(self, parent, items: List[str] = None, on_select: Optional[Callable] = None, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.items = items or []
        self.filtered_items = self.items.copy()
        self.on_select = on_select
        
        self.create_widgets()
        self.populate_list()
    
    def create_widgets(self):
        """Create searchable listbox widgets."""
        # Search entry
        search_frame = ttk.Frame(self)
        search_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(search_frame, text="🔍").pack(side=tk.LEFT, padx=(0, 5))
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search_changed)
        
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        clear_button = ttk.Button(search_frame, text="✕", width=3, command=self.clear_search)
        clear_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Listbox with scrollbar
        list_frame = ttk.Frame(self)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.listbox = tk.Listbox(list_frame, selectmode=tk.SINGLE)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.listbox.yview)
        
        self.listbox.configure(yscrollcommand=scrollbar.set)
        self.listbox.bind('<<ListboxSelect>>', self.on_list_select)
        
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def populate_list(self):
        """Populate listbox with filtered items."""
        self.listbox.delete(0, tk.END)
        for item in self.filtered_items:
            self.listbox.insert(tk.END, item)
    
    def on_search_changed(self, *args):
        """Handle search text changes."""
        search_text = self.search_var.get().lower()
        
        if search_text:
            self.filtered_items = [
                item for item in self.items 
                if search_text in item.lower()
            ]
        else:
            self.filtered_items = self.items.copy()
        
        self.populate_list()
    
    def clear_search(self):
        """Clear search text."""
        self.search_var.set("")
    
    def on_list_select(self, event):
        """Handle listbox selection."""
        selection = self.listbox.curselection()
        if selection and self.on_select:
            index = selection[0]
            item = self.filtered_items[index]
            self.on_select(item)
    
    def set_items(self, items: List[str]):
        """Set new items list."""
        self.items = items
        self.filtered_items = items.copy()
        self.populate_list()
    
    def get_selection(self) -> Optional[str]:
        """Get currently selected item."""
        selection = self.listbox.curselection()
        if selection:
            index = selection[0]
            return self.filtered_items[index]
        return None

class ThemeToggle(ttk.Frame):
    """Theme toggle widget with sun/moon icons."""
    
    def __init__(self, parent, on_theme_change: Optional[Callable[[str], None]] = None, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.current_theme = "dark"
        self.on_theme_change = on_theme_change
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create theme toggle widgets."""
        self.toggle_button = tk.Button(
            self,
            text="🌙",
            font=('Arial', 16),
            command=self.toggle_theme,
            relief='flat',
            borderwidth=0,
            cursor='hand2',
            bg='transparent'
        )
        self.toggle_button.pack()
        
        # Tooltip (simple hover text)
        self.create_tooltip()
    
    def create_tooltip(self):
        """Create hover tooltip."""
        def show_tooltip(event):
            tooltip_text = "Switch to Light Theme" if self.current_theme == "dark" else "Switch to Dark Theme"
            # Could implement actual tooltip widget here
            pass
        
        def hide_tooltip(event):
            pass
        
        self.toggle_button.bind('<Enter>', show_tooltip)
        self.toggle_button.bind('<Leave>', hide_tooltip)
    
    def toggle_theme(self):
        """Toggle between dark and light themes."""
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        
        # Update button icon
        icon = "☀️" if self.current_theme == "dark" else "🌙"
        self.toggle_button.configure(text=icon)
        
        # Notify callback
        if self.on_theme_change:
            self.on_theme_change(self.current_theme)
    
    def set_theme(self, theme: str):
        """Set theme programmatically."""
        self.current_theme = theme
        icon = "☀️" if theme == "dark" else "🌙"
        self.toggle_button.configure(text=icon)

class RecentFilesWidget(ttk.Frame):
    """Widget showing recently used files."""
    
    def __init__(self, parent, on_file_select: Optional[Callable[[str], None]] = None, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.on_file_select = on_file_select
        self.recent_files = []
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create recent files widgets."""
        # Header
        header_label = ttk.Label(self, text="📁 Recent Files", font=('Helvetica', 10, 'bold'))
        header_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Files frame
        self.files_frame = ttk.Frame(self)
        self.files_frame.pack(fill=tk.X)
        
        # Initially show "no recent files" message
        self.no_files_label = ttk.Label(
            self.files_frame, 
            text="No recent files", 
            foreground='gray'
        )
        self.no_files_label.pack()
    
    def update_files(self, file_paths: List[str]):
        """Update the list of recent files."""
        self.recent_files = file_paths
        
        # Clear existing widgets
        for widget in self.files_frame.winfo_children():
            widget.destroy()
        
        if not file_paths:
            self.no_files_label = ttk.Label(
                self.files_frame, 
                text="No recent files", 
                foreground='gray'
            )
            self.no_files_label.pack()
            return
        
        # Create buttons for each recent file
        from pathlib import Path
        
        for i, file_path in enumerate(file_paths[:5]):  # Show max 5 files
            if not Path(file_path).exists():
                continue
                
            file_name = Path(file_path).name
            
            # Truncate long filenames
            if len(file_name) > 30:
                display_name = file_name[:27] + "..."
            else:
                display_name = file_name
            
            file_button = ttk.Button(
                self.files_frame,
                text=f"{i+1}. {display_name}",
                command=lambda path=file_path: self.select_file(path),
                width=35
            )
            file_button.pack(fill=tk.X, pady=1)
    
    def select_file(self, file_path: str):
        """Handle file selection."""
        if self.on_file_select:
            self.on_file_select(file_path)

# Utility function for creating themed frames
def create_card_frame(parent, title: str = "", padding: int = 10) -> ttk.Frame:
    """Create a card-style frame with optional title."""
    if title:
        frame = ttk.LabelFrame(parent, text=title, padding=padding)
    else:
        frame = ttk.Frame(parent, padding=padding)
    
    return frame

# Utility function for creating icon buttons
def create_icon_button(parent, icon: str, command: Optional[Callable] = None, 
                      tooltip: str = "") -> tk.Button:
    """Create a simple icon button."""
    button = tk.Button(
        parent,
        text=icon,
        font=('Arial', 12),
        command=command,
        relief='flat',
        borderwidth=0,
        cursor='hand2',
        width=3,
        height=1
    )
    
    # Simple hover effect
    def on_enter(e):
        button.configure(bg='lightgray')
    
    def on_leave(e):
        button.configure(bg='SystemButtonFace')
    
    button.bind('<Enter>', on_enter)
    button.bind('<Leave>', on_leave)
    
    return button