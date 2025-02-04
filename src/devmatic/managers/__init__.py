from typing import Dict, Type
from ..core.base.installer import WindowsInstaller

# Registry of available installers
installers: Dict[str, Type[WindowsInstaller]] = {}

def register_installer(name: str):
    """Decorator to register installer classes"""
    def wrapper(cls):
        installers[name] = cls
        return cls
    return wrapper

def get_installer(name: str) -> Type[WindowsInstaller]:
    """Get installer class by name"""
    return installers.get(name) 