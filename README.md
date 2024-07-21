# FASTAPI

FastAPI boilerplate

## Dependencies

This project require the following depencies.

-   python 3.8 or later
-   postgresql, optional: [mysql, mongodb, sqlite]
-   FastApi

## Setup

1. Create a virtual environment and activate it.

    ```sh
    python3 -m venv .venv
    source .venv/bin/activate
    ```

2. Install project dependencies

    ```sh
    pip install -r requirements.txt
    ```

3. Create a .env file by copying the .env.sample file

    ```sh
    cp .env.sample .env
    ```

4. Setup database.

    ```sh
    cat setup_database.sql | sudo -u postgres psql
    ```

5. Create tables

    ```sh
    alembic upgrade head
    ```

6. Seed some data.
    ```sh
    python3 -m seed.py
    ```

## Features

1. feature 1
2. feature 2

## Contribute

1. Fork the repository
2. Clone the forked repository
3. Create a new branch please keep the name short and descriptive.
4. please follow this format for naming branches

    ```
    feature/feature_name-issue_id` or `bug/bug_name-issue_id
    for example:
    feature/auth_login-12 or bug/missing_module-124
    ```

5. Make your changes and commit them:
    - Provide a detailed commit message.
    - Your pull request should be descriptive and provide a summary of the changes made.
    - Your pull should contain a reference to the issue you are assigned to.
    - Your pull request should pass all new and existing tests.
    - Make sure your code is well formatted.

## Database Migrations

if you make changes to the database models, you need to run the following commands.

```sh
alembic revision --autogenerate -m "Migration message"
alembic upgrade head
```
