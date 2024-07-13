# Your Project API

Welcome to the documentation for Your Project API. This API provides endpoints for user authentication, message handling, payment processing, user management, organization management, and various other functionalities.

## Base URL

The base URL for the API is: `https://virtserver.swaggerhub.com/SUNDINOH_1/ForumAPI/1.0.0`

## Endpoints

### Authentication

#### User Login

*   **Endpoint:** `/auth/login`
*   **Method:** `POST`
*   **Description:** User login
*   **Request Body:**
    
    ```json
    {
      "username": "string",
      "password": "string"
    }
    ```
*   **Responses:**
    *   `200`: Login successful
    *   `401`: Unauthorized

#### User Registration

*   **Endpoint:** `/auth/register`
*   **Method:** `POST`
*   **Description:** User registration
*   **Request Body:**
    
    ```json
    {
      "username": "string",
      "email": "string",
      "password": "string"
    }
    ```
*   **Responses:**
    *   `200`: Registration successful
    *   `400`: Bad request

#### Reset User Password

*   **Endpoint:** `/auth/reset-password`
*   **Method:** `POST`
*   **Description:** Reset user password
*   **Request Body:**
    
    ```json
    {
      "email": "string"
    }
    ```
*   **Responses:**
    *   `200`: Password reset successful
    *   `400`: Bad request

### Messages

#### Get All Messages

*   **Endpoint:** `/messages`
*   **Method:** `GET`
*   **Description:** Get all messages
*   **Responses:**
    *   `200`: List of messages

#### Create a New Message

*   **Endpoint:** `/messages`
*   **Method:** `POST`
*   **Description:** Create a new message
*   **Request Body:**
    
    ```json
    {
      "sender": "string",
      "content": "string"
    }
    ```
*   **Responses:**
    *   `201`: Message created
    *   `400`: Bad request

#### Get a Message by ID

*   **Endpoint:** `/messages/{id}`
*   **Method:** `GET`
*   **Description:** Get a message by ID
*   **Parameters:**
    *   `id` (path, required): integer
*   **Responses:**
    *   `200`: Retrieved message
    *   `404`: Message not found

#### Update a Message

*   **Endpoint:** `/messages/{id}`
*   **Method:** `PUT`
*   **Description:** Update a message
*   **Parameters:**
    *   `id` (path, required): integer
*   **Request Body:**
    
    ```json
    {
      "sender": "string",
      "content": "string"
    }
    ```
*   **Responses:**
    *   `200`: Message updated
    *   `400`: Bad request

#### Delete a Message

*   **Endpoint:** `/messages/{id}`
*   **Method:** `DELETE`
*   **Description:** Delete a message
*   **Parameters:**
    *   `id` (path, required): integer
*   **Responses:**
    *   `204`: Message deleted
    *   `404`: Message not found

### Payments

#### Get All Payments

*   **Endpoint:** `/payments`
*   **Method:** `GET`
*   **Description:** Get all payments
*   **Responses:**
    *   `200`: List of payments

#### Create a New Payment

*   **Endpoint:** `/payments`
*   **Method:** `POST`
*   **Description:** Create a new payment
*   **Request Body:**
    
    ```json
    {
      "amount": "number",
      "description": "string"
    }
    ```
*   **Responses:**
    *   `201`: Payment created
    *   `400`: Bad request

#### Get a Payment by ID

*   **Endpoint:** `/payments/{id}`
*   **Method:** `GET`
*   **Description:** Get a payment by ID
*   **Parameters:**
    *   `id` (path, required): integer
*   **Responses:**
    *   `200`: Retrieved payment
    *   `404`: Payment not found

#### Update a Payment

*   **Endpoint:** `/payments/{id}`
*   **Method:** `PUT`
*   **Description:** Update a payment
*   **Parameters:**
    *   `id` (path, required): integer
*   **Request Body:**
    
    ```json
    {
      "amount": "number",
      "description": "string"
    }
    ```
*   **Responses:**
    *   `200`: Payment updated
    *   `400`: Bad request

#### Delete a Payment

*   **Endpoint:** `/payments/{id}`
*   **Method:** `DELETE`
*   **Description:** Delete a payment
*   **Parameters:**
    *   `id` (path, required): integer
