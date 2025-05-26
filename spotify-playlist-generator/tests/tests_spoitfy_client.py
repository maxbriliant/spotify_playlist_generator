# tests/test_spotify_client.py
"""
Unit tests for Spotify Client
=============================
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.spotify_client import SpotifyClient, SpotifyError, AuthenticationError

class TestSpotifyClient(unittest.TestCase):
    """Test cases for SpotifyClient."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_client_id = "test_client_id"
        self.test_client_secret = "test_client_secret"
        self.test_redirect_uri = "http://127.0.0.1:8888/callback"
    
    def test_init_with_credentials(self):
        """Test client initialization with credentials."""
        client = SpotifyClient(
            client_id=self.test_client_id,
            client_secret=self.test_client_secret,
            redirect_uri=self.test_redirect_uri
        )
        
        self.assertEqual(client.client_id, self.test_client_id)
        self.assertEqual(client.client_secret, self.test_client_secret)
        self.assertEqual(client.redirect_uri, self.test_redirect_uri)
    
    def test_init_without_credentials_raises_error(self):
        """Test that missing credentials raise AuthenticationError."""
        with self.assertRaises(AuthenticationError):
            SpotifyClient(client_id="", client_secret="")
    
    @patch.dict('os.environ', {
        'SPOTIPY_CLIENT_ID': 'env_client_id',
        'SPOTIPY_CLIENT_SECRET': 'env_client_secret'
    })
    def test_init_from_environment(self):
        """Test client initialization from environment variables."""
        client = SpotifyClient()
        
        self.assertEqual(client.client_id, 'env_client_id')
        self.assertEqual(client.client_secret, 'env_client_secret')
    
    @patch('core.spotify_client.spotipy.Spotify')
    @patch('core.spotify_client.SpotifyOAuth')
    def test_authentication_success(self, mock_oauth, mock_spotify):
        """Test successful authentication."""
        # Mock successful authentication
        mock_spotify_instance = MagicMock()
        mock_spotify_instance.me.return_value = {'id': 'test_user', 'display_name': 'Test User'}
        mock_spotify.return_value = mock_spotify_instance
        
        client = SpotifyClient(
            client_id=self.test_client_id,
            client_secret=self.test_client_secret
        )
        
        # Access client property to trigger authentication
        spotify_client = client.client
        
        self.assertIsNotNone(spotify_client)
        self.assertEqual(client.user_id, 'test_user')
    
    def test_search_track(self):
        """Test track search functionality."""
        with patch.object(SpotifyClient, 'client') as mock_client:
            mock_client.search.return_value = {
                'tracks': {
                    'items': [
                        {'id': 'track1', 'name': 'Test Song', 'artists': [{'name': 'Test Artist'}]}
                    ]
                }
            }
            
            client = SpotifyClient(
                client_id=self.test_client_id,
                client_secret=self.test_client_secret
            )
            
            results = client.search_track("test query")
            
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0]['id'], 'track1')

# =====================================

# tests/test_playlist_creator.py
"""
Unit tests for Playlist Creator
==============================
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.playlist_creator import PlaylistCreator, PlaylistCreationResult
from core.spotify_client import SpotifyClient

class TestPlaylistCreator(unittest.TestCase):
    """Test cases for PlaylistCreator."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_spotify_client = Mock(spec=SpotifyClient)
        self.creator = PlaylistCreator(self.mock_spotify_client)
    
    def test_create_from_tracks_success(self):
        """Test successful playlist creation."""
        # Mock spotify client responses
        self.mock_spotify_client.create_playlist.return_value = {
            'id': 'playlist123',
            'external_urls': {'spotify': 'https://open.spotify.com/playlist/playlist123'}
        }
        
        self.mock_spotify_client.add_tracks_to_playlist.return_value = (True, 3)
        
        # Mock searcher to return successful results
        with patch.object(self.creator, 'searcher') as mock_searcher:
            mock_search_result = Mock()
            mock_search_result.success = True
            mock_search_result.track_id = 'track123'
            
            mock_searcher.search_track.return_value = mock_search_result
            
            # Test playlist creation
            track_strings = ['Artist1 - Song1', 'Artist2 - Song2', 'Artist3 - Song3']
            result = self.creator.create_from_tracks('Test Playlist', track_strings)
            
            self.assertTrue(result.success)
            self.assertEqual(result.tracks_found, 3)
            self.assertEqual(result.tracks_added, 3)
    
    def test_create_from_tracks_no_tracks_found(self):
        """Test playlist creation when no tracks are found."""
        # Mock searcher to return no results
        with patch.object(self.creator, 'searcher') as mock_searcher:
            mock_search_result = Mock()
            mock_search_result.success = False
            mock_search_result.track_id = None
            
            mock_searcher.search_track.return_value = mock_search_result
            
            track_strings = ['Nonexistent Artist - Nonexistent Song']
            result = self.creator.create_from_tracks('Test Playlist', track_strings)
            
            self.assertFalse(result.success)
            self.assertEqual(result.tracks_found, 0)
    
    def test_create_from_file(self):
        """Test creating playlist from file."""
        test_file_content = ['Artist1 - Song1', 'Artist2 - Song2']
        
        with patch('core.playlist_creator.read_playlist_file') as mock_read:
            mock_read.return_value = test_file_content
            
            with patch.object(self.creator, 'create_from_tracks') as mock_create:
                mock_result = PlaylistCreationResult(
                    success=True,
                    playlist_id='playlist123',
                    playlist_url='https://open.spotify.com/playlist/playlist123',
                    total_tracks_requested=2,
                    tracks_found=2,
                    tracks_added=2,
                    failed_tracks=[],
                    search_results=[]
                )
                mock_create.return_value = mock_result
                
                success, url = self.creator.create_from_file('Test Playlist', 'test.txt')
                
                self.assertTrue(success)
                self.assertEqual(url, 'https://open.spotify.com/playlist/playlist123')

