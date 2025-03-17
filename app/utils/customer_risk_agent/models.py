from pydantic import BaseModel, field_validator
from typing import Dict
from pydantic.fields import Field

class CustomerData(BaseModel):
    age: int = Field(ge=18, le=100)
    gender: str = Field(pattern="^(Male|Female)$")
    vehicleType: str = Field(pattern="^(Hiring|Private)$")
    totalClaims: int = Field(ge=0) 
    reason: str = Field(pattern="^(Driver Fault|3rd Party Fault)$")
    premium: float = Field(gt=0)  # Positive premium
    claimAmount: float = Field(ge=0)  # Non-negative claim amount
    insuredPeriod: int = Field(gt=0)  # Positive insured period
    
    
    @field_validator('age')
    def validate_age(cls, v):
        if v < 18 or v > 100:
            raise ValueError('Age must be between 18 and 100')
        return v