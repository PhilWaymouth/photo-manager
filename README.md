# Photo Manager

A CLI tool to manage and compare photo libraries stored in OneDrive and Google Photos.

## Features

- Compare photo libraries across OneDrive (folder structure) and Google Photos (albums)
- Identify missing or orphan albums between the two services
- Compare content counts between corresponding albums
- Manage authentication for both services securely

## Installation

```bash
uv pip install -e .
```

Or for development:

```bash
uv pip install -e ".[dev]"
```

## Usage

### Compare Photo Libraries

Compare your OneDrive and Google Photos libraries to identify discrepancies:

```bash
photo-manager compare --onedrive-path ~/OneDrive/Photos --output report.json
```

## Configuration

The tool uses OAuth 2.0 for both OneDrive and Google Photos. Credentials are stored locally in `~/.photo-manager/credentials/` after initial authentication.

## Development

Run tests:

```bash
uv run pytest
```

Format code:

```bash
uv run black .
```

Lint:

```bash
uv run ruff check .
```
