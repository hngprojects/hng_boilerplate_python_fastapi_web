<!--- Provide a general summary of your changes in the Title above -->

​

## Description

Implemented an API endpoint to update job post details using FastAPI. The endpoint allows authenticated users to update existing job posts by providing updated job details. Added appropriate permission checks to ensure only the job owner or an admin can update the job post. The endpoint handles both success and error responses based on the validity of the job post ID and the user's permissions.

​

## Related Issue (Link to issue ticket)

[Get job details](https://github.com/hngprojects/hng_boilerplate_python_fastapi_web/issues/63)

[Retrieve All Job Listings](https://github.com/hngprojects/hng_boilerplate_python_fastapi_web/issues/47)

​

## Motivation and Context

This change is required to allow users to correct or update job details in case of errors or changes. It ensures that job postings are kept accurate and up-to-date, improving the overall user experience and data integrity.
​

## How Has This Been Tested?

1. Successful update with a valid job ID and authenticated user.
2. Update attempt with an invalid job ID, returning a 404 Not Found response.
3. Unauthorized update attempt by a user who is not the owner or an admin, returning a 403 Forbidden response.
4. Update attempt with an invalid request body, returning a 422 Unprocessable Entity response.
​
Testing was done using pytest with a TestClient to simulate API requests and validate responses. The test environment included a mock database setup to ensure isolation and reliability of tests.

## Screenshots (if appropriate - Postman, etc):

​

## Types of changes

<!--- What types of changes does your code introduce? Put an `x` in all the boxes that apply: -->

- [ ] Bug fix (non-breaking change which fixes an issue)
- [X] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to change)
      ​

## Checklist:

<!--- Go over all the following points, and put an `x` in all the boxes that apply. -->
<!--- If you're unsure about any of these, don't hesitate to ask. We're here to help! -->

- [X] My code follows the code style of this project.
- [ ] My change requires a change to the documentation.
- [ ] I have updated the documentation accordingly.
- [x] I have read the **CONTRIBUTING** document.
- [X] I have added tests to cover my changes.
- [X] All new and existing tests passed.
