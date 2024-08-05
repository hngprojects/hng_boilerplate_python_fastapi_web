from sqlalchemy.orm import Session
from api.v1.models.regions import Region

def get_unique_languages(db: Session):
    try:
        result = db.query(Region.language).filter(Region.language.isnot(None)).distinct().all()
        languages = [row[0] for row in result]
        return languages
    except Exception as e:
        raise Exception(f"Error retrieving languages: {str(e)}")
