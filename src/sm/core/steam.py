from pathlib import Path
from dataclasses import dataclass
import vdf
from dataclasses import field

from .data_manager import SteamCache


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
        cache_key = f"{self.install_type}_active_user_id"

        if self.cache.has_key(cache_key):
            return self.cache.get_cache(cache_key)

        """Get the most recently active Steam user ID"""
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
        user_id = self._get_most_recent_user()
        self.cache.set_cache(cache_key, user_id)
        return user_id

    @property
    def get_shortcuts_path(self) -> Path | None:
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
            print(f"Error parsing loginusers.vdf: {e}")

        return None

    def _get_most_recent_user(self) -> str | None:
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
            print(f"Error parsing shortcuts.vdf: {e}")
            return []

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
                    "start_dir": shortcut_data.get(
                        "StartDir", shortcut_data.get("StartDir", "")
                    ),
                    "launch_options": shortcut_data.get("LaunchOptions", ""),
                    "last_played": shortcut_data.get("LastPlayed", 0),
                }
                games.append(game_info)

            return games

        except Exception as e:
            print(f"Error parsing shortcuts.vdf with vdf library: {e}")
            return []


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
