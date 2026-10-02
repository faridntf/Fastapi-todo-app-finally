from fastapi import(
    APIRouter,
    Depends,
    status,
    HTTPException,
    Query
)

from fastapi.responses import JSONResponse

from .schema import(
    TaskCreateSc,
    TaskResponseSc,
    TaskUpdateSc,
    TaskMarkCompleted
)

from users import(
    UserModel,
    get_current_user,
    EnUserRole
)

from .services import (
    exist_task,
    find_task_by_id,
    find_task_by_name,
    search_task,
    get_my_all_tasks,
    get_all_user_tasks,
    find_complete_or_not_tasks,
    find_task_names_by_category
)
from .models import TaskModel
from core import get_db
from fastapi.exceptions import ResponseValidationError
from sqlalchemy.orm import Session
from categories import category_exists_id
from typing import List


router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
    redirect_slashes=True
)

@router.post("/create",response_model=TaskResponseSc,status_code=status.HTTP_201_CREATED)
def create_new_task(
    data:TaskCreateSc,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    new_task = data.model_dump()
    set_task = TaskModel(**new_task)
    set_task.user_id_fk = current_user.id
    
    exist_category = category_exists_id(db=db,category_id = set_task.category_id_fk)
    if exist_category == False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="category id is invalid, please check the category id"
        )
    exist_title_for_task_user = exist_task(db=db,task_title=set_task.title,user_id=current_user.id)
    if exist_title_for_task_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="this Task is already exist!!!"
        )
    db.add(set_task)
    db.commit()
    db.refresh(set_task)
    return set_task
    

@router.get("/list-tasks",response_model=List[TaskResponseSc],status_code=status.HTTP_200_OK)
def get_list_tasks(
    limit:int,
    offset:int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    my_tasks = get_my_all_tasks(db=db,limitt=limit,offsett=offset,user_id=current_user.id)
    return my_tasks


@router.get("/all_tasks",response_model=List[TaskResponseSc])
def get_all_users_tasks(
    user_id : int,
    limit:int,
    offset:int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    if current_user.role==EnUserRole.GUEST or current_user.role == EnUserRole.USER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Oooops!!!!, just admin users access the section"
        )
    all_user_tasks = get_all_user_tasks(limit=limit,offset=offset,db=db,user_id=user_id)
    return all_user_tasks
    


@router.get("/task-name")
def get_task_by_name(
    task_name: str,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    find_task = find_task_by_name(db=db,task_name=task_name,user_id=current_user.id)
    if not find_task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Task not found")
    return find_task


@router.get("/task-id/{task_id}")
def get_task_by_id(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    find_task = find_task_by_id(db=db,task_id=task_id,user_id=current_user.id)
    if not find_task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Task not found")
    return find_task


@router.patch("/update-task/{task_id}",response_model=TaskResponseSc)
def update_task(
    task_id:int,
    data:TaskUpdateSc,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    if current_user.role == EnUserRole.GUEST:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="just user and admins access the endpoint")
    find_task = find_task_by_id(db=db,task_id=task_id,user_id=current_user.id)
    if not find_task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Task not found")
    update_data = data.model_dump(exclude_unset=True)
    for field,value in update_data.items():
        setattr(find_task,field,value)
    db.commit()
    db.refresh(find_task)
    return find_task
    

@router.patch("/update-task-complete/{task_id}")
def mark_the_task_completed(
    task_id:int,
    data:TaskMarkCompleted,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    if current_user.role == EnUserRole.GUEST:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="oops, guest users cannot access this endpoint")
    find_task = find_task_by_id(db=db,task_id=task_id,user_id=current_user.id)
    if not find_task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="task not found.")
    if find_task.is_completed == True:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="this task is already completed")
    try:
        find_task.is_completed = data.is_completed
        db.commit()
        return JSONResponse(status_code=status.HTTP_200_OK,content={
            "message" : "your is great, continue",
            "task" : find_task
        })
    except:
        db.rollback()
    
    
@router.delete("/task/{task_id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_task_id(
    task_id:int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    if current_user.role != EnUserRole.GUEST:
        find_task = find_task_by_id(db=db,task_id=task_id,user_id=current_user.id)
        if find_task is None:
            raise HTTPException(detail="The task was not found or has been deleted.",status_code=status.HTTP_404_NOT_FOUND)
        find_task.soft_delete()
        db.commit()
        
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="oops, guest users cannot access this endpoint"
        )
    

@router.delete("/taskk/{task_name}",status_code=status.HTTP_204_NO_CONTENT)
def delete_task_name(
    task_name:str,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    if current_user.role != EnUserRole.GUEST:
        find_task = find_task_by_name(db=db,task_name=task_name,user_id=current_user.id)
        if find_task is None:
            raise HTTPException(detail="The task was not found or has been deleted.",status_code=status.HTTP_404_NOT_FOUND)
        find_task.soft_delete()
        db.commit()
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="oops, guest users cannot access this endpoint"
        )

@router.get("/search-task/",response_model=List[TaskResponseSc],status_code=status.HTTP_200_OK)
def search_task_query(
    q: str = Query(...,min_length=1,max_length=50),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    if current_user.role == EnUserRole.GUEST:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="oops, guest users cannot access this endpoint")
    result = search_task(db=db,parametr=q,user_id=current_user.id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="task not found")
    try:
        return result
    except ResponseValidationError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Unknown error! Please try again later.")

@router.get("/task-status")
def get_task_by_status(
    is_completeed: bool = Query(...),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    if current_user.role == EnUserRole.GUEST:
        raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="oops, guest users cannot access this endpoint"
                )
    find_task = find_complete_or_not_tasks(db=db,status=is_completeed,user_id=current_user.id)
    if not find_task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Task not found.")
    return find_task

@router.get("/get-task-by-category")
def task_by_category(
    cat_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    if current_user.role == EnUserRole.GUEST:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="oops, guest users cannot access this endpoint",
        )
        
    if not category_exists_id(db=db, category_id=cat_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )
    tasks = find_task_names_by_category(db=db,cat_id=cat_id,user_id=current_user.id)
    if not tasks:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="tasks not found")
    return tasks