from typing import Any, Optional
from sqlalchemy.orm import Session

from api.core.base.services import Service
from api.utils.db_validators import check_model_existence
from api.v1.models.product import Product
from api.v1.models import Organization
from api.utils.db_validators import check_user_in_org


class ProductService(Service):
    '''Product service functionality'''

    def create(self, db: Session,  schema):
        '''Create a new product'''

        new_product = Product(**schema.model_dump())
        db.add(new_product)
        db.commit()
        db.refresh(new_product)

        return new_product
    

    def fetch_all(self, db: Session, **query_params: Optional[Any]):
        '''Fetch all products with option tto search using query parameters'''

        query = db.query(Product)

        # Enable filter by query parameter
        if query_params:
            for column, value in query_params.items():
                if hasattr(Product, column) and value:
                    query = query.filter(getattr(Product, column).ilike(f'%{value}%'))

        return query.all()

    
    def fetch(self, db: Session, id: str):
        '''Fetches a product by id'''

        product = check_model_existence(db, Product, id)
        return product

    def fetch_by_organization(self, db: Session, user, org_id, limit, page):
        '''Fetches all products of an organization'''

        # check if organization exists
        organization = check_model_existence(db, Organization, org_id)

        # Check if the user exist in the organization
        check_user_in_org(user=user, organization=organization)

        # calculating offset value from page and limit given
        offset_value = (page - 1) * limit

        # Filter to return only products of the org_id
        products = db.query(Product).filter(Product.org_id == org_id).offset(offset_value).limit(limit).all()

        return products

    def update(self, db: Session, id: str, schema):
        '''Updates a product'''

        product = self.fetch(db=db, id=id)
        
        # Update the fields with the provided schema data
        update_data = schema.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(product, key, value)
        
        db.commit()
        db.refresh(product)
        return product
    

    def delete(self, db: Session, id: str):
        '''Deletes a product'''
        
        product = self.fetch(id=id)
        db.delete(product)
        db.commit()
    
product_service = ProductService()