"""Library comparison logic."""

from typing import Dict
from difflib import SequenceMatcher

from photo_manager.models import Album, LibraryComparison


class LibraryComparator:
    """Compare two photo libraries."""
    
    def __init__(self, similarity_threshold: float = 0.8):
        """Initialize comparator.
        
        Args:
            similarity_threshold: Threshold for fuzzy matching album names (0-1)
        """
        self.similarity_threshold = similarity_threshold
    
    def _similarity(self, a: str, b: str) -> float:
        """Calculate string similarity ratio."""
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()
    
    def _match_albums(self, 
                      onedrive_albums: Dict[str, Album],
                      google_albums: Dict[str, Album]) -> Dict[str, str]:
        """Match albums between services based on name similarity.
        
        Returns:
            Dictionary mapping OneDrive album names to Google Photos album names
        """
        matches = {}
        google_matched = set()
        
        # Sort OneDrive albums for deterministic matching
        for od_name in sorted(onedrive_albums.keys()):
            best_match = None
            best_score = self.similarity_threshold
            
            for gp_name in sorted(google_albums.keys()):
                if gp_name in google_matched:
                    continue
                
                score = self._similarity(od_name, gp_name)
                if score > best_score:
                    best_score = score
                    best_match = gp_name
            
            if best_match:
                matches[od_name] = best_match
                google_matched.add(best_match)
        
        return matches
    
    def compare(self,
                onedrive_albums: Dict[str, Album],
                google_albums: Dict[str, Album]) -> LibraryComparison:
        """Compare two photo libraries.
        
        Args:
            onedrive_albums: Albums from OneDrive
            google_albums: Albums from Google Photos
        
        Returns:
            LibraryComparison object with detailed results
        """
        result = LibraryComparison(
            onedrive_albums=onedrive_albums,
            google_albums=google_albums,
        )
        
        # Match albums between services
        matches = self._match_albums(onedrive_albums, google_albums)
        
        onedrive_names = set(onedrive_albums.keys())
        google_names = set(google_albums.keys())
        matched_od_names = set(matches.keys())
        matched_gp_names = set(matches.values())
        
        # Find missing and orphan albums
        result.missing_in_google = sorted(onedrive_names - matched_od_names)
        result.missing_in_onedrive = sorted(google_names - matched_gp_names)
        result.orphan_in_onedrive = sorted(onedrive_names - matched_od_names)
        result.orphan_in_google = sorted(google_names - matched_gp_names)
        
        # Compare counts for matched albums
        for od_name, gp_name in matches.items():
            od_album = onedrive_albums[od_name]
            gp_album = google_albums[gp_name]
            
            if od_album.item_count != gp_album.item_count:
                result.count_mismatches[od_name] = (
                    od_album.item_count,
                    gp_album.item_count
                )
        
        return result
