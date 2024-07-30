from typing import Any, List
from sqlalchemy.orm import Session

from api.utils.success_response import success_response


def paginated_response(db: Session, model, limit: int, skip: int):
    '''
    Custom response for pagination.\n
    This takes in four atguments:
        * items- this is your database query eg ```db.query(Product)```
        * limit- this is the number of items to fetch per page, this would be a query parameter
        * skip- this is the number of items to skip before fetching the next page of data. This would also
        be a query parameter
    '''

    query = db.query(model)
    total_items = query.count()
    items = query.offset(skip).limit(limit).all()
    # total_items = len(items)
    total_pages = int(total_items / limit) + (total_items % limit > 0)

    return success_response(
        status_code=200,
        message="Successfully fetched items",
        data={
            'pages': total_pages,
            "total": total_items,
            "skip": skip,
            "limit": limit,
            "data": items
        }
    )
