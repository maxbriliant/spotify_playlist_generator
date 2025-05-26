"""
Track Search Algorithms - Advanced search strategies for finding tracks
=====================================================================
Version: 2.0.0
Author: MaxBriliant

Implements multiple search strategies and algorithms for finding tracks on Spotify
with high accuracy and fuzzy matching capabilities.
"""

import re
import logging
from typing import List, Dict, Any, Optional, Tuple, Set
from dataclasses import dataclass
from enum import Enum
import difflib

logger = logging.getLogger(__name__)

class SearchStrategy(Enum):
    """Available search strategies."""
    EXACT_MATCH = "exact_match"
    FUZZY_MATCH = "fuzzy_match"  
    CLEANED_SEARCH = "cleaned_search"
    PARTIAL_MATCH = "partial_match"
    PHONETIC_MATCH = "phonetic_match"

@dataclass
class SearchResult:
    """Result of a track search."""
    track_id: str
    confidence: float  # 0.0 to 1.0
    strategy_used: SearchStrategy
    match_details: Dict[str, Any]

class TrackSearchEngine:
    """Advanced track search engine with multiple strategies."""
    
    def __init__(self, spotify_client):
        self.spotify = spotify_client
        self.cache = {}  # Simple in-memory cache
        
    def search_track(self, artist: str, title: str, max_results: int = 5) -> List[SearchResult]:
        """
        Search for a track using multiple strategies.
        
        Args:
            artist: Artist name
            title: Track title
            max_results: Maximum number of results to return
            
        Returns:
            List of SearchResult objects, sorted by confidence
        """
        cache_key = f"{artist.lower()}_{title.lower()}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        all_results = []
        
        # Strategy 1: Exact match with quotes
        exact_results = self._exact_match_search(artist, title)
        all_results.extend(exact_results)
        
        # Strategy 2: Fuzzy matching
        if len(all_results) < max_results:
            fuzzy_results = self._fuzzy_match_search(artist, title)
            all_results.extend(fuzzy_results)
        
        # Strategy 3: Cleaned search (remove special chars)
        if len(all_results) < max_results:
            cleaned_results = self._cleaned_search(artist, title)
            all_results.extend(cleaned_results)
        
        # Strategy 4: Partial matching
        if len(all_results) < max_results:
            partial_results = self._partial_match_search(artist, title)
            all_results.extend(partial_results)
        
        # Remove duplicates and sort by confidence
        unique_results = self._deduplicate_results(all_results)
        sorted_results = sorted(unique_results, key=lambda x: x.confidence, reverse=True)
        
        # Cache results
        final_results = sorted_results[:max_results]
        self.cache[cache_key] = final_results
        
        return final_results
    
    def _exact_match_search(self, artist: str, title: str) -> List[SearchResult]:
        """Search using exact quoted strings."""
        try:
            query = f'track:"{title}" artist:"{artist}"'
            tracks = self.spotify.search_track(query, limit=3)
            
            results = []
            for track in tracks:
                confidence = self._calculate_exact_confidence(track, artist, title)
                if confidence > 0.8:  # High threshold for exact matches
                    results.append(SearchResult(
                        track_id=track['id'],
                        confidence=confidence,
                        strategy_used=SearchStrategy.EXACT_MATCH,
                        match_details={
                            'query': query,
                            'track_name': track.get('name', ''),
                            'artists': [a['name'] for a in track.get('artists', [])]
                        }
                    ))
            
            return results
            
        except Exception as e:
            logger.debug(f"Exact match search failed: {e}")
            return []
    
    def _fuzzy_match_search(self, artist: str, title: str) -> List[SearchResult]:
        """Search using fuzzy string matching."""
        try:
            # Try broader search first
            query = f"{artist} {title}"
            tracks = self.spotify.search_track(query, limit=10)
            
            results = []
            for track in tracks:
                confidence = self._calculate_fuzzy_confidence(track, artist, title)
                if confidence > 0.6:  # Lower threshold for fuzzy matches
                    results.append(SearchResult(
                        track_id=track['id'],
                        confidence=confidence,
                        strategy_used=SearchStrategy.FUZZY_MATCH,
                        match_details={
                            'query': query,
                            'track_name': track.get('name', ''),
                            'artists': [a['name'] for a in track.get('artists', [])],
                            'fuzzy_scores': self._get_fuzzy_scores(track, artist, title)
                        }
                    ))
            
            return results
            
        except Exception as e:
            logger.debug(f"Fuzzy match search failed: {e}")
            return []
    
    def _cleaned_search(self, artist: str, title: str) -> List[SearchResult]:
        """Search using cleaned strings (remove special characters)."""
        try:
            clean_artist = self._clean_string(artist)
            clean_title = self._clean_string(title)
            
            query = f"{clean_artist} {clean_title}"
            tracks = self.spotify.search_track(query, limit=5)
            
            results = []
            for track in tracks:
                confidence = self._calculate_cleaned_confidence(track, clean_artist, clean_title)
                if confidence > 0.5:
                    results.append(SearchResult(
                        track_id=track['id'],
                        confidence=confidence,
                        strategy_used=SearchStrategy.CLEANED_SEARCH,
                        match_details={
                            'query': query,
                            'original_artist': artist,
                            'original_title': title,
                            'cleaned_artist': clean_artist,
                            'cleaned_title': clean_title,
                            'track_name': track.get('name', ''),
                            'artists': [a['name'] for a in track.get('artists', [])]
                        }
                    ))
            
            return results
            
        except Exception as e:
            logger.debug(f"Cleaned search failed: {e}")
            return []
    
    def _partial_match_search(self, artist: str, title: str) -> List[SearchResult]:
        """Search using partial matching of words."""
        try:
            # Extract key words
            artist_words = self._extract_keywords(artist)
            title_words = self._extract_keywords(title)
            
            # Try different combinations
            queries = []
            if artist_words and title_words:
                queries.append(f"{artist_words[0]} {title_words[0]}")
                if len(title_words) > 1:
                    queries.append(f"{artist_words[0]} {' '.join(title_words[:2])}")
            
            results = []
            for query in queries:
                try:
                    tracks = self.spotify.search_track(query, limit=3)
                    for track in tracks:
                        confidence = self._calculate_partial_confidence(track, artist, title)
                        if confidence > 0.4:
                            results.append(SearchResult(
                                track_id=track['id'],
                                confidence=confidence,
                                strategy_used=SearchStrategy.PARTIAL_MATCH,
                                match_details={
                                    'query': query,
                                    'artist_keywords': artist_words,
                                    'title_keywords': title_words,
                                    'track_name': track.get('name', ''),
                                    'artists': [a['name'] for a in track.get('artists', [])]
                                }
                            ))
                except Exception:
                    continue
            
            return results
            
        except Exception as e:
            logger.debug(f"Partial match search failed: {e}")
            return []
    
    def _calculate_exact_confidence(self, track: Dict[str, Any], artist: str, title: str) -> float:
        """Calculate confidence for exact matches."""
        track_name = track.get('name', '').lower()
        track_artists = [a['name'].lower() for a in track.get('artists', [])]
        
        title_match = title.lower() == track_name
        artist_match = any(artist.lower() == ta for ta in track_artists)
        
        if title_match and artist_match:
            return 1.0
        elif title_match and any(artist.lower() in ta or ta in artist.lower() for ta in track_artists):
            return 0.9
        elif artist_match and title.lower() in track_name:
            return 0.85
        else:
            return 0.0
    
    def _calculate_fuzzy_confidence(self, track: Dict[str, Any], artist: str, title: str) -> float:
        """Calculate confidence using fuzzy string matching."""
        track_name = track.get('name', '').lower()
        track_artists = [a['name'].lower() for a in track.get('artists', [])]
        
        # Calculate similarity ratios
        title_ratio = difflib.SequenceMatcher(None, title.lower(), track_name).ratio()
        
        artist_ratios = []
        for track_artist in track_artists:
            ratio = difflib.SequenceMatcher(None, artist.lower(), track_artist).ratio()
            artist_ratios.append(ratio)
        
        best_artist_ratio = max(artist_ratios) if artist_ratios else 0.0
        
        # Weighted combination
        confidence = (title_ratio * 0.6) + (best_artist_ratio * 0.4)
        
        return confidence
    
    def _calculate_cleaned_confidence(self, track: Dict[str, Any], clean_artist: str, clean_title: str) -> float:
        """Calculate confidence for cleaned searches."""
        track_name = self._clean_string(track.get('name', ''))
        track_artists = [self._clean_string(a['name']) for a in track.get('artists', [])]
        
        title_match = clean_title.lower() in track_name.lower() or track_name.lower() in clean_title.lower()
        artist_match = any(clean_artist.lower() in ta.lower() or ta.lower() in clean_artist.lower() 
                          for ta in track_artists)
        
        if title_match and artist_match:
            return 0.8
        elif title_match or artist_match:
            return 0.6
        else:
            return 0.0
    
    def _calculate_partial_confidence(self, track: Dict[str, Any], artist: str, title: str) -> float:
        """Calculate confidence for partial matches."""
        track_name = track.get('name', '').lower()
        track_artists = [a['name'].lower() for a in track.get('artists', [])]
        
        artist_words = set(self._extract_keywords(artist.lower()))
        title_words = set(self._extract_keywords(title.lower()))
        
        track_name_words = set(self._extract_keywords(track_name))
        track_artist_words = set()
        for ta in track_artists:
            track_artist_words.update(self._extract_keywords(ta))
        
        # Calculate word overlap
        title_overlap = len(title_words.intersection(track_name_words)) / max(len(title_words), 1)
        artist_overlap = len(artist_words.intersection(track_artist_words)) / max(len(artist_words), 1)
        
        confidence = (title_overlap * 0.6) + (artist_overlap * 0.4)
        
        return confidence
    
    def _get_fuzzy_scores(self, track: Dict[str, Any], artist: str, title: str) -> Dict[str, float]:
        """Get detailed fuzzy matching scores."""
        track_name = track.get('name', '').lower()
        track_artists = [a['name'].lower() for a in track.get('artists', [])]
        
        title_score = difflib.SequenceMatcher(None, title.lower(), track_name).ratio()
        artist_scores = [
            difflib.SequenceMatcher(None, artist.lower(), ta).ratio() 
            for ta in track_artists
        ]
        
        return {
            'title_score': title_score,
            'artist_scores': artist_scores,
            'best_artist_score': max(artist_scores) if artist_scores else 0.0
        }
    
    def _clean_string(self, text: str) -> str:
        """Clean string by removing special characters and extra spaces."""
        # Remove special characters but keep spaces and alphanumeric
        cleaned = re.sub(r'[^\w\s]', ' ', text)
        # Remove extra spaces
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        return cleaned
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract meaningful keywords from text."""
        # Common stop words to ignore
        stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'feat', 'ft'}
        
        words = self._clean_string(text.lower()).split()
        keywords = [word for word in words if word not in stop_words and len(word) > 1]
        
        return keywords
    
    def _deduplicate_results(self, results: List[SearchResult]) -> List[SearchResult]:
        """Remove duplicate results, keeping the one with highest confidence."""
        seen_ids = {}
        unique_results = []
        
        for result in results:
            if result.track_id not in seen_ids:
                seen_ids[result.track_id] = result
                unique_results.append(result)
            else:
                # Keep the result with higher confidence
                if result.confidence > seen_ids[result.track_id].confidence:
                    # Replace in the list
                    for i, ur in enumerate(unique_results):
                        if ur.track_id == result.track_id:
                            unique_results[i] = result
                            break
                    seen_ids[result.track_id] = result
        
        return unique_results
    
    def clear_cache(self):
        """Clear the search cache."""
        self.cache.clear()
        logger.debug("Search cache cleared")
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics."""
        return {
            'cache_size': len(self.cache),
            'cache_hit_rate': getattr(self, '_cache_hits', 0) / max(getattr(self, '_cache_requests', 1), 1)
        }