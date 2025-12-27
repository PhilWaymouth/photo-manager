# Setup Guide for Photo Manager

## Prerequisites

- Python 3.9 or higher
- `uv` package manager ([install here](https://docs.astral.sh/uv/))
- A Google account with Google Photos
- A Microsoft account with OneDrive

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/PhilWaymouth/photo-manager.git
cd photo-manager
```

### 2. Install Dependencies

Using `uv`:

```bash
# Basic installation
uv pip install -e .

# With development tools (for testing, linting, etc.)
uv pip install -e ".[dev]"
```

## Configuration

### Google Photos Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)

2. Create a new OAuth 2.0 Desktop Application:
   - Click "Create Credentials" → "OAuth client ID"
   - Choose "Desktop application"
   - Download the JSON credentials file

3. Save this file (typically named `client_secret.json`) to a safe location

4. Enable the Google Photos Library API:
   - Search for "Photos Library API" in the console
   - Click "Enable"

### OneDrive Setup

OneDrive uses interactive browser authentication (OAuth 2.0 via Azure AD), so you don't need to pre-configure credentials. Just ensure:

- Your OneDrive Photos folder path is accessible
- You have read permissions on the folder

## Usage

### Basic Comparison

```bash
photo-manager compare \
  --onedrive-path ~/OneDrive/Photos \
  --google-credentials ~/Downloads/client_secret.json \
  --output comparison_report.json \
  --verbose
```

### Options

- `--onedrive-path`: Path to your OneDrive Photos folder (required)
- `--google-credentials`: Path to Google client_secret.json
- `--output`: Optional JSON file to save the comparison report
- `--similarity`: Album name matching threshold (0-1, default: 0.8)
- `--verbose`: Show detailed output during comparison

### Output Example

```
==================================================
COMPARISON RESULTS
==================================================

📈 Summary:
   OneDrive Albums:  12
   Google Albums:    11

❌ Missing in Google Photos (1):
   - Work Events (8 items)

❌ Missing in OneDrive (2):
   - Archived Photos (45 items)
   - Shared Family (23 items)

⚠️  Count Mismatches (3):
   - Vacation 2023: OneDrive=47, Google=45 (diff: -2)
   - Family: OneDrive=123, Google=125 (diff: +2)
```

## Security Notes

### Credentials Storage

- Google credentials are stored in `~/.photo-manager/credentials/google_photos.pickle`
- These files contain OAuth tokens and should be kept private
- Never commit these to version control (they're in `.gitignore`)

### Authorization Scopes

- **Google Photos**: Read-only access to your photo library
- **OneDrive**: Read-only access to your OneDrive files

### Best Practices

1. **Use application-specific credentials**: Create dedicated OAuth apps rather than using existing ones
2. **Monitor permissions**: Review granted permissions in your Google Account and Azure settings
3. **Rotate tokens**: Periodically revoke and re-authenticate
4. **Backup credentials**: Keep a copy of your `.photo-manager/credentials/` directory

## Development

### Running Tests

```bash
uv run pytest
uv run pytest --cov=photo_manager  # With coverage
```

### Code Quality

```bash
# Format code
uv run black photo_manager tests

# Lint
uv run ruff check photo_manager tests

# Type checking
uv run mypy photo_manager
```

## Troubleshooting

### Google Photos Authentication Loop

If authentication keeps failing, try:
1. Remove `~/.photo-manager/credentials/google_photos.pickle`
2. Ensure you downloaded the correct `client_secret.json` from Google Cloud Console
3. Verify the Photos Library API is enabled

### OneDrive Path Not Found

Ensure:
1. The path uses your actual OneDrive location (typically `~/OneDrive` or `~/Microsoft OneDrive`)
2. You have read permissions on the folder
3. The path exists and contains subdirectories (albums)

### Missing Albums in Results

Albums are matched using fuzzy string matching with an 80% similarity threshold. If albums with similar names aren't matching:
1. Rename one or both albums to be more similar
2. Use `--similarity 0.6` to lower the threshold (but may cause false matches)

## Advanced Usage

### Custom Album Matching

The comparison uses fuzzy string matching to align albums across services. The default threshold is 0.8 (80% similarity). Lower this value to match more loosely:

```bash
photo-manager compare \
  --onedrive-path ~/OneDrive/Photos \
  --similarity 0.6
```

### Programmatic Usage

```python
from photo_manager import OneDriveService, GooglePhotosService, LibraryComparator
from photo_manager.auth import GooglePhotosAuth

# Scan OneDrive
onedrive = OneDriveService("~/OneDrive/Photos")
od_albums = onedrive.scan_libraries()

# Authenticate and scan Google Photos
google_auth = GooglePhotosAuth(
    credentials_file="~/Downloads/client_secret.json"
)
creds = google_auth.authenticate()
google = GooglePhotosService(creds)
gp_albums = google.scan_libraries()

# Compare
comparator = LibraryComparator()
result = comparator.compare(od_albums, gp_albums)

# Access results
print(f"Missing in Google: {result.missing_in_google}")
print(f"Count mismatches: {result.count_mismatches}")
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes and add tests
4. Ensure all tests pass
5. Submit a pull request

## License

MIT
