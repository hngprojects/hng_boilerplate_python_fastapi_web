# models.py
from sqlalchemy import Table, Column, Integer, String, MetaData

metadata = MetaData()

plans = Table(
    "plans",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("plan_name", String, unique=True, index=True),
    Column("amount", Integer),
)
