from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.staticfiles import StaticFiles # Import StaticFiles
from fastapi.responses import FileResponse # To serve index.html at root
from fastapi.middleware.cors import CORSMiddleware # <--- Add this import
import os # To construct path for static files
from sqlalchemy.orm import Session
from typing import List, Optional

from . import crud, models, schemas # Relative imports
from .database import SessionLocal, engine, get_db

# Determine the path to the static directory
# This assumes main.py is in app/db/playgroud/full/
static_file_path = os.path.join(os.path.dirname(__file__), "static")

# Create all tables in the database.
# This should ideally be handled by migrations (e.g., Alembic) in a production app.

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Credit Risk Data API",
    description="API for managing credit risk data including Obligors, Facilities, and Ratings.",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows all origins
    # allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"], # Or specific origins
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods (GET, POST, etc.)
    allow_headers=["*"], # Allows all headers
)

# Mount static files first, for paths like /static/main_full.js
app.mount("/static", StaticFiles(directory=static_file_path), name="static")

 
# API Endpoints (defined after static mount to avoid conflicts if API paths overlap)

# --- Root Endpoint to serve index.html ---
@app.get("/", response_class=FileResponse, include_in_schema=False)
async def read_index():
    index_html_path = os.path.join(static_file_path, "index.html")
    return FileResponse(index_html_path)

# --- Obligor Endpoints ---
@app.post("/obligors/", response_model=schemas.Obligor, tags=["Obligors"], summary="Create an Obligor")
def create_obligor(obligor: schemas.ObligorCreate, db: Session = Depends(get_db)):
    # Optionally, check if obligor with the same name already exists if names should be unique
    return crud.create_obligor(db=db, obligor=obligor)

@app.get("/obligors/", response_model=schemas.PaginatedObligors, tags=["Obligors"], summary="Get all Obligors")
def read_obligors(
    skip: int = 0, 
    limit: int = 100, 
    name_contains: Optional[str] = Query(None, alias="name_contains"),
    sort_by: Optional[str] = Query(None, alias="sort_by"),
    sort_desc: Optional[bool] = Query(False, alias="sort_desc"),
    facility_id: Optional[int] = Query(None, alias="facility_id"),
    db: Session = Depends(get_db)
):
    result = crud.get_obligors(
        db, 
        skip=skip, 
        limit=limit, 
        name_contains=name_contains, 
        sort_by=sort_by, 
        sort_desc=sort_desc,
        facility_id=facility_id
    )
    return result

@app.get("/obligors/{obligor_id}", response_model=schemas.Obligor, tags=["Obligors"], summary="Get an Obligor by ID")
def read_obligor(obligor_id: int, db: Session = Depends(get_db)):
    db_obligor = crud.get_obligor(db, obligor_id=obligor_id)
    if db_obligor is None:
        raise HTTPException(status_code=404, detail="Obligor not found")
    return db_obligor

# --- Obligor Profile Endpoints ---
@app.post("/obligors/{obligor_id}/profiles/", response_model=schemas.ObligorProfile, tags=["Obligor Profiles"], summary="Create an Obligor Profile")
def create_obligor_profile(obligor_id: int, profile: schemas.ObligorProfileCreate, db: Session = Depends(get_db)):
    # Ensure obligor_id in path matches obligor_id in profile, or remove from profile schema if always from path
    if profile.obligor_id != obligor_id:
        raise HTTPException(status_code=400, detail=f"Obligor ID in path ({obligor_id}) does not match Obligor ID in request body ({profile.obligor_id}).")
    db_obligor = crud.get_obligor(db, obligor_id=obligor_id)
    if not db_obligor:
        raise HTTPException(status_code=404, detail="Obligor not found, cannot create profile.")
    return crud.create_obligor_profile(db=db, profile=profile)