*   **Responses:**
    *   `204`: Payment deleted
    *   `404`: Payment not found

### Users

#### Get All Users

*   **Endpoint:** `/users`
*   **Method:** `GET`
*   **Description:** Get all users
*   **Responses:**
    *   `200`: List of users

#### Create a New User

*   **Endpoint:** `/users`
*   **Method:** `POST`
*   **Description:** Create a new user
*   **Request Body:**
    
    ```json
    {
      "username": "string",
      "email": "string",
      "password": "string"
    }
    ```
*   **Responses:**
    *   `201`: User created
    *   `400`: Bad request

#### Get a User by ID

*   **Endpoint:** `/users/{id}`
*   **Method:** `GET`
*   **Description:** Get a user by ID
*   **Parameters:**
    *   `id` (path, required): integer
*   **Responses:**
    *   `200`: Retrieved user
    *   `404`: User not found

#### Update a User

*   **Endpoint:** `/users/{id}`
*   **Method:** `PUT`
*   **Description:** Update a user
*   **Parameters:**
    *   `id` (path, required): integer
*   **Request Body:**
    
    ```json
    {
      "username": "string",
      "email": "string",
      "password": "string"
    }
    ```
*   **Responses:**
    *   `200`: User updated
    *   `400`: Bad request

#### Delete a User

*   **Endpoint:** `/users/{id}`
*   **Method:** `DELETE`
*   **Description:** Delete a user
*   **Parameters:**
    *   `id` (path, required): integer
*   **Responses:**
    *   `204`: User deleted
    *   `404`: User not found

### Organizations

#### Get All Organizations

*   **Endpoint:** `/organizations`
*   **Method:** `GET`
*   **Description:** Get all organizations
*   **Responses:**
    *   `200`: List of organizations

#### Create a New Organization

*   **Endpoint:** `/organizations`
*   **Method:** `POST`
*   **Description:** Create a new organization
*   **Request Body:**
    
    ```json
    {
      "name": "string",
      "description": "string"
    }
    ```
*   **Responses:**
    *   `201`: Organization created
    *   `400`: Bad request

#### Get an Organization by ID

*   **Endpoint:** `/organizations/{id}`
*   **Method:** `GET`
*   **Description:** Get an organization by ID
*   **Parameters:**
    *   `id` (path, required): integer
*   **Responses:**
    *   `200`: Retrieved organization
    *   `404`: Organization not found

#### Update an Organization

*   **Endpoint:** `/organizations/{id}`
*   **Method:** `PUT`
*   **Description:** Update an organization
*   **Parameters:**
    *   `id` (path, required): integer
*   **Request Body:**
    
    ```json
    {
      "name": "string",
      "description": "string"
    }
    ```
*   **Responses:**
    *   `200`: Organization updated
    *   `400`: Bad request

#### Delete an Organization

*   **Endpoint:** `/organizations/{id}`
*   **Method:** `DELETE`
*   **Description:** Delete an organization
*   **Parameters:**
    *   `id` (path, required): integer
*   **Responses:**
    *   `204`: Organization deleted
    *   `404`: Organization not found

### Superadmin

#### Get Superadmin Details

*   **Endpoint:** `/superadmin`
*   **Method:** `GET`
*   **Description:** Get superadmin details
*   **Responses:**
    *   `200`: Superadmin details retrieved

### Settings

#### Get Settings

*   **Endpoint:** `/settings`
*   **Method:** `GET`
*   **Description:** Get settings
*   **Responses:**
    *   `200`: Settings retrieved

#### Update Settings

*   **Endpoint:** `/settings`
*   **Method:** `PUT`
*   **Description:** Update settings
*   **Request Body:**
    
    ```json
    {
      "setting_name": "string",
      "setting_value": "string"
    }
    ```
*   **Responses:**
    *   `200`: Settings updated
    *   `400`: Bad request

### Profile

#### Get Profile Settings

*   **Endpoint:** `/profile`
*   **Method:** `GET`
*   **Description:** Get profile settings
*   **Responses:**
    *   `200`: Profile settings retrieved

#### Update Profile Settings

