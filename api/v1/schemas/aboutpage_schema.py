from pydantic import BaseModel, Field
from typing import Dict, Any

class AboutPageUpdate(BaseModel):
    """
    A Pydantic model representing an update to an About page.

    Attributes:
        title (str): The title of the About page.
        introduction (str): The introduction text for the About page.
        custom_sections (Dict[str, Any]): A dictionary containing custom sections for the About page.
    """
    
    title: str = Field(...)
    introduction: str = Field(...)
    custom_sections: Dict[str, Any] = Field(...)

    class Config:
        json_schema_extra = {
            "examples": {
                "example_1": {
                    "title": "More Than Just A Boilerplate",
                    "introduction": "Welcome to Hng Boilerplate, where passion meets innovation.",
                    "custom_sections": {
                        "stats": {
                            "years_in_business": 10,
                            "customers": 75000,
                            "monthly_blog_readers": 10000,
                            "social_followers": 120000
                        },
                        "services": {
                            "title": "Trained To Give You The Best",
                            "description": "Since our founding, Hng Boilerplate has been dedicated to constantly evolving to stay ahead of the curve."
                        }
                    }
                }
            }
        }
