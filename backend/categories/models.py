from sqlalchemy import(
    ForeignKey,
    String,
    Integer,
    Boolean
)
from sqlalchemy.orm import(
    Mapped,
    mapped_column,
    relationship
)

from core.database import Base


class CategoriesModel(Base):
    
    __tablename__ = "tblCategory"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )
    
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    
    parent_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("tblCategory.id"),
        nullable=True,
    )
    
    description: Mapped[str] = mapped_column(
        String(250),
        nullable=True
    )
    
    is_system : Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False
    )

    parent: Mapped["CategoriesModel"] = relationship(
        'CategoriesModel',
        back_populates="children",
        remote_side=lambda: [CategoriesModel.id],
    )
    
    children: Mapped[list["CategoriesModel"]] = relationship(
        'CategoriesModel',
        back_populates="parent",
    )
    
    def __str__(self) -> str:
        return {
            "id" : self.id,
            "name" : self.name
        }