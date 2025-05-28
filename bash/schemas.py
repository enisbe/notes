from pydantic import BaseModel
from typing import List, Optional, Any
from datetime import date, datetime

# Forward declarations for circular dependencies
class ObligorProfile(BaseModel): pass
class FacilityProfile(BaseModel): pass
class LrrRating(BaseModel): pass
class OrrRating(BaseModel): pass
class RatingRecord(BaseModel): pass
class Facility(BaseModel): pass
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
    src_arng_num: Optional[str] = None
    name: Optional[str] = None
    address: Optional[str] = None

class ObligorCreate(ObligorBase):
    name: str  # Name is required for creation

class Obligor(ObligorBase):
    obligor_id: int
    created: datetime
    modified: datetime
    profiles: List['ObligorProfile'] = []
    facilities: List['Facility'] = []
    rating_records: List['RatingRecord'] = []

    class Config:
        from_attributes = True

# Paginated Obligor Schema
class PaginatedObligors(BaseModel):
    items: List[Obligor]
    total: int

# ObligorProfile Schemas
class ObligorProfileBase(BaseModel):
    obligor_id: Optional[int] = None
    as_of_date: Optional[date] = None
    credit_officer: Optional[str] = None
    comment: Optional[str] = None

class ObligorProfileCreate(ObligorProfileBase):
    pass

class ObligorProfile(ObligorProfileBase):
    obligor_profile_id: int 
    insert_datetime: Optional[datetime] = None
    update_datetime: Optional[datetime] = None
    obligor: Optional['Obligor'] = None
    orr_ratings: Optional['OrrRating'] = None

    class Config:
        from_attributes = True

# Facility Schemas
class FacilityBase(BaseModel):
    description: Optional[str] = None
    name: Optional[str] = None
    src_facility_num: Optional[str] = None
    address: Optional[str] = None
    property_type: Optional[str] = None

class FacilityCreate(FacilityBase):
    name: str  # Name is required for creation

class Facility(FacilityBase):
    facility_id: int
    insert_datetime: Optional[datetime] = None
    update_datetime: Optional[datetime] = None
    profiles: List['FacilityProfile'] = []
    obligors: List['Obligor'] = []

    class Config:
        from_attributes = True

# Paginated Facility Schema
class PaginatedFacilities(BaseModel):
    items: List[Facility]
    total: int

# FacilityProfile Schemas
class FacilityProfileBase(BaseModel):
    facility_id: int
    as_of_date: Optional[date] = None
    rec_web_deal_number: int
    statement_date: Optional[date] = None
    stabilized: Optional[str] = None
    statement_type: Optional[str] = None
    snc_indicator: Optional[str] = None
    key_bank_percentage: Optional[float] = None
    global_commitment: Optional[float] = None
    key_bank_commitment: Optional[float] = None
    key_bank_outstandings: Optional[float] = None
    global_operating_income: Optional[float] = None
    operating_expense: Optional[float] = None
    net_operating_income: Optional[float] = None
    appraisal_value: Optional[float] = None
    cap_rate: Optional[float] = None
    ltv: Optional[float] = None
 

class FacilityProfileCreate(FacilityProfileBase):
    pass

class FacilityProfile(FacilityProfileBase):
    facility_profile_id: int
    insert_datetime: Optional[datetime] = None
    update_datetime: Optional[datetime] = None
    facility: Optional['Facility'] = None
    lrr_ratings: List['LrrRating'] = []

    class Config:
        from_attributes = True

# RatingRecord Schemas
class RatingRecordBase(BaseModel):
    obligor_id: int
    effective_date: date
    submitted: bool
    credit_officer: Optional[str] = None

class RatingRecordCreate(RatingRecordBase):
    pass

class RatingRecord(RatingRecordBase):
    rating_record_id: int
    insert_datetime: Optional[datetime] = None
    update_datetime: Optional[datetime] = None
    obligor: Optional['Obligor'] = None
    lrr_ratings: List['LrrRating'] = []
    orr_rating: Optional['OrrRating'] = None

    class Config:
        from_attributes = True

# LRR Rating Schemas
class LrrRatingBase(BaseModel):
    rating_record_id: int
    facility_id: int
    facility_profile_id: int
    json_inputs: Optional[Any] = None
    assigned_lrr: Optional[float] = None
    assigned_lgd: Optional[float] = None
    comment: Optional[str] = None

class LrrRatingCreate(LrrRatingBase):
    pass

class LrrRating(LrrRatingBase):
    lrr_rating_id: int
    insert_datetime: Optional[datetime] = None
    update_datetime: Optional[datetime] = None
    rating_record: Optional['RatingRecord'] = None
    facility_profile: Optional['FacilityProfile'] = None

    class Config:
        from_attributes = True

# ORR Rating Schemas
class OrrRatingBase(BaseModel):
    rating_record_id: int
    obligor_profile_id: int
    json_inputs: Optional[Any] = None
    assigned_orr: Optional[float] = None
    assigned_pd: Optional[float] = None
    comment: Optional[str] = None

class OrrRatingCreate(OrrRatingBase):
    pass

class OrrRating(OrrRatingBase):
    orr_rating_id: int
    insert_datetime: Optional[datetime] = None
    update_datetime: Optional[datetime] = None
    rating_record: Optional['RatingRecord'] = None
    obligor_profile: Optional['ObligorProfile'] = None

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