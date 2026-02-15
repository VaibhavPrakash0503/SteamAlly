from typing import Dict, List, Optional
from .steam import get_steam_installations, SteamInstallation
from .steam_editor import SteamGameEditor


class SteamManager:
    """High-level interface for Steam operations"""

    def __init__(self):
        """Initialize and load Steam installations once"""
        self._installations: Dict[str, SteamInstallation] = {}
        self._load_installations()

    def _load_installations(self):
        """Private: Load Steam installations at startup"""
        self._installations = get_steam_installations()

    # Query methods
    def get_available_install_types(self) -> List[str]:
        """Returns ['native', 'flatpak', 'snap'] based on what's found"""
        return list(self._installations.keys())

    def get_installation(self, install_type: str) -> Optional[SteamInstallation]:
        """Get specific installation or None"""
        return self._installations.get(install_type)

    # Shortcut operations
    def get_shortcuts(self, install_type: str) -> List[dict]:
        """Get all non-Steam shortcuts for an installation
        Returns list of dicts with keys: id, name, exe, start_dir, etc."""
        installation = self.get_installation(install_type)
        if not installation:
            return []

        return installation.get_non_steam_games()

    def shortcut_prefix(self, install_type: str) -> dict:
        """Get mapping of game names to their Wine prefixes"""
        installation = self.get_installation(install_type)

        return installation.get_game_prefix_mapping() if installation else {}

    # Utility methods
    def get_steam_root(self, install_type: str) -> Optional[str]:
        """Get Steam root path as string"""
        installation = self.get_installation(install_type)
        return str(installation.base_path) if installation else None

    def has_installations(self) -> bool:
        """Check if any Steam installations found"""
        return len(self._installations) > 0

    def get_primary_installation(self) -> Optional[SteamInstallation]:
        """Get the primary Steam installation (native takes priority)"""
        if not self._installations:
            return None

        # Priority order: native > flatpak > snap
        if "native" in self._installations:
            return self._installations["native"]
        elif "flatpak" in self._installations:
            return self._installations["flatpak"]
        elif "snap" in self._installations:
            return self._installations["snap"]

        # Fallback to first available
        return next(iter(self._installations.values()))

    def _get_editor(self, installation_name: Optional[str] = None) -> Optional[SteamGameEditor]:
        """Get editor for specific installation or primary"""
        if installation_name:
            install = self._installations.get(installation_name)
        else:
            install = self.get_primary_installation()

        if not install:
            return None

        return SteamGameEditor(steam_installation=install, status_callback=self._on_editor_status)

    def _on_editor_status(self, message: str):
        """Handle status messages from editor"""
        print(f"[Steam Editor] {message}")

    def update_exe(self, game_name: str, new_exe: str, installation: Optional[str] = None) -> bool:
        """Update exe path for a non Steam Game"""
        editor = self._get_editor(installation)
        if not editor:
            print("No Steam installation avaiable")
            return False

        try:
            editor.update_game_exe(game_name, new_exe)
            return True
        except Exception as e:
            print(f"Error updating game exe: {e}")
            return False

    def update_start_dir(
        self, game_name: str, new_start_dir: str, installation: Optional[str] = None
    ) -> bool:
        """Update start directory for a non Steam Game"""
        editor = self._get_editor(installation)
        if not editor:
            print("No Steam installation avaiable")
            return False

        try:
            editor.update_game_start_dir(game_name, new_start_dir)
            return True
        except Exception as e:
            print(f"Error updating game start dir: {e}")
            return False
