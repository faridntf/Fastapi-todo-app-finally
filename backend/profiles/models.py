from sqlalchemy import (
    Integer,
    String,
    DateTime,
    Enum as SqlEnum,
    Text,
    text,
    ForeignKey
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from datetime import date
from core import Base
from enum import Enum
from users import UserModel


def enum_values(enum_class: type[Enum]) -> list[str]:
    return [member.value for member in enum_class]

class EnGender(str,Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"

class ProfileModel(Base):
    __tablename__ = "tblProfiles"

    id: Mapped[int] = mapped_column(
        Integer,
        autoincrement=True,
        primary_key=True,
        index=True
    )

    bio: Mapped[str] = mapped_column(
        Text,
        nullable=True
    )

    profile_url: Mapped[str] = mapped_column(
        String(250),
        nullable=True
    )
    
    national_id : Mapped[str] = mapped_column(
            String(10),
            unique=True,
            nullable=True
    )
    
    first_name : Mapped[str] = mapped_column(
            String(50),
            nullable=True
    )

    last_name : Mapped[str] = mapped_column(
        String(50),
        nullable=True
    )
    
    date_of_birth: Mapped[date] = mapped_column(
        DateTime(True),
        nullable=True
    )
    
    gender: Mapped[EnGender] = mapped_column(
        SqlEnum(EnGender),
        nullable=True
    )

    postal_code : Mapped[str] = mapped_column(
        String(10),
        nullable=True
    )
    
    address: Mapped[str] = mapped_column(
        Text,
        nullable=True
    )

    user_id_fk: Mapped[int] = mapped_column(
        ForeignKey("tblUsers.id", ondelete="CASCADE"),
        unique=True,  
        nullable=False 
    )

    user: Mapped["UserModel"] = relationship(
        "UserModel",
        back_populates="profile",
        single_parent=True
    )

    def __repr__(self) -> str:
        return f"<Profile(id={self.id}, user_id={self.user_id_fk})>"

    @property
    def full_name(self) -> str:
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name or self.last_name or ""