"""
Steam Game Editor Module

This module provides functionality to edit Steam VDF files,
specifically for managing non-Steam game shortcuts.
"""

import vdf

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
    ):
        """
        Initialize the Steam Game Editor.

        Args:
            steam_installation: SteamInstallation object
            status_callback: Optional callback function for status updates
        """
        self.steam_installation = steam_installation

    def _update_game(self, game_name: str, updates: dict) -> None:
        """Internal method to update game properties"""
        shortcuts_path = self.steam_installation.shortcuts_path

        if not shortcuts_path or not shortcuts_path.exists():
            raise ShortcutsNotFoundError("shortcuts.vdf not found")

        try:
            with open(shortcuts_path, "rb") as f:
                data = vdf.binary_load(f)

            shortcuts = data.get("shortcuts", {})

            game_found = False
            for shortcut_data in shortcuts.values():
                current_name = shortcut_data.get("AppName")
                if current_name == game_name:
                    shortcut_data.update(updates)
                    game_found = True
                    break

            if not game_found:
                raise GameNotFoundError(
                    f"Game '{game_name}' not found in shortcuts.vdf"
                )

            with open(shortcuts_path, "wb") as f:
                vdf.binary_dump(data, f)

        except (ShortcutsNotFoundError, GameNotFoundError):
            raise
        except Exception as e:
            raise SteamEditorError(f"Error updating shortcuts.vdf: {e}") from e

    def update_game_exe(self, game_name: str, new_exe_path: str) -> None:
        """Update the executable path for a game"""
        self._update_game(game_name, {"Exe": new_exe_path})

    def update_game_start_dir(self, game_name: str, new_start_dir: str) -> None:
        """Update the start directory for a game"""
        self._update_game(game_name, {"StartDir": new_start_dir})
