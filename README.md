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

After creating new tables, or adding new models. Make sure you import the new model properly in th 'api/v1/models/__init__.py file

After importing it in the init file, you need not import it in the /alembic/env.py file anymore


**Adding new routes**

To add a new route, confirm if a file relating to that route is not already created. If it is add the route in that file using the already declared router

If the there is no file relating to the route in the 'api/v1/routes/' directory create a new one following the naming convention

After creating the new route file, declare the router and add the prefix as well as the tag

The prefix should not include the base prefix ('/api/v1') as it is already includedin the base `api_version_one` router

After creating the router, import it in the 'api/v1/routes/__init__.py' file and include the router in the `api_version_one` router using
```python
api_version_one.include_router(<router_name>)
```

## TEST THE ENDPOINT
- run the following code
```
python -m unittest tests/v1/test_login.py
python -m unittest tests/v1/test_signup.py
```

## Issues
if you encounter the following Error, when you run the code below

**alembic revision --autogenerate -m 'your migration message'**

```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
ERROR [alembic.util.messaging] Target database is not up to date.
  FAILED: Target database is not up to date.
```

## Solutions
Run the following code below first to update the datebase
**alembic upgrade head**
then, run this again.
**alembic revision --autogenerate -m 'your migration message'**

## update 
please make sure to test your endpoint or model before pushing.
push your alembic migrations.
