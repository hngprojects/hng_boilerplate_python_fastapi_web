from pydantic import BaseModel, field_validator
import bleach
from enum import Enum

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


def sanitize_html(template: str) -> str:
    cleaned_html = bleach.clean(
        template,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=False
    )
    return cleaned_html

class TemplateStatusEnum(str, Enum):
    online = 'online'
    offline = 'offline'

class EmailTemplateSchema(BaseModel):
    title: str
    template: str
    type: str
    template_status: TemplateStatusEnum | None = TemplateStatusEnum.online  # Default to 'online'

    @field_validator("template")
    @classmethod
    def template_validator(cls, value):
        return sanitize_html(value)
