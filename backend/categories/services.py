from sqlalchemy import exists
from .models import CategoriesModel

def get_all(db):
    return db.query(CategoriesModel).order_by(CategoriesModel.id).all()


def category_exists_id(db, category_id: int) -> bool:
    return db.query(
        exists().where(CategoriesModel.id == category_id)
    ).scalar()
    
    
def category_exists_name(db, category_name: str) -> bool:
    return db.query(
        exists().where(CategoriesModel.name == category_name)
    ).scalar()
    
def find_category_by_id(db,cat_id):
    return db.query(CategoriesModel).filter(CategoriesModel.id == cat_id).one_or_none()


def find_category_by_name(db,cat_name):
    return db.query(CategoriesModel).filter(CategoriesModel.name == cat_name).one_or_none()

