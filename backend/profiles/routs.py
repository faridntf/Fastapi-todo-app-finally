from fastapi import(
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    status
)

from sqlalchemy.exc import(
    IntegrityError,
    SQLAlchemyError
)

from .models import(
    UserModel,
    ProfileModel
)

from .schema import(
    ProfileCreateSc,
    ProfileResponseSc,
    ProfileUpdateSc
)

from .services import(
    upload_avatar,
    delete_old_profile_avatar,
    check_userID,
    check_nationalID,
    change_profile_status,
    get_profile_db
)

from sqlalchemy.orm import Session
from core import get_db
from users import get_current_user,EnUserRole


router = APIRouter(
    prefix="/profile",
    tags=["profile"],
)


@router.post("/create",)
def new_profile(data: ProfileCreateSc,db: Session = Depends(get_db), login_user : UserModel = Depends(get_current_user)):
    check_user_id = check_userID(data=login_user.id,db=db)
    if check_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="you can not create the new user profile"
        )
    new_data = data.model_dump()
    check_national = check_nationalID(data=new_data.get("national_id"),db=db)
    if check_national:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="national Id already in use"
        )
    create_profile = ProfileModel(**new_data)
    create_profile.user_id_fk = login_user.id
    try:
        db.flush()
        db.add(create_profile)
        db.commit()
        change_profile_status(user_id=login_user.id,is_completed=True,db=db,)
        raise HTTPException(status_code=status.HTTP_200_OK,detail="create profile successfully")
    except IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{e}"
        )


@router.post("/upload-avatarf2")
def avatar_uploadf2(
    avatar: UploadFile,
    db: Session = Depends(get_db),
    login_user: UserModel =Depends(get_current_user),
):
    find_profile = get_profile_db(db=db,user_id=login_user.id)
    if find_profile.profile_url is None:
        new_path = upload_avatar(data=avatar,current_user_id=login_user.id)
        try:
            find_profile.profile_url = new_path
            db.commit()
        except SQLAlchemyError:
            db.rollback()
            delete_old_profile_avatar(new_path)
    else:
        old_avatar = find_profile.profile_url
        new_avatar = upload_avatar(data=avatar,current_user_id=login_user.id)
        try:
            find_profile.profile_url = new_avatar
            db.commit()
            delete_old_profile_avatar(old_avatar)
        except:
            db.flush(old_avatar)
            db.rollback()
            raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Could not save avatar",
                    )


@router.patch("/change-profile-information")
def change_info(
    data: ProfileUpdateSc,
    db: Session = Depends(get_db),
    login_user: UserModel =Depends(get_current_user),
):
    profile = get_profile_db(db=db, user_id=login_user.id)
    update_data = data.model_dump(exclude_unset=True)
    check_national = check_nationalID(data=update_data.get("national_id"),db=db)
    if check_national:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="the nationalId already in use, please try again.")
    for field,value in update_data.items():
        setattr(profile,field,value)
    db.commit()
    raise HTTPException(status_code=status.HTTP_200_OK,detail="change information successfully")
    

@router.delete("/profile-information",status_code=status.HTTP_204_NO_CONTENT,)
def delete_profile(
    db: Session = Depends(get_db),
    login_user: UserModel =Depends(get_current_user)
):
    if login_user.role not in(EnUserRole.GUEST,EnUserRole.USER):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="admin users can not deleted the profile information")
    profile = get_profile_db(db=db, user_id=login_user.id)
    old_avatar = profile.profile_url
    try:
        db.delete(profile)
        change_profile_status(
            user_id=login_user.id,
            is_completed=False,
            db=db,
        )
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not delete profile",
        )

    delete_old_profile_avatar(old_data=old_avatar)

    raise HTTPException(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/profile-avatar",status_code=status.HTTP_204_NO_CONTENT,)
def delete_profile_avatar(
    db: Session = Depends(get_db),
    login_user=Depends(get_current_user),
):
    if login_user.role not in(EnUserRole.GUEST,EnUserRole.USER):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="admin users can not deleted the profile information")
    profile = get_profile_db(db=db, user_id=login_user.id)
    if not profile.profile_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Avatar not found",
        )
    old_avatar = profile.profile_url
    try:
        profile.profile_url = None
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not delete avatar",
        )
    delete_old_profile_avatar(old_data=old_avatar)
    return HTTPException(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/profile-detail",response_model=ProfileResponseSc,)
def get_profile_detail(
    db: Session = Depends(get_db),
    login_user=Depends(get_current_user),
):
    return get_profile_db(db=db, user_id=login_user.id)


@router.get("/profile-details",response_model=ProfileResponseSc,)
def get_user_profile(
    user_id: int,
    db: Session = Depends(get_db),
    login_user: UserModel =Depends(get_current_user),
):
    if login_user.role not in(EnUserRole.SUPER_ADMIN,EnUserRole.ADMIN):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="just admin users access the endpoint")
    profile = get_profile_db(db=db,user_id=user_id)
    return profile