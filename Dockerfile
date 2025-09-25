FROM python:3.11-slim-bookworm

# Install Tkinter + deps + curl
RUN apt-get update && \
    apt-get install -y python3-tk tk-dev curl && \
    rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false

# Copy dependency files
COPY ./poetry.lock ./pyproject.toml ./

WORKDIR /app

# Copy all files and subdirectories from ./app to /app in the image
COPY ./app /app

# Install Python dependencies from poetry
RUN poetry install --no-root

LABEL org.opencontainers.image.source=https://github.com/redis-developer/ArxivChatGuru

# Start the app with Streamlit
CMD ["poetry", "run", "streamlit", "run", "app.py", "--server.fileWatcherType=none", "--browser.gatherUsageStats=false", "--server.enableXsrfProtection=false", "--server.address=0.0.0.0"]

