from typing import Any, Dict, List, Optional
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from api.utils.success_response import success_response


def paginated_response(
    db: Session,
    model,
    skip: int,
    limit: int,
    filters: Optional[Dict[str, Any]]=None
):
    
    '''
    Custom response for pagination.\n
    This takes in four atguments:
        * db- this is the database session
        * model- this is the database table model eg Product, Organization```
        * limit- this is the number of items to fetch per page, this would be a query parameter
        * skip- this is the number of items to skip before fetching the next page of data. This would also
        be a query parameter
        * filters- this is an optional dictionary of filters to apply to the query

    Example use:
        **Without filter**
        ``` python
        return paginated_response(
            db=db,
            model=Product,
            limit=limit,
            skip=skip
        )
        ```

        **With filter**
        ``` python
        return paginated_response(
            db=db,
            model=Product,
            limit=limit,
            skip=skip,
            filters={'org_id': org_id}
        )
        ```
    '''

    query = db.query(model)

    if filters:
        # Apply filters
        for attr, value in filters.items():
            if value is not None:
                query = query.filter(getattr(model, attr).like(f"%{value}%"))
    
    total = query.count()
    results = jsonable_encoder(query.offset(skip).limit(limit).all())
    total_pages = int(total / limit) + (total % limit > 0)

    return success_response(
        status_code=200,
        message="Successfully fetched items",
        data={
            'pages': total_pages,
            "total": total,
            "skip": skip,
            "limit": limit,
            "items": results
        }
    )