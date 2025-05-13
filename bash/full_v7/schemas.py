from pydantic import BaseModel
from typing import List, Optional, Any
from datetime import date

# Forward declarations for circular dependencies - ensure all are here
class ObligorProfile(BaseModel): pass
class FacilityProfile(BaseModel): pass
class LrrRating(BaseModel): pass
class OrrRating(BaseModel): pass
class RatingRecord(BaseModel): pass
class Facility(BaseModel): pass # Ensure Facility is forward declared before Obligor uses it
class Obligor(BaseModel): pass

# ObligorFacility Schemas
class ObligorFacilityBase(BaseModel):
    obligor_id: int
    facility_id: int

class ObligorFacilityCreate(ObligorFacilityBase):
    pass

class ObligorFacility(ObligorFacilityBase):
    obligor_facility_id: int

    class Config:
        from_attributes = True

# Obligor Schemas
class ObligorBase(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None

class ObligorCreate(ObligorBase):
    name: str # Name is required for creation

class Obligor(ObligorBase):
    obligor_id: int
    profiles: List['ObligorProfile'] = []
    facilities: List['Facility'] = []
    rating_records: List['RatingRecord'] = []  # Added this relationship

    class Config:
        from_attributes = True

# Paginated Obligor Schema
class PaginatedObligors(BaseModel):
    items: List[Obligor]
    total: int

# ObligorProfile Schemas
class ObligorProfileBase(BaseModel):
    as_of_date: date
    custom: Optional[bool] = False
    commitment: Optional[float] = None
    moody_rating: Optional[float] = None
    obligor_id: int

class ObligorProfileCreate(ObligorProfileBase):
    pass

class ObligorProfile(ObligorProfileBase):
    obligor_profile_id: int
    obligor: Optional['Obligor'] = None
    lrr_rating: Optional['LrrRating'] = None

    class Config:
        from_attributes = True

# Facility Schemas
class FacilityBase(BaseModel):
    description: Optional[str] = None
    name: Optional[str] = None
    address: Optional[str] = None
    property_type: Optional[str] = None

class FacilityCreate(FacilityBase):
    name: str # Name is required for creation

class Facility(FacilityBase):
    facility_id: int
    profiles: List['FacilityProfile'] = []
    obligors: List['Obligor'] = []  # Uncommented as we need this relationship

    class Config:
        from_attributes = True

# Paginated Facility Schema
class PaginatedFacilities(BaseModel):
    items: List[Facility]
    total: int

# FacilityProfile Schemas
class FacilityProfileBase(BaseModel):
    as_of_date: date
    loan_amount: Optional[float] = None
    collateral_amount: Optional[float] = None
    custom: Optional[bool] = False
    ltv: Optional[float] = None
    cap_rate: Optional[float] = None
    workout_cost: Optional[float] = None
    facility_id: int

class FacilityProfileCreate(FacilityProfileBase):
    pass

class FacilityProfile(FacilityProfileBase):
    facility_profile_id: int
    facility: Optional['Facility'] = None
    orr_ratings: List['OrrRating'] = []  # Changed to List for 1:N relationship

    class Config:
        from_attributes = True

# LRR Rating Schemas
class LrrRatingBase(BaseModel):
    data: Optional[float] = None
    rating: Optional[float] = None
    pd: Optional[float] = None
    rating_record_id: int
    obligor_profile_id: int

class LrrRatingCreate(LrrRatingBase):
    pass

class LrrRating(LrrRatingBase):
    lrr_rating_id: int
    rating_record: Optional['RatingRecord'] = None
    obligor_profile: Optional['ObligorProfile'] = None

    class Config:
        from_attributes = True

# ORR Rating Schemas
class OrrRatingBase(BaseModel):
    data: Optional[float] = None
    json_inputs: Optional[Any] = None # Using Any for JSON for simplicity
    rating: Optional[float] = None
    lgd: Optional[float] = None
    rating_record_id: int
    facility_profile_id: int

class OrrRatingCreate(OrrRatingBase):
    pass

class OrrRating(OrrRatingBase):
    orr_rating_id: int
    rating_record: Optional['RatingRecord'] = None
    facility_profile: Optional['FacilityProfile'] = None

    class Config:
        from_attributes = True

# RatingRecord Schemas
class RatingRecordBase(BaseModel):
    effective_date: date
    submitted: Optional[bool] = False
    obligor_id: int  # Added obligor_id as required field

class RatingRecordCreate(RatingRecordBase):
    pass

class RatingRecord(RatingRecordBase):
    rating_record_id: int
    obligor: Optional['Obligor'] = None
    lrr_rating: Optional['LrrRating'] = None  # Changed to Optional for 1:1
    orr_ratings: List['OrrRating'] = []  # Changed to List for 1:N

    class Config:
        from_attributes = True

# Update forward references
Obligor.update_forward_refs()
ObligorProfile.update_forward_refs()
Facility.update_forward_refs()
FacilityProfile.update_forward_refs()
RatingRecord.update_forward_refs()
LrrRating.update_forward_refs()
OrrRating.update_forward_refs() 