import click
from src.core.steam_manager import SteamManager
from typing import Optional


@click.group()
def cli():
    """Steam Ally - A tool to manage your Non Steam games."""
    pass


@cli.command()
def list():
    """Lists all Non Steam games and their prefix."""

    manager = SteamManager()
    choice = option_install_type(manager)
    if not choice:
        return
    click.echo(f"Listing Non Steam games for installation type: {choice}\n")
    games_prefix = manager.shortcut_prefix(choice)
    for game, prefix in games_prefix.items():
        click.echo(f"{game} -> {prefix}")

    click.echo(
        "\n\nNOTE: A game must be launched at least once before SteamAlly can find the game."
    )


@cli.command()
def list_install():
    """List all detected Steam installations"""
    manager = SteamManager()
    install_types = manager.get_available_install_types()
    if not install_types:
        click.echo("No Steam installations found.")
        return

    click.echo("Detected Steam installations:")
    i = 1
    click.echo("Install Type\tBase Path")
    click.echo("-" * 40)
    for install_type in install_types:
        steam_root = manager.get_steam_root(install_type)
        click.echo(f"{install_type}\t\t{steam_root}")
        i += 1


@cli.command()
@click.argument("game_name")
@click.argument("exe_path")
def update_exe(game_name, exe_path):
    """Update game executable path."""
    manager = SteamManager()
    choice = option_install_type(manager)
    if not choice:
        return
    try:
        success = manager.update_exe(game_name, exe_path, choice)
        click.echo("✅ Success!" if success else "❌ Failed")
    except Exception as e:
        click.echo(click.style(f"❌ Unexpected error: {e}", fg="red"))


@cli.command()
@click.argument("game_name")
@click.argument("start_dir")
def update_sDir(game_name: str, start_dir: str):
    """Update game start directory."""
    manager = SteamManager()
    choice = option_install_type(manager)
    if not choice:
        return

    try:
        success = manager.update_start_dir(game_name, start_dir, choice)
        click.echo("✅ Success!" if success else "❌ Failed")
    except Exception as e:
        click.echo(click.style(f"❌ Unexpected error: {e}", fg="red"))


def option_install_type(manager: SteamManager) -> Optional[str]:
    """Prompt user to select Steam installation type if multiple are found."""
    install_types = manager.get_available_install_types()
    if len(install_types) == 0:
        click.echo("No Steam installations found.")
        return
    elif len(install_types) == 1:
        return install_types[0]
    else:
        click.echo("Multiple Steam installations found:")
        for i, install in enumerate(install_types, 1):
            click.echo(f"{i}: {install}")
        click.echo("Enter number (1, 2...) or 'q' to quit:")

        choice = click.prompt("Choose", type=str).strip()
        if choice.lower() == "q":
            click.echo("Exiting.")
            return None

        try:
            index = int(choice) - 1
            if 0 <= index < len(install_types):
                return install_types[index]
            else:
                click.echo("Invalid number, exiting.")
                return None
        except ValueError:
            click.echo("Invalid input, exiting.")
            return None


if __name__ == "__main__":
    cli()
