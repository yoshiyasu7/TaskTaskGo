# Start localhost
run:
	python -B -m src.main

run-dev:
	find src -type d -name '__pycache__' -exec rm -r {} + && python -B -m src.main

# Docker config
-include settings/.env.docker
REPO    := $(shell sed -n 's/^name = "\(.*\)"/\1/p' pyproject.toml | head -1)
VERSION := $(shell sed -n 's/^version = "\(.*\)"/\1/p' pyproject.toml | head -1)
IMAGE   := $(DOCKER_REGISTRY)/$(REPO)
.PHONY: docker docker-dev

# Create Docker containers
docker:
ifndef DOCKER_REGISTRY
	$(error DOCKER_REGISTRY not defined. Add it to settings/.env.docker)
endif
	docker build --platform=linux/amd64 --build-arg DOCKER_TAG=$(VERSION) -t $(IMAGE):$(VERSION) .
	docker tag $(IMAGE):$(VERSION) $(IMAGE):latest
	docker push $(IMAGE):$(VERSION)
	docker push $(IMAGE):latest

docker-dev:
ifndef DOCKER_REGISTRY
	$(error DOCKER_REGISTRY not defined. Add it to settings/.env.docker)
endif
	docker build --platform=linux/amd64 --build-arg DOCKER_TAG=$(VERSION)Dev -t $(IMAGE):$(VERSION)Dev .
	docker tag $(IMAGE):$(VERSION)Dev $(IMAGE):latestDev
	docker push $(IMAGE):$(VERSION)Dev
	docker push $(IMAGE):latestDev

# Check formatting
black:
	isort --profile black .
	black -l75 .

check: black
	poetry run flake8 .
	poetry run ruff check .
	poetry run mypy .
	poetry run pylint .

# Start tests
test:
	poetry run pytest