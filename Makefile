# ---------------------------------------------------------------------------
# Uniform EPS demo CLI (per eps-demo-devx / eps-demo-repo-hygiene). Same four
# verbs in every repo: dev / test / lint / deploy.
#
# This demo is a single stdlib Python process serving one HTML file, so there
# is no install step, no bundler, and no backend/frontend split — the verbs are
# wired straight to it rather than to the template's auto-detecting stack
# probes. See docs/adr/0007.
# ---------------------------------------------------------------------------
.DEFAULT_GOAL := help
.PHONY: help install dev test lint deploy bicep-lint down

help: ## Show available commands
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

install: ## Nothing to install - the app is Python standard library only
	@python --version
	@echo "no dependencies by design (eps-demo-devx: keep the demo readable on stage)"

dev: ## Run the demo locally on http://localhost:8000
	@python server.py

test: ## Run the roster end to end against Azure and check every rate against the live price feed
	@python smoke_test.py
	@python refresh_prices.py

lint: ## Syntax-check the Python and validate the committed config
	@python -m py_compile server.py smoke_test.py verify.py refresh_prices.py
	@python -c "import json; json.load(open('config.example.json')); print('config.example.json ok')"
	@echo "lint ok"

bicep-lint: ## Compile the infrastructure templates
	@az bicep build --file infra/main.bicep --stdout > /dev/null && echo "bicep ok"

deploy: ## Provision and deploy to Azure (azd up)
	@azd up

down: ## Delete the deployed environment - the App Service plan bills continuously
	@azd down --purge
