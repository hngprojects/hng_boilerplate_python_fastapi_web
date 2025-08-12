import asyncio
from fastapi import FastAPI
from datetime import datetime

from api.utils.logger import logger
from api.v1.models.blog import Blog, BlogStatus
from api.db.database import get_db

class BlogScheduler:
    def __init__(self, app: FastAPI):
        self.app = app
        self.db = next(get_db())

    def publish_schedule_blog(self):
        """
        Publish scheduled blogs which are due for publishing
        """
        scheduled_blogs = (
            self.db.query(Blog).filter(
                Blog.status == BlogStatus.PENDING,
                Blog.scheduled_at <= datetime.now(),
                Blog.is_deleted == False
            ).all()
        )
        if len(scheduled_blogs) > 0:
            logger.info(f"Found {len(scheduled_blogs)} scheduled blogs ready for publication")
            for blog in scheduled_blogs:
                blog.status = BlogStatus.PUBLISHED
                self.db.commit()
                self.db.refresh(blog)
            logger.info(f"Published {len(scheduled_blogs)} scheduled blogs")
        else:
            logger.info("No scheduled blog posts are ready for publication at this time.")


    async def schedule_checker(self):
        """ Background task to check for scheduled blogs and publish them """
        while True:
            logger.info("Checking for scheduled blogs...")
            self.publish_schedule_blog()
            await asyncio.sleep(60)


def setup_blog_scheduler(app: FastAPI):
    """ Setup the blog scheduler """
    scheduler = BlogScheduler(app)
    asyncio.create_task(scheduler.schedule_checker())

