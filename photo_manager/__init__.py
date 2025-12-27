"""Photo Manager - Manage photo libraries across cloud services."""

__version__ = "0.1.0"
__author__ = "Phil"

from photo_manager.models import Album, PhotoItem, LibraryComparison
from photo_manager.auth import GooglePhotosAuth, OneDriveAuth, CredentialManager
from photo_manager.services.onedrive import OneDriveService
from photo_manager.services.google_photos import GooglePhotosService
from photo_manager.services import LibraryComparator

__all__ = [
    "Album",
    "PhotoItem",
    "LibraryComparison",
    "GooglePhotosAuth",
    "OneDriveAuth",
    "CredentialManager",
    "OneDriveService",
    "GooglePhotosService",
    "LibraryComparator",
]
