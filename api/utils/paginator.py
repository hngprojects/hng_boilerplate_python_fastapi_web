from sqlalchemy.orm import Session

def total_row_count(model, organization_id, db: Session):
    return db.query(model).filter(model.organization_id == organization_id).filter(
        model.is_deleted == False).count()

def off_set(page: int, size: int):
    return (page-1)*size


def size_validator(size:int):
    if size < 0 or size > 100:
        return "page size must be between 0 and 100"
    return size


def page_urls(page: int, size: int, count: int, endpoint: str):
    paging = {}
    if (size + off_set(page, size)) >= count:
        paging['next'] = None
        if page > 1:
            paging['previous'] = f"{endpoint}?page={page-1}&size={size}"
        else:
            paging['previous'] = None
    else:
        paging['next'] = f"{endpoint}?page={page+1}&size={size}"
        if page > 1:
            paging['previous'] = f"{endpoint}?page={page-1}&size={size}"
        else:
            paging['previous'] = None

    return paging


def build_paginated_response(
    page: int, size: int, total: int, pointers: dict, items
) -> dict:
    response = {
        "page": page,
        "size": size,
        "total": total,
        "previous_page": pointers["previous"],
        "next_page": pointers["next"],
        "items": items,
    }

    return response