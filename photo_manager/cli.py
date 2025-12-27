"""Main CLI interface using Click."""

import json
from pathlib import Path
from typing import Optional

import click

from photo_manager.auth import GooglePhotosAuth, CredentialManager
from photo_manager.services.onedrive import OneDriveService
from photo_manager.services.google_photos import GooglePhotosService
from photo_manager.services import LibraryComparator


@click.group()
@click.version_option()
def main():
    """Photo Manager: Manage and compare photo libraries across OneDrive and Google Photos."""
    pass


@main.command()
@click.option(
    "--onedrive-path",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    required=True,
    help="Path to OneDrive Photos folder",
)
@click.option(
    "--google-credentials",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, path_type=Path),
    help="Path to Google client_secret.json (downloaded from Cloud Console)",
)
@click.option(
    "--output",
    type=click.Path(file_okay=True, dir_okay=False, path_type=Path),
    default=None,
    help="Output file for comparison report (JSON)",
)
@click.option(
    "--similarity",
    type=float,
    default=0.8,
    help="Album name similarity threshold for matching (0-1)",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose output",
)
def compare(
    onedrive_path: Path,
    google_credentials: Optional[Path],
    output: Optional[Path],
    similarity: float,
    verbose: bool,
):
    """Compare photo libraries in OneDrive and Google Photos.
    
    This command scans your OneDrive folder structure and Google Photos albums,
    then identifies:
    - Albums missing in one service
    - Albums with different numbers of photos
    - Orphaned albums (only in one service)
    """
    try:
        if verbose:
            click.echo("📷 Photo Manager - Library Comparison")
            click.echo("=" * 50)
        
        # Initialize OneDrive service
        if verbose:
            click.echo(f"\n🔍 Scanning OneDrive at: {onedrive_path}")
        
        onedrive_service = OneDriveService(onedrive_path)
        onedrive_albums = onedrive_service.scan_libraries()
        
        if verbose:
            click.echo(f"   Found {len(onedrive_albums)} albums with {sum(a.item_count for a in onedrive_albums.values())} items total")
        
        # Authenticate with Google Photos
        if verbose:
            click.echo("\n🔐 Authenticating with Google Photos...")
        
        google_auth = GooglePhotosAuth(
            credentials_file=str(google_credentials) if google_credentials else None
        )
        credentials = google_auth.authenticate()
        
        if verbose:
            click.echo("   ✓ Authentication successful")
        
        # Scan Google Photos
        if verbose:
            click.echo("\n🔍 Scanning Google Photos albums...")
        
        google_service = GooglePhotosService(credentials)
        google_albums = google_service.scan_libraries()
        
        if verbose:
            click.echo(f"   Found {len(google_albums)} albums with {sum(a.item_count for a in google_albums.values())} items total")
        
        # Compare libraries
        if verbose:
            click.echo("\n📊 Comparing libraries...")
        
        comparator = LibraryComparator(similarity_threshold=similarity)
        comparison = comparator.compare(onedrive_albums, google_albums)
        
        # Display results
        click.echo("\n" + "=" * 50)
        click.echo("COMPARISON RESULTS")
        click.echo("=" * 50)
        
        summary = comparison.summary()
        click.echo(f"\n📈 Summary:")
        click.echo(f"   OneDrive Albums:  {summary['onedrive_album_count']}")
        click.echo(f"   Google Albums:    {summary['google_album_count']}")
        
        if comparison.missing_in_google:
            click.echo(f"\n❌ Missing in Google Photos ({len(comparison.missing_in_google)}):")
            for album in comparison.missing_in_google:
                count = onedrive_albums[album].item_count
                click.echo(f"   - {album} ({count} items)")
        
        if comparison.missing_in_onedrive:
            click.echo(f"\n❌ Missing in OneDrive ({len(comparison.missing_in_onedrive)}):")
            for album in comparison.missing_in_onedrive:
                count = google_albums[album].item_count
                click.echo(f"   - {album} ({count} items)")
        
        if comparison.count_mismatches:
            click.echo(f"\n⚠️  Count Mismatches ({len(comparison.count_mismatches)}):")
            for album, (od_count, gp_count) in sorted(comparison.count_mismatches.items()):
                diff = gp_count - od_count
                click.echo(f"   - {album}: OneDrive={od_count}, Google={gp_count} (diff: {diff:+d})")
        
        if not comparison.missing_in_google and not comparison.missing_in_onedrive and not comparison.count_mismatches:
            click.echo("\n✨ Libraries are in sync!")
        
        # Save report if requested
        if output:
            if verbose:
                click.echo(f"\n💾 Saving report to: {output}")
            
            report = {
                "summary": summary,
                "missing_in_google": comparison.missing_in_google,
                "missing_in_onedrive": comparison.missing_in_onedrive,
                "count_mismatches": {
                    k: {"onedrive": v[0], "google": v[1]}
                    for k, v in comparison.count_mismatches.items()
                },
                "matched_albums": {
                    k: {
                        "onedrive_count": v.item_count,
                        "google_count": google_albums.get(k, {}).item_count if isinstance(google_albums.get(k), dict) else google_albums.get(v).__dict__.get('item_count', 0) if hasattr(v, 'item_count') else 0
                    }
                    for k, v in onedrive_albums.items()
                    if k not in comparison.missing_in_google
                }
            }
            
            with open(output, "w") as f:
                json.dump(report, f, indent=2, default=str)
            
            if verbose:
                click.echo(f"   ✓ Report saved")
        
        click.echo("\n" + "=" * 50)
    
    except FileNotFoundError as e:
        click.echo(f"❌ Error: {e}", err=True)
        raise click.Exit(1)
    except ValueError as e:
        click.echo(f"❌ Error: {e}", err=True)
        raise click.Exit(1)
    except RuntimeError as e:
        click.echo(f"❌ Error: {e}", err=True)
        raise click.Exit(1)
    except Exception as e:
        click.echo(f"❌ Unexpected error: {e}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        raise click.Exit(1)


@main.command()
@click.option(
    "--path",
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    default=None,
    help="Path to check credentials location",
)
def auth(path: Optional[Path]):
    """Manage authentication credentials.
    
    Displays information about stored credentials and allows re-authentication.
    """
    cred_manager = CredentialManager(path)
    
    click.echo("🔐 Credential Status")
    click.echo("=" * 50)
    click.echo(f"Credentials stored at: {cred_manager.base_path}")
    click.echo()
    
    # Check Google credentials
    google_creds = cred_manager.load_google_credentials()
    if google_creds:
        click.echo("✓ Google Photos credentials found")
        if hasattr(google_creds, 'expiry'):
            click.echo(f"  Expires: {google_creds.expiry}")
    else:
        click.echo("✗ Google Photos credentials not found")
    
    # Check OneDrive credentials
    onedrive_creds = cred_manager.load_onedrive_credentials()
    if onedrive_creds:
        click.echo("✓ OneDrive credentials found")
    else:
        click.echo("✗ OneDrive credentials not found")


if __name__ == "__main__":
    main()
