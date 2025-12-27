"""OneDrive service for accessing photo libraries."""

import os
from pathlib import Path
from typing import Optional, Dict, List

from photo_manager.models import Album, PhotoItem


class OneDriveService:
    """Service for accessing OneDrive photo libraries via folder structure."""
    
    PHOTO_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.heic', '.mp4', '.mov', '.mkv'}
    
    def __init__(self, base_path: str | Path):
        """Initialize OneDrive service.
        
        Args:
            base_path: Root path to OneDrive photos folder
        """
        self.base_path = Path(base_path)
        if not self.base_path.exists():
            raise ValueError(f"OneDrive path does not exist: {base_path}")
    
    def is_photo_file(self, filename: str) -> bool:
        """Check if a file is likely a photo/video."""
        return Path(filename).suffix.lower() in self.PHOTO_EXTENSIONS
    
    def scan_libraries(self) -> Dict[str, Album]:
        """Scan OneDrive folder structure for photo albums.
        
        Each subdirectory is treated as an album.
        
        Returns:
            Dictionary mapping album names to Album objects
        """
        albums: Dict[str, Album] = {}
        
        if not self.base_path.is_dir():
            return albums
        
        for item in self.base_path.iterdir():
            if not item.is_dir():
                continue
            
            album_name = item.name
            album_id = f"onedrive-{album_name}"
            
            # Count photos in this album
            items = []
            for file_item in item.rglob("*"):
                if file_item.is_file() and self.is_photo_file(file_item.name):
                    try:
                        stat = file_item.stat()
                        photo = PhotoItem(
                            id=str(file_item),
                            name=file_item.name,
                            source="onedrive",
                            album_id=album_id,
                            album_name=album_name,
                            size_bytes=stat.st_size,
                        )
                        items.append(photo)
                    except (OSError, IOError):
                        # Skip files we can't access
                        pass
            
            albums[album_name] = Album(
                id=album_id,
                name=album_name,
                source="onedrive",
                item_count=len(items),
                items=items,
            )
        
        return albums
