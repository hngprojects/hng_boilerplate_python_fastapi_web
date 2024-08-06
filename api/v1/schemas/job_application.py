from typing_extensions import List
from pydantic import BaseModel

"""
Job application schemas
"""
from pydantic import BaseModel, ConfigDict
from typing import Union


class JobApplicationBase(BaseModel):
    """
    Schema for job application base
    """
    job_id: str
    applicant_name: str
    applicant_email: str
    resume_link: str
    portfolio_link: Union[str, None]
    cover_letter: Union[str, None]
    application_status: str


    model_config = ConfigDict(from_attributes=True)

class JobApplicationData(BaseModel):
    """
    Schema for job application data
    """

    page: int = 1
    per_page: int = 20
    total_pages: int = 0
    applications: List[JobApplicationBase] = []

class JobApplicationResponse(BaseModel):
    status_code: int = 200
    message: str
    success: bool = True
    data: JobApplicationData


class SingleJobAppResponse(BaseModel):
    """
    Single job application response schema
    """
    status: str
    message: str
    status_code: int
    data: JobApplicationBase