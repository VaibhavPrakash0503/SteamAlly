import gi
from src.core.steam_manager import SteamManager

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib


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

        self.info_label.set_text(
            f"Selected: {self.selected_game['name']}\n"
            f"Steam Type: {self.selected_game['install_type']}\n"
            f"Prefix: {self.selected_game['prefix']}"
        )

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

        # Info label (shows selected game)
        self.info_label = Gtk.Label(label="Select a game from the list")
        self.info_label.set_wrap(True)
        self.info_label.set_margin_top(10)
        self.info_label.set_margin_bottom(20)
        box.append(self.info_label)

        # Change EXE button
        self.exe_button = Gtk.Button(label="Change Game Executable")
        self.exe_button.set_sensitive(False)  # Disabled until game selected
        # self.exe_button.connect("clicked", self.on_change_exe_clicked)
        box.append(self.exe_button)

        # Change Start Dir button
        self.startdir_button = Gtk.Button(label="Change Start Directory")
        self.startdir_button.set_sensitive(False)  # Disabled until game selected
        # self.startdir_button.connect("clicked", self.on_change_startdir_clicked)
        box.append(self.startdir_button)

        return box


def on_activate(app):
    win = MyApp(app)
    win.present()


app = Gtk.Application(application_id="com.steamally.app")
app.connect("activate", on_activate)
app.run(None)
