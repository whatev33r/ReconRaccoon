NAME=reconraccoon
PYTHON=python3.11
PIP=pip3
MAIN=reconraccoon
VERSION=1.1.0


help: ## Get help for Makefile
	@echo "\n#### $(NAME) v$(VERSION) ####\n"
	@echo "Available targets:\n"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
	@echo "\n"

docker-build: ## Build docker image
	docker build -t $(NAME) .

docker-sh: ## Shell into docker container
	docker run --network=host --privileged -it $(NAME) bash

docker-remove: ## Remove docker container
	@docker container rm $(NAME)

test: ## Run tests
	@$(PYTHON) -m pytest tests/

.PHONY: help docker-build docker-sh docker-remove