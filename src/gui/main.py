import gi
from src.core.steam_manager import SteamManager
from pathlib import Path
import os

os.environ["GTK_USE_PORTAL"] = "0"

gi.require_version("Gtk", "4.0")
gi.require_version("Gio", "2.0")
from gi.repository import Gtk, Gio


class MyApp(Gtk.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app, title="Steam Ally")

        self.set_default_size(850, 600)

        header = Gtk.HeaderBar()
        header.set_show_title_buttons(True)
        self.set_titlebar(header)

        self.steam_manager = SteamManager()

        main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)

        # LEFT SIDE - Game List
        left_panel = self.create_left_panel()
        left_panel.set_size_request(400, -1)  # Fixed width 400px
        main_box.append(left_panel)
        # Separator line between left and right
        separator = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
        main_box.append(separator)

        # RIGHT SIDE - Options
        right_panel = self.create_right_panel()
        right_panel.set_hexpand(True)  # Takes remaining space
        main_box.append(right_panel)

        self.set_child(main_box)

    def create_left_panel(self):
        """Left side - Games list"""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)

        # Header label
        header_label = Gtk.Label(label="Games")
        header_label.add_css_class("title-2")
        header_label.set_margin_top(12)
        header_label.set_margin_bottom(12)
        box.append(header_label)

        # Scrollable list of games
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)

        games_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        games_container.set_margin_top(12)
        games_container.set_margin_bottom(12)
        games_container.set_margin_start(12)
        games_container.set_margin_end(12)

        install_types = self.steam_manager.get_available_install_types()
        if not install_types:
            no_steam_label = Gtk.Label(label="No Steam installations found.")
            no_steam_label.set_margin_top(20)
            games_container.append(no_steam_label)
        else:
            for install_type in install_types:
                games_prefix = self.steam_manager.shortcut_prefix(install_type)
                if not games_prefix:
                    continue

                # Section label for this installation type
                section_label = Gtk.Label(label=install_type.capitalize())
                section_label.add_css_class("title-3")
                section_label.set_xalign(0)
                section_label.set_margin_top(12)
                games_container.append(section_label)

                # ListBox for games in this installation
                games_list = Gtk.ListBox()
                games_list.set_selection_mode(Gtk.SelectionMode.SINGLE)
                games_list.connect("row-selected", self.on_game_selected)

                for game_name, prefix in games_prefix.items():
                    row = Gtk.ListBoxRow()

                    # create a vertical box to stack game name and prefix
                    row_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
                    row_box.set_margin_top(8)
                    row_box.set_margin_bottom(8)
                    row_box.set_margin_start(12)
                    row_box.set_margin_end(12)

                    # Game name label
                    name_label = Gtk.Label(label=game_name)
                    name_label.set_xalign(0)  # Left align
                    name_label.add_css_class("heading")  # Makes it stand out
                    row_box.append(name_label)

                    # Prefix label (smaller/italic)
                    prefix_label = Gtk.Label(label=prefix)
                    prefix_label.set_xalign(0)  # Left align
                    prefix_label.add_css_class("dim-label")  # Dimmed style
                    row_box.append(prefix_label)

                    row.set_child(row_box)
                    row.game_data = {
                        "name": game_name,
                        "install_type": install_type,
                        "prefix": prefix,
                    }
                    games_list.append(row)

                games_container.append(games_list)

        # put the container inside scrolled
        scrolled.set_child(games_container)
        box.append(scrolled)

        return box

    def on_game_selected(self, listbox, row):
        if row is None:
            self.exe_button.set_sensitive(False)
            self.startdir_button.set_sensitive(False)
            self.info_label.set_text("Select a game from the list")
            return

        self.selected_game = row.game_data

        self.exe_button.set_sensitive(True)
        self.startdir_button.set_sensitive(True)

    def create_right_panel(self):
        """right side - options"""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_top(20)
        box.set_margin_bottom(20)
        box.set_margin_start(20)
        box.set_margin_end(20)

        # Title
        title = Gtk.Label(label="Options")
        title.add_css_class("title-2")
        box.append(title)

        # Change EXE button
        self.exe_button = Gtk.Button(label="Change Game Executable")
        self.exe_button.set_sensitive(False)  # Disabled until game selected
        self.exe_button.connect("clicked", self.on_change_exe_clicked)
        box.append(self.exe_button)

        # Change Start Dir button
        self.startdir_button = Gtk.Button(label="Change Start Directory")
        self.startdir_button.set_sensitive(False)  # Disabled until game selected
        self.startdir_button.connect("clicked", self.on_change_startdir_clicked)
        box.append(self.startdir_button)

        return box

    def get_base_path(self, install_type):
        """Get base path for given installation type"""
        match install_type:
            case "native":
                return Path.home() / ".local/share/Steam/steamapps/compatdata"
            case "flatpak":
                return (
                    Path.home()
                    / ".var/app/com.valvesoftware.Steam/data/Steam/steamapps/compatdata"
                )
            case "snap":
                return (
                    Path.home()
                    / "snap/steam/current/.local/share/Steam/steamapps/compatdata"
                )
            case _:
                raise ValueError(f"Unknown installation type: {install_type}")

    def on_change_exe_clicked(self, button):
        """Change game executable path"""

        base_path = self.get_base_path(self.selected_game["install_type"])

        initial_folder = Gio.File.new_for_path(
            str(base_path / self.selected_game["prefix"] / "pfx/drive_c")
        )

        dialog = Gtk.FileDialog.new()
        dialog.set_title("Select Game Executable")
        dialog.set_initial_folder(initial_folder)

        # Filter for .exe files
        filter_exe = Gtk.FileFilter()
        filter_exe.set_name(".exe")
        filter_exe.add_pattern("*.exe")

        filters = Gio.ListStore.new(Gtk.FileFilter)
        filters.append(filter_exe)
        dialog.set_filters(filters)

        dialog.open(self, None, self.on_exe_selected)

    def on_exe_selected(self, dialog, result):
        """Handle selected exe file"""
        try:
            file = dialog.open_finish(result)
            path = file.get_path()

            exe_parent_dir = Path(path).parent

            # Call your backend to update
            self.steam_manager.update_exe(
                game_name=self.selected_game["name"],
                new_exe=path,
                installation=self.selected_game["install_type"],
            )

            self.steam_manager.update_start_dir(
                game_name=self.selected_game["name"],
                new_start_dir=str(exe_parent_dir),
                installation=self.selected_game["install_type"],
            )

            self.show_success_dialog(
                "Update Successful",
                f"Successfully updated {self.selected_game['name']}\n\n"
                f"New EXE: {path}\n"
                f"New Start Dir: {exe_parent_dir}",
            )

        except Exception as e:
            if "Dismissed by user" in str(e):
                return

            # Show error dialog
            self.show_error_dialog(
                "Update Failed", f"Failed to update start directory\n\nError: {str(e)}"
            )

    def on_change_startdir_clicked(self, button):
        """Change start directory"""
        base_path = self.get_base_path(self.selected_game["install_type"])

        initial_folder = Gio.File.new_for_path(str(base_path))

        dialog = Gtk.FileDialog.new()
        dialog.set_title("Select Start Directory")
        dialog.set_initial_folder(initial_folder)

        dialog.select_folder(self, None, self.on_startdir_selected)

    def on_startdir_selected(self, dialog, result):
        """Handle selected directory"""
        try:
            folder = dialog.select_folder_finish(result)
            path = folder.get_path()

            # Call your backend to update
            self.steam_manager.update_start_dir(
                game_name=self.selected_game["name"],
                new_start_dir=path,
                installation=self.selected_game["install_type"],
            )

            print(f"Updated Start Dir for {self.selected_game['name']} to {path}")

            self.show_success_dialog(
                "Update Successful",
                f"Successfully updated start directory for {self.selected_game['name']}\n\n"
                f"New Start Dir: {path}",
            )

        except Exception as e:
            if "Dismissed by user" in str(e):
                return

            self.show_error_dialog(
                "Update Failed", f"Failed to update start directory\n\nError: {str(e)}"
            )

    def show_success_dialog(self, title, message):
        """Show success dialog to user"""
        dialog = Gtk.AlertDialog()
        dialog.set_message(title)
        dialog.set_detail(message)
        dialog.set_modal(True)
        dialog.show(self)

    def show_error_dialog(self, title, message):
        """Show error dialog to user"""
        dialog = Gtk.AlertDialog()
        dialog.set_message(title)
        dialog.set_detail(message)
        dialog.set_modal(True)
        dialog.show(self)


def on_activate(app):
    win = MyApp(app)
    win.present()


def main():
    app = Gtk.Application(application_id="com.steamally.app")
    app.connect("activate", on_activate)
    app.run(None)


if __name__ == "__main__":
    main()
