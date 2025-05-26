"""
Playlist Creator - Smart playlist generation with multiple search strategies
=========================================================================
Version: 2.0.0
Author: MaxBriliant

This module handles the intelligent creation of Spotify playlists from various
input formats with multiple fallback search strategies.
"""

import re
import logging
from typing import List, Tuple, Optional, Dict, Any, Set
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

from .spotify_client import SpotifyClient, SpotifyError

logger = logging.getLogger(__name__)

class TrackFormat(Enum):
    """Supported track input formats."""
    SPOTIFY_ID = "spotify_id"
    SPOTIFY_URL = "spotify_url"
    SPOTIFY_URI = "spotify_uri"
    ARTIST_TITLE = "artist_title"
    UNKNOWN = "unknown"

@dataclass
class TrackSearchResult:
    """Result of a track search operation."""
    original_query: str
    track_id: Optional[str]
    track_info: Optional[Dict[str, Any]]
    format_detected: TrackFormat
    search_method: Optional[str]
    success: bool
    error_message: Optional[str] = None

@dataclass
class PlaylistCreationResult:
    """Result of playlist creation operation."""
    success: bool
    playlist_id: Optional[str]
    playlist_url: Optional[str]
    total_tracks_requested: int
    tracks_found: int
    tracks_added: int
    failed_tracks: List[str]
    search_results: List[TrackSearchResult]

