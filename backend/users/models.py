from sqlalchemy import (
    Integer,
    String,
    DateTime,
    Boolean,
    Enum as SqlEnum,
    Text,
    Index,
    text,
    ForeignKey,
    func
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from typing import TYPE_CHECKING
from datetime import date
from core import Base
from enum import Enum
from pwdlib import PasswordHash

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from profiles.models import ProfileModel
    from tasks.models import TaskModel
    

def enum_values(enum_class: type[Enum]) -> list[str]:
    return [member.value for member in enum_class]

class EnUserRole(str, Enum):
    SUPER_ADMIN = "super admin"
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"

class UserModel(Base):
    __tablename__ = "tblUsers"
        
    id : Mapped[int] = mapped_column(
        Integer,
        autoincrement=True,
        primary_key=True,
        index=True
    )
    
    username : Mapped[str] = mapped_column(
        String(50),
        index=True,
        unique=True,
        nullable=False
    )
    
    email : Mapped[str] = mapped_column(
        String(250),
        nullable=False,
        index=True,
        unique=True
    )
    
    password : Mapped[str] = mapped_column(
        String(500),
        nullable=False
    )
    
    phone_number: Mapped[str] = mapped_column(
        String(20),
        nullable=True,
        index=True,
        unique=True
    )
    
    created_at : Mapped[date] = mapped_column(
        DateTime(True),
        server_default=func.now()
    )
    
    updated_at : Mapped[date] = mapped_column(
        DateTime(True),
        nullable=True,
        server_onupdate=func.now()
    )
    
    role: Mapped[EnUserRole] = mapped_column(
        SqlEnum(EnUserRole),
        default=EnUserRole.GUEST,
        nullable=False,
    )
    
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )
    
    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    
    last_login: Mapped[date] = mapped_column(
        DateTime(True),
        nullable=True
    )
    
    is_delete: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True
    )
    
    deleted_at: Mapped[date] = mapped_column(
        DateTime(True),
        nullable=True
    )
    
    is_profile_completed: Mapped[bool] = mapped_column(
            Boolean,
            default=False
        )
    
    profile: Mapped["ProfileModel"] = relationship(
        "ProfileModel",
        back_populates="user",
        uselist=False,
        cascade="all,delete-orphan",
        single_parent=True,
        lazy="joined"
    )
    
    tasks_user: Mapped[list["TaskModel"]] = relationship(
            "TaskModel",
            back_populates="user_task",
            uselist=True,
            cascade="all,delete-orphan",
            single_parent=True,
        )
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', role={self.role})>"
    
    def __str__(self) -> str:
        return f"{self.username} ({self.email})"
    
    def soft_delete(self) -> None:
        self.is_delete = True
        self.deleted_at = func.now()
    
    password_hash = PasswordHash.recommended()
    
    def hash_password(self, plain_password: str) -> str:
        return self.password_hash.hash(plain_password)
    
    def verify_password(self, plain_password: str) -> bool:
        return self.password_hash.verify(plain_password, self.password)

    def set_password(self,plain_password):
        self.password = self.hash_password(plain_password)