import os
import subprocess
import platform
from pathlib import Path
import json
import time
from urllib.parse import quote

def git_installed():
    """Check if git is installed"""
    try:
        subprocess.run(['git', '--version'], capture_output=True, check=True)
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False

def add_to_github_desktop(repo_path):
    """Add a local repository to GitHub Desktop"""
    try:
        system = platform.system()
        
        # Convert to absolute path and normalize slashes
        repo_path = os.path.abspath(repo_path).replace('\\', '/')
        
        if system == "Windows":
            try:
                # Initialize COM
                import pythoncom
                pythoncom.CoInitialize()
                
                # Use protocol handler to add repository
                url = f"x-github-client://openRepo/{repo_path}"
                os.startfile(url)
                
                # Clean up COM
                pythoncom.CoUninitialize()
            except ImportError:
                # Fallback if pythoncom not available
                subprocess.run(['cmd', '/c', 'start', f"x-github-client://openRepo/{repo_path}"], check=True)
        elif system == "Darwin":  # macOS
            url = f"github-desktop://openRepo/{repo_path}"
            subprocess.run(["open", url])
        else:  # Linux
            url = f"github-desktop://openRepo/{repo_path}"
            subprocess.run(["xdg-open", url])
            
        print(f"✓ Opening repository in GitHub Desktop: {repo_path}")
        
        # Wait for GitHub Desktop to process
        time.sleep(2)
        
        # Verify repository is added
        if system == "Windows":
            config_path = os.path.join(os.getenv('APPDATA'), 'GitHub Desktop', '.config', 'repositories.json')
        elif system == "Darwin":
            config_path = os.path.expanduser('~/Library/Application Support/GitHub Desktop/repositories.json')
        else:
            config_path = os.path.expanduser('~/.config/GitHub Desktop/repositories.json')
            
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                repos = json.loads(f.read())
                for repo in repos:
                    if repo.get('path', '').replace('\\', '/') == repo_path:
                        print("✓ Repository successfully added to GitHub Desktop")
                        return True
                        
        print("[yellow]Repository added but not verified in GitHub Desktop[/yellow]")
        return True
        
    except Exception as e:
        print(f"Error adding to GitHub Desktop: {str(e)}")
        return False

def get_github_desktop_folder():
    """Get the default GitHub Desktop repository folder"""
    system = platform.system()
    
    if system == "Windows":
        # Default is Documents/GitHub
        docs_path = os.path.join(os.path.expanduser("~"), "Documents", "GitHub")
    elif system == "Darwin":  # macOS
        docs_path = os.path.join(os.path.expanduser("~"), "Documents", "GitHub")
    else:  # Linux
        docs_path = os.path.join(os.path.expanduser("~"), "Documents", "GitHub")
        
    return docs_path

def sign_in_to_github_desktop():
    """Programmatically sign in to GitHub Desktop"""
    try:
        system = platform.system()
        
        if system == "Windows":
            try:
                # Initialize COM in single-threaded apartment mode
                import pythoncom
                pythoncom.CoInitialize()
                
                # Launch GitHub Desktop with OAuth flow
                url = "x-github-client://oauth/login"
                os.startfile(url)
                
                # Clean up COM
                pythoncom.CoUninitialize()
            except ImportError:
                # Fallback if pythoncom not available
                subprocess.run(['cmd', '/c', 'start', url], check=True)
        elif system == "Darwin":  # macOS
            url = "github-desktop://oauth/login"
            subprocess.run(["open", url])
        else:  # Linux
            url = "github-desktop://oauth/login"
            subprocess.run(["xdg-open", url])
            
        print("✓ Launched GitHub Desktop sign in flow")
        print("Please complete the authentication in your browser")
        
        # Wait for user to complete authentication
        input("Press Enter after signing in...")
        
        # Verify sign in by checking config file
        if system == "Windows":
            config_path = os.path.join(os.getenv('APPDATA'), 'GitHub Desktop', '.config', 'config.json')
        elif system == "Darwin":
            config_path = os.path.expanduser('~/Library/Application Support/GitHub Desktop/config.json')
        else:
            config_path = os.path.expanduser('~/.config/GitHub Desktop/config.json')
            
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.loads(f.read())
                if config.get('accounts', {}).get('github.com'):
                    print("✓ Successfully signed in to GitHub Desktop")
                    return True
                    
        print("[yellow]Could not verify GitHub Desktop sign in[/yellow]")
        return False
        
    except Exception as e:
        print(f"Error signing in to GitHub Desktop: {str(e)}")
        return False

