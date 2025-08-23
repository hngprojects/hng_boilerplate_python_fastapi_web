from sqlalchemy import Column, String, Text, ForeignKey, Enum as SqlAlchemyEnum
from api.v1.models.base_model import BaseTableModel
from enum import Enum


class ReportStatusEnum(Enum):
    resolved = "resolved"
    pending = "pending"


class Report(BaseTableModel):

    __tablename__ = "reports"

    reported_by = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    reported_user = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    reason = Column(String, nullable=False)
    status = Column(SqlAlchemyEnum(ReportStatusEnum), default=ReportStatusEnum.pending)
