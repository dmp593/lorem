FROM python:slim

# Create a Lorem Home Directory
WORKDIR /lorem

# Install curl
RUN apt update && apt install -y curl

# Install poetry
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python3 -

# Add poetry symbolic link
RUN ln -s /opt/poetry/bin/poetry /usr/local/bin/poetry

# Do not create virtualenvs, install globally instead
RUN poetry config virtualenvs.create false

# Copy using pyproject.toml and poetry.lock to install dependencies
COPY pyproject.toml poetry.lock ./

# Installs the dependencies https://python-poetry.org/docs/cli/#options-2
RUN poetry install --no-root --without dev

# Removes poetry.lock after installing dependencies
RUN rm -rf pyproject.toml poetry.lock

# Copies the project folder
COPY ./app ./app

# Export port 80 to host
EXPOSE 80

# Serves our App with uvicorn
ENTRYPOINT uvicorn app.main:app --host 0.0.0.0 --port 80 --log-level ${LOG_LEVEL:-debug} --reload
