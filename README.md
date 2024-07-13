# Community Forum Application

This project is a community forum application where users can join various communities, engage in discussions on various topics, and receive notifications related to their communities.

## API Routes

### User Authentication

- **Signup**
  - **URL:** `/api/signup`
  - **Method:** `POST`
  - **Request Body:**
    ```json
    {
      "username": "string",
      "email": "string",
      "password": "string",
      "first_name": "string",
      "last_name": "string"
    }
    ```
  - **Response:**
    - Success: 201 Created
      ```json
      {
        "message": "User created successfully.",
        "data": {
          "id": "integer",
          "username": "string",
          "email": "string",
          "first_name": "string",
          "last_name": "string"
        }
      }
      ```
    - Failure: 400 Bad Request
      ```json
      {
        "message": "Error message."
      }
      ```

- **Login**
  - **URL:** `/api/login`
  - **Method:** `POST`
  - **Request Body:**
    ```json
    {
      "email": "string",
      "password": "string"
    }
    ```
  - **Response:**
    - Success: 200 OK
      ```json
      {
        "access_token": "string",
        "refresh_token": "string",
        "token_type": "bearer"
      }
      ```
    - Failure: 401 Unauthorized
      ```json
      {
        "message": "Invalid credentials."
      }
      ```

- **Logout**
  - **URL:** `/api/logout`
  - **Method:** `POST`
  - **Request Body:** `None`
  - **Response:**
    - Success: 200 OK
      ```json
      {
        "message": "User logged out successfully."
      }
      ```
    - Failure: 401 Unauthorized
      ```json
      {
        "message": "Error message."
      }
      ```

### Community Management

- **Create Community**
  - **URL:** `/api/communities`
  - **Method:** `POST`
  - **Request Body:**
    ```json
    {
      "name": "string",
      "description": "string"
    }
    ```
  - **Response:**
    - Success: 201 Created
      ```json
      {
        "message": "Community created successfully.",
        "data": {
          "id": "integer",
          "name": "string",
          "description": "string",
          "created_by": "integer"
        }
      }
      ```
    - Failure: 400 Bad Request
      ```json
      {
        "message": "Error message."
      }
      ```

- **Join Community**
  - **URL:** `/api/communities/{community_id}/join`
  - **Method:** `POST`
  - **Request Body:** `None`
  - **Response:**
    - Success: 200 OK
      ```json
      {
        "message": "Joined community successfully."
      }
      ```
    - Failure: 400 Bad Request
      ```json
      {
        "message": "Error message."
      }
      ```

- **List All Communities**
  - **URL:** `/api/communities`
  - **Method:** `GET`
  - **Request Body:** `None`
  - **Response:**
    - Success: 200 OK
      ```json
      {
        "message": "Communities retrieved successfully.",
        "data": [
          {
            "id": "integer",
            "name": "string",
            "description": "string",
            "created_by": "integer",
            "date_created": "datetime"
          },
          ...
        ]
      }
      ```
    - Failure: 400 Bad Request
      ```json
      {
        "message": "Error message."
      }
      ```

- **Retrieve Community by Name**
  - **URL:** `/api/communities/{name}`
  - **Method:** `GET`
  - **Request Body:** `None`
  - **Response:**
    - Success: 200 OK
      ```json
      {
        "message": "Community retrieved successfully.",
        "data": {
          "id": "integer",
          "name": "string",
          "description": "string",
          "created_by": "integer",
          "date_created": "datetime"
        }
      }
      ```
    - Failure: 404 Not Found
      ```json
      {
        "message": "Community not found."
      }
      ```

### Discussion Management

- **Create Topic**
  - **URL:** `/api/communities/{community_id}/topics`
  - **Method:** `POST`
  - **Request Body:**
    ```json
    {
      "title": "string",
      "content": "string"
    }
    ```
  - **Response:**
    - Success: 201 Created
      ```json
      {
        "message": "Topic created successfully.",
        "data": {
          "id": "integer",
          "title": "string",
          "content": "string",
          "community_id": "integer",
          "created_by": "integer"
        }
      }
      ```
    - Failure: 400 Bad Request
      ```json
      {
        "message": "Error message."
      }
      ```

- **Create Post**
  - **URL:** `/api/topics/{topic_id}/posts`
  - **Method:** `POST`
  - **Request Body:**
    ```json
    {
      "content": "string"
    }
    ```
  - **Response:**
    - Success: 201 Created
      ```json
      {
        "message": "Post created successfully.",
        "data": {
          "id": "integer",
          "content": "string",
          "topic_id": "integer",
          "created_by": "integer"
        }
      }
      ```
    - Failure: 400 Bad Request
      ```json
      {
        "message": "Error message."
      }
      ```

- **Create Reply**
  - **URL:** `/api/posts/{post_id}/replies`
  - **Method:** `POST`
  - **Request Body:**
    ```json
    {
      "content": "string"
    }
    ```
  - **Response:**
    - Success: 201 Created
      ```json
      {
        "message": "Reply created successfully.",
        "data": {
          "id": "integer",
          "content": "string",
          "post_id": "integer",
          "created_by": "integer"
        }
      }
      ```
    - Failure: 400 Bad Request
      ```json
      {
        "message": "Error message."
      }
      ```

### Notifications

- **Create Notification**
  - **URL:** `/api/communities/{community_id}/notifications`
  - **Method:** `POST`
  - **Request Body:**
    ```json
    {
      "message": "string"
    }
    ```
  - **Response:**
    - Success: 201 Created
      ```json
      {
        "message": "Notification created successfully.",
        "data": {
          "id": "integer",
          "message": "string",
          "community_id": "integer",
          "created_by": "integer"
        }
      }
      ```
    - Failure: 400 Bad Request
      ```json
      {
        "message": "Error message."
      }
      ```



  <img width="989" alt="database design for the forum" src="https://dbdiagram.io/d/66914a259939893daec898a0">

