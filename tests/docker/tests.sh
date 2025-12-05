#!/usr/bin/bash

docker build -f tests/docker/Dockerfile --build-arg IMAGE=python:3.9-slim -t venv39 .
docker run --mount type=bind,src=.,dst=/app/git-local --tty venv39
[ $? -eq 0 ]  || exit 1

docker build -f tests/docker/Dockerfile --build-arg IMAGE=python:3.10-slim -t venv310 .
docker run --mount type=bind,src=.,dst=/app/git-local --tty venv310
[ $? -eq 0 ]  || exit 1

docker build -f tests/docker/Dockerfile --build-arg IMAGE=python:3.11-slim -t venv311 .
docker run --mount type=bind,src=.,dst=/app/git-local --tty venv311
[ $? -eq 0 ]  || exit 1

docker build -f tests/docker/Dockerfile --build-arg IMAGE=python:3.12-slim -t venv312 .
docker run --mount type=bind,src=.,dst=/app/git-local --tty venv312
[ $? -eq 0 ]  || exit 1

docker build -f tests/docker/Dockerfile --build-arg IMAGE=python:3.13-slim -t venv313 .
docker run --mount type=bind,src=.,dst=/app/git-local --tty venv313
[ $? -eq 0 ]  || exit 1

docker build -f tests/docker/Dockerfile --build-arg IMAGE=python:3.14-slim -t venv314 .
docker run --mount type=bind,src=.,dst=/app/git-local --tty venv314
[ $? -eq 0 ]  || exit 1
