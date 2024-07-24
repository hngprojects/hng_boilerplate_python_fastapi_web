## Description
Implement endpoints for all CRUD operation on comments model associated with a blog post

## Acceptance Criteria
### API implementation
- POST api/v1/comments/{blog_id}
- GET api/v1/comments/{blog_id}
- GET api/v1/comments/{comment_id}
- PUT api/v1/comments/{comment_id}
- DELETE api/v1/comments/{comment_id}

> Ensure all endpoints are only accessible to authenticated users
### Add comments to blog
#### Request body
```json
{
     "content": "comment about the blog"
}
```

#### Successful response
```json
{    
      "status_code": 201,
      "message": "comment created"
}
```
 
### Get blogs comment
#### Query parameters
- page: int
- per_page: int
> page is a parameter indicating which page of comment of the blog you want to retrieve (default = 1)
> per_page is a query param indicating number of comments per page (default = 10)
#### Successful Response
```json
{
    "status_code": 200,
    "pagination": {
         "pages": 9,
         "current_page": 7,
         "per_page": 5
    },
    "comments": [
    {
        "id": 1,
        "content": "great comment",
        "user": {
            "username": "...",
                       
        }
    }
    {
        "id": 2,
        "content": "great comment",
        "user": {
            "username": "...",
                       
        }
    }
]

}
```
### Get comment by id
#### Successful Response

```json
{    
    "status_code": 200, 
    "comments": {
        "id": 1,
        "content": "great comment",
        "user": {
            "username": "...",
        },
   }
}
```
### Update comment by id
#### Request body
```json
{
     "content": "comment about the blog"
}
```
#### Successful Response

```json
{  
    "status_code": 200,  
    "comments": {
        "id": 1,
        "content": "great comment",
        "user": {
                "username": "...",
        },
   },
}
```
### Delete comment by id
#### Successful Response

```json
{      
      
}
```
- status_code: 204

## Purpose 
The purpose of this task is to implement endpoints for all CRUD operation on comments model associated with a blog post

## Requirements 
- [ ] Implement add comment to blog endpoint 
- [ ] Implement get comments of a blog endpoint
- [ ] Implement get comment by id endpoint
- [ ] Implement update comment by id endpoint
- [ ] Implement delete comment by id endpoint
- [ ] Ensure all endpoints are only accessible to authenticated users
- [ ] Implement proper error handling and user feedback for all operations 

## Expected Outcome 
Users can add, view, update and delete comments associated with a blog post
 
## Status Codes and Error Response 
### 200, 204, 201 
[successful responses are already defined for each endpoint above]

### 400 Bad Request 
```json 
{
    "status_code": 400, 
    "error": "Invalid request", 
    "message": "specific error message" 
}


### 401 Unauthorized 
```json 
{
    "status_code": 401, 
    "error": "Unauthorized", 
    "message": "Authentication required" 
}
```

### 500 Internal Server Error 
```json 
{
    "status_code": 500, 
    "error": "Internal Server Error", 
    "message": "An error occurred while processing your request" 
}
```

## Testing 
- [ ] Test all endpoints using postman
- [ ] Test all endpoints using unit tests
