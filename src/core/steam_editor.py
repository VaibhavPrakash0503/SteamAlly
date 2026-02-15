"""
Steam Game Editor Module

This module provides functionality to edit Steam VDF files,
specifically for managing non-Steam game shortcuts.
"""

from typing import Callable
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
