from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from sqlalchemy import (
    func,
    Boolean,
    String,
    Integer,
    DateTime,
    Enum as SqlEnum,
    ForeignKey
)

from enum import Enum
from core import Base



def enum_values(enum_class: type[Enum]) -> list[str]:
    return [member.value for member in enum_class]


class EnTaskGrading(str,Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    
class TaskModel(Base):
    __tablename__ = "tblTasks"
    
    id : Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )
    
    title : Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )
    
    description : Mapped[str] = mapped_column(
        String(500),
        nullable=True
    )
    
    is_completed : Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )
    
    created_at : Mapped[str] = mapped_column(
        DateTime,
        server_default=func.now()
    )
    
    updated_at : Mapped[str] = mapped_column(
        DateTime,
        server_onupdate=func.now(),
        server_default=func.now()
    )
    
    grading: Mapped[EnTaskGrading] = mapped_column(
        SqlEnum(EnTaskGrading,values_callable=enum_values),
        default=EnTaskGrading.MEDIUM,
        nullable=False
    )
    
    is_delete : Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )
    
    user_id_fk : Mapped[int] = mapped_column(
        Integer,
        ForeignKey("tblUsers.id"),
        nullable=True
    )
    
    category_id_fk : Mapped[int] = mapped_column(
        Integer,
        ForeignKey("tblCategory.id")
    )
    
    user_task = relationship(
        "UserModel",
        back_populates="tasks_user",
    )
    
    category = relationship(
        "CategoriesModel",
        backref="categorys",
        uselist=False
    )
    
    def soft_delete(self) -> None:
        self.is_delete = True