*   **Endpoint:** `/profile`
*   **Method:** `PUT`
*   **Description:** Update profile settings
*   **Request Body:**
    
    ```json
    {
      "field_name": "string",
      "field_value": "string"
    }
    ```
*   **Responses:**
    *   `200`: Profile settings updated
    *   `400`: Bad request

### Landing Page

#### Get Landing Page Details

*   **Endpoint:** `/landing`
*   **Method:** `GET`
*   **Description:** Get landing page details
*   **Responses:**
    *   `200`: Landing page details retrieved

### Contact

#### Get Contact Details

*   **Endpoint:** `/contact`
*   **Method:** `GET`
*   **Description:** Get contact details
*   **Responses:**
    *   `200`: Contact details retrieved

### GDPR

#### Get GDPR Details

*   **Endpoint:** `/gdpr`
*   **Method:** `GET`
*   **Description:** Get GDPR details
*   **Responses:**
    *   `200`: GDPR details retrieved

### Dashboard

#### Get Basic Dashboard Details

*   **Endpoint:** `/dashboard`
*   **Method:** `GET`
*   **Description:** Get basic dashboard details
*   **Responses:**
    *   `200`: Basic dashboard details retrieved

### Waitlist

#### Get Waitlist Details

*   **Endpoint:** `/waitlist`
*   **Method:** `GET`
*   **Description:** Get waitlist details
*   **Responses:**
    *   `200`: Waitlist details retrieved

### Invitation

#### Send Invitation

*   **Endpoint:** `/invite`
*   **Method:** `POST`
*   **Description:** Send invitation
*   **Request Body:**
    
    ```json
    {
      "email": "string"
    }
    ```
*   **Responses:**
    *   `200`: Invitation sent
    *   `400`: Bad request

#### Generate Invite Link

*   **Endpoint:** `/invite-link`
*   **Method:** `POST`
*   **Description:** Generate invite link
*   **Request Body:**
    
    ```json
    {
      "email": "string"
    }
    ```
*   **Responses:**
    *   `200`: Invite link generated
    *   `400`: Bad request

### Export

#### Export User Data

*   **Endpoint:** `/export`
*   **Method:** `GET`
*   **Description:** Export user data
*   **Responses:**
    *   `200`: User data exported

### Random Data

#### Get Random Data Associated with User

*   **Endpoint:** `/random-data`
*   **Method:** `GET`
*   **Description:** Get random data associated with user
*   **Responses:**
    *   `200`: Random data retrieved

#### Get a Single Random Data by ID

*   **Endpoint:** `/random-data/{id}`
*   **Method:** `GET`
*   **Description:** Get a single random data by ID
*   **Parameters:**
    *   `id` (path, required): integer
*   **Responses:**
    *   `200`: Retrieved random data
    *   `404`: Random data not found

### Other Data

#### Get Other Data List with Search and Sorting

*   **Endpoint:** `/other-data`
*   **Method:** `GET`
*   **Description:** Get other data list with search and sorting
*   **Responses:**
    *   `200`: Other data list retrieved

### Chart

#### Get Chart Data

*   **Endpoint:** `/chart`
*   **Method:** `GET`
*   **Description:** Get chart data
*   **Responses:**
    *   `200`: Chart data retrieved

### Content

#### Get Content Details

*   **Endpoint:** `/content`
*   **Method:** `GET`
*   **Description:** Get content details
*   **Responses:**
    *   `200`: Content details retrieved

#### Update Content Details

*   **Endpoint:** `/content`
*   **Method:** `PUT`
*   **Description:** Update content details
*   **Request Body:**
    
    ```json
    {
      "title": "string",
      "body": "string"
    }
    ```
*   **Responses:**
    *   `200`: Content details updated
    *   `400`: Bad request

### Notifications

#### Get Notifications

*   **Endpoint:** `/notifications`
*   **Method:** `GET`
*   **Description:** Get notifications
*   **Responses:**
    *   `200`: Notifications retrieved

### Blog

#### Get Blog Posts

*   **Endpoint:** `/blog`
*   **Method:** `GET`
*   **Description:** Get blog posts
*   **Responses:**
    *   `200`: List of blog posts

## Components

### Schemas

#### LoginRequest

```json
{
  "username": "string",
  "password": "string"
}
