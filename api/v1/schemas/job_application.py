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

class SingleJobAppResponse(BaseModel):
    """
    Single job application response schema
    """
    status: str
    message: str
    status_code: int
    data: JobApplicationBase