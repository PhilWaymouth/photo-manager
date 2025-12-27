"""Tests for photo_manager."""

import pytest
from pathlib import Path
from tempfile import TemporaryDirectory

from photo_manager.services.onedrive import OneDriveService
from photo_manager.services import LibraryComparator
from photo_manager.models import Album


class TestOneDriveService:
    """Test OneDrive service."""
    
    def test_initialization_with_valid_path(self):
        """Test initializing with a valid path."""
        with TemporaryDirectory() as tmpdir:
            service = OneDriveService(tmpdir)
            assert service.base_path == Path(tmpdir)
    
    def test_initialization_with_invalid_path(self):
        """Test initializing with an invalid path."""
        with pytest.raises(ValueError):
            OneDriveService("/nonexistent/path")
    
    def test_is_photo_file(self):
        """Test photo file detection."""
        with TemporaryDirectory() as tmpdir:
            service = OneDriveService(tmpdir)
            
            assert service.is_photo_file("image.jpg")
            assert service.is_photo_file("image.JPG")
            assert service.is_photo_file("video.mp4")
            assert service.is_photo_file("video.MOV")
            assert not service.is_photo_file("document.txt")
            assert not service.is_photo_file("document.pdf")
    
    def test_scan_empty_directory(self):
        """Test scanning an empty directory."""
        with TemporaryDirectory() as tmpdir:
            service = OneDriveService(tmpdir)
            albums = service.scan_libraries()
            assert albums == {}
    
    def test_scan_with_albums(self):
        """Test scanning with album directories."""
        with TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)
            
            # Create album directories
            (base_path / "Vacation 2023").mkdir()
            (base_path / "Family").mkdir()
            (base_path / "work").mkdir()
            
            # Create some photo files
            (base_path / "Vacation 2023" / "photo1.jpg").touch()
            (base_path / "Vacation 2023" / "photo2.png").touch()
            (base_path / "Family" / "family.jpg").touch()
            (base_path / "work" / "presentation.pdf").touch()  # Not a photo
            
            service = OneDriveService(base_path)
            albums = service.scan_libraries()
            
            assert len(albums) == 3
            assert albums["Vacation 2023"].item_count == 2
            assert albums["Family"].item_count == 1
            assert albums["work"].item_count == 0


class TestLibraryComparator:
    """Test library comparison."""
    
    def test_similarity_matching(self):
        """Test album name similarity matching."""
        comparator = LibraryComparator(similarity_threshold=0.8)
        
        # High similarity
        assert comparator._similarity("Vacation 2023", "Vacation 2023") == 1.0
        assert comparator._similarity("Family Photos", "Family photos") == 1.0
        
        # Lower similarity
        assert comparator._similarity("Trip", "Travel") > 0.0
    
    def test_match_albums_exact(self):
        """Test exact album matching."""
        comparator = LibraryComparator()
        
        onedrive = {
            "Vacation": Album("1", "Vacation", "onedrive", 5),
            "Family": Album("2", "Family", "onedrive", 10),
        }
        
        google = {
            "Vacation": Album("g1", "Vacation", "google_photos", 5),
            "Family": Album("g2", "Family", "google_photos", 10),
        }
        
        matches = comparator._match_albums(onedrive, google)
        assert matches == {"Vacation": "Vacation", "Family": "Family"}
    
    def test_compare_identical_libraries(self):
        """Test comparing identical libraries."""
        comparator = LibraryComparator()
        
        albums = {
            "Vacation": Album("1", "Vacation", "onedrive", 5),
            "Family": Album("2", "Family", "onedrive", 10),
        }
        
        google = {
            "Vacation": Album("g1", "Vacation", "google_photos", 5),
            "Family": Album("g2", "Family", "google_photos", 10),
        }
        
        result = comparator.compare(albums, google)
        
        assert result.missing_in_google == []
        assert result.missing_in_onedrive == []
        assert result.count_mismatches == {}
    
    def test_compare_with_missing_albums(self):
        """Test comparing libraries with missing albums."""
        comparator = LibraryComparator()
        
        onedrive = {
            "Vacation": Album("1", "Vacation", "onedrive", 5),
            "Family": Album("2", "Family", "onedrive", 10),
        }
        
        google = {
            "Vacation": Album("g1", "Vacation", "google_photos", 5),
        }
        
        result = comparator.compare(onedrive, google)
        
        assert "Family" in result.missing_in_google
        assert result.missing_in_onedrive == []
    
    def test_compare_with_count_mismatch(self):
        """Test comparing libraries with count mismatches."""
        comparator = LibraryComparator()
        
        onedrive = {
            "Vacation": Album("1", "Vacation", "onedrive", 5),
        }
        
        google = {
            "Vacation": Album("g1", "Vacation", "google_photos", 8),
        }
        
        result = comparator.compare(onedrive, google)
        
        assert "Vacation" in result.count_mismatches
        assert result.count_mismatches["Vacation"] == (5, 8)
