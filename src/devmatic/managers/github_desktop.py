import os
import subprocess
import platform
import json
import shutil
from pathlib import Path
from rich.console import Console
import base64
import plyvel
import time

console = Console()

def load_sdk_env():
    """Load SDK environment variables from sdk.env"""
    env_file = Path("sdk.env")
    if not env_file.exists():
        console.print("[red]sdk.env file not found[/red]")
        return {}
        
    env_vars = {}
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip()
    return env_vars

def get_github_desktop_db_path():
    """Get GitHub Desktop's database path"""
    system = platform.system()
    
    if system == "Windows":
        base_path = Path(os.environ.get('APPDATA', '')) / "GitHub Desktop"
    elif system == "Darwin":
        base_path = Path.home() / "Library/Application Support/GitHub Desktop"
    else:  # Linux
        base_path = Path.home() / ".config/GitHub Desktop"
        
    # Find IndexedDB directory
    db_path = base_path / "IndexedDB"
    if not db_path.exists():
        console.print(f"[red]GitHub Desktop database not found at {db_path}[/red]")
        return None
        
    # Find LevelDB directory (it has a random name)
    leveldb_dirs = list(db_path.glob("*leveldb"))
    if not leveldb_dirs:
        console.print("[red]LevelDB directory not found[/red]")
        return None
        
    return leveldb_dirs[0]

def setup_ssh_key(email, key_name="github_desktop"):
    """Generate and configure SSH key for GitHub"""
    try:
        # Generate SSH key
        key_path = Path.home() / ".ssh" / f"{key_name}"
        if not key_path.parent.exists():
            key_path.parent.mkdir(parents=True, mode=0o700)
            
        if not key_path.exists():
            console.print(f"Generating SSH key for {email}...")
            subprocess.run([
                'ssh-keygen',
                '-t', 'ed25519',
                '-C', email,
                '-f', str(key_path),
                '-N', ''  # Empty passphrase
            ], check=True)
            
            # Add to SSH config
            config_path = Path.home() / ".ssh" / "config"
            config_content = f"""
Host github.com
    HostName github.com
    User git
    IdentityFile {key_path}
    IdentitiesOnly yes
"""
            with open(config_path, 'a') as f:
                f.write(config_content)
                
            console.print("[green]✓ SSH key generated and configured[/green]")
            
            # Show public key
            with open(f"{key_path}.pub", 'r') as f:
                public_key = f.read().strip()
                console.print("\n[yellow]Add this public key to your GitHub account:[/yellow]")
                console.print(public_key)
                
            return True
    except Exception as e:
        console.print(f"[red]Error setting up SSH key: {str(e)}[/red]")
        return False

def configure_github_desktop(name, email):
    """Configure GitHub Desktop with user details"""
    try:
        config_path = Path(os.environ.get('APPDATA', '')) / "GitHub Desktop" / ".config" / "config.json"
        
        config = {
            "accounts": {
                "github.com": {
                    "name": name,
                    "email": email,
                    "token": "",  # Will be filled by GitHub Desktop OAuth
                    "protocol": "ssh"
                }
            },
            "protocol": "ssh",
            "automaticallySwitchTheme": True,
            "confirmRepositoryRemoval": True
        }
        
        # Ensure directory exists
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
            
        console.print("[green]✓ GitHub Desktop configured successfully[/green]")
        return True
        
    except Exception as e:
        console.print(f"[red]Error configuring GitHub Desktop: {str(e)}[/red]")
        return False

def get_github_desktop_db():
    """Get connection to GitHub Desktop's LevelDB database"""
    db_path = get_github_desktop_db_path()
    if not db_path:
        return None
    
    try:
        # Try to open the database with retry mechanism
        retries = 3
        while retries > 0:
            try:
                return plyvel.DB(str(db_path), create_if_missing=False)
            except plyvel.IOError as e:
                if "lock" in str(e).lower() and retries > 1:
                    console.print("[yellow]Database is locked, retrying...[/yellow]")
                    time.sleep(1)
                    retries -= 1
                else:
                    raise
        return None
    except Exception as e:
        console.print(f"[red]Error opening LevelDB: {str(e)}[/red]")
        return None

