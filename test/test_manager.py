import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from src.sm.core.steam_manager import SteamManager
from src.sm.core.steam import SteamInstallation


@pytest.fixture
def mock_steam_installation():
    """Create a mock SteamInstallation"""
    mock_install = Mock(spec=SteamInstallation)
    mock_install.base_path = Path("/home/user/.steam")
    mock_install.get_non_steam_games.return_value = [
        {
            "id": 123,
            "name": "Test Game",
            "exe": "/path/to/game.exe",
            "start_dir": "/path/to/game",
        }
    ]
    mock_install.get_game_prefix_mapping.return_value = {"Test Game": "/path/to/prefix"}
    return mock_install


@pytest.fixture
def mock_installations(mock_steam_installation):
    """Mock multiple Steam installations"""
    native_install = Mock(spec=SteamInstallation)
    native_install.base_path = Path("/home/user/.steam")
    native_install.get_non_steam_games.return_value = []
    native_install.get_game_prefix_mapping.return_value = {}

    flatpak_install = Mock(spec=SteamInstallation)
    flatpak_install.base_path = Path("/home/user/.var/app/com.valvesoftware.Steam")
    flatpak_install.get_non_steam_games.return_value = []
    flatpak_install.get_game_prefix_mapping.return_value = {}

    return {
        "native": native_install,
        "flatpak": flatpak_install,
    }


class TestSteamManagerInit:
    """Test SteamManager initialization"""

    @patch("src.sm.core.steam_manager.get_steam_installations")
    def test_init_loads_installations(self, mock_get_installations, mock_installations):
        """Test that __init__ loads installations"""
        mock_get_installations.return_value = mock_installations

        manager = SteamManager()

        mock_get_installations.assert_called_once()
        assert manager._installations == mock_installations

    @patch("src.sm.core.steam_manager.get_steam_installations")
    def test_init_with_no_installations(self, mock_get_installations):
        """Test initialization with no Steam installations found"""
        mock_get_installations.return_value = {}

        manager = SteamManager()

        assert manager._installations == {}
        assert not manager.has_installations()


class TestQueryMethods:
    """Test query methods"""

    @patch("src.sm.core.steam_manager.get_steam_installations")
    def test_get_available_install_types(
        self, mock_get_installations, mock_installations
    ):
        """Test getting available installation types"""
        mock_get_installations.return_value = mock_installations

        manager = SteamManager()
        types = manager.get_available_install_types()

        assert set(types) == {"native", "flatpak"}

    @patch("src.sm.core.steam_manager.get_steam_installations")
    def test_get_installation_existing(
        self, mock_get_installations, mock_installations
    ):
        """Test getting an existing installation"""
        mock_get_installations.return_value = mock_installations

        manager = SteamManager()
        install = manager.get_installation("native")

        assert install == mock_installations["native"]

    @patch("src.sm.core.steam_manager.get_steam_installations")
    def test_get_installation_nonexistent(
        self, mock_get_installations, mock_installations
    ):
        """Test getting a non-existent installation returns None"""
        mock_get_installations.return_value = mock_installations

        manager = SteamManager()
        install = manager.get_installation("snap")

        assert install is None

    @patch("src.sm.core.steam_manager.get_steam_installations")
    def test_has_installations_true(self, mock_get_installations, mock_installations):
        """Test has_installations returns True when installations exist"""
        mock_get_installations.return_value = mock_installations

        manager = SteamManager()

        assert manager.has_installations() is True

    @patch("src.sm.core.steam_manager.get_steam_installations")
    def test_has_installations_false(self, mock_get_installations):
        """Test has_installations returns False when no installations"""
        mock_get_installations.return_value = {}

        manager = SteamManager()

        assert manager.has_installations() is False


