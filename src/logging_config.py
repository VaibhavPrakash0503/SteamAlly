import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging():
    log_dir = Path.home() / ".local/share/steam_ally" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            RotatingFileHandler(
                log_dir / "steam-ally.log",
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5,
            )
        ],
    )


if __name__ == "__main__":
    setup_logging()
    logging.info("This is a test log message.")
