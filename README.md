# **FASTAPI Boilerplate**  
A FastAPI boilerplate for efficient project setup.  

## **Cloning the Repository**  

1. **Fork the repository** and clone it:  
   ```sh
   git clone https://github.com/<username>/hng_boilerplate_python_fastapi_web.git
   ```
2. **Navigate into the project directory**:  
   ```sh
   cd hng_boilerplate_python_fastapi_web
   ```
3. **Switch to the development branch** (if not already on `dev`):  
   ```sh
   git checkout dev
   ```


## **Setup Instructions**  

1. **Create a virtual environment**:  
   ```sh
   python3 -m venv .venv
   ```
2. **Activate the virtual environment**:  
   - On macOS/Linux:  
     ```sh
     source .venv/bin/activate
     ```
   - On Windows (PowerShell):  
     ```sh
     .venv\Scripts\Activate
     ```
3. **Install project dependencies**:  
   ```sh
   pip install -r requirements.txt
   ```
4. **Create a `.env` file** from `.env.sample`:  
   ```sh
   cp .env.sample .env
   ```
5. **Start the server**:  
   ```sh
   python main.py
   ```

---

## **Database Setup**  

### **Replacing Placeholders in Database Setup**  

When setting up the database, you need to replace **placeholders** with your actual values. Below is a breakdown of where to replace them:

---

## **Step 1: Create a Database User**
```sql
CREATE USER user WITH PASSWORD 'your_password';
```
🔹 **Replace:**  
- `user` → Your **preferred database username** (e.g., `fastapi_user`).  
- `'your_password'` → A **secure password** for the user (e.g., `'StrongP@ssw0rd'`).  

✅ **Example:**  
```sql
CREATE USER fastapi_user WITH PASSWORD 'StrongP@ssw0rd';
```

---

## **Step 2: Create the Database**
```sql
CREATE DATABASE hng_fast_api;
```
🔹 **Replace:**  
- `hng_fast_api` → Your **preferred database name** (e.g., `fastapi_db`).  

✅ **Example:**  
```sql
CREATE DATABASE fastapi_db;
```

---

## **Step 3: Grant Permissions**
```sql
GRANT ALL PRIVILEGES ON DATABASE hng_fast_api TO user;
```
🔹 **Replace:**  
- `hng_fast_api` → The **database name you used** in Step 2.  
- `user` → The **username you created** in Step 1.  

✅ **Example:**  
```sql
GRANT ALL PRIVILEGES ON DATABASE fastapi_db TO fastapi_user;
```

---

## **Step 4: Update `.env` File**
Edit the `.env` file to match your setup.

```env
DATABASE_URL=postgresql://user:your_password@localhost/hng_fast_api
```
🔹 **Replace:**  
- `user` → Your **database username**.  
- `your_password` → Your **database password**.  
- `hng_fast_api` → Your **database name**.  

✅ **Example:**  
```env
DATABASE_URL=postgresql://fastapi_user:StrongP@ssw0rd@localhost/fastapi_db
```

---

## **Step 5: Verify Connection**
After setting up the database, test the connection:

```sh
psql -U user -d hng_fast_api -h localhost
```
🔹 **Replace:**  
- `user` → Your **database username**.  
- `hng_fast_api` → Your **database name**.  

✅ **Example:**  
```sh
psql -U fastapi_user -d fastapi_db -h localhost
```

## **Step 6: Run database migrations**  
   ```sh
   alembic upgrade head
   ```
   _Do NOT run `alembic revision --autogenerate -m 'initial migration'` initially!_

## **Step 7: If making changes to database models, update migrations**  
```sh
   alembic revision --autogenerate -m 'your migration message'
   alembic upgrade head
   ```
## **Step 8: Seed dummy data**  
   ```sh
   python3 seed.py
   ```

---

## **Adding Tables and Columns**  

1. **After creating new tables or modifying models**:  
   - Run Alembic migrations:  
     ```sh
     alembic revision --autogenerate -m "Migration message"
     alembic upgrade head
     ```
   - Ensure you **import new models** into `api/v1/models/__init__.py`.  
   - You do NOT need to manually import them in `alembic/env.py`.

---

## **Adding New Routes**  

1. **Check if a related route file already exists** in `api/v1/routes/`.  
   - If yes, add your route inside the existing file.  
   - If no, create a new file following the naming convention.  
2. **Define the router** inside the new route file:  
   - Include the prefix (without `/api/v1` since it's already handled).  
3. **Register the router in `api/v1/routes/__init__.py`**:  
   ```python
   from .new_route import router as new_router
   api_version_one.include_router(new_router)
   ```

---

## **Running Tests with Pytest**  

### **Install Pytest**  
Ensure `pytest` is installed in your virtual environment:  
```sh
pip install pytest
```

### **Run all tests in the project**  
From the **project root directory**, run:  
```sh
pytest
```
This will automatically discover and execute all test files in the `tests/` directory.

### **Run tests in a specific directory**  
To run tests in a specific model directory (e.g., `tests/v1/user/`):  
```sh
pytest tests/v1/user/
```

### **Run a specific test file**  
To run tests from a specific test file (e.g., `test_signup.py` inside `tests/v1/auth/`):  
```sh
pytest tests/v1/auth/test_signup.py
```

### **Run a specific test function**  
If you want to run a specific test inside a file, use:  
```sh
pytest tests/v1/auth/test_signup.py::test_user_signup
```

### **Run tests with detailed output**  
For verbose output, add the `-v` flag:  
```sh
pytest -v
```

### **Run tests and generate coverage report**  
To check test coverage, install `pytest-cov`:  
```sh
pip install pytest-cov
```
Then run:  
```sh
pytest --cov=api
```

---

## **Common Migration Issues & Solutions**  

### **Error: "Target database is not up to date."**  
If you encounter this issue when running:  
```sh
alembic revision --autogenerate -m 'your migration message'
```
#### **Solution**:  
Run the following command first:  
```sh
alembic upgrade head
```
Then retry:  
```sh
alembic revision --autogenerate -m 'your migration message'
```

---

## **Contribution Guidelines**  

- **Test your endpoints and models** before pushing changes.  
- **Push Alembic migrations** if database models are modified.  
- Ensure your code **follows project standards** and **passes tests** before submitting a pull request.  