class TestPrimaryInstallation:
    """Test primary installation selection"""

    @patch("src.sm.core.steam_manager.get_steam_installations")
    def test_primary_installation_native_priority(
        self, mock_get_installations, mock_installations
    ):
        """Test that native installation has priority"""
        mock_get_installations.return_value = mock_installations

        manager = SteamManager()
        primary = manager.get_primary_installation()

        assert primary == mock_installations["native"]

    @patch("src.sm.core.steam_manager.get_steam_installations")
    def test_primary_installation_flatpak_fallback(self, mock_get_installations):
        """Test flatpak is chosen when native not available"""
        flatpak_only = {"flatpak": Mock(spec=SteamInstallation)}
        mock_get_installations.return_value = flatpak_only

        manager = SteamManager()
        primary = manager.get_primary_installation()

        assert primary == flatpak_only["flatpak"]

    @patch("src.sm.core.steam_manager.get_steam_installations")
    def test_primary_installation_snap_fallback(self, mock_get_installations):
        """Test snap is chosen when native and flatpak not available"""
        snap_only = {"snap": Mock(spec=SteamInstallation)}
        mock_get_installations.return_value = snap_only

        manager = SteamManager()
        primary = manager.get_primary_installation()

        assert primary == snap_only["snap"]

    @patch("src.sm.core.steam_manager.get_steam_installations")
    def test_primary_installation_none(self, mock_get_installations):
        """Test primary installation returns None when no installations"""
        mock_get_installations.return_value = {}

        manager = SteamManager()
        primary = manager.get_primary_installation()

        assert primary is None


class TestShortcutMethods:
    """Test shortcut-related methods"""

    @patch("src.sm.core.steam_manager.get_steam_installations")
    def test_get_shortcuts(self, mock_get_installations, mock_steam_installation):
        """Test getting shortcuts for an installation"""
        mock_get_installations.return_value = {"native": mock_steam_installation}

        manager = SteamManager()
        shortcuts = manager.get_shortcuts("native")

        assert len(shortcuts) == 1
        assert shortcuts[0]["name"] == "Test Game"
        mock_steam_installation.get_non_steam_games.assert_called_once()

    @patch("src.sm.core.steam_manager.get_steam_installations")
    def test_get_shortcuts_nonexistent_install(
        self, mock_get_installations, mock_steam_installation
    ):
        """Test getting shortcuts for non-existent installation returns empty list"""
        mock_get_installations.return_value = {"native": mock_steam_installation}

        manager = SteamManager()
        shortcuts = manager.get_shortcuts("flatpak")

        assert shortcuts == []

    @patch("src.sm.core.steam_manager.get_steam_installations")
    def test_shortcut_prefix(self, mock_get_installations, mock_steam_installation):
        """Test getting shortcut prefix mapping"""
        mock_get_installations.return_value = {"native": mock_steam_installation}

        manager = SteamManager()
        prefixes = manager.shortcut_prefix("native")

        assert prefixes == {"Test Game": "/path/to/prefix"}
        mock_steam_installation.get_game_prefix_mapping.assert_called_once()

    @patch("src.sm.core.steam_manager.get_steam_installations")
    def test_shortcut_prefix_nonexistent_install(
        self, mock_get_installations, mock_steam_installation
    ):
        """Test getting prefix for non-existent installation returns empty dict"""
        mock_get_installations.return_value = {"native": mock_steam_installation}

        manager = SteamManager()
        prefixes = manager.shortcut_prefix("flatpak")

        assert prefixes == {}


class TestUtilityMethods:
    """Test utility methods"""

    @patch("src.sm.core.steam_manager.get_steam_installations")
    def test_get_steam_root(self, mock_get_installations, mock_steam_installation):
        """Test getting Steam root path"""
        mock_get_installations.return_value = {"native": mock_steam_installation}

        manager = SteamManager()
        root = manager.get_steam_root("native")

        assert root == "/home/user/.steam"

    @patch("src.sm.core.steam_manager.get_steam_installations")
    def test_get_steam_root_nonexistent(
        self, mock_get_installations, mock_steam_installation
    ):
        """Test getting Steam root for non-existent installation returns None"""
        mock_get_installations.return_value = {"native": mock_steam_installation}

        manager = SteamManager()
        root = manager.get_steam_root("flatpak")

        assert root is None


