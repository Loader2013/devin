# Makefile for OpenDevin project

# Variables
DOCKER_IMAGE = ghcr.io/opendevin/sandbox
BACKEND_PORT = 3000
BACKEND_HOST = "127.0.0.1:$(BACKEND_PORT)"
FRONTEND_PORT = 3001
DEFAULT_WORKSPACE_DIR = "./workspace"
DEFAULT_MODEL = "gpt-4-0125-preview"
CONFIG_FILE = config.toml

UNAME_SYS = $(shell uname -s)
# fallback to python3 if python is not available (e.g. on macOS)
PYTHON_BIN = $(shell which python || which python3)
ifeq ($(PYTHON_BIN),)
	$(error "Python is not installed. Please install Python 3.")
endif

ifeq ($(shell which node), )
	$(error "Node.js is not installed. Please install Node.js.")
endif

ifeq ($(shell which npm), )
	$(error "npm is not installed. Please install npm.")
endif

INSTALL_PIPENV_BASE_CMD = $(PYTHON_BIN) -m pip install pipenv

ifeq ($(shell which brew), )
	INSTALL_PIPENV_BREW_CMD = echo "Error: Homebrew is not installed. Please install Homebrew from https://brew.sh/ and try again." && exit 1
else
	INSTALL_PIPENV_BREW_CMD = echo "Install pipenv from pip failed, try brew install pipenv..." && brew install pipenv
endif

ifeq ($(shell which pipenv), )
	ifeq ($(UNAME_SYS),Darwin)
		INSTALL_PIPENV_CMD = $(INSTALL_PIPENV_BASE_CMD) || $(INSTALL_PIPENV_BREW_CMD)
	else
		INSTALL_PIPENV_CMD = $(INSTALL_PIPENV_BASE_CMD)
	endif
else
	INSTALL_PIPENV_CMD = echo "Pipenv is already installed."
endif

# Build
build:
	@echo "Building project..."
	@echo "Pulling Docker image..."
	@docker pull $(DOCKER_IMAGE)
	@echo "Installing Python dependencies..."
	@$(INSTALL_PIPENV_CMD)
	@$(PYTHON_BIN) -m pipenv install
	@echo "Setting up frontend environment..."
	@cd frontend && npm install

# Start backend
start-backend:
	@echo "Starting backend..."
	@$(PYTHON_BIN) -m pipenv run uvicorn opendevin.server.listen:app --port $(BACKEND_PORT)

# Start frontend
start-frontend:
	@echo "Starting frontend..."
	@cd frontend && BACKEND_HOST=$(BACKEND_HOST) FRONTEND_PORT=$(FRONTEND_PORT) npm run start

# Run the app
run:
	@echo "Running the app..."
	@mkdir -p logs
	@rm -f logs/pipe
	@mkfifo logs/pipe
	@cat logs/pipe | (make start-backend) &
	@echo 'test' | tee logs/pipe | (make start-frontend)

# Setup config.toml
setup-config:
	@echo "Setting up config.toml..."
	@read -p "Enter your LLM Model name (see docs.litellm.ai/docs/providers for full list) [default: $(DEFAULT_MODEL)]: " llm_model; \
	 llm_model=$${llm_model:-$(DEFAULT_MODEL)}; \
	 echo "LLM_MODEL=\"$$llm_model\"" >> $(CONFIG_FILE).tmp

	@read -p "Enter your LLM API key: " llm_api_key; \
	 echo "LLM_API_KEY=\"$$llm_api_key\"" >> $(CONFIG_FILE).tmp

	@read -p "Enter your workspace directory [default: $(DEFAULT_WORKSPACE_DIR)]: " workspace_dir; \
	 workspace_dir=$${workspace_dir:-$(DEFAULT_WORKSPACE_DIR)}; \
	 echo "WORKSPACE_DIR=\"$$workspace_dir\"" >> $(CONFIG_FILE).tmp

	@mv $(CONFIG_FILE).tmp $(CONFIG_FILE)

# Help
help:
	@echo "Usage: make [target]"
	@echo "Targets:"
	@echo "  build               - Build project, including environment setup and dependencies."
	@echo "  start-backend       - Start the backend server for the OpenDevin project."
	@echo "  start-frontend      - Start the frontend server for the OpenDevin project."
	@echo "  run                 - Run the OpenDevin application, starting both backend and frontend servers."
	@echo "                        Backend Log file will be stored in the 'logs' directory."
	@echo "  setup-config        - Setup the configuration for OpenDevin by providing LLM API key, LLM Model name, and workspace directory."
	@echo "  help                - Display this help message, providing information on available targets."

# Phony targets
.PHONY: install start-backend start-frontend run setup-config help
