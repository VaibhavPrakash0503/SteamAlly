"""
Steam Game Editor Module

This module provides functionality to edit Steam VDF files,
specifically for managing non-Steam game shortcuts.
"""

from pathlib import Path
from typing import Callable
import vdf
import re
from typing import Optional
from datetime import datetime, timedelta

from .steam import SteamInstallation


# Custom Exceptions
class SteamEditorError(Exception):
    """Base exception for Steam editor operations"""

    pass


class ShortcutsNotFoundError(SteamEditorError):
    """Raised when shortcuts.vdf file is not found"""

    pass


class GameNotFoundError(SteamEditorError):
    """Raised when a game is not found in shortcuts.vdf"""

    pass


class SteamGameEditor:
    """
    Editor for Steam non-Steam game shortcuts.

    Provides methods to update game properties in shortcuts.vdf
    """

    def __init__(
        self,
        steam_installation: SteamInstallation,
        status_callback: Callable[[str], None] | None = None,
    ):
        """
        Initialize the Steam Game Editor.

        Args:
            steam_installation: SteamInstallation object
            status_callback: Optional callback function for status updates
        """
        self.steam_installation = steam_installation
        self.status_callback = status_callback

    def _notify(self, message: str):
        """
        Send status update to callback or print to console.

        Args:
            message: Status message to send
        """
        if self.status_callback:
            self.status_callback(message)
        else:
            print(message)

    def update_game_exe(self, game_name: str, new_exe_path: str) -> None:
        """
        Update the executable path for a given game in shortcuts.vdf

        Args:
            game_name: Name of the game to update
            new_exe_path: New executable path

        Raises:
            ShortcutsNotFoundError: If shortcuts.vdf doesn't exist
            GameNotFoundError: If game not found in shortcuts
            SteamEditorError: For other errors
        """
        shortcuts_path = self.steam_installation.get_shortcuts_path

        self._notify(f"Loading shortcuts from {shortcuts_path}")

        if not shortcuts_path:
            raise ShortcutsNotFoundError(f"shortcuts.vdf not found at {shortcuts_path}")

        try:
            # Load the shortcuts file
            with open(shortcuts_path, "rb") as f:
                data = vdf.binary_load(f)

            shortcuts = data.get("shortcuts", {})

            # Find and update the game
            game_found = False
            for shortcut_id, shortcut_data in shortcuts.items():
                current_name = shortcut_data.get("AppName")
                if current_name == game_name:
                    shortcut_data["Exe"] = new_exe_path
                    game_found = True
                    self._notify(f"Updated executable for '{game_name}'")
                    break

            if not game_found:
                raise GameNotFoundError(
                    f"Game '{game_name}' not found in shortcuts.vdf"
                )

            # Write back to file
            self._notify("Saving changes to shortcuts.vdf")
            with open(shortcuts_path, "wb") as f:
                vdf.binary_dump(data, f)

            self._notify(f"Successfully updated '{game_name}'")

        except (ShortcutsNotFoundError, GameNotFoundError):
            raise
        except Exception as e:
            raise SteamEditorError(f"Error updating shortcuts.vdf: {e}") from e

    def update_game_start_dir(self, game_name: str, new_start_dir: str) -> None:
        """
        Update the start directory for a given game in shortcuts.vdf

        Args:
            game_name: Name of the game to update
            new_start_dir: New start directory path

        Raises:
            ShortcutsNotFoundError: If shortcuts.vdf doesn't exist
            GameNotFoundError: If game not found in shortcuts
            SteamEditorError: For other errors
        """
        shortcuts_path = self.steam_installation.get_shortcuts_path

        self._notify(f"Loading shortcuts from {shortcuts_path}")

        if not shortcuts_path:
            raise ShortcutsNotFoundError(f"shortcuts.vdf not found at {shortcuts_path}")

        try:
            # Load the shortcuts file
            with open(shortcuts_path, "rb") as f:
                data = vdf.binary_load(f)

            shortcuts = data.get("shortcuts", {})

            # Find and update the game
            game_found = False
            for shortcut_id, shortcut_data in shortcuts.items():
                current_name = shortcut_data.get("AppName")
                if current_name == game_name:
                    shortcut_data["StartDir"] = new_start_dir
                    game_found = True
                    self._notify(f"Updated start directory for '{game_name}'")
                    break

            if not game_found:
                raise GameNotFoundError(
                    f"Game '{game_name}' not found in shortcuts.vdf"
                )

            # Write back to file
            self._notify("Saving changes to shortcuts.vdf")
            with open(shortcuts_path, "wb") as f:
                vdf.binary_dump(data, f)

            self._notify(f"Successfully updated '{game_name}'")

        except (ShortcutsNotFoundError, GameNotFoundError):
            raise
        except Exception as e:
            raise SteamEditorError(f"Error updating shortcuts.vdf: {e}") from e

    def update_game_properties(
        self,
        game_name: str,
        exe_path: str | None = None,
        start_dir: str | None = None,
        launch_options: str | None = None,
    ) -> None:
        """
        Update multiple properties for a game at once.

        Args:
            game_name: Name of the game to update
            exe_path: New executable path (optional)
            start_dir: New start directory (optional)
            launch_options: New launch options (optional)

        Raises:
            ShortcutsNotFoundError: If shortcuts.vdf doesn't exist
            GameNotFoundError: If game not found in shortcuts
            SteamEditorError: For other errors
        """

        shortcuts_path = self.steam_installation.get_shortcuts_path

        self._notify(f"Loading shortcuts from {shortcuts_path}")

        if not shortcuts_path:
            raise ShortcutsNotFoundError(f"shortcuts.vdf not found at {shortcuts_path}")

        try:
            # Load the shortcuts file
            with open(shortcuts_path, "rb") as f:
                data = vdf.binary_load(f)

            shortcuts = data.get("shortcuts", {})

            # Find and update the game
            game_found = False
            for shortcut_id, shortcut_data in shortcuts.items():
                current_name = shortcut_data.get(
                    "AppName", shortcut_data.get("appname", "")
                )
                if current_name == game_name:
                    if exe_path is not None:
                        shortcut_data["Exe"] = exe_path
                        self._notify("Updated executable path")

                    if start_dir is not None:
                        shortcut_data["StartDir"] = start_dir
                        self._notify("Updated start directory")

                    if launch_options is not None:
                        shortcut_data["LaunchOptions"] = launch_options
                        self._notify("Updated launch options")

                    game_found = True
                    break

            if not game_found:
                raise GameNotFoundError(
                    f"Game '{game_name}' not found in shortcuts.vdf"
                )

            # Write back to file
            self._notify("Saving changes to shortcuts.vdf")
            with open(shortcuts_path, "wb") as f:
                vdf.binary_dump(data, f)

            self._notify(f"Successfully updated '{game_name}'")

        except (ShortcutsNotFoundError, GameNotFoundError):
            raise
        except Exception as e:
            raise SteamEditorError(f"Error updating shortcuts.vdf: {e}") from e

    def get_game_prefix_mapping(self) -> dict[str, Optional[Path]]:
        """Get mapping of game names to their Wine prefixes"""
        shortcuts = self.list_shortcuts()
        mapping = {}

        for shortcut in shortcuts:
            game_name = shortcut.get("AppName")
            prefix = self.find_prefix_for_shortcut(shortcut)
            mapping[game_name] = prefix

        return mapping

    def list_shortcuts(self) -> list[dict]:
        """Parse and return all shortcuts from shortcuts.vdf"""
        shortcuts_path = self.steam_installation.get_shortcuts_path
        if not shortcuts_path:
            return []

        # shortcuts.vdf is binary format
        with open(shortcuts_path, "rb") as f:
            shortcuts_data = vdf.binary_load(f)

        # Extract shortcuts list
        shortcuts = shortcuts_data.get("shortcuts", {})
        return list(shortcuts.values()) if shortcuts else []

    def find_prefix_for_shortcut(self, shortcut: dict) -> Optional[str]:
        """Find Wine prefix linked to a Steam shortcut"""

        # Method 1: Check for compatdata reference
        prefix = self._check_compatdata_path(shortcut)
        if prefix:
            return prefix

        # Method 2: Fallback to timestamp matching
        return self._match_by_timestamp(shortcut)

    def _check_compatdata_path(self, shortcut: dict) -> Optional[str]:
        """Extract prefix from compatdata path in shortcut"""

        # Check Exe and StartDir fields
        paths_to_check = [
            shortcut.get("Exe", ""),
            shortcut.get("StartDir", ""),
            shortcut.get("LaunchOptions", ""),
        ]

        compatdata_pattern = r"compatdata/(\d+)"

        for path in paths_to_check:
            match = re.search(compatdata_pattern, str(path))
            if match:
                app_id = match.group(1)
                prefix_path = (
                    self.steam_installation.base_path
                    / "steamapps"
                    / "compatdata"
                    / app_id
                    / "pfx"
                )
                if prefix_path.exists():
                    return app_id

        return None

    def _match_by_timestamp(self, shortcut: dict) -> Optional[str]:
        """Match prefix by comparing last played timestamps"""

        last_played = shortcut.get("LastPlayTime", 0)
        if not last_played:
            return None

        # Convert to datetime for comparison
        shortcut_time = datetime.fromtimestamp(last_played)

        # Find all compatdata prefixes
        compatdata_path = self.steam_installation.base_path / "steamapps" / "compatdata"
        if not compatdata_path.exists():
            return None

        best_match = None
        best_time_diff = None

        # Tolerance window (e.g., within 5 minutes)
        tolerance = timedelta(minutes=1)

        for app_dir in compatdata_path.iterdir():
            if not app_dir.is_dir():
                continue

            lock_file = app_dir / "pfx.lock"

            if not lock_file.exists():
                continue

            try:
                mtime = lock_file.stat().st_mtime  # Use st_mtime like your test
                prefix_time = datetime.fromtimestamp(mtime)

                time_diff = abs((shortcut_time - prefix_time).total_seconds())

                # If within tolerance and better than current best match
                if time_diff <= tolerance.total_seconds():
                    if best_time_diff is None or time_diff < best_time_diff:
                        best_match = app_dir.name
                        best_time_diff = time_diff
            except OSError:
                continue

        return best_match
