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

def create_sdk_files():
    """Create SDK template files"""
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
    return sdk_dir

def build_executable():
    """Build the DevMatic executable"""
    try:
        # Clean previous builds
        clean_build()
        
        # Create SDK files first
        sdk_dir = create_sdk_files()
        
        # Get the path to the spec file in root directory
        script_dir = Path(__file__).parent
        root_dir = script_dir.parent
        spec_file = root_dir / 'devmatic.spec'
        
        if not spec_file.exists():
            print(f"✗ Spec file not found at: {spec_file}")
            return False
            
        print("Building DevMatic executable...")
        # Use spec file for build configuration with correct path
        PyInstaller.__main__.run([str(spec_file), '--clean'])
        
        print("✓ Build completed successfully")
        return True
        
    except Exception as e:
        print(f"✗ Build failed: {str(e)}")
        return False

if __name__ == '__main__':
    sys.exit(0 if build_executable() else 1) 