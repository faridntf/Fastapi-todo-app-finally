from fastapi import(
    APIRouter,
    Depends,
    status,
    HTTPException,
    Security,
    Response,
    Request
)

from .schema import (
    UserResponseSc,
    UserChangePassword,
    UserCreateSc,
    UserUpdateSc,
    UserInfoSc
)

from fastapi.security import OAuth2PasswordRequestForm
from auth.jwt_auth import(
    create_access_token,
    create_refresh_token,
    set_coookie
)

from .models import UserModel,EnUserRole
from core import get_db
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from .services import check_duplicate_account,find_user,get_current_user,find_user_by_id,set_lastlogin_time

#sqlalchemy.exc.IntegrityError

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.post("/register",response_model=UserResponseSc,status_code=status.HTTP_201_CREATED)
def create_account(new_account:UserCreateSc, db:Session = Depends(get_db)):
    new_user = new_account.model_dump(exclude=["re_password","password"])
    exist_account = check_duplicate_account(
        username=new_user.get("username"),
        email=new_user.get("email"),
        phone_number=new_user.get("phone_number"),
        db=db
    )
    if exist_account:
        raise HTTPException(
            detail="username, email or phone number field is already exist",
            status_code=status.HTTP_409_CONFLICT)
    create = UserModel(**new_user)
    create.set_password(new_account.password)
    try:
        db.add(create)
        db.commit()
        db.refresh(create)
        return create
    except:
        raise HTTPException(detail="unknow error", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@router.post("/login")
def login_account(response: Response,login_data: OAuth2PasswordRequestForm = Depends(),db:Session = Depends(get_db)):
    user = find_user(data=login_data.username,db=db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="username or email or phone number or password is incorrect"
            )
    verify_password = user.verify_password(login_data.password)
    if verify_password == False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="username or email or phone number or password is incorrect"
            )
    if user.is_active == False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="this account is not active"
            )
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)
    set_coookie("access_token",access_token,response=response)
    set_coookie("refresh_token",refresh_token,response=response)
    set_lastlogin_time(db=db,username=user.username)
    return "login successfully"
    
@router.post("/logout")
def logout_account(request:Request,response:Response):
    access_token = request.cookies.get("access_token")
    refresh_token = request.cookies.get("refresh_token")
    if not (access_token and refresh_token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Please login to your account",
            )
    response.delete_cookie(key="access_token",path="/")
    response.delete_cookie(key="refresh_token",path="/")
    return "Logout successfully"

@router.post("/user/change-password")
def change_password(
    change: UserChangePassword,
    response: Response,
    db: Session = Depends(get_db),
    login_user=Depends(get_current_user),
):
    user = find_user_by_id(data=login_user.id, db=db)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Please login to your account",
        )

    if not user.verify_password(change.old_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Old password is incorrect",
        )

    if change.new_password == change.old_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from old password",
        )

    try:
        user.set_password(change.new_password)
        db.commit()
        response.delete_cookie("access_token", path="/")
        response.delete_cookie("refresh_token", path="/")
        
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not change password",
        ) from None

    return {"message": "Password changed successfully"}
    

@router.patch("/change_info", response_model=UserResponseSc)
def change_information_user(
    change: UserUpdateSc,
    db: Session = Depends(get_db),
    logiin_user: UserModel = Depends(get_current_user),
):
    if logiin_user.role == EnUserRole.GUEST:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="oops, guest users cannot access this endpoint",
        )

    detail = change.model_dump(exclude_unset=True)

    get_user = find_user_by_id(data=logiin_user.id, db=db)
    if get_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    check_info = check_duplicate_account(
        username=None,
        email=detail.get("email"),
        phone_number=detail.get("phone_number"),
        db=db,
        exclude_user_id=logiin_user.id,
    )

    if check_info:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email or phone number is already in use",
        )

    try:
        for field, value in detail.items():
            setattr(get_user, field, value)

        db.commit()
        db.refresh(get_user)
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not update user information",
        )
    return get_user

@router.get("/user_detail",response_model=UserInfoSc,status_code=status.HTTP_200_OK)
def user_detail(db:Session = Depends(get_db),logiin_user: UserModel = Depends(get_current_user)):
    get_info = find_user_by_id(data=logiin_user.id,db=db)
    return get_info