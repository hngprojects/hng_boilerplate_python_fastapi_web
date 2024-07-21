import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.v1.models.base import Base
from api.v1.models.product import Category  # Adjust this import path as needed

# Create a test database
@pytest.fixture(scope="module")
def engine():
    return create_engine('sqlite:///:memory:')

@pytest.fixture(scope="module")
def tables(engine):
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)

@pytest.fixture
def dbsession(engine, tables):
    """Returns an sqlalchemy session, and after the test tears down everything properly."""
    connection = engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection)()
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

def test_create_category(dbsession):
    category = Category(name="Test Category", description="Test Description", slug="test-category")
    dbsession.add(category)
    dbsession.commit()
    
    assert category.id is not None
    assert category.name == "Test Category"
    assert category.description == "Test Description"
    assert category.slug == "test-category"
    assert category.parent_id is None

def test_create_subcategory(dbsession):
    parent_category = Category(name="Parent Category", description="Parent Description", slug="parent-category")
    dbsession.add(parent_category)
    dbsession.commit()
    
    child_category = Category(name="Child Category", description="Child Description", slug="child-category", parent_id=parent_category.id)
    dbsession.add(child_category)
    dbsession.commit()
    
    assert child_category.parent_id == parent_category.id
    
    # Test relationship
    parent = dbsession.query(Category).filter_by(id=parent_category.id).first()
    assert len(parent.children) == 1
    assert parent.children[0].name == "Child Category"

def test_unique_name_constraint(dbsession):
    category1 = Category(name="Unique Category", description="Description", slug="unique-slug-1")
    dbsession.add(category1)
    dbsession.commit()
    
    # Try to add another category with the same name
    category2 = Category(name="Unique Category", description="Another Description", slug="unique-slug-2")
    dbsession.add(category2)
    with pytest.raises(Exception) as excinfo:  # This will depend on the specific exception your database raises
        dbsession.commit()
    assert "unique constraint" in str(excinfo.value).lower()
    dbsession.rollback()

def test_unique_slug_constraint(dbsession):
    category1 = Category(name="Category One", description="Description", slug="unique-slug")
    dbsession.add(category1)
    dbsession.commit()
    
    # Try to add another category with the same slug
    category2 = Category(name="Category Two", description="Another Description", slug="unique-slug")
    dbsession.add(category2)
    with pytest.raises(Exception) as excinfo:
        dbsession.commit()
    assert "unique constraint" in str(excinfo.value).lower()
    dbsession.rollback()

def test_category_without_parent(dbsession):
    category = Category(name="No Parent", description="Top-level category", slug="no-parent")
    dbsession.add(category)
    dbsession.commit()
    
    assert category.parent_id is None
    
    fetched_category = dbsession.query(Category).filter_by(id=category.id).first()
    assert fetched_category.parent_id is None

def test_multiple_subcategories(dbsession):
    parent = Category(name="Parent", description="Parent category", slug="parent")
    dbsession.add(parent)
    dbsession.commit()
    
    child1 = Category(name="Child 1", description="First child", slug="child-1", parent_id=parent.id)
    child2 = Category(name="Child 2", description="Second child", slug="child-2", parent_id=parent.id)
    dbsession.add_all([child1, child2])
    dbsession.commit()
    
    fetched_parent = dbsession.query(Category).filter_by(id=parent.id).first()
    assert len(fetched_parent.children) == 2
    child_names = [child.name for child in fetched_parent.children]
    assert "Child 1" in child_names
    assert "Child 2" in child_names