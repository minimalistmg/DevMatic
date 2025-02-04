import socket
import requests
from typing import Optional, Tuple
import urllib.parse

class NetworkUtils:
    @staticmethod
    def is_port_available(port: int, host: str = 'localhost') -> bool:
        """Check if port is available"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((host, port))
                return True
        except:
            return False

    @staticmethod
    def get_free_port(start_port: int = 8000, host: str = 'localhost') -> Optional[int]:
        """Find next available port"""
        port = start_port
        while port < 65535:
            if NetworkUtils.is_port_available(port, host):
                return port
            port += 1
        return None

    @staticmethod
    def download_file(url: str, destination: Path) -> Tuple[bool, str]:
        """Simple file download"""
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            with open(destination, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return True, ""
        except Exception as e:
            return False, str(e) 