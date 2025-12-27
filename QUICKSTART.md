# Quick Start

## Installation

```bash
# Clone and install
git clone https://github.com/PhilWaymouth/photo-manager.git
cd photo-manager
uv pip install -e .
```

## Google Photos Setup (First Time Only)

1. Download `client_secret.json` from [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Ensure Google Photos Library API is enabled

## Run Comparison

```bash
photo-manager compare \
  --onedrive-path ~/OneDrive/Photos \
  --google-credentials ~/Downloads/client_secret.json \
  --output report.json \
  --verbose
```

## What It Does

✅ Scans your OneDrive folder structure (subfolders = albums)  
✅ Scans your Google Photos albums  
✅ Identifies missing albums in each service  
✅ Detects different photo counts between matching albums  
✅ Generates a JSON report with discrepancies  

## Output

The tool shows:
- Albums missing in Google Photos
- Albums missing in OneDrive
- Albums with different photo counts
- A summary of all discrepancies

## GitHub Repository

https://github.com/PhilWaymouth/photo-manager
