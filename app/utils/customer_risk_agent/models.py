from pydantic import BaseModel, field_validator
from typing import Dict
from pydantic.fields import Field

class CustomerData(BaseModel):
    age: int = Field(ge=18, le=100)
    gender: str = Field(pattern="^(Male|Female)$")
    vehicleType: str = Field(pattern="^(Hiring|Private)$")
    totalClaims: int
    reason: str = Field(pattern="^(Driver Fault|3rd Party Fault)$")
    premium: float
    claimAmount: float
    insuredPeriod: int

    @field_validator('age')
    def validate_age(cls, v):
        if v < 18 or v > 100:
            raise ValueError('Age must be between 18 and 100')
        return v