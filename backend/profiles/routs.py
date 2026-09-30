from fastapi import(
    APIRouter,
    Depends,
    HTTPException,
    UploadFile
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
    duplicate_data_NID,
    upload_avatar,
    delete_old_profile_avatar
)

import logging
from sqlalchemy.orm import Session
from core import get_db
from users import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/profile",
    tags=["profile"]
)

def profile_values(data):
    values = data.model_dump(exclude_unset=True)
    if values.get("website") is not None:
        values["website"] = str(values["website"])
    return values


def completed(profile):
    return bool(profile.first_name and profile.last_name and profile.national_id)


def save_profile(db, profile):
    try:
        db.commit()
        db.refresh(profile)
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Profile or national ID already exists") from None
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(500, "Unable to save profile") from None


@router.patch("/my-profile", response_model=ProfileResponseSc)
def update_profile_detail(profile_data: ProfileUpdateSc, db: Session = Depends(get_db),
                          current_user: UserModel = Depends(get_current_user)):
    profile = db.query(ProfileModel).filter(ProfileModel.user_id_fk == current_user.id).one_or_none()
    if profile is None:
        raise HTTPException(404, "Profile not found")
    if "national_id" in profile_data.model_fields_set:
        duplicate_data_NID(profile_data.national_id, db, exclude_profile_id=profile.id)
    for key, value in profile_values(profile_data).items():
        setattr(profile, key, value)
    current_user.is_profile_completed = completed(profile)
    save_profile(db, profile)
    return profile


@router.post("/avatar", status_code=201)
def upload_profile_avatar(data: UploadFile, db: Session = Depends(get_db),
                          current_user: UserModel = Depends(get_current_user)):
    avatar_path = upload_avatar(data, current_user.id)
    old_profile_path = None
    try:
        profile = db.query(ProfileModel).filter(ProfileModel.user_id_fk == current_user.id).one_or_none()
        if profile is None:
            profile = ProfileModel(user_id_fk=current_user.id)
            db.add(profile)
        else:
            old_profile_path = profile.profile_url
        profile.profile_url = f"uploads/profiles/{avatar_path.name}"
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        try:
            avatar_path.unlink(missing_ok=True)
        except OSError:
            logger.warning("Could not remove uncommitted avatar")
        raise HTTPException(500, "Unable to save avatar") from None
    # A cleanup failure must not undo or misreport a committed profile update.
    try:
        delete_old_profile_avatar(old_profile_path)
    except OSError:
        logger.warning("Could not remove previous avatar")
    return {"message": "Avatar uploaded"}


@router.post("/my-profile", response_model=ProfileResponseSc, status_code=201)
def create_new_profile(profile_data: ProfileCreateSc, db: Session = Depends(get_db),
                       current_user: UserModel = Depends(get_current_user)):
    profile = db.query(ProfileModel).filter(ProfileModel.user_id_fk == current_user.id).one_or_none()
    if profile is not None and completed(profile):
        raise HTTPException(409, "Profile already exists; use PATCH")
    duplicate_data_NID(profile_data.national_id, db,
                       exclude_profile_id=profile.id if profile else None)
    # An avatar-only profile can be completed without creating a second row.
    if profile is None:
        profile = ProfileModel(user_id_fk=current_user.id)
        db.add(profile)
    for key, value in profile_values(profile_data).items():
        setattr(profile, key, value)
    current_user.is_profile_completed = completed(profile)
    save_profile(db, profile)
    return profile


@router.get("/my-profile", response_model=ProfileResponseSc)
def show_my_profile(db: Session = Depends(get_db),
                    current_user: UserModel = Depends(get_current_user)):
    profile = db.query(ProfileModel).filter(ProfileModel.user_id_fk == current_user.id).one_or_none()
    if profile is None:
        raise HTTPException(404, "Please complete your profile")
    return profile
