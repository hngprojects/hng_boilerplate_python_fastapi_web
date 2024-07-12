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

### Database Design

```plaintext
Table Users {
  id int [pk, increment]
  username varchar(50) [unique, not null]
  email varchar(100) [unique, not null]
  password varchar(255) [not null]
  first_name varchar(50)
  last_name varchar(50)
  date_created timestamp [default: `current_timestamp`]
  last_updated timestamp [default: `current_timestamp`]
}

Table Communities {
  id int [pk, increment]
  name varchar(100) [not null]
  description text
  created_by int [not null, ref: > Users.id]
  date_created timestamp [default: `current_timestamp`]
}

Table UserCommunity {
  community_id int [not null, ref: > Communities.id]
  user_id int [not null, ref: > Users.id]
  role varchar(50) [default: 'member']
  indexes {
    (community_id, user_id) [pk]
  }
}

Table Topics {
  id int [pk, increment]
  title varchar(255) [not null]
  content text [not null]
  community_id int [not null, ref: > Communities.id]
  created_by int [not null, ref: > Users.id]
  date_created timestamp [default: `current_timestamp`]
}

Table Posts {
  id int [pk, increment]
  content text [not null]
  topic_id int [not null, ref: > Topics.id]
  created_by int [not null, ref: > Users.id]
  date_created timestamp [default: `current_timestamp`]
}

Table Replies {
  id int [pk, increment]
  content text [not null]
  post_id int [not null, ref: > Posts.id]
  created_by int [not null, ref: > Users.id]
  date_created timestamp [default: `current_timestamp`]
}

Table Notifications {
  id int [pk, increment]
  message text [not null]
  community_id int [not null, ref: > Communities.id]
  created_by int [not null, ref: > Users.id]
  date_created timestamp [default: `current_timestamp`]
}
