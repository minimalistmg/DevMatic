import os
import subprocess
import platform
import json
from pathlib import Path
from rich.console import Console
import time
import shutil
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

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

def find_postgres():
    """Find PostgreSQL executables using sdk.env"""
    env_vars = load_sdk_env()
    pg_home = env_vars.get('POSTGRESQL_HOME')
    
    if not pg_home:
        console.print("[red]PostgreSQL path not found in sdk.env[/red]")
        return None
        
    pg_home = Path(pg_home)
    if platform.system() == "Windows":
        pg_bin = pg_home / "bin"
        return {
            'psql': pg_bin / "psql.exe",
            'initdb': pg_bin / "initdb.exe",
            'pg_ctl': pg_bin / "pg_ctl.exe"
        }
    else:
        pg_bin = pg_home / "bin"
        return {
            'psql': pg_bin / "psql",
            'initdb': pg_bin / "initdb",
            'pg_ctl': pg_bin / "pg_ctl"
        }

def init_postgres_db(data_dir=None, port=5432):
    """Initialize PostgreSQL database"""
    try:
        pg_bins = find_postgres()
        if not pg_bins:
            return False
            
        # Use default data directory if not specified
        if not data_dir:
            env_vars = load_sdk_env()
            pg_home = env_vars.get('POSTGRESQL_HOME')
            data_dir = Path(pg_home) / "data"
            
        data_dir = Path(data_dir)
        
        # Create data directory if it doesn't exist
        data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize database cluster
        console.print(f"Initializing PostgreSQL database cluster in {data_dir}...")
        result = subprocess.run(
            [str(pg_bins['initdb']), "-D", str(data_dir), "-U", "postgres", "-E", "UTF8", "--locale=C"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            console.print(f"[red]Error initializing database: {result.stderr}[/red]")
            return False
            
        # Modify postgresql.conf
        conf_file = data_dir / "postgresql.conf"
        with open(conf_file, 'a') as f:
            f.write(f"\nport = {port}\nlisten_addresses = '*'\n")
            
        # Modify pg_hba.conf for local connections
        hba_file = data_dir / "pg_hba.conf"
        with open(hba_file, 'w') as f:
            f.write("""
# TYPE  DATABASE        USER            ADDRESS                 METHOD
local   all            all                                     trust
host    all            all             127.0.0.1/32           trust
host    all            all             ::1/128                 trust
""")
            
        console.print("[green]✓ PostgreSQL database cluster initialized[/green]")
        return True
        
    except Exception as e:
        console.print(f"[red]Error initializing PostgreSQL: {str(e)}[/red]")
        return False

def start_postgres(data_dir=None, port=5432):
    """Start PostgreSQL server"""
    try:
        pg_bins = find_postgres()
        if not pg_bins:
            return False
            
        if not data_dir:
            env_vars = load_sdk_env()
            pg_home = env_vars.get('POSTGRESQL_HOME')
            data_dir = Path(pg_home) / "data"
            
        # Start the server
        console.print("Starting PostgreSQL server...")
        result = subprocess.run(
            [str(pg_bins['pg_ctl']), "-D", str(data_dir), "-l", str(data_dir / "logfile"), "start"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            console.print(f"[red]Error starting server: {result.stderr}[/red]")
            return False
            
        # Wait for server to start
        time.sleep(3)
        console.print("[green]✓ PostgreSQL server started[/green]")
        return True
        
    except Exception as e:
        console.print(f"[red]Error starting PostgreSQL: {str(e)}[/red]")
        return False

def create_test_db(dbname="testdb", user="postgres", password=None):
    """Create a test database"""
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            host="localhost",
            user=user,
            password=password if password else ""
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        # Create database
        with conn.cursor() as cur:
            # Check if database exists
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (dbname,))
            if not cur.fetchone():
                cur.execute(f"CREATE DATABASE {dbname}")
                console.print(f"[green]✓ Created database: {dbname}[/green]")
            else:
                console.print(f"[yellow]Database already exists: {dbname}[/yellow]")
                
            # Create a test table
            test_conn = psycopg2.connect(
                host="localhost",
                database=dbname,
                user=user,
                password=password if password else ""
            )
            with test_conn.cursor() as test_cur:
                test_cur.execute("""
                    CREATE TABLE IF NOT EXISTS test_table (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(100),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                test_conn.commit()
                console.print("[green]✓ Created test table[/green]")
                
        return True
        
    except Exception as e:
        console.print(f"[red]Error creating test database: {str(e)}[/red]")
        return False
    finally:
        if 'conn' in locals():
            conn.close()
        if 'test_conn' in locals():
            test_conn.close()

def stop_postgres(data_dir=None):
    """Stop PostgreSQL server"""
    try:
        pg_bins = find_postgres()
        if not pg_bins:
            return False
            
        if not data_dir:
            env_vars = load_sdk_env()
            pg_home = env_vars.get('POSTGRESQL_HOME')
            data_dir = Path(pg_home) / "data"
            
        # Stop the server
        console.print("Stopping PostgreSQL server...")
        result = subprocess.run(
            [str(pg_bins['pg_ctl']), "-D", str(data_dir), "stop"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            console.print(f"[red]Error stopping server: {result.stderr}[/red]")
            return False
            
        console.print("[green]✓ PostgreSQL server stopped[/green]")
        return True
        
    except Exception as e:
        console.print(f"[red]Error stopping PostgreSQL: {str(e)}[/red]")
        return False

# Example usage:
if __name__ == "__main__":
    # Initialize and start PostgreSQL
    if init_postgres_db():
        if start_postgres():
            # Create test database
            create_test_db("testdb")
            
            # Stop server when done
            stop_postgres() 