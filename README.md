# SteamAlly

A non-Steam game manager for Linux that simplifies the management of game prefixes and properties.

## Description

SteamAlly solves the tedious problem of manually finding and linking prefix folders for non-Steam games on Linux. It provides an intuitive GUI interface to manage your gaming library without the hassle of manual configuration.

## Features

- **Easy Prefix Linking** - Automatically find and link game prefix folders
- **Game Properties Editor** - Edit game executables and start folders with ease
- **Intuitive GUI** - Simple, user-friendly interface built with GTK
- **Streamlined Workflow** - No more manual searching through directories

## Tech Stack

- Python
- GTK 4
- Click (CLI framework)
- VDF (Valve Data Format parser)

## Prerequisites

Install GTK and system dependencies for your distribution:

**Fedora:**
```bash
sudo dnf install python3-gobject gtk4 python3-pip python3-devel
```

**Ubuntu/Debian:**
```bash
sudo apt install python3-gi gir1.2-gtk-4.0 python3-pip python3-dev
```

**Arch Linux:**
```bash
sudo pacman -S python-gobject gtk4 python-pip base-devel
```

## Installation

### From Source
```bash
git clone https://github.com/yourusername/SteamAlly.git
cd SteamAlly
pip install --user .
```

### Using Makefile (recommended)
```bash
git clone https://github.com/yourusername/SteamAlly.git
cd SteamAlly
make install
```

## Usage

### GUI Application
```bash
steamally-gui
```

### Command Line Interface
```bash
# List all non-Steam games
steamally list

# List Steam installations
steamally list-install

# Update game executable
steamally update-exe

# Update start directory
steamally update-sDir

# Show help
steamally --help
```

# Uninstall
```bash
make uninstall
```

Or manually:
```bash
pip uninstall steamally
rm ~/.local/share/applications/steamally.desktop
```

## License

This project is licensed under the GNU General Public License (GPL).

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests.

*Making Linux gaming more accessible, one prefix at a time.*
