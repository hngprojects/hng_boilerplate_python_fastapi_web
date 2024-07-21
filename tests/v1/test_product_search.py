import pytest
from httpx import AsyncClient
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from api.v1.models.base import Base
from api.v1.models.product import Product
from api.v1.routes.product import router as product_router
from api.v1.schemas.product import ProductCreate
from api.db.database import get_db

# Database URL for testing
DATABASE_URL = "postgresql://postgres.papbnyufdxepjdnumjdx:be_fast_api@aws-0-us-east-1.pooler.supabase.com:6543/postgres"

engine = create_async_engine(DATABASE_URL, echo=True)
TestSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

@pytest.fixture(scope="module")
async def db_session():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with TestSessionLocal() as session:
        yield session
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture(scope="module")
def app(db_session):
    def get_test_db():
        yield db_session

    app = FastAPI()
    app.dependency_overrides[get_db] = get_test_db
    app.include_router(product_router, prefix="/api/v1/products", tags=["Products"])
    return app

@pytest.fixture(scope="module")
async def client(app: FastAPI):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
async def test_search_items(client: AsyncClient, db_session: AsyncSession):
    products = [
        Product(name="Test Product 1", description="Description 1", price=10.0),
        Product(name="Test Product 2", description="Description 2", price=20.0),
        Product(name="Another Product", description="Description 3", price=30.0),
    ]
    db_session.add_all(products)
    await db_session.commit()

    # Test searching for a product that exists
    response = await client.get("/api/v1/products/search", params={"q": "Test"})
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["results"]) == 2
    assert data["results"][0]["name"] == "Test Product 1"

    # Test searching for a product that does not exist
    response = await client.get("/api/v1/products/search", params={"q": "NonExistent"})
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert len(data["results"]) == 0
    assert data["message"] == "No results found"

    # Test searching with an empty query parameter
    response = await client.get("/api/v1/products/search", params={"q": ""})
    assert response.status_code == 400
    data = response.json()
    assert data["error"] == "Bad Request"
    assert data["message"] == "The query parameter 'q' must be a non-empty string."

    # Test searching without a query parameter
    response = await client.get("/api/v1/products/search")
    assert response.status_code == 400
    data = response.json()
    assert data["error"] == "Bad Request"
    assert data["message"] == "The query parameter 'q' is required."
