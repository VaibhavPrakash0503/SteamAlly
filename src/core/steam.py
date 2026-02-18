from pathlib import Path
from dataclasses import dataclass, field
import vdf
from typing import Optional
from datetime import datetime, timedelta
import re

from .data_manager import SteamCache


class VDFParseError(Exception):
    """Raised when VDF parsing fails."""

    pass


class SteamUserError(Exception):
    """No active Steam user found."""

    pass


class ShortcutsNotFoundError(Exception):
    """shortcuts.vdf not found."""

    pass


class LoginUsersParseError(Exception):
    """Error parsing loginusers.vdf."""

    pass


@dataclass
class SteamInstallation:
    install_type: str  # "native", "flatpak", "snap"
    base_path: Path
    cache: SteamCache = field(default_factory=SteamCache)

    @property
    def compatdata(self) -> Path:
        """Wine prefixes location"""
        return self.base_path / "steamapps" / "compatdata"

    @property
    def active_user_id(self) -> str | None:
        """Get the most recently active Steam user ID"""
        cache_key = f"{self.install_type}_active_user_id"

        if self.cache.has_key(cache_key):
            return self.cache.get_cache(cache_key)

        # Try loginusers.vdf first (primary method)
        loginusers = self.base_path / "config" / "loginusers.vdf"

        if loginusers.exists():
            try:
                user_id = self._parse_loginusers_vdf(loginusers)
                if user_id:
                    self.cache.set_cache(cache_key, user_id)
                    return user_id
            except Exception:
                pass  # Fall through to fallback

        # Fallback: most recently modified userdata directory
        user_id = self.most_recent_user
        if not user_id:
            raise SteamUserError("No active Steam user found.")
        self.cache.set_cache(cache_key, user_id)
        return user_id

    @property
    def shortcuts_path(self) -> Path | None:
        cached_key = f"{self.install_type}_shortcuts_path"

        if self.cache.has_key(cached_key):
            return self.cache.get_cache(cached_key)

        user_id = self.active_user_id
        if not user_id:
            return None

        shortcut: Path = (
            self.base_path / "userdata" / user_id / "config" / "shortcuts.vdf"
        )

        self.cache.set_cache(cached_key, shortcut)
        return shortcut

    def _parse_loginusers_vdf(self, vdf_path: Path) -> str | None:
        """Parse loginusers.vdf to find most recent user"""

        try:
            data = vdf.load(open(vdf_path, "r", encoding="utf-8", errors="ignore"))

            user = data.get("users", {})

            for steamid64, user_data in user.items():
                if user_data.get("MostRecent") == "1":
                    steamid3 = str((int(steamid64) - 76561197960265728) & 0xFFFFFFFF)
                    return steamid3
        except Exception as e:
            raise LoginUsersParseError(f"Error parsing loginusers.vdf: {e}")

        return None

    @property
    def most_recent_user(self) -> str | None:
        """Fallback: Get most recently modified user directory"""
        userdata_path = self.base_path / "userdata"

        if not userdata_path.exists():
            return None

        user_dirs = [
            d for d in userdata_path.iterdir() if d.is_dir() and d.name.isdigit()
        ]

        if not user_dirs:
            return None

        # Return directory with most recent modification time
        most_recent = max(user_dirs, key=lambda d: d.stat().st_mtime)
        return most_recent.name

    def get_non_steam_games(self) -> list[dict]:
        """Parse shortcuts.vdf for non-Steam games"""
        user_id = self.active_user_id

        if not user_id:
            return []

        shortcuts_file = (
            self.base_path / "userdata" / user_id / "config" / "shortcuts.vdf"
        )

        if not shortcuts_file.exists():
            return []

        try:
            return self._parse_shortcuts_vdf(shortcuts_file)
        except Exception as e:
            raise ShortcutsNotFoundError(f"Error parsing shortcuts.vdf: {e}")

    def _parse_shortcuts_vdf(self, vdf_path: Path) -> list[dict]:
        """Parse binary shortcuts.vdf file"""
        try:
            data = vdf.binary_load(open(vdf_path, "rb"))

            shortcuts = data.get("shortcuts", {})

            games = []
            for shortcut_id, shortcut_data in shortcuts.items():
                game_info = {
                    "name": shortcut_data.get(
                        "AppName", shortcut_data.get("appname", "Unknown")
                    ),
                    "exe": shortcut_data.get("Exe", shortcut_data.get("exe", "")),
                    "start_dir": shortcut_data.get("StartDir", ""),
                    "launch_options": shortcut_data.get("LaunchOptions", ""),
                    "last_play_time": shortcut_data.get("LastPlayTime", 0),
                }
                games.append(game_info)

            return games

        except Exception as e:
            raise ShortcutsNotFoundError(f"Error parsing shortcuts.vdf: {e}")

    def get_game_prefix_mapping(self) -> dict[str, Optional[Path]]:
        """Get mapping of game names to their Wine prefixes"""
        shortcuts = self.get_list_shortcuts()
        mapping = {}

        for shortcut in shortcuts:
            game_name = shortcut.get("AppName")
            prefix = self.find_prefix_for_shortcut(shortcut)
            mapping[game_name] = prefix

        return mapping

    def get_list_shortcuts(self) -> list[dict]:
        """Parse and return all shortcuts from shortcuts.vdf"""
        shortcuts_path = self.shortcuts_path
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
                    self.base_path / "steamapps" / "compatdata" / app_id / "pfx"
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
        compatdata_path = self.base_path / "steamapps" / "compatdata"
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


def get_steam_installations() -> dict[str, SteamInstallation]:
    """
    This checks for the steam types installed on the system
    by looking for their data directories.
    """
    installations = {}

    flatpak_path = Path("~/.var/app/com.valvesoftware.Steam/data/Steam").expanduser()
    if flatpak_path.exists():
        installations["flatpak"] = SteamInstallation("flatpak", flatpak_path)

    snap_path = Path("~/snap/steam/common/.local/share/Steam").expanduser()
    if snap_path.exists():
        installations["snap"] = SteamInstallation("snap", snap_path)

    native_path = Path("~/.local/share/Steam").expanduser()
    if native_path.exists():
        installations["native"] = SteamInstallation("native", native_path)

    return installations


if __name__ == "__main__":
    steam_installs = get_steam_installations()
    print(f"Available Steam types: {', '.join(steam_installs.keys())}")

    for install_type, installation in steam_installs.items():
        print(f"\n{install_type.upper()} Steam:")
        print(f"  Base path: {installation.base_path}")
        print(f"  Active user: {installation.active_user_id}")

        games = installation.get_non_steam_games()
        print(f"  Non-Steam games found: {len(games)}")
        for game in games[:5]:  # Show first 5
            print(f"    - {game['name']}")
