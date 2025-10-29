from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime

# This defines the data model for country (helps with data validation)
class CountryBase(BaseModel):
    # Required fields based on project specs and enforced validation
    
    name: str = Field(
        ..., 
        json_schema_extra={"description": "Official country name"}
    )
    
    population: int = Field(
        ..., 
        ge=0, 
        json_schema_extra={"description": "Country's population"}
    )
    
    currency_code: Optional[str] = Field(
        None, 
        max_length=6, 
        json_schema_extra={"description": "Country's currency code"}
    )

    # Optional fields can be present or not 
    capital: Optional[str] = None
    region: Optional[str] = None
    flag_url: Optional[str] = None


class Country(CountryBase):
    # Database-specific primary key
    id: int = Field(
        ..., 
        json_schema_extra={"description": "Unique auto-generated identifier."}
    )
    
    # optional fields
    exchange_rate: Optional[float] = Field(
        None, 
        json_schema_extra={"description": "Exchange rate relative to the base currency (USD)."}
    )
    
    # Computed field
    estimated_gdp: Optional[float] = Field(
        None, 
        ge=0, # Added constraint
        json_schema_extra={"description": "Computed GDP based on population and exchange rate."}
    )
    
    # Metadata required by the response
    last_refreshed_at: datetime = Field(
        ..., 
        json_schema_extra={"description": "Timestamp of the last refresh operation."}
    )

    model_config = ConfigDict(
        from_attributes=True)

class StatusResponse(BaseModel):
    total_countries: int
    last_refreshed_at: Optional[datetime] = None
