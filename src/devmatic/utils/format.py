"""
Format utilities for DevMatic

Provides functions for formatting time and file sizes.
"""

def format_time(seconds):
    """Format seconds into minutes and seconds"""
    if seconds < 60:
        return f"{int(seconds) if seconds.is_integer() else f'{seconds:.1f}'}s"
    minutes = int(seconds // 60)
    seconds = seconds % 60
    return f"{minutes}m {int(seconds) if seconds.is_integer() else f'{seconds:.1f}'}s"

def format_size(size_bytes):
    """Format bytes into human readable size"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            # Remove .0 if it's a whole number
            size_str = str(int(size_bytes)) if size_bytes.is_integer() else f"{size_bytes:.1f}"
            return f"{size_str} {unit}"
        size_bytes /= 1024
    size_str = str(int(size_bytes)) if size_bytes.is_integer() else f"{size_bytes:.1f}"
    return f"{size_str} GB" 