def add_repository_to_desktop_db(repo_path, name, url, branch="main"):
    """Add repository to GitHub Desktop's LevelDB database"""
    try:
        db = get_github_desktop_db()
        if not db:
            return False

        # Normalize paths and URLs
        repo_path = str(Path(repo_path).resolve())
        if url.endswith('.git'):
            url = url[:-4]

        # Create repository entry
        repo_data = {
            "path": repo_path,
            "name": name,
            "url": url,
            "gitHubRepository": {
                "cloneUrl": url,
                "defaultBranch": branch,
                "private": False,
                "fork": False
            },
            "missing": False,
            "lastStashCheckDate": None,
            "pruneRemoteInProgress": False,
            "timestamp": int(time.time() * 1000)  # Current time in milliseconds
        }

        # Convert to JSON and encode
        repo_json = json.dumps(repo_data)
        
        try:
            # Add to repositories
            key = f"repositories/{repo_path}".encode('utf-8')
            db.put(key, repo_json.encode('utf-8'))

            # Add to recent repositories
            recent_key = f"recent-repositories/{repo_path}".encode('utf-8')
            db.put(recent_key, repo_json.encode('utf-8'))

            console.print(f"[green]✓ Added repository to GitHub Desktop database: {name}[/green]")
            
            # Also add to repositories.json for compatibility
            add_repository_to_json(repo_path, name, url)
            
            return True

        finally:
            db.close()

    except Exception as e:
        console.print(f"[red]Error adding repository to database: {str(e)}[/red]")
        return False

def add_repository_to_json(repo_path, name, url):
    """Add repository to GitHub Desktop's repositories.json file"""
    try:
        repos_file = Path(os.environ.get('APPDATA', '')) / "GitHub Desktop" / ".config" / "repositories.json"
        
        repos = []
        if repos_file.exists():
            with open(repos_file, 'r') as f:
                repos = json.load(f)
                
        # Create repository entry
        repo_data = {
            "path": str(Path(repo_path).resolve()),
            "name": name,
            "url": url,
            "gitHubRepository": {
                "cloneUrl": url,
                "private": False,
                "fork": False
            }
        }
        
        # Check if already exists
        if not any(r.get('path') == repo_data['path'] for r in repos):
            repos.append(repo_data)
            
            # Ensure directory exists
            repos_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(repos_file, 'w') as f:
                json.dump(repos, f, indent=2)
                
            return True
        return True
            
    except Exception as e:
        console.print(f"[yellow]Warning: Could not update repositories.json: {str(e)}[/yellow]")
        return False

def list_desktop_repositories():
    """List all repositories in GitHub Desktop's database"""
    try:
        db = get_github_desktop_db()
        if not db:
            return

        console.print("\n[bold]GitHub Desktop Repositories:[/bold]")
        try:
            for key, value in db.iterator(prefix=b'repositories/'):
                try:
                    repo_data = json.loads(value.decode('utf-8'))
                    console.print(f"\n[cyan]{repo_data['name']}[/cyan]")
                    console.print(f"  Path: {repo_data['path']}")
                    console.print(f"  URL:  {repo_data['url']}")
                except:
                    continue
        finally:
            db.close()

    except Exception as e:
        console.print(f"[red]Error listing repositories: {str(e)}[/red]")

# Example usage:
if __name__ == "__main__":
    # Setup SSH and configure GitHub Desktop
    email = "your.email@example.com"
    name = "Your Name"
    
    setup_ssh_key(email)
    configure_github_desktop(name, email)
    
    # Add repository to both JSON and LevelDB
    add_repository_to_desktop_db(
        repo_path="C:/Projects/MyRepo",
        name="MyRepo",
        url="https://github.com/username/MyRepo.git",
        branch="main"
    )
    
    # List all repositories
    list_desktop_repositories() 