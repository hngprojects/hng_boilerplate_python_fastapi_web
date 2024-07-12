# FastAPI Authentication API
This repository contains a FastAPI-based authentication system providing essential functionalities such as user signup, login, logout, token refresh, and user information retrieval. The project uses OAuth2 password flow with JWT tokens for secure authentication.

## Table of Contents
- Getting Started
- Project Structure
- Environment Variables
- Endpoints
  - Signup
  - Login
  - Get User
  - Refresh Access Token
  - Logout
  - Delete User
  - Create User Roles
- Dependencies

## Getting Started

### Prerequisites
- Python 3.8+
- PostgreSQL (or any other preferred database supported by SQLAlchemy)

### Installation
1. Clone the repository:
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2. Create a virtual environment and activate it:
    ```bash
    python3 -m venv env
    source env/bin/activate  # On Windows use `env\Scripts\activate`
    ```

3. Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Set up the environment variables:
    ```bash
    cp .env.example .env
    ```

5. Update the `.env` file with your database configuration and other necessary settings.

### Running the Application
To run the FastAPI application, execute the following command:
```bash
uvicorn main:app --reload
```

## Project Structure
```
.
├── api
│   ├── core
│   │   ├── dependencies
│   │   │   └── user.py
│   │   └── responses.py
│   ├── db
│   │   └── database.py
│   ├── v1
│   │   ├── models
│   │   │   └── auth.py
│   │   ├── schemas
│   │   │   └── auth.py
│   │   ├── services
│   │   │   └── auth.py
│   │   └── routes.py
├── main.py
├── requirements.txt
├── .env.example
└── README.md
```

## Environment Variables
The following environment variables need to be set in your `.env` file:
- `ACCESS_TOKEN_EXPIRE_MINUTES`
- `JWT_REFRESH_EXPIRY`
- `PYTHON_ENV` (set to `production` for secure cookies)
- `DATABASE_URL` (database connection URL)

## Endpoints

### Signup
**Endpoint:** `POST /signup`  
**Description:** Endpoint to create a user.  
**Returns:** Created User, Access Token, and Refresh Token.

**Request Body:**
```json
{
  "username": "string",
  "email": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "message": "Success",
  "data": {
    "id": 1,
    "username": "string",
    "email": "string"
  },
  "access_token": "string",
  "refresh_token": "string",
  "token_type": "bearer"
}
```

### Login
**Endpoint:** `POST /login`  
**Description:** Login and get access token.  
**Returns:** Logged in User, Access Token, and Refresh Token.

**Request Body:**
```json
{
  "email": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "data": {
    "id": 1,
    "username": "string",
    "email": "string"
  },
  "access_token": "string",
  "refresh_token": "string",
  "token_type": "bearer"
}
```

### Get User
**Endpoint:** `GET /user`  
**Description:** Returns authenticated user's information.  
**Returns:** User information.

**Response:**
```json
{
  "id": 1,
  "username": "string",
  "email": "string"
}
```

### Refresh Access Token
**Endpoint:** `GET /refresh-access-token`  
**Description:** Refreshes the access token using the refresh token.  
**Returns:** New Access Token and User information.

**Response:**
```json
{
  "user": {
    "id": 1,
    "username": "string",
    "email": "string"
  },
  "access_token": "string",
  "expires_in": 900
}
```

### Logout
**Endpoint:** `POST /logout`  
**Description:** Logs out an authenticated user.  
**Returns:** Logout success message.

**Response:**
```json
{
  "message": "User logged out successfully."
}
```

### Delete User
**Endpoint:** `DELETE /users/{user_id}`  
**Description:** Deletes a user (soft delete).  
**Returns:** User deletion success message.

**Response:**
```json
{
  "message": "User deleted successfully."
}
```

### Create User Roles
**Endpoint:** `POST /users/roles`  
**Description:** Endpoint to create custom roles for users mixing permissions.  
**Returns:** Created role.

**Response:**
```json
{
  "message": "Role created successfully."
}
```

## Dependencies
- FastAPI
- SQLAlchemy
- Pydantic
- Decouple
- Uvicorn

Ensure to have all dependencies installed by running:
```bash
pip install -r requirements.txt
```

Sure! Here’s a more suitable conclusion for your README file:

---

## Conclusion

This FastAPI-based authentication system provides a robust and secure foundation for managing user authentication in your applications. By utilizing OAuth2 password flow with JWT tokens, the system ensures secure handling of user credentials and session management.

Feel free to explore the code, raise issues, or contribute to the project by submitting pull requests. Your feedback and contributions are invaluable to improving this project.

For more detailed information on using FastAPI, refer to the [FastAPI Documentation](https://fastapi.tiangolo.com/).

Thank you for using and contributing to this project!

