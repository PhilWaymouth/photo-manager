"""Data models for photo library management."""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class PhotoItem:
    """Represents a single photo or media item."""
    
    id: str
    name: str
    source: str  # "onedrive" or "google_photos"
    album_id: str
    album_name: str
    created_at: Optional[datetime] = None
    size_bytes: Optional[int] = None
    mime_type: Optional[str] = None


@dataclass
class Album:
    """Represents an album/collection in a photo library."""
    
    id: str
    name: str
    source: str  # "onedrive" or "google_photos"
    item_count: int = 0
    items: list[PhotoItem] = field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class LibraryComparison:
    """Results of comparing two photo libraries."""
    
    onedrive_albums: dict[str, Album] = field(default_factory=dict)
    google_albums: dict[str, Album] = field(default_factory=dict)
    
    # Discrepancies
    missing_in_onedrive: list[str] = field(default_factory=list)  # Album names
    missing_in_google: list[str] = field(default_factory=list)    # Album names
    orphan_in_onedrive: list[str] = field(default_factory=list)   # Album names
    orphan_in_google: list[str] = field(default_factory=list)     # Album names
    
    # Count mismatches: {album_name: (onedrive_count, google_count)}
    count_mismatches: dict[str, tuple[int, int]] = field(default_factory=dict)
    
    comparison_timestamp: datetime = field(default_factory=datetime.now)
    
    def summary(self) -> dict:
        """Return a summary of the comparison."""
        return {
            "onedrive_album_count": len(self.onedrive_albums),
            "google_album_count": len(self.google_albums),
            "missing_in_onedrive": len(self.missing_in_onedrive),
            "missing_in_google": len(self.missing_in_google),
            "orphan_in_onedrive": len(self.orphan_in_onedrive),
            "orphan_in_google": len(self.orphan_in_google),
            "count_mismatches": len(self.count_mismatches),
            "comparison_timestamp": self.comparison_timestamp.isoformat(),
        }
