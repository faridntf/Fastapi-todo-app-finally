from fastapi import(
    APIRouter,
    Depends,
    status,
    HTTPException,
)

from .schema import(
    CategoryCreateSc,
    CategoryResponseSC,
    CategoryUpdateSc
)

from .services import (
    get_all,
    find_category_by_id,
    find_category_by_name,
    category_exists_name,
    category_exists_id
)

from .models import CategoriesModel
from core import get_db
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from users import UserModel
from users import get_current_user
from users import EnUserRole
from typing import List

router = APIRouter(
    prefix="/category",
    tags=["category"],
    redirect_slashes=True
)

@router.post("/new-category")
def create_new_category(
    data:CategoryCreateSc,
    db:Session = Depends(get_db),
    current_user : UserModel = Depends(get_current_user)
):
    if current_user.role == EnUserRole.GUEST or current_user.role == EnUserRole.USER:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="guest and users members cannot access")
    else:
        new_data = data.model_dump(exclude_unset=True)
        check_category = category_exists_name(db=db,category_name=new_data.get("name"))
        if check_category:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="category already exist")
        else:
            set_data = CategoriesModel(**new_data)
            try:
                db.add(set_data)
                db.commit()
                db.refresh(set_data)
                return set_data
            except IntegrityError as e: #todo => bepors bbin nemayesh khata khube ke kamel neshun bede khata ro?
                db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                    detail=f"Error message: {e}"
                )

@router.get("/categories",response_model=List[CategoryResponseSC],status_code=status.HTTP_200_OK)
def get_all_categories(
    db:Session = Depends(get_db),
):
    all_category =  get_all(db=db)
    if not all_category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="list is empty, please create first category.")
    return all_category

@router.patch("/categories")
def change_detail_category(
    cat_id: int,
    data:CategoryUpdateSc,
    db:Session = Depends(get_db),
    current_user : UserModel = Depends(get_current_user)
):
    if current_user.role == EnUserRole.ADMIN or current_user.role == EnUserRole.SUPER_ADMIN:
        category = find_category_by_id(db=db,cat_id=cat_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No category has been created."
            )
            
        update_data = data.model_dump(exclude_unset=True,)
        if update_data.get("parent_id"):
            check_parent_category = category_exists_id(db=db,category_id=update_data.get("parent_id"))
            
            if check_parent_category == False:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="parent category not Found"
                )
        for key, value in update_data.items():
            setattr(category, key, value)
        try:
            db.commit()
            db.refresh(category)
            return category
        except IntegrityError as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"message \n {e}")
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="guest and users members cannot access")

@router.delete("/category-id")
def delete_category_by_id(
    cat_id:int, db:Session = Depends(get_db), current_user : UserModel = Depends(get_current_user)):
    if not current_user.role == EnUserRole.ADMIN or current_user.role == EnUserRole.SUPER_ADMIN:
        category = find_category_by_id(db=db,cat_id=cat_id)
        for task in category.tasks:
            task.category_id_fk == 1
        db.flush(task)
        print(task.category_id_fk)  # => id hamun task ro baraye mn mide = 8,     != 1
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No category has been created."
            )
        if category.is_system == True:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="It is not possible to delete the default categories."
            )
        db.delete(category)
        db.commit()
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="guest and users members cannot access")


@router.delete("/category-name")
def delete_category_by_name(
    cat_name: str,
    db:Session = Depends(get_db),
    current_user : UserModel = Depends(get_current_user)
):
    if current_user.role == EnUserRole.ADMIN or current_user.role == EnUserRole.SUPER_ADMIN:
        category = find_category_by_name(db=db,cat_name = cat_name)
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No category has been created."
            )
        if category.name == "Uncategorized":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="this category cannot be delete")
        db.delete(category)
        db.commit()
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="guest and users members cannot access")