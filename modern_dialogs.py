import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
import webbrowser
import subprocess

from modern_spotify_gui import ModernConfig, ModernWidget

class ModernDialog(tk.Toplevel):
    def __init__(self, parent, title="Dialog", width=480, height=340):
        super().__init__(parent)
        self.parent = parent
        self.title(title)
        self.configure(bg=ModernConfig.COLORS['dark']['background'])
        self.resizable(False, False)
        self.geometry(f"{width}x{height}")
        self.transient(parent)
        self.grab_set()
        self.center_on_parent(width, height)

    def center_on_parent(self, width, height):
        self.update_idletasks()
        px = self.parent.winfo_rootx()
        py = self.parent.winfo_rooty()
        pw = self.parent.winfo_width()
        ph = self.parent.winfo_height()
        x = px + (pw - width) // 2
        y = py + (ph - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")

class ModernHelpDialog(ModernDialog):
    def __init__(self, parent):
        # Theme dynamisch wählen
        style_manager = getattr(parent, 'style_manager', None)
        theme = style_manager.current_theme if style_manager else 'light'
        colors = ModernConfig.COLORS[theme]
        fonts = ModernConfig.FONTS
        super().__init__(parent, title="Hilfe", width=540, height=420)
        self.configure(bg=colors['background'])
        main = tk.Frame(self, bg=colors['surface_container'])
        main.pack(fill='both', expand=True, padx=24, pady=18)
        header = tk.Label(main, text="Spotify Playlist Generator – Hilfe", font=fonts['title'], fg=colors['primary'], bg=colors['surface_container'])
        header.pack(anchor='w', pady=(0, 8))
        text = (
            "📝 So funktioniert's:\n"
            "1. Gib einen Playlist-Namen ein\n"
            "2. Wähle eine .txt-Datei mit Songs\n"
            "3. Klicke auf 'Generate Playlist'\n\n"
            "📄 Dateiformat:\n"
            "Jede Zeile: Artist - Song Title\n"
            "Beispiel:\nKavinsky - Nightcall\nThe Midnight - Sunset\n\n"
            "💡 Tipps:\n"
            "• Auch Spotify-URLs oder Track-IDs möglich\n"
            "• Nutze AI-Tools wie ChatGPT für Playlists\n"
            "• API-Key im Setup hinterlegen\n"
            "• Bei Problemen: Logfile und .env prüfen\n"
        )
        label = tk.Label(main, text=text, font=fonts['body'], fg=colors['on_surface'], bg=colors['surface_container'], justify='left', anchor='nw', wraplength=480)
        label.pack(fill='both', expand=True, pady=(8, 0))
        btns = tk.Frame(main, bg=colors['surface_container'])
        btns.pack(fill='x', pady=(18, 0))
        ok_btn = ModernWidget.create_modern_button(btns, text="OK", command=self.destroy, style='primary')
        ok_btn.pack(side='right')

class ModernCredentialsDialog(ModernDialog):
    def __init__(self, parent, env_path):
        # Theme dynamisch wählen
        style_manager = getattr(parent, 'style_manager', None)
        theme = style_manager.current_theme if style_manager else 'light'
        self.colors = ModernConfig.COLORS[theme]
        self.fonts = ModernConfig.FONTS
        # Größeres, luftiges Fenster
        super().__init__(parent, title="Spotify Credentials Setup", width=600, height=480)
        # Passe auch den äußeren Rahmen an
        self.configure(bg=self.colors['background'], highlightthickness=0, bd=0)
        self.env_path = env_path
        self.result = False
        self.client_id_var = tk.StringVar()
        self.client_secret_var = tk.StringVar()
        self.redirect_uri_var = tk.StringVar(value="http://127.0.0.1:8888/callback")
        self.create_widgets()
        self.load_existing_credentials()

    def create_widgets(self):
        colors = self.colors
        fonts = self.fonts
        # Hauptcontainer mit Theme-Hintergrund und abgerundeten Ecken
        main = tk.Frame(self, bg=colors['surface_container'], highlightthickness=0, bd=0)
        main.pack(fill='both', expand=True, padx=32, pady=28)
        header = tk.Label(main, text="Spotify API Credentials", font=fonts['title'], fg=colors['primary'], bg=colors['surface_container'])
        header.pack(anchor='w', pady=(0, 8))
        desc = tk.Label(main, text="Trage hier deine Spotify API-Daten ein. Diese findest du im Spotify Developer Dashboard.", font=fonts['body'], fg=colors['on_surface_variant'], bg=colors['surface_container'], wraplength=520, justify='left')
        desc.pack(anchor='w', pady=(0, 12))
        # Buttons für Dev-Portal und .env-Editor
        btnrow = tk.Frame(main, bg=colors['surface_container'], highlightthickness=0, bd=0)
        btnrow.pack(anchor='w', pady=(0, 10))
        dev_btn = ModernWidget.create_modern_button(btnrow, text="🌐 Spotify Developer Portal", command=lambda: webbrowser.open("https://developer.spotify.com/dashboard"), style='secondary')
        dev_btn.pack(side='left', padx=(0, 8))
        edit_btn = ModernWidget.create_modern_button(btnrow, text="📝 .env bearbeiten", command=self.open_env_in_editor, style='secondary')
        edit_btn.pack(side='left')
        # Client ID
        cid_label = tk.Label(main, text="Client ID", font=fonts['body_medium'], fg=colors['on_surface'], bg=colors['surface_container'])
        cid_label.pack(anchor='w')
        cid_entry_frame, cid_entry = ModernWidget.create_modern_entry(main, textvariable=self.client_id_var, placeholder="Deine Client ID")
        cid_entry_frame.pack(fill='x', pady=(0, 10))
        # Client Secret
        cs_label = tk.Label(main, text="Client Secret", font=fonts['body_medium'], fg=colors['on_surface'], bg=colors['surface_container'])
        cs_label.pack(anchor='w')
        cs_entry_frame, cs_entry = ModernWidget.create_modern_entry(main, textvariable=self.client_secret_var, placeholder="Dein Client Secret", show="*")
        cs_entry_frame.pack(fill='x', pady=(0, 10))
        # Redirect URI
        ru_label = tk.Label(main, text="Redirect URI", font=fonts['body_medium'], fg=colors['on_surface'], bg=colors['surface_container'])
        ru_label.pack(anchor='w')
        ru_entry_frame, ru_entry = ModernWidget.create_modern_entry(main, textvariable=self.redirect_uri_var, placeholder="http://127.0.0.1:8888/callback")
        ru_entry_frame.pack(fill='x', pady=(0, 10))
        # Buttons
        btns = tk.Frame(main, bg=colors['surface_container'], highlightthickness=0, bd=0)
        btns.pack(fill='x', pady=(18, 0))
        save_btn = ModernWidget.create_modern_button(btns, text="💾 Speichern", command=self.save_credentials, style='primary')
        save_btn.pack(side='right', padx=(8, 0))
        cancel_btn = ModernWidget.create_modern_button(btns, text="Abbrechen", command=self.cancel, style='secondary')
        cancel_btn.pack(side='right')

    def load_existing_credentials(self):
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
        except Exception:
            pass

    def save_credentials(self):
        cid = self.client_id_var.get().strip()
        cs = self.client_secret_var.get().strip()
        ru = self.redirect_uri_var.get().strip()
        if not cid or not cs:
            messagebox.showwarning("Fehlende Daten", "Bitte Client ID und Secret eingeben.", parent=self)
            return
        try:
            with open(self.env_path, "w") as f:
                f.write("# Spotify API Credentials - Fill these values!\n")
                f.write(f"SPOTIPY_CLIENT_ID={cid}\n")
                f.write(f"SPOTIPY_CLIENT_SECRET={cs}\n")
                f.write(f"SPOTIPY_REDIRECT_URI={ru}\n")
            self.result = True
            self.destroy()
        except Exception as e:
            messagebox.showerror("Fehler", f"Konnte nicht speichern: {e}", parent=self)

    def cancel(self):
        self.result = False
        self.destroy()

    def open_env_in_editor(self):
        try:
            if os.path.exists(self.env_path):
                if sys.platform == 'win32':
                    os.startfile(self.env_path)
                elif sys.platform == 'darwin':
                    subprocess.run(['open', self.env_path])
                else:
                    subprocess.run(['xdg-open', self.env_path])
            else:
                with open(self.env_path, "w") as f:
                    f.write("# Spotify API Credentials\n")
                    f.write("SPOTIPY_CLIENT_ID=\n")
                    f.write("SPOTIPY_CLIENT_SECRET=\n")
                    f.write("SPOTIPY_REDIRECT_URI=http://127.0.0.1:8888/callback\n")
                self.open_env_in_editor()
        except Exception as e:
            messagebox.showerror("Fehler", f".env konnte nicht geöffnet werden: {e}", parent=self)
