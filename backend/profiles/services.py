from fastapi import(
    Depends,
    HTTPException,
    status
)

from sqlalchemy.orm import Session
from sqlalchemy import exists,or_,update
from core import get_db
from .models import ProfileModel
from users import UserModel,EnUserRole
from io import BytesIO
from core.setting import BASE_DIR
from uuid import uuid4
from PIL import Image, UnidentifiedImageError
from pathlib import Path


MAX_FILE_SIZE = 1*1024*1024
MAX_PIXELS = 1100000
ALLOWED_FORMATS = {
    ".jpg": "JPEG",
    ".jpeg": "JPEG",
    ".png": "PNG",
}

def get_profile_db(db: Session, user_id: int):
    profile = db.query(ProfileModel).where(
        ProfileModel.user_id_fk == user_id
    ).one_or_none()
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )
    return profile

def upload_avatar(
    data,
    current_user_id
):
    try:
        extension = Path(data.filename or "").suffix.lower()
        if extension not in ALLOWED_FORMATS:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="The file must be in the following formats: .jpg, .jpeg, .png"
            )
        content = data.file.read(MAX_FILE_SIZE + 1)
        if not content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Please currect the upload picture file"
            )
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                detail="Error! file is more than 1MB"
            )
        try:
            with Image.open(
                BytesIO(content),
                formats=["JPEG","PNG"],
            ) as picture:
                if picture.format != ALLOWED_FORMATS[extension]:
                    raise HTTPException(
                        status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                        detail="this file is incorrect uploaded"
                    )
                if picture.width * picture.height > MAX_PIXELS:
                    raise HTTPException(
                        status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                        detail="The image dimensions exceed the allowed limit"
                    )
                picture.verify()
            with Image.open(BytesIO(content)) as picture:
                picture.load()
                mode = "RGBA" if "A" in picture.getbands() else "RGB"
                with picture.convert(mode) as converted:
                    output = BytesIO()
                    converted.save(output, format="PNG")
                    image_bytes = output.getvalue()
        except Image.DecompressionBombError:
            raise HTTPException(
                status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                detail="The image dimensions exceed the allowed limit."
            )
        except (UnidentifiedImageError, OSError, SyntaxError, ValueError):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="The submitted photo is not valid."
            )
        filename = f"{current_user_id}_{uuid4().hex}.png"
        destination = BASE_DIR.parent.parent/"uploads"/ "profiles" / filename
        try:
            destination.parent.mkdir(parents=True, exist_ok=True)

            with destination.open("xb") as target:
                try:
                    target.write(image_bytes)
                except OSError:
                    target.close()
                    destination.unlink(missing_ok=True)
                    raise
        except OSError:
            raise HTTPException(
                status_code=500,
                detail="Internal Server Error, please Try again.",
            )
        return filename
    finally:
        data.file.close()

def delete_old_profile_avatar(
    old_data
)-> None:
    upload_dir = (BASE_DIR.parent.parent / "uploads" / "profiles").resolve()
    if old_data:
        old_path = (BASE_DIR.parent.parent /"uploads"/"profiles"/ old_data).resolve()
        if (old_path.is_relative_to(upload_dir) and old_path.is_file()):
            old_path.unlink(missing_ok=True)

def check_nationalID(data,db:Session):
    return db.query(
        exists().where(
            ProfileModel.national_id == data,
        )
    ).scalar()
    
def check_userID(data,db:Session):
    return db.query(
        exists().where(
            ProfileModel.user_id_fk == data
        )
    ).scalar()
    
def change_profile_status(
    user_id: int,
    is_completed: bool,
    db: Session,
):
    db.execute(
        update(UserModel)
        .where(
            UserModel.id == user_id,
            UserModel.role.in_([
                EnUserRole.GUEST,
                EnUserRole.USER,
            ]),
        )
        .values(
            is_profile_completed=is_completed,
            role=EnUserRole.USER if is_completed else EnUserRole.GUEST,
        )
            
    )