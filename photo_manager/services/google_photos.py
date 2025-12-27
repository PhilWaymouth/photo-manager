"""Google Photos service for accessing photo libraries."""

from typing import Optional, Dict, List

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from photo_manager.models import Album, PhotoItem


class GooglePhotosService:
    """Service for accessing Google Photos libraries."""
    
    def __init__(self, credentials: Credentials):
        """Initialize Google Photos service.
        
        Args:
            credentials: Authenticated Google OAuth 2.0 credentials
        """
        self.credentials = credentials
        self.service = build("photoslibrary", "v1", credentials=credentials, static_discovery=False)
    
    def scan_libraries(self) -> Dict[str, Album]:
        """Scan Google Photos for albums.
        
        Returns:
            Dictionary mapping album names to Album objects
        """
        albums: Dict[str, Album] = {}
        
        try:
            # Get all shared albums
            results = self.service.sharedAlbums().list(pageSize=50).execute()
            shared_albums = results.get("sharedAlbums", [])
            
            # Get all regular albums
            results = self.service.albums().list(pageSize=50).execute()
            regular_albums = results.get("albums", [])
            
            all_albums = regular_albums + shared_albums
            
            for album in all_albums:
                album_name = album.get("title", "Untitled")
                album_id = album.get("id", "")
                item_count = int(album.get("mediaItemsCount", 0))
                
                # For detailed photo list, we'd need to call searchMediaItems
                # but that's heavier - for now we'll use the count from album metadata
                albums[album_name] = Album(
                    id=f"google-{album_id}",
                    name=album_name,
                    source="google_photos",
                    item_count=item_count,
                    items=[],  # Would need separate API calls to populate
                )
            
            return albums
        
        except Exception as e:
            raise RuntimeError(f"Failed to scan Google Photos: {e}")
    
    def get_album_items(self, album_id: str, limit: Optional[int] = None) -> List[PhotoItem]:
        """Get detailed items in a specific album.
        
        Args:
            album_id: Google Photos album ID
            limit: Maximum number of items to return
        
        Returns:
            List of PhotoItem objects
        """
        items = []
        page_token = None
        fetched = 0
        
        try:
            while True:
                # Search for media items in the album
                request_body = {
                    "albumId": album_id,
                    "pageSize": 100,
                }
                if page_token:
                    request_body["pageToken"] = page_token
                
                results = self.service.mediaItems().search(body=request_body).execute()
                
                media_items = results.get("mediaItems", [])
                if not media_items:
                    break
                
                for media_item in media_items:
                    if limit and fetched >= limit:
                        return items
                    
                    photo = PhotoItem(
                        id=media_item.get("id", ""),
                        name=media_item.get("filename", ""),
                        source="google_photos",
                        album_id=album_id,
                        album_name="",  # Would need to track separately
                    )
                    items.append(photo)
                    fetched += 1
                
                page_token = results.get("nextPageToken")
                if not page_token:
                    break
            
            return items
        
        except Exception as e:
            raise RuntimeError(f"Failed to get album items from Google Photos: {e}")
