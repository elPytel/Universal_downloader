SCRIPT_DIR := scripts
DOCS_DIR   := docs
APT_DEPENDENCIES := apt-dependencies.txt
PIP_DEPENDENCIES := requirements.txt
VENV             := venv
VENV_BIN         := $(VENV)/bin
PYTHON           := $(shell if grep -Eq '^[[:space:]]*INSTALL_PYTHON_TO_SYSTEM[[:space:]]*=[[:space:]]*(true|TRUE|1|yes|YES)[[:space:]]*$$' .env 2>/dev/null; then printf 'python3'; else printf '%s/python' '$(VENV_BIN)'; fi)

# Colors for output
RED    := $(shell printf '\033[0;31m')
GREEN  := $(shell printf '\033[0;32m')
YELLOW := $(shell printf '\033[0;33m')
BLUE   := $(shell printf '\033[0;34m')
PURPLE := $(shell printf '\033[0;35m')
CYAN   := $(shell printf '\033[0;36m')
BOLD   := $(shell printf '\033[1m')
RESET  := $(shell printf '\033[0m')

ALL: install-dependencies test build generate-doc

install-dependencies: $(APT_DEPENDENCIES) $(PIP_DEPENDENCIES)
	@echo "$(GREEN)Installing dependencies...$(RESET)"
	@./install.sh

test:
	@echo "$(GREEN)Running tests...$(RESET)"
	@$(PYTHON) -m pytest

build: install-dependencies
	@echo "$(GREEN)Building the project...$(RESET)"
	@$(SCRIPT_DIR)/build.sh

generate-doc:
	@echo "$(GREEN)Generating documentation...$(RESET)"
	@$(SCRIPT_DIR)/generate-doc.sh

run:
	@echo "$(GREEN)Running the project...$(RESET)"
	@$(PYTHON) gui.py

clean:
	@echo "$(YELLOW)Cleaning build artifacts...$(RESET)"
	rm -rf dist 
	rm -rf build *.egg-info
	rm -rf logs
	rm ${DOCS_DIR}/* 2>/dev/null || true
	@echo "$(GREEN)Cleaned!$(RESET)"

help:
	@echo "$(CYAN)Available targets:$(RESET)"
	@echo "  $(BOLD)install-dependencies$(RESET) - Install all required dependencies."
	@echo "  $(BOLD)test$(RESET) - Run the test suite."
	@echo "  $(BOLD)build$(RESET) - Build the project."
	@echo "  $(BOLD)generate-doc$(RESET) - Generate project documentation."
	@echo "  $(BOLD)run$(RESET) - Run the project."
	@echo "  $(BOLD)clean$(RESET) - Clean build artifacts and logs."
	@echo "  $(BOLD)help$(RESET) - Show this help message."