@app.get("/obligors/{obligor_id}/profiles/", response_model=List[schemas.ObligorProfile], tags=["Obligor Profiles"], summary="Get all Profiles for an Obligor")
def read_obligor_profiles(obligor_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    # db_obligor = crud.get_obligor(db, obligor_id=obligor_id) # Ensure obligor exists
    # if not db_obligor:
    #     raise HTTPException(status_code=404, detail="Obligor not found")
    profiles = crud.get_obligor_profiles_by_obligor(db, obligor_id=obligor_id, skip=skip, limit=limit)
    return profiles



# --- Facility Endpoints ---
@app.post("/facilities/", response_model=schemas.Facility, tags=["Facilities"], summary="Create a Facility")
def create_facility(facility: schemas.FacilityCreate, db: Session = Depends(get_db)):
    return crud.create_facility(db=db, facility=facility)







@app.get("/facilities/", response_model=schemas.PaginatedFacilities, tags=["Facilities"], summary="Get all Facilities")
def read_facilities(
    skip: int = 0, 
    limit: int = 100, 
    name_contains: Optional[str] = Query(None, alias="name_contains"),
    sort_by: Optional[str] = Query(None, alias="sort_by"),
    sort_desc: Optional[bool] = Query(False, alias="sort_desc"),
    facility_ids_in: Optional[str] = Query(None, alias="facility_ids_in"),
    obligor_id: Optional[int] = Query(None, alias="obligor_id"),
    db: Session = Depends(get_db)
):
    # Convert comma-separated string of facility IDs to list of integers
    facility_ids = None
    if facility_ids_in:
        try:
            facility_ids = [int(id_str) for id_str in facility_ids_in.split(',') if id_str.strip()]
        except ValueError:
            raise HTTPException(status_code=422, detail="Invalid facility_ids_in format. Expected comma-separated integers.")

    result = crud.get_facilities(
        db, 
        skip=skip, 
        limit=limit, 
        name_contains=name_contains, 
        sort_by=sort_by, 
        sort_desc=sort_desc, 
        facility_ids_in=facility_ids,
        obligor_id=obligor_id
    )
    return result

@app.get("/facilities/{facility_id}", response_model=schemas.Facility, tags=["Facilities"], summary="Get a Facility by ID")
def read_facility(facility_id: int, db: Session = Depends(get_db)):
    db_facility = crud.get_facility(db, facility_id=facility_id)
    if db_facility is None:
        raise HTTPException(status_code=404, detail="Facility not found")
    return db_facility

# --- Facility Profile Endpoints ---
@app.post("/facilities/{facility_id}/profiles/", response_model=schemas.FacilityProfile, tags=["Facility Profiles"], summary="Create a Facility Profile")
def create_facility_profile(facility_id: int, profile: schemas.FacilityProfileCreate, db: Session = Depends(get_db)):
    if profile.facility_id != facility_id:
        raise HTTPException(status_code=400, detail=f"Facility ID in path ({facility_id}) does not match Facility ID in request body ({profile.facility_id}).")
    db_facility = crud.get_facility(db, facility_id=facility_id)
    if not db_facility:
        raise HTTPException(status_code=404, detail="Facility not found, cannot create profile.")
    return crud.create_facility_profile(db=db, profile=profile)

@app.get("/facilities/{facility_id}/profiles/", response_model=List[schemas.FacilityProfile], tags=["Facility Profiles"], summary="Get all Profiles for a Facility")
def read_facility_profiles(facility_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    profiles = crud.get_facility_profiles_by_facility(db, facility_id=facility_id, skip=skip, limit=limit)
    return profiles

# --- RatingRecord Endpoints ---
@app.post("/rating-records/", response_model=schemas.RatingRecord, tags=["Rating Records"], summary="Create a Rating Record")
def create_rating_record(rating_record: schemas.RatingRecordCreate, db: Session = Depends(get_db)):
    return crud.create_rating_record(db=db, rating_record=rating_record)

@app.get("/rating-records/", response_model=List[schemas.RatingRecord], tags=["Rating Records"], summary="Get all Rating Records")
def read_rating_records(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    records = crud.get_rating_records(db, skip=skip, limit=limit)
    return records

@app.get("/rating-records/{rating_record_id}", response_model=schemas.RatingRecord, tags=["Rating Records"], summary="Get a Rating Record by ID")
def read_rating_record(rating_record_id: int, db: Session = Depends(get_db)):
    db_record = crud.get_rating_record(db, rating_record_id=rating_record_id)
    if db_record is None:
        raise HTTPException(status_code=404, detail="Rating Record not found")
    return db_record

# --- LRR Rating Endpoints ---
@app.post("/lrr-ratings/", response_model=schemas.LrrRating, tags=["LRR Ratings"], summary="Create an LRR Rating")
def create_lrr_rating(lrr_rating: schemas.LrrRatingCreate, db: Session = Depends(get_db)):
    db_rating_record = crud.get_rating_record(db, rating_record_id=lrr_rating.rating_record_id)
    if not db_rating_record:
        raise HTTPException(status_code=404, detail=f"RatingRecord with id {lrr_rating.rating_record_id} not found.")
    
    db_obligor_profile = crud.get_obligor_profile(db, obligor_profile_id=lrr_rating.obligor_profile_id)
    if not db_obligor_profile:
        raise HTTPException(status_code=404, detail=f"ObligorProfile with id {lrr_rating.obligor_profile_id} not found.")
    
    lrr_obligor_id = db_obligor_profile.obligor_id

    # Constraint 1: Check if tied to the same obligor as any existing ORR for this rating record
    if db_rating_record.orr_ratings:  # Changed from orr_rating to orr_ratings
        for orr in db_rating_record.orr_ratings:
            orr_facility_profile = orr.facility_profile
            if not orr_facility_profile or not orr_facility_profile.facility:
                # This case implies data inconsistency, should ideally not happen if relations are enforced
                raise HTTPException(status_code=500, detail=f"Data integrity issue: ORR {orr.orr_rating_id} has no valid facility profile or facility.")
            
            facility_obligor_ids = [o.obligor_id for o in orr_facility_profile.facility.obligors]
            if lrr_obligor_id not in facility_obligor_ids:
                raise HTTPException(status_code=400, 
                                    detail=f"Obligor mismatch: LRR's Obligor (ID: {lrr_obligor_id}) is not associated with the Facility (ID: {orr_facility_profile.facility_id}) of the existing ORR for RatingRecord (ID: {lrr_rating.rating_record_id}). Facility is linked to Obligors: {facility_obligor_ids}")

    return crud.create_lrr_rating(db=db, lrr_rating=lrr_rating)

# --- ORR Rating Endpoints ---
@app.post("/orr-ratings/", response_model=schemas.OrrRating, tags=["ORR Ratings"], summary="Create an ORR Rating")
def create_orr_rating(orr_rating: schemas.OrrRatingCreate, db: Session = Depends(get_db)):
    db_rating_record = crud.get_rating_record(db, rating_record_id=orr_rating.rating_record_id)
    if not db_rating_record:
        raise HTTPException(status_code=404, detail=f"RatingRecord with id {orr_rating.rating_record_id} not found.")
        
    db_facility_profile = crud.get_facility_profile(db, facility_profile_id=orr_rating.facility_profile_id)
    if not db_facility_profile:
        raise HTTPException(status_code=404, detail=f"FacilityProfile with id {orr_rating.facility_profile_id} not found.")

    if not db_facility_profile.facility:
         raise HTTPException(status_code=500, detail=f"Data integrity issue: FacilityProfile {db_facility_profile.facility_profile_id} is not linked to a Facility.")

    orr_facility_obligor_ids = [o.obligor_id for o in db_facility_profile.facility.obligors]
    if not orr_facility_obligor_ids:
        # If the facility for ORR is not linked to any obligor, then no LRR can satisfy the constraint.
        # However, an LRR might not yet exist. If an LRR *does* exist, it will fail the check below.
        # If no LRR exists yet, this ORR can be created, but a subsequent LRR creation might fail if its obligor is not this (empty) set.
        # This specific scenario (facility with no obligors) might also be a business rule violation itself.
        pass # Allow creation, but subsequent LRR creation might be problematic or indicate other issues.

    # Constraint 1: Check if tied to the same obligor as any existing LRRs for this rating record
    if db_rating_record.lrr_rating:  # Changed from lrr_ratings to lrr_rating
        if not db_rating_record.lrr_rating.obligor_profile:
             raise HTTPException(status_code=500, detail=f"Data integrity issue: LRR {db_rating_record.lrr_rating.lrr_rating_id} has no valid obligor profile.")
        lrr_obligor_id = db_rating_record.lrr_rating.obligor_profile.obligor_id
        if lrr_obligor_id not in orr_facility_obligor_ids:
            raise HTTPException(status_code=400, 
                                detail=f"Obligor mismatch: ORR's Facility (ID: {db_facility_profile.facility_id}, linked to Obligors: {orr_facility_obligor_ids}) is not associated with the Obligor (ID: {lrr_obligor_id}) of LRR (ID: {db_rating_record.lrr_rating.lrr_rating_id}) for RatingRecord (ID: {orr_rating.rating_record_id}).")

    return crud.create_orr_rating(db=db, orr_rating=orr_rating)

# --- ObligorFacility Link Endpoint ---
@app.post("/obligor-facility-links/", response_model=schemas.ObligorFacility, tags=["Obligor-Facility Links"], summary="Link an Obligor to a Facility")
def create_obligor_facility_link(link: schemas.ObligorFacilityCreate, db: Session = Depends(get_db)):
    # Check if obligor exists
    db_obligor = crud.get_obligor(db, obligor_id=link.obligor_id)
    if not db_obligor:
        raise HTTPException(status_code=404, detail=f"Obligor with id {link.obligor_id} not found.")
    # Check if facility exists
    db_facility = crud.get_facility(db, facility_id=link.facility_id)
    if not db_facility:
        raise HTTPException(status_code=404, detail=f"Facility with id {link.facility_id} not found.")
    
    # Check if link already exists (optional, depending on requirements)
    # existing_link = db.query(models.ObligorFacility).filter_by(obligor_id=link.obligor_id, facility_id=link.facility_id).first()
    # if existing_link:
    #     raise HTTPException(status_code=400, detail="Link between Obligor and Facility already exists.")

    return crud.create_obligor_facility_link(db=db, obligor_id=link.obligor_id, facility_id=link.facility_id)


# Basic GET endpoints for individual LRR and ORR ratings (if needed for direct access)
@app.get("/lrr-ratings/{lrr_rating_id}", response_model=schemas.LrrRating, tags=["LRR Ratings"], summary="Get an LRR Rating by ID")
def read_lrr_rating(lrr_rating_id: int, db: Session = Depends(get_db)):
    db_lrr = crud.get_lrr_rating(db, lrr_rating_id=lrr_rating_id)
    if db_lrr is None:
        raise HTTPException(status_code=404, detail="LRR Rating not found")
    return db_lrr

@app.get("/orr-ratings/{orr_rating_id}", response_model=schemas.OrrRating, tags=["ORR Ratings"], summary="Get an ORR Rating by ID")
def read_orr_rating(orr_rating_id: int, db: Session = Depends(get_db)):
    db_orr = crud.get_orr_rating(db, orr_rating_id=orr_rating_id)
    if db_orr is None:
        raise HTTPException(status_code=404, detail="ORR Rating not found")
    return db_orr

# To run the app (e.g., using uvicorn):
# uvicorn app.db.playgroud.full.main:app --reload --app-dir app/db/playgroud/full/
# Or if your CWD is app/db/playgroud/full: uvicorn main:app --reload 