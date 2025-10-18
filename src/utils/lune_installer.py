import platform
import urllib.request
import json
import zipfile
import tarfile
import stat
import ssl
from pathlib import Path
from typing import Optional, Tuple


class LuneInstaller:
    GITHUB_API_URL = "https://api.github.com/repos/lune-org/lune/releases/latest"
    
    def __init__(self, install_dir: Path):
        self.install_dir = install_dir
        self.lune_path = install_dir / ("lune.exe" if platform.system() == "Windows" else "lune")
    
    def is_installed(self) -> bool:
        return self.lune_path.exists() and self.lune_path.is_file()
    
    def get_platform_info(self) -> Tuple[str, str]:
        system = platform.system()
        machine = platform.machine().lower()
        
        if system == "Windows":
            if machine in ("amd64", "x86_64"):
                return "windows", "x86_64"
            elif machine in ("arm64", "aarch64"):
                return "windows", "aarch64"
        elif system == "Linux":
            if machine in ("amd64", "x86_64"):
                return "linux", "x86_64"
            elif machine in ("arm64", "aarch64"):
                return "linux", "aarch64"
        elif system == "Darwin":
            if machine == "x86_64":
                return "macos", "x86_64"
            elif machine in ("arm64", "aarch64"):
                return "macos", "aarch64"
        
        raise Exception(f"Unsupported platform: {system} {machine}")
    
    def get_latest_release(self) -> Tuple[str, str]:
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        with urllib.request.urlopen(self.GITHUB_API_URL, context=context) as response:
            data = json.loads(response.read())
        
        version = data["tag_name"].lstrip("v")
        assets = data["assets"]
        
        os_type, arch = self.get_platform_info()
        
        asset_patterns = {
            ("windows", "x86_64"): "lune-{version}-windows-x86_64.zip",
            ("windows", "aarch64"): "lune-{version}-windows-aarch64.zip",
            ("linux", "x86_64"): "lune-{version}-linux-x86_64.zip",
            ("linux", "aarch64"): "lune-{version}-linux-aarch64.zip",
            ("macos", "x86_64"): "lune-{version}-macos-x86_64.zip",
            ("macos", "aarch64"): "lune-{version}-macos-aarch64.zip",
        }
        
        pattern = asset_patterns.get((os_type, arch))
        if not pattern:
            raise Exception(f"No Lune release found for {os_type} {arch}")
        
        asset_name = pattern.format(version=version)
        
        for asset in assets:
            if asset["name"] == asset_name:
                return asset["browser_download_url"], version
        
        raise Exception(f"Asset {asset_name} not found in release")
    
    def download_and_install(self, progress_callback=None) -> str:
        download_url, version = self.get_latest_release()
        
        if progress_callback:
            progress_callback(f"Downloading Lune v{version}...")
        
        self.install_dir.mkdir(parents=True, exist_ok=True)
        
        zip_path = self.install_dir / "lune.zip"
        
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        req = urllib.request.Request(download_url)
        with urllib.request.urlopen(req, context=context) as response:
            with open(zip_path, 'wb') as f:
                f.write(response.read())
        
        if progress_callback:
            progress_callback("Extracting...")
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(self.install_dir)
        
        zip_path.unlink()
        
        if platform.system() != "Windows":
            self.lune_path.chmod(self.lune_path.stat().st_mode | stat.S_IEXEC)
        
        if progress_callback:
            progress_callback(f"✓ Lune v{version} installed successfully!")
        
        return str(self.lune_path)
