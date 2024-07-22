from sqlalchemy import Column, Integer, String, ForeignKey, Table, JSON
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy.types as types
from sqlalchemy import create_engine

Base = declarative_base()

# Custom type that adapts to the database dialect
class CustomArray(types.TypeDecorator):
    impl = types.String

    def load_dialect_impl(self, dialect):
        if dialect.name == 'sqlite':
            return dialect.type_descriptor(JSON())
        else:
            return dialect.type_descriptor(ARRAY(String(20)))

class Plan(Base):
    __tablename__ = 'plans'
    id = Column(Integer, primary_key=True, index=True)
    features = Column(CustomArray)