def find_github_desktop():
    """Find GitHub Desktop executable"""
    system = platform.system()
    
    if system == "Windows":
        paths = [
            os.path.join(os.environ.get('LOCALAPPDATA', ''), 'GitHubDesktop', 'GitHubDesktop.exe'),
            os.path.join(os.environ.get('PROGRAMFILES', ''), 'GitHub Desktop', 'GitHubDesktop.exe'),
            os.path.join(os.environ.get('PROGRAMFILES(X86)', ''), 'GitHub Desktop', 'GitHubDesktop.exe'),
        ]
    elif system == "Darwin":
        paths = [
            '/Applications/GitHub Desktop.app/Contents/MacOS/GitHub Desktop',
            os.path.expanduser('~/Applications/GitHub Desktop.app/Contents/MacOS/GitHub Desktop'),
        ]
    else:  # Linux
        paths = [
            '/usr/bin/github-desktop',
            '/usr/local/bin/github-desktop',
            os.path.expanduser('~/.local/bin/github-desktop'),
        ]

    for path in paths:
        if os.path.exists(path):
            return path
    return None

def get_unique_folder_path(base_path):
    """Get a unique folder path by appending _1, _2 etc. if needed"""
    if not os.path.exists(base_path):
        return base_path
        
    counter = 1
    while True:
        new_path = f"{base_path}_{counter}"
        if not os.path.exists(new_path):
            return new_path
        counter += 1

def clone_repository(repo_url, target_path=None):
    """Clone a repository using GitHub Desktop"""
    try:
        # Find GitHub Desktop
        github_desktop = find_github_desktop()
        if not github_desktop:
            print("GitHub Desktop not found. Please ensure it's installed.")
            return False

        # Format repository URL
        if repo_url.endswith('/'):
            repo_url = repo_url[:-1]
        if repo_url.endswith('.git'):
            repo_url = repo_url[:-4]
            
        # Ensure URL starts with https://
        if not repo_url.startswith('https://'):
            repo_url = f'https://github.com/{repo_url}'

        # First open GitHub Desktop
        app_url = "x-github-client://openRepo"
        if platform.system() == "Windows":
            try:
                import pythoncom
                pythoncom.CoInitialize()
                os.startfile(app_url)
                time.sleep(2)  # Wait for GitHub Desktop to open
                
                # Now initiate the clone
                clone_url = f"x-github-client://openRepo/{repo_url}"
                os.startfile(clone_url)
                pythoncom.CoUninitialize()
            except ImportError:
                subprocess.run(['cmd', '/c', 'start', app_url], check=True)
                time.sleep(2)
                subprocess.run(['cmd', '/c', 'start', clone_url], check=True)
        elif platform.system() == "Darwin":
            subprocess.run(["open", app_url])
            time.sleep(2)
            subprocess.run(["open", clone_url])
        else:
            subprocess.run(["xdg-open", app_url])
            time.sleep(2)
            subprocess.run(["xdg-open", clone_url])

        print(f"✓ Opening GitHub Desktop to clone repository")
        print(f"Please complete the clone in GitHub Desktop window")
        
        # Wait for user confirmation
        input("Press Enter after the clone is complete...")
        
        # Verify clone
        if os.path.exists(target_path) and os.path.isdir(target_path):
            try:
                subprocess.run(['git', 'rev-parse', '--git-dir'], 
                             cwd=target_path, 
                             capture_output=True, 
                             check=True)
                print(f"✓ Repository cloned successfully to: {target_path}")
                return True
            except subprocess.CalledProcessError:
                pass
                
        print("[yellow]Could not verify clone completion[/yellow]")
        return False

    except Exception as e:
        print(f"Error cloning repository: {str(e)}")
        return False

# Example usage:
if __name__ == "__main__":    
    clone_repository("https://github.com/minimalistmg/MaticWorkspace.git", "C:/Users/Maruthi Gowda/Documents/GitHub/DevMatic_1")
