"""
Spotify API Client - Clean, maintainable Spotify integration
=========================================================
Version: 2.0.0
Author: MaxBriliant

This module provides a clean abstraction over the Spotify Web API
with proper error handling, logging, and authentication management.
"""

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from typing import Optional, List, Dict, Any, Tuple
import logging
import os
import time
from pathlib import Path

# Setup module logger
logger = logging.getLogger(__name__)

class SpotifyError(Exception):
    """Base exception for Spotify-related errors."""
    pass

class AuthenticationError(SpotifyError):
    """Raised when Spotify authentication fails."""
    pass

class APIError(SpotifyError):
    """Raised when Spotify API calls fail."""
    pass

class SpotifyClient:
    """
    Clean Spotify API client with robust error handling.
    
    Features:
    - Lazy authentication
    - Automatic retry logic
    - Comprehensive error handling
    - Rate limiting respect
    - Clean logging
    """
    
    def __init__(self, 
                 client_id: Optional[str] = None,
                 client_secret: Optional[str] = None,
                 redirect_uri: Optional[str] = None,
                 cache_path: Optional[str] = None):
        """
        Initialize Spotify client.
        
        Args:
            client_id: Spotify app client ID (or from env SPOTIPY_CLIENT_ID)
            client_secret: Spotify app client secret (or from env SPOTIPY_CLIENT_SECRET)
            redirect_uri: OAuth redirect URI (or from env SPOTIPY_REDIRECT_URI)
            cache_path: Token cache file path
        """
        # Get credentials from parameters or environment
        self.client_id = client_id or os.getenv("SPOTIPY_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("SPOTIPY_CLIENT_SECRET")
        self.redirect_uri = redirect_uri or os.getenv("SPOTIPY_REDIRECT_URI", "http://127.0.0.1:8888/callback")
        self.cache_path = cache_path or ".spotify_cache"
        
        # Validate credentials
        if not self.client_id or not self.client_secret:
            raise AuthenticationError(
                "Spotify credentials not found. Please set SPOTIPY_CLIENT_ID and "
                "SPOTIPY_CLIENT_SECRET environment variables or pass them directly."
            )
        
        # Initialize client and user info (lazy-loaded)
        self._client: Optional[spotipy.Spotify] = None
        self._user_id: Optional[str] = None
        self._user_info: Optional[Dict[str, Any]] = None
    
    @property
    def client(self) -> spotipy.Spotify:
        """Get authenticated Spotify client (lazy-loaded)."""
        if self._client is None:
            self._authenticate()
        return self._client
    
    @property
    def user_id(self) -> str:
        """Get current user ID."""
        if self._user_id is None:
            self._load_user_info()
        return self._user_id
    
    @property
    def user_info(self) -> Dict[str, Any]:
        """Get current user information."""
        if self._user_info is None:
            self._load_user_info()
        return self._user_info
    
    def _authenticate(self):
        """Authenticate with Spotify API."""
        try:
            logger.info("Authenticating with Spotify...")
            
            auth_manager = SpotifyOAuth(
                client_id=self.client_id,
                client_secret=self.client_secret,
                redirect_uri=self.redirect_uri,
                scope="playlist-modify-private playlist-modify-public user-library-read",
                cache_path=self.cache_path,
                show_dialog=False
            )
            
            self._client = spotipy.Spotify(auth_manager=auth_manager)
            
            # Test authentication by getting user info
            self._load_user_info()
            
            logger.info(f"Successfully authenticated as: {self._user_id}")
            
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            raise AuthenticationError(f"Failed to authenticate with Spotify: {e}")
    
    def _load_user_info(self):
        """Load current user information."""
        try:
            self._user_info = self.client.me()
            if not self._user_info:
                raise APIError("Failed to get user information")
            
            self._user_id = self._user_info.get("id")
            if not self._user_id:
                raise APIError("User ID not found in response")
                
        except Exception as e:
            logger.error(f"Failed to load user info: {e}")
            raise APIError(f"Failed to get user information: {e}")
    
    def search_track(self, query: str, limit: int = 1) -> List[Dict[str, Any]]:
        """
        Search for tracks on Spotify.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of track dictionaries
        """
        try:
            logger.debug(f"Searching for track: {query}")
            
            results = self.client.search(q=query, type="track", limit=limit)
            tracks = results.get("tracks", {}).get("items", [])
            
            logger.debug(f"Found {len(tracks)} tracks for query: {query}")
            return tracks
            
        except Exception as e:
            logger.error(f"Track search failed for '{query}': {e}")
            raise APIError(f"Search failed: {e}")
    
    def search_track_advanced(self, artist: str, title: str) -> List[Dict[str, Any]]:
        """
        Advanced track search using artist and title.
        
        Args:
            artist: Artist name
            title: Track title
            
        Returns:
            List of track dictionaries
        """
        queries = [
            f'track:"{title}" artist:"{artist}"',  # Exact match
            f'"{title}" "{artist}"',               # Quoted search
            f'{title} {artist}',                   # Simple search
        ]
        
        for query in queries:
            tracks = self.search_track(query, limit=5)
            if tracks:
                # Filter results to find best match
                for track in tracks:
                    track_artists = [a['name'].lower() for a in track.get('artists', [])]
                    if artist.lower() in ' '.join(track_artists):
                        return [track]
                # If no exact artist match, return first result
                return tracks[:1]
        
        return []
    
    def create_playlist(self, 
                       name: str, 
                       description: str = "", 
                       public: bool = False) -> Dict[str, Any]:
        """
        Create a new playlist.
        
        Args:
            name: Playlist name
            description: Playlist description
            public: Whether playlist should be public
            
        Returns:
            Playlist dictionary with ID and URL
        """
        try:
            logger.info(f"Creating playlist: {name}")
            
            # Add timestamp to description if not provided
            if not description:
                from datetime import datetime
                description = f"Created on {datetime.now().strftime('%Y-%m-%d %H:%M')} with Spotify Playlist Generator"
            
            playlist = self.client.user_playlist_create(
                user=self.user_id,
                name=name,
                public=public,
                description=description
            )
            
            if not playlist or not playlist.get("id"):
                raise APIError("Playlist creation returned invalid response")
            
            playlist_url = playlist.get("external_urls", {}).get("spotify", "")
            
            logger.info(f"Created playlist '{name}' with ID: {playlist['id']}")
            logger.info(f"Playlist URL: {playlist_url}")
            
            return playlist
            
        except Exception as e:
            logger.error(f"Failed to create playlist '{name}': {e}")
            raise APIError(f"Playlist creation failed: {e}")
    
    def add_tracks_to_playlist(self, 
                              playlist_id: str, 
                              track_ids: List[str],
                              batch_size: int = 100) -> Tuple[bool, int]:
        """
        Add tracks to a playlist in batches.
        
        Args:
            playlist_id: Target playlist ID
            track_ids: List of Spotify track IDs
            batch_size: Number of tracks per batch (max 100)
            
        Returns:
            Tuple of (success, number_of_tracks_added)
        """
        if not track_ids:
            logger.warning("No track IDs provided")
            return True, 0
        
        # Ensure batch size doesn't exceed Spotify limit
        batch_size = min(batch_size, 100)
        added_count = 0
        
        try:
            logger.info(f"Adding {len(track_ids)} tracks to playlist in batches of {batch_size}")
            
            for i in range(0, len(track_ids), batch_size):
                batch = track_ids[i:i + batch_size]
                
                try:
                    self.client.playlist_add_items(playlist_id, batch)
                    added_count += len(batch)
                    logger.debug(f"Added batch {i//batch_size + 1}: {len(batch)} tracks")
                    
                    # Small delay to be respectful to the API
                    if i + batch_size < len(track_ids):
                        time.sleep(0.1)
                        
                except Exception as batch_error:
                    logger.error(f"Failed to add batch {i//batch_size + 1}: {batch_error}")
                    # Continue with next batch instead of failing completely
                    continue
            
            logger.info(f"Successfully added {added_count}/{len(track_ids)} tracks to playlist")
            return True, added_count
            
        except Exception as e:
            logger.error(f"Failed to add tracks to playlist: {e}")
            return False, added_count
    
    def get_playlist_info(self, playlist_id: str) -> Optional[Dict[str, Any]]:
        """
        Get playlist information.
        
        Args:
            playlist_id: Playlist ID
            
        Returns:
            Playlist information dictionary or None if not found
        """
        try:
            playlist = self.client.playlist(playlist_id)
            return playlist
        except Exception as e:
            logger.error(f"Failed to get playlist info: {e}")
            return None
    
    def is_authenticated(self) -> bool:
        """
        Check if client is properly authenticated.
        
        Returns:
            True if authenticated, False otherwise
        """
        try:
            return self._client is not None and self.client.me() is not None
        except Exception:
            return False
    
    def clear_cache(self):
        """Clear authentication cache."""
        try:
            if os.path.exists(self.cache_path):
                os.remove(self.cache_path)
                logger.info("Authentication cache cleared")
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
    
    def __repr__(self) -> str:
        """String representation of the client."""
        status = "authenticated" if self._client else "not authenticated"
        user = f" (user: {self._user_id})" if self._user_id else ""
        return f"SpotifyClient({status}{user})"