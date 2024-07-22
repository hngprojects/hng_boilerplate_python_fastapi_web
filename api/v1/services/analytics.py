from sqlalchemy.orm import Session
from sqlalchemy import func
from api.v1.models import User, Product, Subscription, UserActivity, DailyMetric
from datetime import datetime, timedelta

class AnalyticsService:
    @staticmethod
    def get_summary(db: Session):
        today = datetime.utcnow().date()
        daily_metric = db.query(DailyMetric).filter(DailyMetric.date == today).first()

        if not daily_metric:
            # If no daily metric exists for today, calculate and create one
            total_users = db.query(User).count()
            active_users = db.query(User).filter(User.is_active == True).count()
            new_users = db.query(User).filter(func.date(User.created_at) == today).count()
            total_revenue = db.query(func.sum(Product.price)).join(Subscription).filter(Subscription.is_active == True).scalar() or 0

            daily_metric = DailyMetric(
                date=today,
                total_users=total_users,
                active_users=active_users,
                new_users=new_users,
                total_revenue=total_revenue
            )
            db.add(daily_metric)
            db.commit()

        return {
            "total_users": daily_metric.total_users,
            "active_users": daily_metric.active_users,
            "new_users": daily_metric.new_users,
            "total_revenue": daily_metric.total_revenue
        }

    @staticmethod
    def get_line_chart_data(db: Session):
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=30)

        daily_metrics = db.query(DailyMetric).filter(
            DailyMetric.date.between(start_date, end_date)
        ).order_by(DailyMetric.date).all()

        labels = [metric.date.strftime("%Y-%m-%d") for metric in daily_metrics]
        data = [metric.active_users for metric in daily_metrics]

        return {"labels": labels, "data": data}

    @staticmethod
    def get_bar_chart_data(db: Session):
        products = db.query(Product.name, func.count(Subscription.id)).join(Subscription).group_by(Product.name).all()

        categories = [product[0] for product in products]
        data = [product[1] for product in products]

        return {"categories": categories, "data": data}

    @staticmethod
    def get_pie_chart_data(db: Session):
        activity_counts = db.query(UserActivity.activity_type, func.count(UserActivity.id)).group_by(UserActivity.activity_type).all()

        segments = [activity[0] for activity in activity_counts]
        values = [activity[1] for activity in activity_counts]

        return {"segments": segments, "values": values}

    @staticmethod
    def get_active_users_count(db: Session):
        return db.query(User).filter(User.is_active == True).count()