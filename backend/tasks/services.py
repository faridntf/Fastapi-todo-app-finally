from sqlalchemy import exists
from .models import TaskModel
from sqlalchemy.orm import Session


def exist_task(db: Session, task_title: str, user_id: int)-> bool:
    return db.query(
        exists().where(
        TaskModel.title == task_title,
        TaskModel.user_id_fk == user_id,
        TaskModel.is_completed == False
    )).scalar()

def find_task_by_id(db: Session, task_id:int, user_id:int):
    return db.query(TaskModel).where(
        TaskModel.id == task_id,
        TaskModel.user_id_fk == user_id,
        TaskModel.is_delete == False
    ).one_or_none()
    
def find_task_by_name(db: Session, task_name:str, user_id:int):
    return db.query(TaskModel).where(
        TaskModel.title == task_name,
        TaskModel.user_id_fk == user_id,
        TaskModel.is_delete == False
    ).one_or_none()
    
    
def search_task(db: Session,parametr : str, user_id):
    return db.query(TaskModel).where(
        TaskModel.user_id_fk == user_id,
        TaskModel.is_delete == False,
        TaskModel.title.ilike(f"%{parametr}%")  #=> be lowercase va uppercase hassas nist
    ).all()
    
def get_my_all_tasks(db: Session,limit:int,offset:int,user_id:int):
    return db.query(TaskModel).where(
        TaskModel.user_id_fk == user_id,
        TaskModel.is_delete == False
    ).limit(limit).offset(offset).all()
    
def get_all_user_tasks(db: Session,limit:int,offset:int,user_id:int):
    return db.query(
            TaskModel.id,
            TaskModel.title,
            TaskModel.grading,
            TaskModel.user_id_fk,
            TaskModel.created_at,
            TaskModel.is_completed
            ).where(
            TaskModel.user_id_fk == user_id,
            TaskModel.is_delete == False
        ).limit(limit).offset(offset).all()
            
def find_complete_or_not_tasks(db: Session,status,user_id):
    return db.query(TaskModel).where(
        TaskModel.is_completed == status,
        TaskModel.user_id_fk == user_id,
        TaskModel.is_delete == False
    ).all()


def find_task_names_by_category(
    db,
    cat_id: int,
    user_id: int,
):
    tasks = db.query(TaskModel).where(
        TaskModel.category_id_fk == cat_id,
        TaskModel.user_id_fk == user_id,
        TaskModel.is_delete == False
    ).all()
    return tasks