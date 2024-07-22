from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from decouple import config as decouple_config
from api.v1.models.base import Base

# Import models if they are not included in Base
from api.v1.models.user import User
from api.v1.models.org import Organization
from api.v1.models.profile import Profile
from api.v1.models.product import Product
from api.v1.models.subscription import Subscription
from api.v1.models.blog import Blog
from api.v1.models.job import Job
from api.v1.models.invitation import Invitation
from api.v1.models.role import Role
from api.v1.models.permission import Permission
from api.v1.models.newsletter import NEWSLETTER

# Alembic Config object
config = context.config

# Set up logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Retrieve database URL from environment
database_url = decouple_config('DB_URL')
config.set_main_option('sqlalchemy.url', database_url)

# Set target metadata for 'autogenerate'
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
