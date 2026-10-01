from pydantic import(
    BaseModel,
    Field,
    ConfigDict
)
from typing import Optional

class CategoryBase(BaseModel):
    
    name : str = Field(
        title="Category name",
        max_length=50,
        pattern="[a-zA-Z]+"
    )
    
    parent_id : Optional[int] = Field(
        default=None,
        title="parent id",
        description="this category is parent or children, if children enter the number of parent category",
        le=100
    )
    
    description : Optional[str] = Field(
        default=None,
        title="category description",
        max_length=150,
        pattern="[a-zA-Z]+"
    )
    
    model_config = ConfigDict(
        from_attributes=True,
        str_strip_whitespace=True
    )
    
class CategoryResponseSC(CategoryBase):
    
    id : int
    
class CategoryCreateSc(CategoryBase):
    
    model_config = ConfigDict(
        extra="forbid",
        from_attributes=True,
        str_strip_whitespace=True
    )

class CategoryUpdateSc(BaseModel):
    
    name : Optional[str] = Field(
        default=None,
        pattern="[a-zA-Z]+"
    )
    
    parent_id : Optional[int] = Field(
        default=None,
    )
    
    description : Optional[str] = Field(
        default=None,
        pattern="[a-zA-Z]+"
    )
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid"
    )