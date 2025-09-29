

____

## Run the App

### Run Locally

1. First, clone this repo and cd into it.
    ```bash
    $ git clone https://github.com/benisprlh/Demo-HR.git && cd Demo-HR
    ```

2. Create your env file:
    ```bash
    $ cp .env.template .env
    ```
    *fill out values, most importantly, your `OPENAI_API_KEY`.*

3. Install dependencies with Poetry:
    ```bash
    $ poetry install --no-root
    ```

4. Run the app:
    ```bash
    $ poetry run streamlit run app.py --server.fileWatcherType none --browser.gatherUsageStats false --server.enableXsrfProtection false --server.address 0.0.0.0
    ```

5. Navigate to:
    ```
    http://localhost:8501/
    ```


### Docker Compose

First, clone the repo like above.

1. Create your env file:
    ```bash
    $ cp .env.template .env
    ```
    *fill out values, most importantly, your `OPENAI_API_KEY`.*

2. Run with docker compose:
    ```bash
    $ docker compose up
    ```
    *add `-d` option to daemonize the processes to the background if you wish.*

    Issues with dependencies? Try force-building with no-cache:
    ```
    $ docker compose build --no-cache
    ```

3. Navigate to:
    ```
    http://localhost:8501/
    ```
