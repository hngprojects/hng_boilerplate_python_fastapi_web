This documentation will explain the API's purpose, its main features, and requiremens.

# PentaCoder User API Documentation

## Introduction
This project is a user authentication and management API built using FastAPI. It includes endpoints for user signup, login, logout, and token refresh functionalities. The API is designed to be secure and efficient, making use of JWT tokens for authentication.

## Team
- Victor
- Myles
- Wisdom
- Timi
- Adebola

## API Design

1.0.0

## Base URL

All API requests should be made to:
```
https://api.pentacoder.com/v1
```
## Authentication

Most endpoints in this API require authentication. The API uses JSON Web Tokens (JWT) fornauthentication. To authenticate, iclude the JWT token in the Authorization header of your requests:

```
Authorization: Bearer <your_jwt_token>
```
## Main Features

1. User Registration and Authentication
2. Social Authentication
3. Passwordless Authentication (Magic Link)
4. Profile Management
5. Contact Form Submission
6. Email Messaging
7. Payment Processing
8. Organization Management
9. Admin Functions

## Endpoints

### Authentication and Regisration
1. **POST /signup**
- **Description**: Create a new user.
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "string",
    "name": "John Doe"
  }
  ```
2. **POST /auth/login**
- Log in a user
- Required fields: email, password

3. **GET /auth/social/{provider}**
- Initial social authentication
- Supported providers: google, facebook, twitter

4. **POST /auth/magic-link**
- Send a magic link for passwordless authentication
- Required field: email

5. **POST /auth/magic-link/verify**
- Verify magic link and log in user
- Required field: token

6. **POST /logout**
- Log out a user (requires authentication)

7. **GET /auth/refresh-access-token**
- Refresh access token

### Profile Management

1. **GET /profile**
- Get user profile (requires authentication)

2. **PUT /profile**
- Update user profile (requires authentication)

3. **POST /profile/change-password**
- Change user password (requires authentication)

### Contact and Messaging

1. **POST /contact**
- Submit contact form

2. **POST /messaging/send-email**
- Send an email (requires authentication)

3. **GET /messaging/templates**
- List email templates (requires authentication)

### Payments

1. **POST /payments/create-checkout**
- Create a checkout session (PayStack) (requires authentication)

2. **GET /payments/history**
- Get user's payment history (requires authentication)

3. **GET /payments/{payment_id}**
- Get details of a specific payment (requires authentication)

### Organizations

1. **GET /organisations**
- List user's organizations (requires authentication)

2. **POST /organisations**
- Create a new organization (requires authentication)

### Admin Functions

1. **GET /admin/users**
- List all users (admin only)

2. **DELETE /admin/users/{user_id}**
- Delete a user {soft delete} (admin only)

3. **GET /admin/organisations**
- List all organisations (admin only)

4. **GET /admin/organisations/{org}_id/users**
- List users in an organisation (admin only)

5. **GET /admin/payments**
- List all payments (admin only)

6. **GET /admin/activity-log**
- Get activity log (admin only)

## Error Handling

The API uses standard HTTP response code to indicate the success of requests. In case of errors, the API will return a JSON object with details about the error, icluding the location of the error, an error message, and the error type.

Common error responses include:

- 400 Bad Request
- 401 Unauthorized
- 403 Forbidden
- 404 Not Found
- 422 Validation Error

## Requirements

To use this API, you will need:

1. An account with PentaCoder (for authentication)
2. API credentials (for accessing protected endpoints)
3. HTTPS support for secure communication
4. Ability to send and receive JSON data
5. Ability to handle JWT tokens for authentication
6. Integration with a payment provider (PayStack) for payment-related features

## Rate Limiting

The API documentation doesn't specify rate limiting details. IT's recommended to check with the API provider for any rate limiting policies

## Versioning

The documentation is for version 1.0.0 of the API. Future updates to the API may introduce new endpoints or modify existing ones.

## Support

For additional support or questions about the API, please contact the PentaCoder support team.

This documentation provides a comprehensive overview of the PentaCoder User API. Developers can use this as a guide to integrate user management, authentification, payments, and administrative functions into their applications.