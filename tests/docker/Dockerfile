ARG IMAGE
FROM $IMAGE

WORKDIR /app

RUN python3 -m venv venv
RUN venv/bin/python3 -m pip install --upgrade pip --no-cache-dir

CMD venv/bin/python3 -m pip install -e git-local[test] && venv/bin/python3 -m pip list && venv/bin/python3 -m pytest git-local/tests
