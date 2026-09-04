# Developer Guide

This guide helps developers run the Mergington High School Activities API locally, including running it in a container, and understand the CI/CD pipeline used to build and deploy it.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) (with Docker Compose)
- Python 3.12+ (only needed if you want to run the app outside of a container)

## Running locally without a container

```bash
pip install -r requirements.txt
python -m uvicorn src.app:app --reload
```

The app will be available at http://localhost:8000, with API docs at http://localhost:8000/docs.

## Running locally in a container

The repository ships a multistage `Dockerfile`:

1. `base` - shared configuration and dependency manifest.
2. `builder` - installs Python dependencies into a virtualenv.
3. `test` - copies the source code and runs `pytest` against the built environment.
4. `runtime` - a minimal image containing only the virtualenv and application source, run as a non-root user.

### Build and run with Docker

```bash
# Build the runtime image
docker build --target runtime -t mergington-activities-api .

# Run the container, exposing the app on port 8000
docker run --rm -p 8000:8000 mergington-activities-api
```

Then open http://localhost:8000/docs in your browser.

### Build and run with Docker Compose

```bash
docker compose up --build
```

This builds the `runtime` stage and starts the API on http://localhost:8000.

### Running the tests in a container

The `test` stage can be built and run on its own, which is useful for verifying changes before opening a pull request:

```bash
docker build --target test -t mergington-activities-api:test .
```

A non-zero exit code means the build failed, most commonly because `pytest` found a failing test.

## Running the tests locally

```bash
pip install -r requirements.txt
python -m pytest
```

## CI/CD pipeline

The GitHub Actions workflow at [`.github/workflows/docker-ci-cd.yml`](./workflows/docker-ci-cd.yml) automates the full build and deployment flow using three stages/jobs:

1. **Test** - installs dependencies and runs the `pytest` suite on every push and pull request targeting `main`.
2. **Build & Push Image** - builds the Docker image's `test` target to validate the containerized build, then builds and pushes the `runtime` image to the GitHub Container Registry (`ghcr.io`) when changes are pushed to `main`. Images are tagged with both the commit SHA and `latest`.
3. **Deploy** - runs only for pushes to `main` (via the `production` GitHub Environment) and deploys the freshly built image. Replace the placeholder step with your team's actual deployment method (e.g. Kubernetes, Azure, AWS).

Pull requests only run the `test` job and the containerized build validation; they do not push images or deploy.