class TrackParser:
    """Utility class for parsing different track formats."""
    
    # Regex patterns for different formats
    SPOTIFY_ID_PATTERN = re.compile(r'^[A-Za-z0-9]{22})
    SPOTIFY_URL_PATTERN = re.compile(r'open\.spotify\.com/track/([A-Za-z0-9]{22})')
    SPOTIFY_URI_PATTERN = re.compile(r'spotify:track:([A-Za-z0-9]{22})')
    ARTIST_TITLE_PATTERN = re.compile(r'^(.+?)\s*[-–—]\s*(.+))
    
    @classmethod
    def detect_format(cls, track_string: str) -> TrackFormat:
        """Detect the format of a track string."""
        track_string = track_string.strip()
        
        if cls.SPOTIFY_ID_PATTERN.match(track_string):
            return TrackFormat.SPOTIFY_ID
        elif cls.SPOTIFY_URL_PATTERN.search(track_string):
            return TrackFormat.SPOTIFY_URL
        elif cls.SPOTIFY_URI_PATTERN.search(track_string):
            return TrackFormat.SPOTIFY_URI
        elif cls.ARTIST_TITLE_PATTERN.match(track_string):
            return TrackFormat.ARTIST_TITLE
        else:
            return TrackFormat.UNKNOWN
    
    @classmethod
    def extract_track_id(cls, track_string: str) -> Optional[str]:
        """Extract Spotify track ID from various formats."""
        track_string = track_string.strip()
        
        # Direct ID
        if cls.SPOTIFY_ID_PATTERN.match(track_string):
            return track_string
        
        # URL format
        url_match = cls.SPOTIFY_URL_PATTERN.search(track_string)
        if url_match:
            return url_match.group(1)
        
        # URI format
        uri_match = cls.SPOTIFY_URI_PATTERN.search(track_string)
        if uri_match:
            return uri_match.group(1)
        
        return None
    
    @classmethod
    def parse_artist_title(cls, track_string: str) -> Optional[Tuple[str, str]]:
        """Parse artist-title format."""
        match = cls.ARTIST_TITLE_PATTERN.match(track_string.strip())
        if match:
            artist = match.group(1).strip()
            title = match.group(2).strip()
            return artist, title
        return None

class TrackSearcher:
    """Advanced track search with multiple strategies."""
    
    def __init__(self, spotify_client: SpotifyClient):
        self.spotify = spotify_client
    
    def search_track(self, track_string: str) -> TrackSearchResult:
        """
        Search for a track using multiple strategies.
        
        Args:
            track_string: Track string in any supported format
            
        Returns:
            TrackSearchResult with search outcome
        """
        original_query = track_string
        track_format = TrackParser.detect_format(track_string)
        
        try:
            # Strategy 1: Direct ID extraction
            if track_format in [TrackFormat.SPOTIFY_ID, TrackFormat.SPOTIFY_URL, TrackFormat.SPOTIFY_URI]:
                track_id = TrackParser.extract_track_id(track_string)
                if track_id:
                    # Verify track exists
                    track_info = self._get_track_info(track_id)
                    if track_info:
                        return TrackSearchResult(
                            original_query=original_query,
                            track_id=track_id,
                            track_info=track_info,
                            format_detected=track_format,
                            search_method="direct_id",
                            success=True
                        )
            
            # Strategy 2: Artist-Title search
            if track_format == TrackFormat.ARTIST_TITLE:
                parsed = TrackParser.parse_artist_title(track_string)
                if parsed:
                    artist, title = parsed
                    return self._search_by_artist_title(original_query, artist, title, track_format)
            
            # Strategy 3: Fallback general search
            return self._search_general(original_query, track_format)
            
        except Exception as e:
            logger.error(f"Search failed for '{track_string}': {e}")
            return TrackSearchResult(
                original_query=original_query,
                track_id=None,
                track_info=None,
                format_detected=track_format,
                search_method=None,
                success=False,
                error_message=str(e)
            )
    
    def _get_track_info(self, track_id: str) -> Optional[Dict[str, Any]]:
        """Get track information by ID."""
        try:
            return self.spotify.client.track(track_id)
        except Exception as e:
            logger.debug(f"Failed to get track info for ID {track_id}: {e}")
            return None
    
    def _search_by_artist_title(self, original_query: str, artist: str, title: str, 
                               track_format: TrackFormat) -> TrackSearchResult:
        """Search using artist and title with multiple strategies."""
        
        # Strategy 2a: Precise search with quotes
        tracks = self.spotify.search_track_advanced(artist, title)
        if tracks:
            track = tracks[0]
            return TrackSearchResult(
                original_query=original_query,
                track_id=track['id'],
                track_info=track,
                format_detected=track_format,
                search_method="artist_title_precise",
                success=True
            )
        
        # Strategy 2b: General artist-title search
        query = f"{artist} {title}"
        tracks = self.spotify.search_track(query, limit=5)
        if tracks:
            # Try to find best match
            best_match = self._find_best_match(tracks, artist, title)
            if best_match:
                return TrackSearchResult(
                    original_query=original_query,
                    track_id=best_match['id'],
                    track_info=best_match,
                    format_detected=track_format,
                    search_method="artist_title_general",
                    success=True
                )
        
        # Strategy 2c: Cleaned search (remove special characters)
        clean_artist = re.sub(r'[^\w\s]', '', artist)
        clean_title = re.sub(r'[^\w\s]', '', title)
        query = f"{clean_artist} {clean_title}"
        tracks = self.spotify.search_track(query, limit=3)
        if tracks:
            return TrackSearchResult(
                original_query=original_query,
                track_id=tracks[0]['id'],
                track_info=tracks[0],
                format_detected=track_format,
                search_method="artist_title_cleaned",
                success=True
            )
        
        return TrackSearchResult(
            original_query=original_query,
            track_id=None,
            track_info=None,
            format_detected=track_format,
            search_method="artist_title_failed",
            success=False,
            error_message="No matches found for artist-title search"
        )
    
    def _search_general(self, track_string: str, track_format: TrackFormat) -> TrackSearchResult:
        """Fallback general search."""
        tracks = self.spotify.search_track(track_string, limit=1)
        if tracks:
            return TrackSearchResult(
                original_query=track_string,
                track_id=tracks[0]['id'],
                track_info=tracks[0],
                format_detected=track_format,
                search_method="general_search",
                success=True
            )
        
        return TrackSearchResult(
            original_query=track_string,
            track_id=None,
            track_info=None,
            format_detected=track_format,
            search_method="general_search_failed",
            success=False,
            error_message="No matches found in general search"
        )
    
    def _find_best_match(self, tracks: List[Dict[str, Any]], target_artist: str, 
                        target_title: str) -> Optional[Dict[str, Any]]:
        """Find the best matching track from search results."""
        target_artist_lower = target_artist.lower()
        target_title_lower = target_title.lower()
        
        for track in tracks:
            # Check artist match
            track_artists = [artist['name'].lower() for artist in track.get('artists', [])]
            artist_match = any(target_artist_lower in artist or artist in target_artist_lower 
                             for artist in track_artists)
            
            # Check title match
            track_title = track.get('name', '').lower()
            title_match = (target_title_lower in track_title or 
                          track_title in target_title_lower or
                          self._fuzzy_match(target_title_lower, track_title))
            
            if artist_match and title_match:
                return track
        
        # If no perfect match, return first result
        return tracks[0] if tracks else None
    
    def _fuzzy_match(self, str1: str, str2: str, threshold: float = 0.8) -> bool:
        """Simple fuzzy matching based on common words."""
        words1 = set(str1.split())
        words2 = set(str2.split())
        
        if not words1 or not words2:
            return False
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) >= threshold

class PlaylistCreator:
    """Main playlist creation orchestrator."""
    
    def __init__(self, spotify_client: SpotifyClient):
        self.spotify = spotify_client
        self.searcher = TrackSearcher(spotify_client)
    
    def create_from_file(self, playlist_name: str, file_path: str, 
                        public: bool = False) -> Tuple[bool, Optional[str]]:
        """
        Create playlist from a file.
        
        Args:
            playlist_name: Name for the new playlist
            file_path: Path to file containing tracks
            public: Whether playlist should be public
            
        Returns:
            Tuple of (success, playlist_url)
        """
        try:
            # Read tracks from file
            tracks = self._read_tracks_from_file(file_path)
            if not tracks:
                logger.error(f"No tracks found in file: {file_path}")
                return False, None
            
            # Create playlist
            result = self.create_from_tracks(playlist_name, tracks, public)
            
            return result.success, result.playlist_url
            
        except Exception as e:
            logger.error(f"Failed to create playlist from file: {e}")
            return False, None
    
    def create_from_tracks(self, playlist_name: str, track_strings: List[str], 
                          public: bool = False) -> PlaylistCreationResult:
        """
        Create playlist from list of track strings.
        
        Args:
            playlist_name: Name for the new playlist
            track_strings: List of track strings in any supported format
            public: Whether playlist should be public
            
        Returns:
            PlaylistCreationResult with detailed results
        """
        logger.info(f"Creating playlist '{playlist_name}' with {len(track_strings)} tracks")
        
        # Initialize result tracking
        search_results: List[TrackSearchResult] = []
        successful_track_ids: List[str] = []
        failed_tracks: List[str] = []
        
        # Search for all tracks
        for track_string in track_strings:
            if not track_string.strip():
                continue
                
            result = self.searcher.search_track(track_string)
            search_results.append(result)
            
            if result.success and result.track_id:
                successful_track_ids.append(result.track_id)
                logger.debug(f"✓ Found: {track_string}")
            else:
                failed_tracks.append(track_string)
                logger.warning(f"✗ Not found: {track_string}")
        
        # Remove duplicates while preserving order
        unique_track_ids = list(dict.fromkeys(successful_track_ids))
        
        if not unique_track_ids:
            logger.error("No tracks found - cannot create empty playlist")
            return PlaylistCreationResult(
                success=False,
                playlist_id=None,
                playlist_url=None,
                total_tracks_requested=len(track_strings),
                tracks_found=0,
                tracks_added=0,
                failed_tracks=failed_tracks,
                search_results=search_results
            )
        
        try:
            # Create the playlist
            playlist = self.spotify.create_playlist(playlist_name, public=public)
            playlist_id = playlist['id']
            playlist_url = playlist.get('external_urls', {}).get('spotify', '')
            
            # Add tracks to playlist
            success, tracks_added = self.spotify.add_tracks_to_playlist(
                playlist_id, unique_track_ids
            )
            
            logger.info(f"Playlist creation completed: {tracks_added}/{len(unique_track_ids)} tracks added")
            
            return PlaylistCreationResult(
                success=success,
                playlist_id=playlist_id,
                playlist_url=playlist_url,
                total_tracks_requested=len(track_strings),
                tracks_found=len(unique_track_ids),
                tracks_added=tracks_added,
                failed_tracks=failed_tracks,
                search_results=search_results
            )
            
        except SpotifyError as e:
            logger.error(f"Spotify API error during playlist creation: {e}")
            return PlaylistCreationResult(
                success=False,
                playlist_id=None,
                playlist_url=None,
                total_tracks_requested=len(track_strings),
                tracks_found=len(unique_track_ids),
                tracks_added=0,
                failed_tracks=failed_tracks,
                search_results=search_results
            )
    
    def _read_tracks_from_file(self, file_path: str) -> List[str]:
        """Read tracks from a text file."""
        try:
            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            with open(path, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f if line.strip()]
            
            logger.info(f"Read {len(lines)} tracks from {file_path}")
            return lines
            
        except Exception as e:
            logger.error(f"Failed to read tracks from file: {e}")
            raise
    
    def get_creation_summary(self, result: PlaylistCreationResult) -> str:
        """Generate a human-readable summary of playlist creation."""
        if not result.success:
            return f"❌ Playlist creation failed. Found {result.tracks_found}/{result.total_tracks_requested} tracks."
        
        summary_lines = [
            f"✅ Playlist created successfully!",
            f"📊 Statistics:",
            f"   • Total tracks requested: {result.total_tracks_requested}",
            f"   • Tracks found: {result.tracks_found}",
            f"   • Tracks added: {result.tracks_added}",
            f"   • Failed tracks: {len(result.failed_tracks)}"
        ]
        
        if result.playlist_url:
            summary_lines.append(f"🔗 Playlist URL: {result.playlist_url}")
        
        if result.failed_tracks:
            summary_lines.append(f"\n❌ Failed to find:")
            for track in result.failed_tracks[:5]:  # Show max 5 failed tracks
                summary_lines.append(f"   • {track}")
            if len(result.failed_tracks) > 5:
                summary_lines.append(f"   • ... and {len(result.failed_tracks) - 5} more")
        
        return "\n".join(summary_lines)