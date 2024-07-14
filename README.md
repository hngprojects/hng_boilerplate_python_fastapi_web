# Team Gamma
We do hard things together

**Documentation following OpenAPI specifications**
https://abnurkan.github.io/HNG_STAGE3_API_TEST/

**Database Design**
https://imgur.com/a/90xhWlG

Openapi Yaml file is at the root of the folder

**Contributors**
* [jubriltayo](https://github.com/jubriltayo)
* [abnurkan](https://github.com/abnurkan)
* [algamawiy](https://github.com/algamawiy)
* [Kingsley-Opara](https://github.com/Kingsley-Opara)
* [Dricy](https://github.com/Dricy)


Group Gamma Comprehensive API and Database Design

# I. Introduction

This document outlines the API and database design for a comprehensive SaaS platform. The platform includes features such as user authentication, organization management, payments, messaging, and various user-centric functionalities.

API Documentation: OpenAPI 3.0.0

# II. API Design
Our API is designed using OpenAPI 3.0.0 specification. It provides a comprehensive set of endpoints to interact with various features of the SaaS platform.
Key Endpoints:

**API AND DATABASE DESIGN**

 API Design
 
1. Authentication
- POST /auth/signup - User registration.
- POST /auth/login - User login.
- POST /auth/social - Social authentication.
- POST /auth/magic-link - Magic link authentication.
- POST /auth/change-password - Change password.
- POST /auth/forgot-password - Request password reset.
- POST /auth/reset-password - Reset password using token.
2. Messaging
- POST /messages/email - Send email using default templates.
Payments
- POST /payments/stripe - Process Stripe payment.
- POST /payments/flutterwave - Process Flutterwave payment.
- POST /payments/lemonsqueezy - Process LemonSqueezy payment.
3. Users & Organisations
- GET /users - Retrieve a list of users.
- POST /users - Add a new user.
- GET /users/{id} - Retrieve a specific user.
- PUT /users/{id} - Update a specific user.
- DELETE /users/{id} - Delete a specific user.
4. Organisations
- GET /organisations - Retrieve a list of organisations.
- POST /organisations - Add a new organisation.
- GET /organisations/{id} - Retrieve a specific organisation.
- PUT /organisations/{id} - Update a specific organisation.
- DELETE /organisations/{id} - Delete a specific organisation.
5. Superadmin Interface
- GET /admin/users - Retrieve a list of all users.
- GET /admin/organisations - Retrieve a list of all organisations.
- GET /admin/payments - Retrieve a list of all payments.
- GET /admin/activity-log - Retrieve activity log.
6. Settings 
- GET /settings - Retrieve user settings.
- PUT /settings/{id] - Update user settings.
7. Profile
- GET /profile - Retrieve user profile.
- PUT /profile - Update user profile.
8. Landing Pages 
- GET /pages/privacy-policy - Retrieve privacy policy.
- GET /pages/about-us - Retrieve about us page.
9. Contact
- GET /pages/contact-us - Retrieve contact us page.
- POST /pages/contact-us - Submit a contact form.
10. GDPR Cookies
- GET /cookies - Retrieve cookie policy.
- POST /cookies/accept - Accept cookie policy.
11. Dashboard
- GET /dashboard - Retrieve user dashboard.
12. Waitlist
- POST /waitlist - Join waitlist.
13. Squeeze/Marketing Page
- GET /marketing - Retrieve marketing page.
14. Invite Flow
- POST /invite - Send an invite.
15. User Data Export
- GET /user-data/export - Export user data.
16. Random Data
- GET /random-data - Retrieve list of random data.
- GET /random-data/{id} - Retrieve a specific random data item.
- POST /random-data - Create random data.
- PUT /random-data/{id} - Update random data.
- DELETE /random-data/{id} - Delete random data.
17. Data Lists, 
- GET /data-list - Retrieve list of data with search and sorting.
18. Charts page
- GET /charts - Retrieve chart data.
19. Content Editing
- GET /content-edit - Retrieve content for editing.
- PUT /content-edit - Update content.
20. Notifications
- GET /notifications - Retrieve notifications.
- POST /notifications - Create notification.

- GET /notifications/{id} - Retrieve specific notifications.
- PUT /notifications/{id} - Update notification.
- DELETE /notifications/{id} - Delete notification.
21. Blog
- GET /blog - Retrieve blog posts.
- POST /blog - Create blog post.

- GET /blog/{id} - Retrieve a specific blog post.
- PUT /blog/{id} - Update blog post.
- DELETE /blog/{id} - Delete blog post.

22. Invite Link
-POST /invite-link - sent  invite link.
- GET /invite-link - Retrieve invite link.
23. Language and Region
- GET /language-region - Retrieve language and region settings.
- PUT /language-region - Update language and region settings.
24. Email Template Management
- GET /admin/email-templates - Retrieve email templates.
- POST /admin/email-templates - Create email template.
- PUT /admin/email-templates/{id} - Update email template.
- DELETE /admin/email-templates/{id} - Delete email template.




# III. Database Design

Our database is designed to support all the features of the SaaS platform efficiently. It includes tables for users, organizations, roles, payments, content management, and more.
Key Tables:

**DATABASE DESIGN**

Tables

1- Users:
  - id (Primary Key, Integer)
  - username (String, Not Null, Unique)
  - email (String, Not Null, Unique)
  - password (String, Not Null)
  - profile_picture (String, Nullable)
  - created_at (DateTime, Not Null)
  - updated_at (DateTime, Not Null)

2- Organisations:
  - id (Primary Key, Integer)
  - name (String, Not Null, Unique)
  - description (Text, Nullable)
  - created_at (DateTime, Not Null)
  - updated_at (DateTime, Not Null)

3- UserOrganisations:
  - id (Primary Key, Integer)
  - user_id (Foreign Key, Integer, References Users(id))
  - organisation_id (Foreign Key, Integer, References Organisations(id))
  - role (String, Not Null)

4- Sessions:
  - id (Primary Key, Integer)
  - user_id (Foreign Key, Integer, References Users(id))
  - token (String, Not Null)
  - created_at (DateTime, Not Null)
  - expires_at (DateTime, Not Null)

5- Messages:
  - id (Primary Key, Integer)
  - user_id (Foreign Key, Integer, References Users(id))
  - subject (String, Not Null)
  - body (Text, Not Null)
  - sent_at (DateTime, Not Null)

6- Payments:
  - id (Primary Key, Integer)
  - user_id (Foreign Key, Integer, References Users(id))
  - amount (Decimal, Not Null)
  - payment_method (String, Not Null)
  - payment_status (String, Not Null)
  - created_at (DateTime, Not Null)

7- AdminActivityLog:
  - id (Primary Key, Integer)
  - admin_id (Foreign Key, Integer, References Users(id))
  - action (String, Not Null)
  - timestamp (DateTime, Not Null)

8- Settings:
  - id (Primary Key, Integer)
  - user_id (Foreign Key, Integer, References Users(id))
  - setting_key (String, Not Null)
  - setting_value (String, Not Null)

9- Pages:
  - id (Primary Key, Integer)
  - title (String, Not Null)
  - content (Text, Not Null)
  - slug (String, Not Null, Unique)

10- Cookies:
  - id (Primary Key, Integer)
  - user_id (Foreign Key, Integer, References Users(id))
  - accepted (Boolean, Not Null)
  - accepted_at (DateTime, Not Null)

11- Waitlist:
  - id (Primary Key, Integer)
  - email (String, Not Null, Unique)
  - joined_at (DateTime, Not Null)

12- RandomData:
  - id (Primary Key, Integer)
  - user_id (Foreign Key, Integer, References Users(id))
  - data (JSON, Not Null)
  - created_at (DateTime, Not Null)

13- DataList:
  - id (Primary Key, Integer)
  - user_id (Foreign Key, Integer, References Users(id))
  - data (JSON, Not Null)
  - created_at (DateTime, Not Null)


14- Charts:
  - id (Primary Key, Integer)
  - user_id (Foreign Key, Integer, References Users(id))
  - data (JSON, Not Null)
  - created_at (DateTime, Not Null)

15- Notifications:
  - id (Primary Key, Integer)
  - user_id (Foreign Key, Integer, References Users(id))
  - title (String, Not Null)
  - message (Text, Not Null)
  - read (Boolean, Not Null)
  - created_at (DateTime, Not Null)

16- BlogPosts:
  - id (Primary Key, Integer)
  - author_id (Foreign Key, Integer, References Users(id))
  - title (String, Not Null)
  - content (Text, Not Null)
  - created_at (DateTime, Not Null)
  - updated_at (DateTime, Not Null)

17- InviteLinks:
  - id (Primary Key, Integer)
  - user_id (Foreign Key, Integer, References Users(id))
  - token (String, Not Null)
  - expires_at (DateTime, Not Null)

18- LanguageRegionSettings:
  - id (Primary Key, Integer)
  - user_id (Foreign Key, Integer, References Users(id))
  - language (String, Not Null)
  - region (String, Not Null)

19- EmailTemplates:
  - id (Primary Key, Integer)
  - name (String, Not Null, Unique)
  - subject (String, Not Null)
  - body (Text, Not Null)
  - created_at (DateTime, Not Null)
  - updated_at (DateTime, Not Null)

**Entity Relationship Diagram (ERD) Overview**

- Users (1) ⟷ (0..1) UserProfile
- Users (1) ⟷ (0..*) UserSession
- Users (1) ⟷ (0..*) Payments
- Users (1) ⟷ (0..*) OrganisationMemberships
- Users (1) ⟷ (0..*) Messages
- Users (1) ⟷ (0..*) MagicLink
- Users (1) ⟷ (0..*) LanguageRegionSettings
- Users (1) ⟷ (0..*) RandomData
- Users (1) ⟷ (0..*) Notifications
- Organisations (1) ⟷ (0..*) OrganisationMemberships
- Organisations (1) ⟷ (0..*) Payments

**Full SQL Schema**

Entity Relationship Diagram:

[Link to your ERD image or diagram](https://imgur.com/a/90xhWlG)

# IV. Implementation Details
Architecture: [e.g., Microservices, Monolithic]
Authentication: JWT-based authentication for API endpoints
Background Jobs: [e.g., Celery for asynchronous tasks]
Caching: [e.g., Redis for caching frequently accessed data]

V. Setup and Usage

Clone the repository:

```git clone https://github.com/jubriltayo/hng_boilerplate_python_fastapi_web.git```

Create a virtual environment.

    ```python3 -m venv .venv```

Activate virtual environment.

    ```source /path/to/venv/bin/activate```

Install project dependencies  ```pip install -r requirements.txt```

Create a .env file by copying the .env.sample file cp .env.sample .env

Set up the database:
 ```alembic init alembic```

 ```alembic revision --autogenerate -m "Initial migration"```

```alembic upgrade head```

Start server.
```python main.py```

Access the API documentation:
[URL or command to access API documentation](https://abnurkan.github.io/HNG_STAGE3_API_TEST/)


# VI. Contributing
We welcome contributions to improve the API and database design. Please follow these steps to contribute:
Fork the repository
Create a new branch (git checkout -b AmazingFeature)
Make your changes
Commit your changes (git commit -m 'Add some AmazingFeature')
Push to the branch (git push origin AmazingFeature)
Open a Pull Request
Please ensure your code adheres to our coding standards and includes appropriate tests.



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

