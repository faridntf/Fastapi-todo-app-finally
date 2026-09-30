from pydantic import(
    BaseModel,
    Field,
    ConfigDict,
    field_validator
)

from .models import(
    EnTaskGrading,
    enum_values
)

from typing import Optional
from datetime import datetime


class TaskBase(BaseModel):
    description : Optional[str] = Field(
        default=None,
        max_length=100,
    )
    category_id_fk : Optional[int]= Field(
        default=1,
    )
    
    @field_validator("category_id_fk")
    def validate_categor(cls,value : int):
        if not value.is_integer:
            raise ValueError("category just number accept, please try again")
        return value
    
    model_config = ConfigDict(
                from_attributes=True,
                str_strip_whitespace=True
                )


class TaskResponseSc(TaskBase):
    id : int
    title : str
    is_completed: bool
    grading : str
    user_id_fk : int
    created_at : datetime
    updated_at : Optional[datetime] = Field(default=None)
    
    
class TaskCreateSc(TaskBase):
    title : str = Field(
        min_length=1,
        max_length=50
    )
    
    grading : EnTaskGrading = Field(default=EnTaskGrading.MEDIUM)
    
    
    @field_validator("grading")
    def validate_grading_enum(cls, value):
        if not value in enum_values(EnTaskGrading):
            raise ValueError(f"please just select the current values: [{enum_values(EnTaskGrading)}]")
        return value
    
    model_config = ConfigDict(
        from_attributes=True,
        str_strip_whitespace=True,
        extra="forbid"
    )


class TaskUpdateSc(TaskBase):
    
    title : Optional[str] = Field(
        min_length=1,
        max_length=50
    )
    
    model_config = ConfigDict(
        from_attributes=True,
        str_strip_whitespace=True,
        extra="forbid"
    )
    
    
class TaskMarkCompleted(BaseModel):
    is_completed : bool