# =====================================

# tests/test_config.py
"""
Unit tests for Configuration Management
======================================
"""

import unittest
from unittest.mock import patch, mock_open
import sys
from pathlib import Path
import tempfile
import os

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils.config import ConfigManager, SpotifyConfig, UIConfig, AppConfig

class TestConfigManager(unittest.TestCase):
    """Test cases for ConfigManager."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Use temporary directory for tests
        self.temp_dir = Path(tempfile.mkdtemp())
        self.config_manager = ConfigManager(self.temp_dir)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch.dict('os.environ', {
        'SPOTIPY_CLIENT_ID': 'test_client_id',
        'SPOTIPY_CLIENT_SECRET': 'test_client_secret',
        'SPOTIPY_REDIRECT_URI': 'http://test.com/callback'
    })
    def test_get_spotify_config_from_env(self):
        """Test getting Spotify config from environment variables."""
        config = self.config_manager.get_spotify_config()
        
        self.assertEqual(config.client_id, 'test_client_id')
        self.assertEqual(config.client_secret, 'test_client_secret')
        self.assertEqual(config.redirect_uri, 'http://test.com/callback')
    
    def test_get_ui_config_defaults(self):
        """Test getting UI config with default values."""
        config = self.config_manager.get_ui_config()
        
        self.assertEqual(config.theme, 'dark')
        self.assertEqual(config.window_width, 900)
        self.assertEqual(config.window_height, 700)
        self.assertTrue(config.auto_open_playlist)
    
    def test_create_env_template(self):
        """Test creating .env template file."""
        success = self.config_manager.create_env_template()
        
        self.assertTrue(success)
        self.assertTrue(self.config_manager.env_file.exists())
        
        # Check content
        content = self.config_manager.env_file.read_text()
        self.assertIn('SPOTIPY_CLIENT_ID=', content)
        self.assertIn('SPOTIPY_CLIENT_SECRET=', content)
    
    def test_validate_spotify_config(self):
        """Test Spotify config validation."""
        # Test with missing credentials
        is_valid, errors = self.config_manager.validate_spotify_config()
        self.assertFalse(is_valid)
        self.assertTrue(len(errors) > 0)
        
        # Test with placeholder values
        with patch.dict('os.environ', {
            'SPOTIPY_CLIENT_ID': 'your_client_id_here',
            'SPOTIPY_CLIENT_SECRET': 'your_client_secret_here'
        }):
            is_valid, errors = self.config_manager.validate_spotify_config()
            self.assertFalse(is_valid)
            self.assertTrue(any('placeholder' in error for error in errors))

# =====================================

# tests/test_file_utils.py
"""
Unit tests for File Utils
========================
"""

import unittest
import tempfile
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils.file_utils import read_playlist_file, validate_playlist_file, create_sample_playlist

class TestFileUtils(unittest.TestCase):
    """Test cases for file utilities."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_read_playlist_file_success(self):
        """Test successful playlist file reading."""
        test_content = """Artist1 - Song1
        Artist2 - Song2
        # This is a comment
        
        Artist3 - Song3"""
        
        test_file = self.temp_dir / "test_playlist.txt"
        test_file.write_text(test_content)
        
        tracks = read_playlist_file(test_file)
        
        self.assertEqual(len(tracks), 3)
        self.assertEqual(tracks[0], "Artist1 - Song1")
        self.assertEqual(tracks[1], "Artist2 - Song2")
        self.assertEqual(tracks[2], "Artist3 - Song3")
    
    def test_read_playlist_file_not_found(self):
        """Test reading non-existent file."""
        with self.assertRaises(FileNotFoundError):
            read_playlist_file("nonexistent_file.txt")
    
    def test_validate_playlist_file_valid(self):
        """Test validation of valid playlist file."""
        test_file = self.temp_dir / "valid_playlist.txt"
        test_file.write_text("Artist - Song\nAnotherArtist - AnotherSong")
        
        is_valid, error = validate_playlist_file(test_file)
        
        self.assertTrue(is_valid)
        self.assertIsNone(error)
    
    def test_validate_playlist_file_empty(self):
        """Test validation of empty file."""
        test_file = self.temp_dir / "empty_playlist.txt"
        test_file.write_text("")
        
        is_valid, error = validate_playlist_file(test_file)
        
        self.assertFalse(is_valid)
        self.assertIn("empty", error.lower())
    
    def test_create_sample_playlist(self):
        """Test creating sample playlist file."""
        sample_file = self.temp_dir / "sample_playlist.txt"
        
        success = create_sample_playlist(sample_file)
        
        self.assertTrue(success)
        self.assertTrue(sample_file.exists())
        
        # Check content
        content = sample_file.read_text()
        self.assertIn("The Midnight - Sunset", content)
        self.assertIn("Queen - Bohemian Rhapsody", content)

if __name__ == '__main__':
    unittest.main()