from pydantic import BaseModel, field_validator
import bleach

ALLOWED_TAGS = [
    'a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i', 'li', 
    'ol', 'strong', 'ul', 'h1', 'h2', 'h3', 'p', 'br', 'span', 'div', 'table',
    'tr', 'td'
]
ALLOWED_ATTRIBUTES = {
    'a': ['style', 'href', 'title', 'target'],
    'img': ['src', 'alt'],
    'span': ['style'],
    'div': ['style'],
    'p': ['style'],
    'table': ['style'],
    'tr': ['style'],
    'td': ['style'],
}
ALLOWED_STYLES = [
    'color', 'font-weight', 'background-color', 'font-size', 'margin', 'padding'
]


def sanitize_html(html_content: str) -> str:
    cleaned_html = bleach.clean(
        html_content,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=False
    )
    return cleaned_html

class EmailTemplateSchema(BaseModel):

    name: str
    html_content: str

    @field_validator("html_content")
    @classmethod
    def html_content_validator(cls, value):
        return sanitize_html(value)
