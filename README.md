# FASTAPI
FastAPI boilerplate

## Setup

1. Create a virtual environment.
 ```sh
    python3 -m venv .venv
 ```
2. Activate virtual environment.
```sh
    source /path/to/venv/bin/activate`
```
3. Install project dependencies `pip install -r requirements.txt`
4. Create a .env file by copying the .env.sample file
`cp .env.sample .env`

5. Start server.
 ```sh
 python main.py
```

## **DATABASE TEST SETUP**

To set up the database, follow the following steps:

**Cloning**
- clone the repository using `git clone https://github.com/hngprojects/hng_boilerplate_python_fastapi_web`
- `cd` into the directory hng_boilerplate_python_fastapi_web
- switch branch using `git checkout backend`

**Environment Setup**
- run `pip install -r requrements.txt` to install dependencies
- create a `.env` file in the root directory and copy the content of `.env.sample` and update it accordingly

**Create your local database**
```bash
sudo -u root psql
```
```sql
CREATE USER user WITH PASSWORD 'your desired password'; 
CREATE DATABASE hng_fast_api;
GRANT ALL PRIVILEGES ON DATABASE hng_fast_api TO user;
```

**Starting the database**
after cloning the database, dont run 
`alembic revision --autogenerate -m 'initial migration'`
but run
`alembic upgrade head`
if you make changes to any table locally, then run the below command.
```bash
alembic revision --autogenerate -m 'initial migration'
alembic upgrade head
```

**create dummy data**
```bash
python3 seed.py
```


**Adding tables and columns to models**

After creating new tables, or adding new models. Make sure to run alembic revision --autogenerate -m "Migration messge"

## TEST THE ENDPOINT
- run the following code
```
python -m unittest tests/v1/test_login.py
python -m unittest tests/v1/test_signup.py
```

