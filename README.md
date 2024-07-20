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
- switch branch using `git checkout Muritadhor`

**Environment Setup**
- run `pip install -r requrements.txt` to install dependencies
- create a `.env` file in the root directory and copy the content of `.env.sample` and update it accordingly

**Create your local database**
```bash
sudo -u root psql
```
```sql
CREATE USER user WITH PASSWORD 'password';
CREATE DATABASE hng_fast_api;
GRANT ALL PRIVILEGES ON DATABASE hng_fast_api TO user;
```

**Migrate the database**
```bash
alembic upgrade head
```

**create dummy data**
```bash
python3 db_test.py
```
This should run without any errors

**Using the database in your route files:**

make sure to add the following to your file

```python
from api.db.database import create_database, get_db
from api.v1.models.user import User
from api.v1.models.org import Organization
from api.v1.models.profile import Profile
from api.v1.models.product import Product
from api.v1.models.invitation import Invitation
from api.v1.models.role import Role
from api.v1.models.permission import Permission
from api.v1.models.base import Base

create_database()
db = next(get_db())
```
Then use the db for your queries

example
```python
db.add(User(email="test@mail", username="testuser", password="testpass", first_name="John", last_name="Doe"))
```

## Note
 Dont run alembic revision --autogenerate -m "Migration messge", as this may cause conflict with migrating to the database.
 
- after cloning, open **.env** set your database details properly
- open alembic.ini and update your database url in **DATABASE_URL** field
- run **alembic upgrade head** to migrate the currently exising migration to your database.

## Addition of tables
- you are free to include your table to the already existing database
- make sure to link the relationship properly.
- test it locally to make sure it is working.
- you can generate your migration files and test it locally.
- when pushing, gitignore the migration file **alembic** and **alembic.ini** so that it wont cause conflict.

### Endpoint Created
- POST /api/auth/v1/login
- POST /api/auth/v1/register
- POST /api/v1/roles