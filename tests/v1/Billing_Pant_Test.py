from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.db.database import Base
from api.utils.billing import create_billing_plan
from api.v1.models import BillingPlan

# Configuration de la base de données en mémoire pour les tests
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Créer les tables pour les tests
Base.metadata.create_all(bind=engine)

@pytest.fixture(scope="module")
def db_session():
    """Créer une session de base de données pour les tests"""
    session = SessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)

def test_create_billing_plan(db_session):
    """Tester la création d'un plan de facturation"""
    plan_name = "premium"
    amount = 1200
    
    # Appeler la fonction pour créer un plan de facturation
    plan = create_billing_plan(db_session, plan_name, amount)
    
    # Vérifier que le plan a été créé avec les bonnes valeurs
    assert plan is not None
    assert plan.plan_name == plan_name
    assert plan.amount == amount

def test_create_billing_plan_missing_name(db_session):
    """Tester la création d'un plan de facturation avec un nom manquant"""
    with pytest.raises(ValueError, match="Plan name is required"):
        create_billing_plan(db_session, None, 1200)

def test_create_billing_plan_negative_amount(db_session):
    """Tester la création d'un plan de facturation avec un montant négatif"""
    with pytest.raises(ValueError, match="Amount must be a positive number"):
        create_billing_plan(db_session, "basic", -1200)


