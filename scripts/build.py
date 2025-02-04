import PyInstaller.__main__
import shutil
from pathlib import Path
import os
import sys
import json

def clean_build():
    """Clean build directories"""
    dirs_to_clean = ['build', 'dist']
    for dir_name in dirs_to_clean:
        if Path(dir_name).exists():
            shutil.rmtree(dir_name)
    print("✓ Cleaned build directories")

def copy_sdk_files():
    """Copy SDK template files"""
    sdk_dir = Path('dist/SDK')
    sdk_dir.mkdir(parents=True, exist_ok=True)
    
    # Create directory structure
    (sdk_dir / 'tools').mkdir(exist_ok=True)
    (sdk_dir / 'temp').mkdir(exist_ok=True)
    
    # Create empty sdk.env
    with open(sdk_dir / 'sdk.env', 'w') as f:
        f.write("# DevMatic SDK Environment Variables\n")
        f.write("# This file is auto-generated - DO NOT EDIT MANUALLY\n\n")
        f.write(f"SDK_ROOT={sdk_dir.absolute()}\n")
    
    # Create empty sdk.json
    with open(sdk_dir / 'sdk.json', 'w') as f:
        json.dump([], f, indent=2)
    
    print("✓ Created SDK directory structure")

def build_executable():
    """Build the DevMatic executable"""
    try:
        # Clean previous builds
        clean_build()
        
        # Build arguments
        build_args = [
            'src/devmatic/cli/main.py',
            '--name=devmatic',
            '--onefile',
            '--console',
            '--clean',
            '--add-data=SDK;SDK',
            '--icon=resources/devmatic.ico',
            # Add version info
            '--version-file=version.txt',
            # Add manifest for Windows
            '--manifest=resources/devmatic.manifest',
            # Optimize
            '--noupx',
            '--strip'
        ]
        
        print("Building DevMatic executable...")
        PyInstaller.__main__.run(build_args)
        
        # Copy SDK files
        copy_sdk_files()
        
        print("✓ Build completed successfully")
        return True
        
    except Exception as e:
        print(f"✗ Build failed: {str(e)}")
        return False

if __name__ == '__main__':
    sys.exit(0 if build_executable() else 1) 