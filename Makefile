install-deps:
	@echo "Installing dependencies..."
	@pip install -r requirements.txt

install: install-deps
	@echo "Installing the package..."
	@pip install .
	@mkdir -p ~/.local/share/applications
	@mkdir -p ~/.local/share/icons/hicolor/256x256/apps
	@cp steamally.desktop ~/.local/share/applications/
	@cp steamally.png ~/.local/share/icons/hicolor/256x256/apps/
	@gtk-update-icon-cache -f -t ~/.local/share/icons/hicolor 2>/dev/null || true
	@update-desktop-database ~/.local/share/applications/ 2>/dev/null || true
	@echo "Installation complete! You may need to log out and back in for the application to appear in your launcher."

uninstall:
	@echo "Uninstalling the package..."
	@pip uninstall -y steamally
	@rm -f ~/.local/share/applications/steamally.desktop
	@rm -f ~/.local/share/icons/hicolor/256x256/apps/steamally.png
	@gtk-update-icon-cache -f -t ~/.local/share/icons/hicolor 2>/dev/null || true
	@update-desktop-database ~/.local/share/applications/ 2>/dev/null || true

dev-install: install-dev-deps
	@echo "Installing development dependencies..."
	@pip install -e .[dev]

clean:
	@echo "Cleaning up build artifacts..."
	@rm -rf build dist *.egg-info src/*.egg-info __pycache__ .pytest_cache
	
.PHONY: install-deps install dev-install clean
