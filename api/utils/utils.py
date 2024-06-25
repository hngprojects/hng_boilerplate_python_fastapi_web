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