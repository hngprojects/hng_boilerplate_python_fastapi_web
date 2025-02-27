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
4. Create a .env.template file by running the command `python create_env_template.py`. This generates predefined environment variables in the `env_validator.py` file.
5. create a `.env` file.
6. Copy the contents of `.env.template` file into the `.env` file.
`cp .env.sample .env`
7. Key in your environment variable details in the `.env` file.
7. Start server.
 ```sh
 python main.py
```

## **Creating Environment Variables**
To create environment variables based on the env_validator.py, follow these steps:
1. Add your new environment variable to the category you wish, for example:
   ```
         "Core Settings": [
            "SECRET_KEY", "ALGORITHM", "ACCESS_TOKEN_EXPIRE_MINUTES", "JWT_REFRESH_EXPIRY",
                "APP_URL", "PYTHON_ENV", "MY_NEW_VARIABLE" // Added MY_NEW_VARIABLE to core settings category
        ],
   ```
2. Modify env_validator.py to Add a New Variable:
   Open the env_validator.py file and add your new environment variable to the required_vars dictionary. For example, to add a new variable NEW_VARIABLE:
    ```
            "NEW_VARIABLE": {
            "required": True,
            "description": "Description of what this variable does",
            "type": "int",  # if applicable
            "min_length": 8,  # if applicable
            "allowed_values": [12345678, 87654321]  # Example integer values with at least 8 digits
        }
    ```
3. Generate a new template:
    Run the `create_env_template.py` script to generate a new `.env.template` file:
   ```shell
      python create_env_template.py  
     ```
   This will create a .env.template file with all required environment variables, including the new one you added.

4. Update your `.env` File:
   Open your .env file and add the new variable with its value:
    ```
        # Description of what this variable does (Required)
         NEW_VARIABLE=12345678
   ```
5. Validate Environment Variables:
   Ensure that the environment variables are validated at the application startup by importing and running the validator `main.py` file:
    This process ensures that the new environment variable is added to the validator and included in the generated .env.template and .env files.

### Add New Category for Environment variables

1. **Modify the `EnvValidator` class to include the new category:**

   Add the new category to the `CATEGORIES` dictionary in the `EnvValidator` class. For example, to add a new category called "Logging Settings":

   ```python
   class EnvValidator:
       # Class variable to define variable categories for template generation
       CATEGORIES = {
           "Core Settings": [
               "SECRET_KEY", "ALGORITHM", "ACCESS_TOKEN_EXPIRE_MINUTES", "JWT_REFRESH_EXPIRY",
               "APP_URL", "PYTHON_ENV", "MY_NEW_VARIABLE"
           ],
           "Database Settings": [
               "DB_TYPE", "DB_NAME", "DB_USER", "DB_PASSWORD", "DB_HOST", "DB_PORT",
               "MYSQL_DRIVER", "DB_URL"
           ],
           "OAuth Settings": [
               "GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_SECRET", "FRONTEND_URL"
           ],
           "Email Settings": [
               "MAIL_USERNAME", "MAIL_PASSWORD", "MAIL_FROM", "MAIL_PORT", "MAIL_SERVER",
               "MAILJET_API_KEY", "MAILJET_API_SECRET"
           ],
           "SMS Settings": [
               "TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN", "TWILIO_PHONE_NUMBER"
           ],
           "Payment Settings": [
               "FLUTTERWAVE_SECRET", "PAYSTACK_SECRET", "STRIPE_SECRET_KEY", "STRIPE_WEBHOOK_SECRET"
           ],
           "Testing": [
               "TESTING"
           ],
           "Logging Settings": [  # New category
               "LOG_LEVEL", "LOG_FILE_PATH"
           ]
       }
   ```

2. **Add the new environment variables to the `required_vars` dictionary:**

   Define the new environment variables under the `required_vars` dictionary in the `EnvValidator` class. For example:

   ```python
   class EnvValidator:
       def __init__(self):
           self.required_vars = {
               # Core settings
               "SECRET_KEY": {"required": True, "min_length": 16, "description": "Secret key for cryptographic signing"},
               "ALGORITHM": {"required": True, "default": "HS256", "description": "JWT algorithm"},
               "ACCESS_TOKEN_EXPIRE_MINUTES": {"required": True, "type": "int", "default": "3000",
                                               "description": "Access token expiry time in minutes"},
               "JWT_REFRESH_EXPIRY": {"required": True, "type": "int", "default": "7",
                                      "description": "Refresh token expiry time in days"},
               "MY_NEW_VARIABLE": {
                   "required": True,  # or False
                   "description": "Description of what this variable does",
                   # Optional: add any other validation rules
                   "default": "12345678",  # if applicable
                   "type": "int",  # if applicable
                   "min_length": 8,  # if applicable
                   "allowed_values": ["12345678", "87654321"]
               },
               # Logging settings
               "LOG_LEVEL": {"required": True, "allowed_values": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                             "default": "INFO", "description": "Logging level"},
               "LOG_FILE_PATH": {"required": False, "description": "Path to the log file"}
           }
   ```

3. **Generate a new template:**

   Run the `create_env_template.py` script to generate a new `.env.template` file:

   ```sh
   python create_env_template.py
   ```

   This will create a `.env.template` file with all required environment variables, including the new ones you added.

4. **Update your `.env` file:**

   Open your `.env` file and add the new variables with their values:

   ```dotenv
   # Logging Settings
   LOG_LEVEL=INFO
   LOG_FILE_PATH=/path/to/logfile.log
   ```

This process ensures that the new category and its environment variables are added to the validator and included in the generated `.env.template` and `.env` files.

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
