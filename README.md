# Code of Conduct

## Introduction

Welcome to our FastAPI project! Our community values respectful and constructive collaboration. This Code of Conduct establishes clear guidelines for acceptable behavior and outlines the conventions and methods to be used in this project. By participating, you agree to abide by this Code of Conduct.

We encourage participants to read the `README.md` in branch `Setup-workflow` in this repo before pushing code and pulling code.
 

## Conventions

***Code Style***

***Language***: The project uses Python.

***Indentation***: Use 4 spaces for indentation.

***Line Length***: Limit lines to 79 characters.


## Naming Conventions

- **Variables and Functions**: Use snake_case (e.g., my_function).

- **Classes**: Use PascalCase (e.g., MyClass).

- **Constants**: Use UPPER_CASE (e.g., MY_CONSTANT).

- **Comments**: Use # for single-line comments and ''' or """ for docstrings.

## Git Commit Messages

- Format: Follow the conventional commits standard.



## Branching and Pull Requests

***Branch Naming***:

- **Feature Branches**: feature/branch-name

- **Bug Fix Branches**: bugfix/branch-name

- **Hotfix Branches**: hotfix/branch-name

- **Pull Request Titles**: Use the format [Type]: Brief description (e.g., [Bugfix]: Fix user login issue,  [Feat]: add user login).




## PR MESSAGE FORMAT

**Title**: Fix token validation issue in login endpoint

**Description**:
- **Purpose**:
   - Example: This PR resolves an issue where users were unable to log in due to incorrect token validation.

- **Changes**: 
  - Example: Refactored token validation logic in the login endpoint.

- **Impact**:
   - Example: Ensures users can log in successfully with valid credentials. No impact on other endpoints.

- **Testing**:
   - Example: Added unit tests for token validation; all tests pass.

- **Additional Information**:
   - Example: Related to issue #123.





**Endpoint Naming**:

- Use descriptive and concise names.

- Use nouns to represent the resources being acted upon. Example: /users/orders/{order_id}

### HTTP Methods:

Use HTTP methods according to their purpose:

- GET for retrieving resources.
- POST for creating resources.
- PUT for updating resources.
- DELETE for deleting resources.

### Status Codes:

- Use appropriate HTTP status codes to represent the outcome of the operations.

- **Example**: 200 OK for successful operations, 201 Created for successful resource creation, 404 Not Found for missing resources.

**Path Parameters**:
- Use curly braces {} to define path parameters.
         Example: /users/{user_id}
 

## Testing

- **Test Framework**: Use pytest for testing.

- **Pytest**: Write Pytest for all new features and bug fixes.

- **Test Coverage**: Ensure at least 100% test coverage.

### Documentation

- **Docstrings**: Use docstrings for all public functions and classes.

- **Update Frequency**: Update documentation with each significant change.

## Code Reviews

- **Review Process**: All code changes must be reviewed and approved by at least one mentor.

- **Review Criteria**: Ensure changes follow the project's coding conventions, are well-documented, and include appropriate tests.


## Conduct

- Be Respectful

- Treat all members of the community with respect and consideration.

- Refrain from demeaning, discriminatory, or harassing behavior and speech.

- Be Collaborative.

- Seek constructive feedback and be open to suggestions.


## Reach out to Team Member

Instances of you having questions reach out to the project maintainers on slack [@Sunday Mba, @joboy-dev, @TMCoded, @Modupe Akanni, @Olusegun Emmanuel]. All complaints will be reviewed promptly.

## Acknowledgment

By participating in this project, you agree to abide by this Code of Conduct and help foster a positive and productive community.
