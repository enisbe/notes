from sqlalchemy.orm import Session, joinedload, lazyload, selectinload
from sqlalchemy import func, desc, asc # For count and sorting
from typing import Optional, List
from . import models, schemas # Relative imports for files in the same directory

# Obligor CRUD
def get_obligor(db: Session, obligor_id: int):
    return db.query(models.Obligor).options(
        joinedload(models.Obligor.profiles),
        joinedload(models.Obligor.facilities),
        joinedload(models.Obligor.rating_records)
    ).filter(models.Obligor.obligor_id == obligor_id).first()

def get_obligors(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    name_contains: Optional[str] = None, 
    sort_by: Optional[str] = None, 
    sort_desc: Optional[bool] = False,
    facility_id: Optional[int] = None
):
    query = db.query(models.Obligor)
    total_query = db.query(func.count(models.Obligor.obligor_id))

    if name_contains:
        query = query.filter(models.Obligor.name.ilike(f"%{name_contains}%"))
        total_query = total_query.filter(models.Obligor.name.ilike(f"%{name_contains}%"))

    # Add filter by facility_id if provided
    if facility_id is not None:
        query = query.join(models.ObligorFacility).filter(models.ObligorFacility.facility_id == facility_id)
        total_query = total_query.join(models.ObligorFacility).filter(models.ObligorFacility.facility_id == facility_id)

    total = total_query.scalar()

    if sort_by:
        column = getattr(models.Obligor, sort_by, None)
        if column:
            if sort_desc:
                query = query.order_by(desc(column))
            else:
                query = query.order_by(asc(column))
        else:
            query = query.order_by(models.Obligor.obligor_id) # Default sort if column not found
    else:
        query = query.order_by(models.Obligor.obligor_id)

    items = query.offset(skip).limit(limit).all()
    return {"items": items, "total": total}

def create_obligor(db: Session, obligor: schemas.ObligorCreate):
    db_obligor = models.Obligor(**obligor.dict())
    db.add(db_obligor)
    db.commit()
    db.refresh(db_obligor)
    return db_obligor

# ObligorProfile CRUD
def get_obligor_profile(db: Session, obligor_profile_id: int):
    return db.query(models.ObligorProfile).options(
        joinedload(models.ObligorProfile.obligor),
        joinedload(models.ObligorProfile.orr_ratings)
    ).filter(models.ObligorProfile.obligor_profile_id == obligor_profile_id).first()

def get_obligor_profiles_by_obligor(db: Session, obligor_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.ObligorProfile).options(
        joinedload(models.ObligorProfile.orr_ratings)
    ).filter(models.ObligorProfile.obligor_id == obligor_id).offset(skip).limit(limit).all()

def create_obligor_profile(db: Session, profile: schemas.ObligorProfileCreate):
    db_profile = models.ObligorProfile(**profile.dict())
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return get_obligor_profile(db, db_profile.obligor_profile_id)  # Return with relationships loaded

# Facility CRUD
def get_facility(db: Session, facility_id: int):
    return db.query(models.Facility).options(
        joinedload(models.Facility.profiles),
        joinedload(models.Facility.obligors)
    ).filter(models.Facility.facility_id == facility_id).first()

def get_facilities(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    name_contains: Optional[str] = None, 
    sort_by: Optional[str] = None, 
    sort_desc: Optional[bool] = False, 
    facility_ids_in: Optional[List[int]] = None,
    obligor_id: Optional[int] = None
):
    query = db.query(models.Facility)
    total_query = db.query(func.count(models.Facility.facility_id))

    if name_contains:
        query = query.filter(models.Facility.name.ilike(f"%{name_contains}%"))
        total_query = total_query.filter(models.Facility.name.ilike(f"%{name_contains}%"))
    
    if facility_ids_in is not None and len(facility_ids_in) > 0:
        query = query.filter(models.Facility.facility_id.in_(facility_ids_in))
        total_query = total_query.filter(models.Facility.facility_id.in_(facility_ids_in))
    elif facility_ids_in is not None and len(facility_ids_in) == 0:
        return {"items": [], "total": 0}

    # Add filter by obligor_id if provided
    if obligor_id is not None:
        query = query.join(models.ObligorFacility).filter(models.ObligorFacility.obligor_id == obligor_id)
        total_query = total_query.join(models.ObligorFacility).filter(models.ObligorFacility.obligor_id == obligor_id)

    total = total_query.scalar()

    if sort_by:
        column = getattr(models.Facility, sort_by, None)
        if column:
            if sort_desc:
                query = query.order_by(desc(column))
            else:
                query = query.order_by(asc(column))
        else:
            query = query.order_by(models.Facility.facility_id)
    else:
        query = query.order_by(models.Facility.facility_id)

    items = query.offset(skip).limit(limit).all()
    return {"items": items, "total": total}

