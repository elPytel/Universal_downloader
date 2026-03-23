SCRIPT_DIR := scripts
DOCS_DIR := docs

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

install-dependencies:
	@echo "$(GREEN)Installing dependencies...$(RESET)"
	@./install.sh

test:
	@echo "$(GREEN)Running tests...$(RESET)"
	@pytest

build: install-dependencies
	@echo "$(GREEN)Building the project...$(RESET)"
	@$(SCRIPT_DIR)/build.sh

generate-doc:
	@echo "$(GREEN)Generating documentation...$(RESET)"
	@$(SCRIPT_DIR)/generate-doc.sh

run:
	@echo "$(GREEN)Running the project...$(RESET)"
	@python3 gui.py

clean:
	@echo "$(YELLOW)Cleaning build artifacts...$(RESET)"
	rm -rf dist 
	rm -rf build *.egg-info
	rm *.log 2>/dev/null || true
	rm ${DOCS_DIR}/* 2>/dev/null || true
	@echo "$(GREEN)Cleaned!$(RESET)"