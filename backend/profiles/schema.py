from pydantic import(
    BaseModel,
    Field,
    ConfigDict,
    field_validator
)

from .models import (
    EnGender,
    enum_values
)

from typing import Optional
from datetime import date


class ProfileBaseSc(BaseModel):
    bio: Optional[str] = Field(
        default=None,
        max_length=1000
    )
    
    national_id: Optional[str] = Field(
        default=None,
        pattern=r"^\d{10}$"
    )
    
    first_name: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=50
    )
    
    last_name: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=50
    )
    
    date_of_birth: Optional[date] = None
    
    gender: Optional[EnGender] = None
    
    postal_code: Optional[str] = Field(
        default=None,
        max_length=10
        
    )
    
    address: Optional[str] = Field(
        default=None,
        max_length=1000
    )
    
    @field_validator("first_name", "last_name")
    @classmethod
    def check_names(cls, value: str | None) -> str | None:
        if value is None:
            return None
        if any(char.isdigit() for char in value):
            raise ValueError("Names cannot contain digits")
        return value

    @field_validator("national_id", mode="before")
    @classmethod
    def check_nid(cls, value):
        if value is None:
            return None
        if not isinstance(value, str):
                raise ValueError("invalid nationalID please try again!")
        value = value.strip()
        if not value.isascii() or not value.isdigit():
            raise ValueError("کد ملی باید فقط شامل ارقام انگلیسی باشد.")
        if len(value) != 10:
            raise ValueError("nationalId most be 10 charecter")
        return value
    
    @field_validator("gender")
    @classmethod
    def validate_status(cls, v: str) -> str:
        if v is None:
            return None
        if v not in enum_values(EnGender):
            raise ValueError(f"The status must be one of the following states: {enum_values(EnGender)}")
        return v
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid"
    )

class ProfileCreateSc(ProfileBaseSc):
    first_name: str = Field(min_length=2, max_length=50)
    last_name: str = Field(min_length=2, max_length=50)
    national_id: str = Field(pattern=r"^[0-9]{10}$")
    
class ProfileUpdateSc(ProfileBaseSc):
    pass
    
class ProfileResponseSc(ProfileBaseSc):
    
    user_id_fk : int
    
    model_config = ConfigDict(
        from_attributes=True,
    )