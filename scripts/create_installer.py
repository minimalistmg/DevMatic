import os
import subprocess
from pathlib import Path
import shutil
import sys
import winreg
from typing import List, Dict

class InstallerCreator:
    def __init__(self):
        self.dist_dir = Path('dist')
        self.installer_dir = self.dist_dir / 'installer'
        self.resources_dir = Path('resources')
        self.version = self._get_version()

    def _get_version(self) -> str:
        """Get version from version.txt"""
        with open('version.txt', 'r') as f:
            for line in f:
                if line.startswith('filevers='):
                    vers = line.split('=')[1].strip()
                    return '.'.join(vers.split(',')[:3])
        return "1.0.0"

    def create_installer_dirs(self):
        """Create installer directory structure"""
        # Clean existing
        if self.installer_dir.exists():
            shutil.rmtree(self.installer_dir)
        
        # Create directories
        dirs = [
            self.installer_dir,
            self.installer_dir / 'bin',
            self.installer_dir / 'SDK'
        ]
        
        for dir_path in dirs:
            dir_path.mkdir(parents=True)

    def copy_files(self):
        """Copy required files to installer directory"""
        # Copy executable
        shutil.copy2(
            self.dist_dir / 'devmatic.exe',
            self.installer_dir / 'bin' / 'devmatic.exe'
        )
        
        # Copy SDK template
        shutil.copytree(
            self.dist_dir / 'SDK',
            self.installer_dir / 'SDK',
            dirs_exist_ok=True
        )
        
        # Copy resources
        for resource in ['license.rtf', 'banner.bmp', 'dialog.bmp']:
            if (self.resources_dir / resource).exists():
                shutil.copy2(
                    self.resources_dir / resource,
                    self.installer_dir / resource
                )

    def create_inno_script(self):
        """Create Inno Setup script"""
        script = f"""
#define MyAppName "DevMatic"
#define MyAppVersion "{self.version}"
#define MyAppPublisher "DevMatic"
#define MyAppURL "https://github.com/yourusername/DevMatic"
#define MyAppExeName "devmatic.exe"

[Setup]
AppId={{{{8F7E3F9A-5742-4C38-9D61-5BD8F0C5E64B}}}}
AppName={{#MyAppName}}
AppVersion={{#MyAppVersion}}
AppPublisher={{#MyAppPublisher}}
AppPublisherURL={{#MyAppURL}}
AppSupportURL={{#MyAppURL}}
AppUpdatesURL={{#MyAppURL}}
DefaultDirName={{userappdata}}\\{{#MyAppName}}
DefaultGroupName={{#MyAppName}}
DisableProgramGroupPage=yes
LicenseFile=license.rtf
OutputDir=..
OutputBaseFilename=DevMatic_Setup_v{{#MyAppVersion}}
SetupIconFile=..\\resources\\devmatic.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
WizardImageFile=banner.bmp
WizardSmallImageFile=dialog.bmp
PrivilegesRequired=lowest
UsedUserAreasWarning=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{{cm:CreateDesktopIcon}}"; GroupDescription: "{{cm:AdditionalIcons}}"
Name: "quicklaunchicon"; Description: "{{cm:CreateQuickLaunchIcon}}"; GroupDescription: "{{cm:AdditionalIcons}}"; Flags: unchecked

[Files]
Source: "bin\\{{#MyAppExeName}}"; DestDir: "{{app}}\\bin"; Flags: ignoreversion
Source: "SDK\\*"; DestDir: "{{app}}\\SDK"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{{group}}\\{{#MyAppName}}"; Filename: "{{app}}\\bin\\{{#MyAppExeName}}"
Name: "{{userdesktop}}\\{{#MyAppName}}"; Filename: "{{app}}\\bin\\{{#MyAppExeName}}"; Tasks: desktopicon
Name: "{{userappdata}}\\Microsoft\\Internet Explorer\\Quick Launch\\{{#MyAppName}}"; Filename: "{{app}}\\bin\\{{#MyAppExeName}}"; Tasks: quicklaunchicon

[Run]
Filename: "{{app}}\\bin\\{{#MyAppExeName}}"; Description: "{{cm:LaunchProgram,{{#StringChange(MyAppName, '&', '&&')}}}}"; Flags: nowait postinstall skipifsilent
"""
        
        with open(self.installer_dir / 'setup.iss', 'w') as f:
            f.write(script)

    def build_installer(self):
        """Build installer using Inno Setup"""
        try:
            # Find Inno Setup Compiler
            inno_key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Inno Setup 6_is1"
            )
            inno_path = winreg.QueryValueEx(inno_key, "InstallLocation")[0]
            compiler = Path(inno_path) / "ISCC.exe"
            
            if not compiler.exists():
                print("✗ Inno Setup Compiler not found")
                return False
            
            # Build installer
            result = subprocess.run(
                [str(compiler), str(self.installer_dir / 'setup.iss')],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("✓ Installer created successfully")
                return True
            else:
                print(f"✗ Installer creation failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"✗ Error creating installer: {str(e)}")
            return False

    def create(self):
        """Create the installer"""
        try:
            print("Creating DevMatic installer...")
            self.create_installer_dirs()
            self.copy_files()
            self.create_inno_script()
            return self.build_installer()
        except Exception as e:
            print(f"✗ Installer creation failed: {str(e)}")
            return False

if __name__ == '__main__':
    creator = InstallerCreator()
    sys.exit(0 if creator.create() else 1) 