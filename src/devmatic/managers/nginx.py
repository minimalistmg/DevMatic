import os
import subprocess
import platform
import json
from pathlib import Path
from rich.console import Console
import time
import shutil
import ssl
import socket
from OpenSSL import crypto

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

def find_nginx():
    """Find Nginx executable using sdk.env"""
    env_vars = load_sdk_env()
    nginx_home = env_vars.get('NGINX_HOME')
    
    if not nginx_home:
        console.print("[red]Nginx path not found in sdk.env[/red]")
        return None
        
    nginx_path = Path(nginx_home)
    if platform.system() == "Windows":
        return nginx_path / "nginx.exe"
    else:
        return nginx_path / "sbin" / "nginx"

def generate_self_signed_cert(cert_dir):
    """Generate self-signed SSL certificate"""
    try:
        cert_dir = Path(cert_dir)
        cert_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate key
        key = crypto.PKey()
        key.generate_key(crypto.TYPE_RSA, 2048)
        
        # Generate certificate
        cert = crypto.X509()
        cert.get_subject().C = "US"
        cert.get_subject().ST = "State"
        cert.get_subject().L = "City"
        cert.get_subject().O = "Organization"
        cert.get_subject().OU = "Development"
        cert.get_subject().CN = "localhost"
        
        cert.set_serial_number(1000)
        cert.gmtime_adj_notBefore(0)
        cert.gmtime_adj_notAfter(365*24*60*60)  # Valid for one year
        cert.set_issuer(cert.get_subject())
        cert.set_pubkey(key)
        cert.sign(key, 'sha256')
        
        # Save certificate and key
        with open(cert_dir / "server.crt", "wb") as f:
            f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
        with open(cert_dir / "server.key", "wb") as f:
            f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key))
            
        console.print("[green]✓ SSL certificate generated[/green]")
        return True
        
    except Exception as e:
        console.print(f"[red]Error generating SSL certificate: {str(e)}[/red]")
        return False

def configure_nginx(php_enabled=True, django_enabled=True, port=80, ssl_port=443):
    """Configure Nginx with PHP-FPM and Django support"""
    try:
        env_vars = load_sdk_env()
        nginx_home = env_vars.get('NGINX_HOME')
        php_home = env_vars.get('PHP_HOME')
        python_home = env_vars.get('PYTHON_HOME')
        
        if not nginx_home:
            console.print("[red]Nginx path not found in sdk.env[/red]")
            return False
            
        nginx_path = Path(nginx_home)
        conf_dir = nginx_path / "conf"
        ssl_dir = nginx_path / "conf" / "ssl"
        
        # Generate SSL certificate
        if not generate_self_signed_cert(ssl_dir):
            return False
            
        # Create configuration
        nginx_conf = f"""
worker_processes  1;

events {{
    worker_connections  1024;
}}

http {{
    include       mime.types;
    default_type  application/octet-stream;
    sendfile     on;
    keepalive_timeout  65;
    
    # HTTP Server
    server {{
        listen       {port};
        server_name  localhost;
        
        location / {{
            root   html;
            index  index.html index.htm index.php;
        }}
        
        # Redirect HTTP to HTTPS
        return 301 https://$host$request_uri;
    }}
    
    # HTTPS Server
    server {{
        listen       {ssl_port} ssl;
        server_name  localhost;
        
        ssl_certificate      ssl/server.crt;
        ssl_certificate_key  ssl/server.key;
        ssl_protocols       TLSv1.2 TLSv1.3;
        ssl_ciphers         HIGH:!aNULL:!MD5;
        
        location / {{
            root   html;
            index  index.html index.htm index.php;
        }}
"""
        
        # Add PHP configuration if enabled
        if php_enabled and php_home:
            nginx_conf += f"""
        # PHP handling
        location ~ \\.php$ {{
            root           html;
            fastcgi_pass   127.0.0.1:9000;
            fastcgi_index  index.php;
            fastcgi_param  SCRIPT_FILENAME  $document_root$fastcgi_script_name;
            include        fastcgi_params;
        }}
"""
        
        # Add Django configuration if enabled
        if django_enabled and python_home:
            nginx_conf += f"""
        # Django handling
        location /django/ {{
            proxy_pass http://127.0.0.1:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }}
"""
        
        nginx_conf += """
    }
}
"""
        
        # Write configuration
        conf_file = conf_dir / "nginx.conf"
        with open(conf_file, 'w') as f:
            f.write(nginx_conf)
            
        console.print("[green]✓ Nginx configuration created[/green]")
        return True
        
    except Exception as e:
        console.print(f"[red]Error configuring Nginx: {str(e)}[/red]")
        return False

def start_nginx():
    """Start Nginx server"""
    try:
        nginx = find_nginx()
        if not nginx:
            return False
            
        # Test configuration
        result = subprocess.run(
            [str(nginx), '-t'],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            console.print(f"[red]Nginx configuration test failed: {result.stderr}[/red]")
            return False
            
        # Start server
        console.print("Starting Nginx server...")
        result = subprocess.run(
            [str(nginx)],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            console.print(f"[red]Error starting Nginx: {result.stderr}[/red]")
            return False
            
        console.print("[green]✓ Nginx server started[/green]")
        return True
        
    except Exception as e:
        console.print(f"[red]Error starting Nginx: {str(e)}[/red]")
        return False

def stop_nginx():
    """Stop Nginx server"""
    try:
        nginx = find_nginx()
        if not nginx:
            return False
            
        # Stop server
        console.print("Stopping Nginx server...")
        result = subprocess.run(
            [str(nginx), '-s', 'stop'],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            console.print(f"[red]Error stopping Nginx: {result.stderr}[/red]")
            return False
            
        console.print("[green]✓ Nginx server stopped[/green]")
        return True
        
    except Exception as e:
        console.print(f"[red]Error stopping Nginx: {str(e)}[/red]")
        return False

# Example usage:
if __name__ == "__main__":
    # Configure and start Nginx
    if configure_nginx(php_enabled=True, django_enabled=True):
        start_nginx()
        
        # Do some testing here...
        
        # Stop server when done
        stop_nginx() 