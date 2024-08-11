from sqlalchemy import Column, String, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from api.v1.models.base_model import BaseTableModel


class Newsletter(BaseTableModel):
    __tablename__ = "newsletters"

    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)

    newsletter_subscribers: Mapped[list["NewsletterSubscriber"]] = relationship(
        back_populates="newsletter"
    )


class NewsletterSubscriber(BaseTableModel):
    __tablename__ = "newsletter_subscribers"

    email: Mapped[str] = mapped_column(String(120), nullable=False)
    newsletter_id: Mapped[str] = mapped_column(
        ForeignKey("newsletters.id"), nullable=True
    )

    newsletter: Mapped["Newsletter"] = relationship(
        back_populates="newsletter_subscribers"
    )

    __table_args__ = (
        UniqueConstraint("email", "newsletter_id", name="uq_subscriber_newsletter"),
    )