class TestEditorOperations:
    """Test editor-related operations"""

    @patch("src.sm.core.steam_manager.SteamGameEditor")
    @patch("src.sm.core.steam_manager.get_steam_installations")
    def test_update_exe_success(
        self, mock_get_installations, mock_editor_class, mock_steam_installation
    ):
        """Test successful exe update"""
        mock_get_installations.return_value = {"native": mock_steam_installation}
        mock_editor = Mock()
        mock_editor_class.return_value = mock_editor

        manager = SteamManager()
        result = manager.update_exe("Test Game", "/new/path/game.exe", "native")

        assert result is True
        mock_editor.update_game_exe.assert_called_once_with(
            "Test Game", "/new/path/game.exe"
        )

    @patch("src.sm.core.steam_manager.SteamGameEditor")
    @patch("src.sm.core.steam_manager.get_steam_installations")
    def test_update_exe_no_installation(
        self, mock_get_installations, mock_editor_class, capsys
    ):
        """Test exe update with no installation available"""
        mock_get_installations.return_value = {}

        manager = SteamManager()
        result = manager.update_exe("Test Game", "/new/path/game.exe")

        assert result is False
        captured = capsys.readouterr()
        assert "No Steam installation avaiable" in captured.out

    @patch("src.sm.core.steam_manager.SteamGameEditor")
    @patch("src.sm.core.steam_manager.get_steam_installations")
    def test_update_exe_error(
        self, mock_get_installations, mock_editor_class, mock_steam_installation, capsys
    ):
        """Test exe update with exception"""
        mock_get_installations.return_value = {"native": mock_steam_installation}
        mock_editor = Mock()
        mock_editor.update_game_exe.side_effect = Exception("Test error")
        mock_editor_class.return_value = mock_editor

        manager = SteamManager()
        result = manager.update_exe("Test Game", "/new/path/game.exe", "native")

        assert result is False
        captured = capsys.readouterr()
        assert "Error updating game exe: Test error" in captured.out

    @patch("src.sm.core.steam_manager.SteamGameEditor")
    @patch("src.sm.core.steam_manager.get_steam_installations")
    def test_update_start_dir_success(
        self, mock_get_installations, mock_editor_class, mock_steam_installation
    ):
        """Test successful start dir update"""
        mock_get_installations.return_value = {"native": mock_steam_installation}
        mock_editor = Mock()
        mock_editor_class.return_value = mock_editor

        manager = SteamManager()
        result = manager.update_start_dir("Test Game", "/new/start/dir", "native")

        assert result is True
        mock_editor.update_game_start_dir.assert_called_once_with(
            "Test Game", "/new/start/dir"
        )

    @patch("src.sm.core.steam_manager.SteamGameEditor")
    @patch("src.sm.core.steam_manager.get_steam_installations")
    def test_update_start_dir_no_installation(
        self, mock_get_installations, mock_editor_class, capsys
    ):
        """Test start dir update with no installation available"""
        mock_get_installations.return_value = {}

        manager = SteamManager()
        result = manager.update_start_dir("Test Game", "/new/start/dir")

        assert result is False
        captured = capsys.readouterr()
        assert "No Steam installation avaiable" in captured.out

    @patch("src.sm.core.steam_manager.SteamGameEditor")
    @patch("src.sm.core.steam_manager.get_steam_installations")
    def test_update_start_dir_error(
        self, mock_get_installations, mock_editor_class, mock_steam_installation, capsys
    ):
        """Test start dir update with exception"""
        mock_get_installations.return_value = {"native": mock_steam_installation}
        mock_editor = Mock()
        mock_editor.update_game_start_dir.side_effect = Exception("Test error")
        mock_editor_class.return_value = mock_editor

        manager = SteamManager()
        result = manager.update_start_dir("Test Game", "/new/start/dir", "native")

        assert result is False
        captured = capsys.readouterr()
        assert "Error updating game start dir: Test error" in captured.out

    @patch("src.sm.core.steam_manager.SteamGameEditor")
    @patch("src.sm.core.steam_manager.get_steam_installations")
    def test_editor_with_primary_installation(
        self, mock_get_installations, mock_editor_class, mock_installations
    ):
        """Test that editor uses primary installation when no specific one provided"""
        mock_get_installations.return_value = mock_installations
        mock_editor = Mock()
        mock_editor_class.return_value = mock_editor

        manager = SteamManager()
        manager.update_exe("Test Game", "/new/path.exe")  # No installation specified

        # Should use native (primary)
        mock_editor_class.assert_called_once()
        call_kwargs = mock_editor_class.call_args[1]
        assert call_kwargs["steam_installation"] == mock_installations["native"]

    @patch("src.sm.core.steam_manager.get_steam_installations")
    def test_on_editor_status(self, mock_get_installations, capsys):
        """Test status callback prints message"""
        mock_get_installations.return_value = {}

        manager = SteamManager()
        manager._on_editor_status("Test status message")

        captured = capsys.readouterr()
        assert "[Steam Editor] Test status message" in captured.out
