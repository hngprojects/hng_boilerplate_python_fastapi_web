from pydantic import BaseModel
from typing import Dict


class CustomSections(BaseModel):
    stats: Dict[str, int]
    services: Dict[str, str]


class AboutPageContent(BaseModel):
    title: str
    introduction: str
    custom_sections: CustomSections
    last_update: str
    status_code: int = 200
    message: str = "Retrieved About Page content successfully"

    class config:
        about_page_content = {
            "title": "More Than Just A BoilerPlate",
            "introduction": "Welcome to Hng Boilerplate, where passion meets innovation.",
            "custom_sections": {
                "stats": {
                    "years_in_business": 10,
                    "customers": 75000,
                    "monthly_blog_readers": 100000,
                    "social_followers": 1200000
                },
                "services": {
                    "title": "Trained to Give You The Best",
                    "description": "Since our founding, Hng Boilerplate has been dedicated to constantly evolving to stay ahead of the curve."
                }
            },
            "last_update": "2024-07-22T00:00:00Z"
        }
