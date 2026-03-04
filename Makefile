install-deps:
	@echo "Installing dependencies..."
	@pip install -r requirements.txt

install: install-deps
	@echo "Installing the package..."
	@pip install .
	@mkdir -p ~/.local/share/applications
	@cp steamally.desktop ~/.local/share/applications/
	@cp steamally.png ~/.local/share/icons/hicolor/256x256/apps/
	@update-desktop-database ~/.local/share/applications/ 2>/dev/null || true

uninstall:
	@echo "Uninstalling the package..."
	@pip uninstall -y steamally
	@rm -f ~/.local/share/applications/steamally.desktop
	@update-desktop-database ~/.local/share/applications/ 2>/dev/null || true
dev-install: install-dev-deps
	@echo "Installing development dependencies..."
	@pip install -e .[dev]

clean:
	@echo "Cleaning up build artifacts..."
	@rm -rf build dist *.egg-info src/*.egg-info
	
.PHONY: install-deps install dev-install clean
