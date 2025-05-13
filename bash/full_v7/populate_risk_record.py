import random
from datetime import date
from faker import Faker # Included for consistency, though not heavily used
# Assuming these are in the same directory or path is configured correctly
from .database import SessionLocal, engine # Corrected import
from . import models, schemas, crud      # Corrected import

# Initialize Faker
fake = Faker()

# Helper function to get a DB session
def get_db_session():
    return SessionLocal()

def populate_orr_ratings(): # Renamed for clarity
    """
    Populates OrrRating data.
    Creates up to 10 OrrRating records, associated with facilities of obligors
    and using obligor's moody_rating for the OrrRating.data field.
    """
    db = get_db_session()
    print("Starting OrrRating data population...")

    # Fetch a pool of obligors to find ones with profiles and facilities
    # Assuming crud.get_obligors returns a PaginatedObligors schema object
    print("- Attempting to fetch obligors...")
    paginated_obligors_response = crud.get_obligors(db=db, skip=0, limit=50) # Fetch up to 50
    print(f"- Debug: Type of paginated_obligors_response: {type(paginated_obligors_response)}")
    
    # Initialize the list before any other operations
    potential_obligors_list = []
    
    # If it's a dictionary, print its keys to understand its structure
    if isinstance(paginated_obligors_response, dict):
        print(f"- Debug: Dictionary keys: {list(paginated_obligors_response.keys())}")
        # If it has an 'items' key, print what that contains
        if 'items' in paginated_obligors_response:
            print(f"- Debug: Type of paginated_obligors_response['items']: {type(paginated_obligors_response['items'])}")
            # Print the length of the items list
            print(f"- Debug: Length of paginated_obligors_response['items']: {len(paginated_obligors_response['items'])}")
            if paginated_obligors_response['items'] and len(paginated_obligors_response['items']) > 0:
                print(f"- Debug: Type of first item in paginated_obligors_response['items']: {type(paginated_obligors_response['items'][0])}")
                # Directly assign this to potential_obligors_list
                potential_obligors_list = paginated_obligors_response['items']
            else:
                print("! The 'items' list in the response is empty.")
                print("! No obligors were found in the database. Have you run the populate_db.py script?")
                # Keep potential_obligors_list as an empty list
    elif isinstance(paginated_obligors_response, list):
        # If it's a list directly, use it
        potential_obligors_list = paginated_obligors_response
        if not potential_obligors_list:
            print("! The list returned from crud.get_obligors is empty.")
    else:
        # For any other type, keep potential_obligors_list as empty and log
        print(f"! Unexpected response type from crud.get_obligors: {type(paginated_obligors_response)}")
                
    # Print diagnostic info about the potential_obligors_list
    print(f"- Debug: Type of potential_obligors_list: {type(potential_obligors_list)}")
    print(f"- Debug: Length of potential_obligors_list: {len(potential_obligors_list) if potential_obligors_list else 0}")

    if not potential_obligors_list:
        print("! No obligors to process. ORR population will be skipped.")
        print("! Please ensure the database has obligors by running 'populate_db.py' first.")
        db.close()
        return
    else:
        # Convert potential_obligors_list to a regular list if it's not already one
        if not isinstance(potential_obligors_list, list):
            potential_obligors_list = list(potential_obligors_list)
            
        # Debug: Print type and content of the first item
        if potential_obligors_list:
            print(f"- Debug: Type of first item in potential_obligors_list: {type(potential_obligors_list[0])}")
            print(f"- Debug: First item content: {str(potential_obligors_list[0])[:100]}...")  # Limiting output length

    orr_ratings_created_count = 0
    MAX_ORR_RECORDS_TO_CREATE = 10

    print(f"- Processing up to {len(potential_obligors_list)} obligors to create {MAX_ORR_RECORDS_TO_CREATE} ORR records.")
    
    for obligor in potential_obligors_list:
        if orr_ratings_created_count >= MAX_ORR_RECORDS_TO_CREATE:
            break

        # 1. Get latest ObligorProfile for moody_rating
        latest_obligor_profile = None
        if hasattr(obligor, 'profiles') and obligor.profiles:
            try:
                latest_obligor_profile = sorted(obligor.profiles, key=lambda p: p.as_of_date, reverse=True)[0]
            except IndexError: # Should not happen if obligor.profiles is not empty
                pass
        
        if not latest_obligor_profile:
            print(f"  - Obligor ID {obligor.obligor_id} ('{obligor.name}') has no profiles. Skipping.")
            continue
        
        if latest_obligor_profile.moody_rating is None:
            print(f"  - Obligor ID {obligor.obligor_id} latest profile (ID: {latest_obligor_profile.obligor_profile_id}) has no moody_rating. Skipping facilities for this obligor.")
            continue

        # 2. Iterate through Obligor's Facilities
        if not hasattr(obligor, 'facilities') or not obligor.facilities:
            print(f"  - Obligor ID {obligor.obligor_id} ('{obligor.name}') has no associated facilities. Skipping.")
            continue

        for facility in obligor.facilities:
            if orr_ratings_created_count >= MAX_ORR_RECORDS_TO_CREATE:
                break

            # 3. Get latest FacilityProfile
            latest_facility_profile = None
            if hasattr(facility, 'profiles') and facility.profiles:
                try:
                    latest_facility_profile = sorted(facility.profiles, key=lambda p: p.as_of_date, reverse=True)[0]
                except IndexError:
                    pass
            
            if not latest_facility_profile:
                print(f"    - Facility ID {facility.facility_id} ('{facility.name}') for Obligor ID {obligor.obligor_id} has no profiles. Skipping.")
                continue

            try:
                # 4. Create RatingRecord with obligor_id
                rating_record_data = schemas.RatingRecordCreate(
                    obligor_id=obligor.obligor_id,  # Added obligor_id
                    effective_date=date.today(),
                    submitted=False
                )
                db_rating_record = crud.create_rating_record(db=db, rating_record=rating_record_data)
                # Note: create_rating_record should add to session but not commit yet.

                # 5. Create OrrRating
                orr_rating_data = schemas.OrrRatingCreate(
                    rating_record_id=db_rating_record.rating_record_id,
                    facility_profile_id=latest_facility_profile.facility_profile_id,
                    data=float(latest_obligor_profile.moody_rating), # Using obligor's moody rating
                    rating=round(random.uniform(1, 7), 1),      # Placeholder ORR specific rating
                    lgd=round(random.uniform(0.1, 0.9), 2),       # Placeholder LGD
                    json_inputs={
                        "source_obligor_id": obligor.obligor_id,
                        "source_obligor_profile_id": latest_obligor_profile.obligor_profile_id,
                        "source_moody_rating": float(latest_obligor_profile.moody_rating),
                        "facility_id": facility.facility_id,
                        "note": "Populated by script for ORR"
                    }
                )
                # Assuming crud.create_orr_rating adds to session.
                db_orr_rating = crud.create_orr_rating(db=db, orr_rating=orr_rating_data)
                
                if db_orr_rating:
                    orr_ratings_created_count += 1
                    print(f"  - Prepared ORR for Facility ID {facility.facility_id} (Obligor ID {obligor.obligor_id}, Moody's: {latest_obligor_profile.moody_rating}). Count: {orr_ratings_created_count}/{MAX_ORR_RECORDS_TO_CREATE}")
                else:
                    print(f"  - Failed to prepare ORR for Facility ID {facility.facility_id} (create_orr_rating returned None).")

            except Exception as e:
                print(f"  - An unexpected error occurred while processing Facility ID {facility.facility_id} for Obligor ID {obligor.obligor_id}: {e}")
                # Consider rolling back db.add() if not handled by CRUD, or skip commit for this item
                # For simplicity here, we'll let it attempt to commit what it has or fail.

    if orr_ratings_created_count > 0:
        try:
            db.commit() # Commit all prepared OrrRatings and their RatingRecords
            print(f"- Successfully created and committed {orr_ratings_created_count} OrrRating entries.")
        except Exception as e:
            db.rollback()
            print(f"! Error committing ORR ratings to database: {e}. Changes rolled back.")
    elif orr_ratings_created_count < MAX_ORR_RECORDS_TO_CREATE and potential_obligors_list:
        print(f"- No new OrrRating entries were created (Target was {MAX_ORR_RECORDS_TO_CREATE}, created {orr_ratings_created_count}). Check data availability (obligors with profiles & moody_rating, and facilities with profiles).")
    else:
        print("- No OrrRating entries were created.")
        
    db.close()
    print("OrrRating data population script finished.")

if __name__ == "__main__":
    print("Initializing for OrrRating data population...")
    
    try:
        print("Ensuring database tables exist (including RatingRecord, OrrRating)...")
        # This ensures tables from models.py are created if they don't exist.
        # It does NOT drop tables.
        models.Base.metadata.create_all(bind=engine)
        print("Database tables ensured/created.")
        
        populate_orr_ratings()
    except ImportError as e:
        print(f"ImportError: {e}. Please ensure this script is run in an environment where 'full_v6' modules are accessible (e.g., from the parent directory using 'python -m full_v6.populate_risk_record' or if 'full_v6' is in PYTHONPATH).")
    except Exception as e:
        print(f"An error occurred during the OrrRating population process: {e}")
        # Consider logging the stack trace here for debugging
    
    print("OrrRating population process complete.") 