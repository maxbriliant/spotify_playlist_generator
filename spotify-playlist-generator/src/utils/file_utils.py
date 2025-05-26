"""
File Utilities - Helper functions for file operations
===================================================
Version: 2.0.0
Author: MaxBriliant

Provides utilities for reading playlist files and handling different formats.
"""

import os
from pathlib import Path
from typing import List, Optional, Union
import logging

logger = logging.getLogger(__name__)

def read_playlist_file(file_path: Union[str, Path]) -> List[str]:
    """
    Read playlist file and return list of track strings.
    
    Args:
        file_path: Path to the playlist file
        
    Returns:
        List of track strings (empty lines and comments filtered out)
        
    Raises:
        FileNotFoundError: If file doesn't exist
        UnicodeDecodeError: If file encoding is not supported
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"Playlist file not found: {file_path}")
    
    if not file_path.is_file():
        raise ValueError(f"Path is not a file: {file_path}")
    
    encodings = ['utf-8', 'utf-8-sig', 'latin1', 'cp1252']
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                lines = [
                    line.strip() 
                    for line in f 
                    if line.strip() and not line.strip().startswith('#')
                ]
            
            logger.info(f"Successfully read {len(lines)} tracks from {file_path}")
            return lines
            
        except UnicodeDecodeError:
            continue
        except Exception as e:
            logger.error(f"Error reading file with {encoding}: {e}")
            continue
    
    raise UnicodeDecodeError(f"Could not decode file {file_path} with any supported encoding")

def validate_playlist_file(file_path: Union[str, Path]) -> tuple[bool, Optional[str]]:
    """
    Validate if a file can be used as a playlist file.
    
    Args:
        file_path: Path to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        file_path = Path(file_path)
        
        if not file_path.exists():
            return False, "File does not exist"
        
        if not file_path.is_file():
            return False, "Path is not a file"
        
        if file_path.stat().st_size == 0:
            return False, "File is empty"
        
        if file_path.stat().st_size > 10 * 1024 * 1024:  # 10MB limit
            return False, "File is too large (max 10MB)"
        
        # Try to read a few lines
        try:
            tracks = read_playlist_file(file_path)
            if not tracks:
                return False, "No valid tracks found in file"
            
            if len(tracks) > 10000:
                return False, "Too many tracks (max 10,000 per playlist)"
                
        except Exception as e:
            return False, f"Could not read file: {str(e)}"
        
        return True, None
        
    except Exception as e:
        return False, f"Validation error: {str(e)}"

def create_sample_playlist(file_path: Union[str, Path]) -> bool:
    """
    Create a sample playlist file with example tracks.
    
    Args:
        file_path: Path where to create the sample file
        
    Returns:
        True if successful, False otherwise
    """
    sample_content = """# Sample Spotify Playlist
# Format: Artist - Song Title

# Synthwave/Retrowave
The Midnight - Sunset
Timecop1983 - On the Run
FM‑84 feat. Ollie Wride - Running in the Night
Kavinsky - Nightcall
Carpenter Brut - Turbo Killer

# Classic Rock
Queen - Bohemian Rhapsody
Led Zeppelin - Stairway to Heaven
Pink Floyd - Wish You Were Here
The Beatles - Hey Jude
AC/DC - Back in Black

# Modern Pop
Dua Lipa - Levitating
The Weeknd - Blinding Lights
Billie Eilish - bad guy
Harry Styles - As It Was
Olivia Rodrigo - good 4 u

# Alternative formats (also supported):
# https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh
# spotify:track:4iV5W9uYEdYUVa79Axb7Rh
# 4iV5W9uYEdYUVa79Axb7Rh
"""
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(sample_content)
        logger.info(f"Created sample playlist: {file_path}")
        return True
    except Exception as e:
        logger.error(f"Could not create sample playlist: {e}")
        return False

def backup_file(file_path: Union[str, Path], backup_dir: Optional[Union[str, Path]] = None) -> Optional[Path]:
    """
    Create a backup copy of a file.
    
    Args:
        file_path: File to backup
        backup_dir: Directory for backup (default: same directory as original)
        
    Returns:
        Path to backup file if successful, None otherwise
    """
    try:
        file_path = Path(file_path)
        
        if not file_path.exists():
            return None
        
        if backup_dir:
            backup_dir = Path(backup_dir)
            backup_dir.mkdir(parents=True, exist_ok=True)
        else:
            backup_dir = file_path.parent
        
        # Create backup filename with timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{file_path.stem}_backup_{timestamp}{file_path.suffix}"
        backup_path = backup_dir / backup_name
        
        # Copy file
        import shutil
        shutil.copy2(file_path, backup_path)
        
        logger.info(f"Created backup: {backup_path}")
        return backup_path
        
    except Exception as e:
        logger.error(f"Could not create backup: {e}")
        return None

def get_recent_files(max_files: int = 5) -> List[Path]:
    """
    Get list of recently accessed playlist files.
    
    Args:
        max_files: Maximum number of files to return
        
    Returns:
        List of Path objects for recent files that still exist
    """
    # This would typically read from a config file or registry
    # For now, just return files from current directory
    try:
        current_dir = Path.cwd()
        txt_files = list(current_dir.glob("*.txt"))
        
        # Sort by modification time (most recent first)
        txt_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        
        # Filter out files that don't exist or are too old
        recent_files = []
        for file_path in txt_files[:max_files]:
            if file_path.exists() and validate_playlist_file(file_path)[0]:
                recent_files.append(file_path)
        
        return recent_files
        
    except Exception as e:
        logger.error(f"Could not get recent files: {e}")
        return []

def ensure_directory(dir_path: Union[str, Path]) -> bool:
    """
    Ensure a directory exists, create if necessary.
    
    Args:
        dir_path: Directory path to ensure
        
    Returns:
        True if directory exists or was created successfully
    """
    try:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Could not create directory {dir_path}: {e}")
        return False