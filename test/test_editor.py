#!/usr/bin/env python3
from pathlib import Path
from src.core.steam import get_steam_installations
from src.core.steam_editor import SteamGameEditor


def test_editor():
    """Test SteamGameEditor functionality."""

    # Find Steam install
    steam_path = Path.home() / ".local" / "share" / "Steam"
    if not (steam_path / "userdata").exists():
        print("❌ Steam not found, skipping test")
        return

    steam_ver = get_steam_installations()

    # Create SteamInstallation (you need to implement this minimally)

    # Test editor

    editor = SteamGameEditor(steam_ver["native"], print)
    maps = steam_ver["native"].get_game_prefix_mapping()

    print("\n=== Game to Prefix Mapping ===")
    for game_name, prefix_id in maps.items():
        if prefix_id:
            print(f"{game_name} -> {prefix_id}")
        else:
            print(f"{game_name} -> No prefix found")
    print(f"\nTotal games: {len(maps)}")


if __name__ == "__main__":
    test_editor()