def create_facility(db: Session, facility: schemas.FacilityCreate):
    db_facility = models.Facility(**facility.dict())
    db.add(db_facility)
    db.commit()
    db.refresh(db_facility)
    return db_facility

# FacilityProfile CRUD
def get_facility_profile(db: Session, facility_profile_id: int):
    return db.query(models.FacilityProfile).options(
        joinedload(models.FacilityProfile.facility),
        joinedload(models.FacilityProfile.lrr_ratings)
    ).filter(models.FacilityProfile.facility_profile_id == facility_profile_id).first()

def get_facility_profiles_by_facility(db: Session, facility_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.FacilityProfile).options(
        joinedload(models.FacilityProfile.lrr_ratings)
    ).filter(models.FacilityProfile.facility_id == facility_id).offset(skip).limit(limit).all()

def create_facility_profile(db: Session, profile: schemas.FacilityProfileCreate):
    db_profile = models.FacilityProfile(**profile.dict())
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return get_facility_profile(db, db_profile.facility_profile_id)  # Return with relationships loaded

# RatingRecord CRUD
def get_rating_record(db: Session, rating_record_id: int):
    return db.query(models.RatingRecord).options(
        joinedload(models.RatingRecord.lrr_ratings)
            .joinedload(models.LrrRating.facility_profile)
            .joinedload(models.FacilityProfile.facility),
        joinedload(models.RatingRecord.orr_rating)
            .joinedload(models.OrrRating.obligor_profile)
            .joinedload(models.ObligorProfile.obligor)
    ).filter(models.RatingRecord.rating_record_id == rating_record_id).first()

def get_rating_records(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.RatingRecord).options(
        joinedload(models.RatingRecord.orr_rating)
            .joinedload(models.OrrRating.obligor_profile)
            .joinedload(models.ObligorProfile.obligor),
        joinedload(models.RatingRecord.lrr_ratings)
            .joinedload(models.LrrRating.facility_profile)
            .joinedload(models.FacilityProfile.facility)
    ).order_by(models.RatingRecord.rating_record_id).offset(skip).limit(limit).all()

def create_rating_record(db: Session, rating_record: schemas.RatingRecordCreate):
    db_rating_record = models.RatingRecord(**rating_record.dict())
    db.add(db_rating_record)
    db.commit()
    db.refresh(db_rating_record)
    return db_rating_record

# LrrRating CRUD
def get_lrr_rating(db: Session, lrr_rating_id: int):
    return db.query(models.LrrRating).options(
        joinedload(models.LrrRating.rating_record),
        joinedload(models.LrrRating.facility_profile)
    ).filter(models.LrrRating.lrr_rating_id == lrr_rating_id).first()

def create_lrr_rating(db: Session, lrr_rating: schemas.LrrRatingCreate):
    db_lrr_rating = models.LrrRating(**lrr_rating.dict())
    db.add(db_lrr_rating)
    db.commit()
    db.refresh(db_lrr_rating)
    return db_lrr_rating

# OrrRating CRUD
def get_orr_rating(db: Session, orr_rating_id: int):
    return db.query(models.OrrRating).options(
        joinedload(models.OrrRating.rating_record),
        joinedload(models.OrrRating.obligor_profile)
    ).filter(models.OrrRating.orr_rating_id == orr_rating_id).first()

def create_orr_rating(db: Session, orr_rating: schemas.OrrRatingCreate):
    db_orr_rating = models.OrrRating(**orr_rating.dict())
    db.add(db_orr_rating)
    db.commit()
    db.refresh(db_orr_rating)
    return db_orr_rating

# ObligorFacility Link CRUD
def create_obligor_facility_link(db: Session, obligor_id: int, facility_id: int):
    # Check if the link already exists
    existing_link = db.query(models.ObligorFacility).filter(
        models.ObligorFacility.obligor_id == obligor_id,
        models.ObligorFacility.facility_id == facility_id
    ).first()
    
    if existing_link:
        return existing_link
    
    db_link = models.ObligorFacility(obligor_id=obligor_id, facility_id=facility_id)
    db.add(db_link)
    db.commit()
    db.refresh(db_link)
    return db_link

# Note: Update and Delete operations are not implemented here for brevity but would follow a similar pattern. 