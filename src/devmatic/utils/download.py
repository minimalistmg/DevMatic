"""
Download Utilities for DevMatic

Provides async download functionality with progress tracking and hash verification.
"""

import aiohttp
import asyncio
import hashlib
import time
import shutil
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, DownloadColumn, TransferSpeedColumn

from .format import format_size, format_time

console = Console()

def verify_file_hash(file_path: Path, expected_hash: str) -> bool:
    """Verify file integrity using SHA256"""
    if not file_path.exists() or not expected_hash:
        return False
        
    try:
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest() == expected_hash
    except:
        return False

async def download_file_async(url: str, destination: Path, description: str, file_hash: str = None):
    """Download a file asynchronously with multiple connections"""
    try:
        start_time = time.time()
        
        # Check existing file hash
        if destination.exists() and file_hash:
            console.print(f"[yellow]Checking existing file: {destination.name}[/yellow]")
            if verify_file_hash(destination, file_hash):
                file_size = destination.stat().st_size
                console.print(f"[bold green]✓ Using existing {description}[/bold green] [dim]({format_size(file_size)})[/dim]")
                return True
            else:
                console.print(f"[yellow]Existing file is invalid, downloading fresh copy[/yellow]")
                destination.unlink()

        # Delete existing file if it exists
        if destination.exists():
            destination.unlink()
            
        # Constants for optimized download
        CHUNK_SIZE = 1024 * 1024  # 1MB chunks
        MAX_CHUNKS = 8  # Maximum concurrent connections
        
        # Configure TCP connector for better performance
        connector = aiohttp.TCPConnector(
            limit=MAX_CHUNKS,
            force_close=True,
            enable_cleanup_closed=True,
            ssl=False,
            ttl_dns_cache=300,
            use_dns_cache=True,
        )
        
        # Configure client session
        timeout = aiohttp.ClientTimeout(
            total=None,
            connect=60,
            sock_read=30
        )
        
        async with aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={'User-Agent': 'DevMatic/1.0'},
            raise_for_status=True
        ) as session:
            # Get file size
            async with session.head(url) as response:
                total_size = int(response.headers.get('content-length', 0))
                
            if total_size == 0:
                raise ValueError("Could not determine file size")
                
            # Calculate chunk ranges
            chunk_size = max(CHUNK_SIZE, total_size // MAX_CHUNKS)
            chunks = []
            for start in range(0, total_size, chunk_size):
                end = min(start + chunk_size - 1, total_size - 1)
                chunks.append((start, end))
                
            # Progress bar setup
            with Progress(
                SpinnerColumn(),
                TextColumn("[bold blue]{task.description:<20}"),
                TextColumn("[bold green]{task.percentage:>3.1f}% [yellow]({task.elapsed:.1f}s)[/yellow]"),
                BarColumn(bar_width=20),
                DownloadColumn(),
                TransferSpeedColumn(),
                console=console,
                transient=True,
                expand=False,
            ) as progress:
                task = progress.add_task(
                    f"[cyan]Downloading {description[:15]}{'...' if len(description) > 15 else ''}", 
                    total=total_size,
                )
                
                # Create temporary directory for chunks
                temp_dir = destination.parent / f"temp_{destination.stem}"
                if temp_dir.exists():
                    shutil.rmtree(temp_dir)
                temp_dir.mkdir()
                
                temp_files = []
                downloaded = 0
                
                async def download_chunk(chunk_id, start, end):
                    nonlocal downloaded
                    headers = {
                        'Range': f'bytes={start}-{end}',
                        'Accept-Encoding': 'identity'
                    }
                    temp_file = temp_dir / f"part{chunk_id}"
                    temp_files.append(temp_file)
                    
                    async with session.get(url, headers=headers) as response:
                        with open(temp_file, 'wb') as f:
                            async for data in response.content.iter_chunked(65536):
                                f.write(data)
                                downloaded += len(data)
                                progress.update(task, completed=downloaded)
                
                # Download all chunks
                await asyncio.gather(*(download_chunk(i, start, end) 
                                    for i, (start, end) in enumerate(chunks)))
                
                # Verify all chunks exist and have correct size
                expected_sizes = [(end - start + 1) for start, end in chunks]
                actual_sizes = [temp_file.stat().st_size for temp_file in temp_files]
                
                if len(temp_files) != len(chunks) or any(a != e for a, e in zip(actual_sizes, expected_sizes)):
                    raise ValueError("Download chunks are incomplete or corrupted")
                
                # Combine chunks into final file
                with open(destination, 'wb') as outfile:
                    for temp_file in sorted(temp_files, key=lambda x: int(x.stem[4:])):
                        with open(temp_file, 'rb') as infile:
                            shutil.copyfileobj(infile, outfile, length=65536)
                
                # Clean up temp directory
                shutil.rmtree(temp_dir)
                
                # Verify final file size
                if destination.stat().st_size != total_size:
                    raise ValueError("Final file size does not match expected size")
                
                # Verify hash if provided
                if file_hash and not verify_file_hash(destination, file_hash):
                    raise ValueError("File hash verification failed")
                    
        # Show completion stats
        download_time = time.time() - start_time
        file_size = destination.stat().st_size
        console.print(f"[bold green]✓ {description} downloaded successfully![/bold green] [dim]({format_size(file_size)} in {format_time(download_time)})[/dim]")
        return True
        
    except Exception as e:
        console.print(f"[bold red]✗ Error downloading {description}: {str(e)}[/bold red]")
        if destination.exists():
            destination.unlink()
        return False 