# Auth API

## Introduction
This project is a user authentication and management API built using FastAPI. It includes endpoints for user signup, login, logout, and token refresh functionalities. The API is designed to be secure and efficient, making use of JWT tokens for authentication.

## Team
- Member 1
- Member 2
- Member 3
- Member 4
- Member 5

## Table of Contents
- [Introduction](#introduction)
- [Team](#team)
- [API Design](#api-design)
  - [Endpoints](#endpoints)
  - [Schemas](#schemas)
  - [Security](#security)
- [Database Design](#database-design)
- [Contribution Guidelines](#contribution-guidelines)
- [Setup](#setup)
- [License](#license)

## API Design



### Endpoints

#### `POST /signup`
- **Description**: Create a new user.
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "string",
    "name": "John Doe"
  }
