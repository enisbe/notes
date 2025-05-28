import random
from datetime import date, datetime
from faker import Faker
from decimal import Decimal
import json

from .database import SessionLocal, engine
from . import models, schemas, crud
from sqlalchemy.orm import joinedload, Session

# --- Configuration ---
NUM_OBLIGORS_TO_CREATE = 50  # Number of obligors to create
NUM_FACILITIES_PER_OBLIGOR = 2 # Number of facilities to create per obligor
NUM_PROFILES_PER_OBLIGOR = 3   # Number of obligor profiles per obligor
NUM_PROFILES_PER_FACILITY = 3  # Number of facility profiles per facility
MAX_RATING_RECORDS_TO_CREATE = 20 # Max number of full rating sets (RatingRecord + ORR + LRR(s))

# Initialize Faker
fake = Faker()

# Helper function to get a DB session
def get_db_session():
    return SessionLocal()

def decimal_random_uniform(min_val: float, max_val: float, precision: int = 2) -> Decimal:
    """Helper function to generate random decimal numbers"""
    val = random.uniform(min_val, max_val)
    return Decimal(str(round(val, precision)))

def populate_base_data(db: Session, num_obligors: int):
    print("Starting base data population (Obligors, Facilities, Profiles)...")

    # 1. Create obligors
    obligors_db = []
    for i in range(num_obligors):
        obligor_data = schemas.ObligorCreate(
            name=fake.company(),
            address=fake.address(),
            src_arng_num=fake.bothify(text=f"ARG-{'%%#####' if i < 100000 else '%%####'}") # Ensure unique enough
        )
        obligor = crud.create_obligor(db=db, obligor=obligor_data)
        obligors_db.append(obligor)
    print(f"- Created {len(obligors_db)} obligors.")

    # 2. Create facilities and link them
    all_facilities_db = []
    obligor_facility_map = {}

    for obligor in obligors_db:
        for _ in range(NUM_FACILITIES_PER_OBLIGOR):
            facility_data = schemas.FacilityCreate(
                name=f"{fake.bs().capitalize()} {fake.word().capitalize()} Center",
                description=f"Property Type: {random.choice(['Office Building', 'Retail Space', 'Industrial Unit', 'Warehouse', 'Mixed-Use Complex'])} - {fake.catch_phrase()}",
                address=f"{fake.street_address()}, {fake.city()}",
                property_type=random.choice(['Commercial', 'Industrial', 'Mixed-Use', 'Retail', 'Residential High-Rise']),
                src_facility_num=fake.bothify(text=f"FAC-{'%%#####' if len(all_facilities_db) < 100000 else '%%####'}")
            )
            facility = crud.create_facility(db=db, facility=facility_data)
            all_facilities_db.append(facility)
            crud.create_obligor_facility_link(db=db, obligor_id=obligor.obligor_id, facility_id=facility.facility_id)
            obligor_facility_map[facility.facility_id] = obligor.obligor_id
    print(f"- Created {len(all_facilities_db)} facilities and linked them to obligors.")

    # 3. Assign additional obligors to some facilities (optional)
    if len(all_facilities_db) >= 10 and len(obligors_db) >= 2:
        facilities_for_second_obligor = random.sample(all_facilities_db, min(10, len(all_facilities_db)))
        additional_links_created = 0
        for facility_to_share in facilities_for_second_obligor:
            primary_obligor_id = obligor_facility_map.get(facility_to_share.facility_id)
            potential_secondary_obligors = [o for o in obligors_db if o.obligor_id != primary_obligor_id]
            if potential_secondary_obligors:
                secondary_obligor = random.choice(potential_secondary_obligors)
                # Check if link already exists to prevent duplicate entries if the secondary obligor already has this facility.
                # This requires loading the facilities for the secondary obligor or querying the association table directly.
                # For simplicity, we'll rely on the database to prevent duplicates if the link creation logic handles it,
                # or accept that this might try to create duplicates which the DB might reject if unique constraints are in place.
                # crud.create_obligor_facility_link is designed to return existing if found, so this is safe.
                crud.create_obligor_facility_link(db=db, obligor_id=secondary_obligor.obligor_id, facility_id=facility_to_share.facility_id)
                additional_links_created += 1
        print(f"- Assigned a second, distinct obligor to {additional_links_created} facilities.")

    # 4. Create obligor profiles
    obligor_profiles_db = []
    for obligor in obligors_db:
        for _ in range(NUM_PROFILES_PER_OBLIGOR):
            profile_data = schemas.ObligorProfileCreate(
                obligor_id=obligor.obligor_id,
                as_of_date=fake.date_between(start_date='-2y', end_date='today'),
                credit_officer=fake.name(),
                comment=fake.text(max_nb_chars=200)
            )
  
            profile = crud.create_obligor_profile(db=db, profile=profile_data)
            obligor_profiles_db.append(profile)
    print(f"- Created {len(obligor_profiles_db)} obligor profiles.")

    # 5. Create facility profiles
    facility_profiles_db = []
    for facility in all_facilities_db:
        for _ in range(NUM_PROFILES_PER_FACILITY):
            global_commitment = decimal_random_uniform(1000000, 50000000)
            key_bank_percentage = decimal_random_uniform(0.1, 1.0, 5) # Increased precision for percentage
            key_bank_commitment = global_commitment * key_bank_percentage
            key_bank_outstandings = key_bank_commitment
            global_operating_income = decimal_random_uniform(100000, 5000000)
            # Ensure operating_expense max is not negative or zero if global_operating_income is small
            max_op_expense = float(global_operating_income * Decimal('0.8'))
            min_op_expense = 50000
            if max_op_expense < min_op_expense: # handle edge case where 80% of income is less than min fixed expense
                max_op_expense = min_op_expense + 10000 # ensure max > min

            operating_expense = decimal_random_uniform(min_op_expense, max_op_expense)
            net_operating_income = global_operating_income - operating_expense
            appraisal_value = decimal_random_uniform(1000000, 100000000)
            cap_rate = decimal_random_uniform(0.03, 0.10, 5) # Increased precision
            ltv = decimal_random_uniform(0.5, 0.85, 5)      # Increased precision
            workout_cost = decimal_random_uniform(0.03, 0.10, 5)

            profile_data = schemas.FacilityProfileCreate(
                facility_id=facility.facility_id,
                as_of_date=fake.date_between(start_date='-2y', end_date='today'),
                rec_web_deal_number=random.randint(10000, 99999),
                statement_date=fake.date_between(start_date='-2y', end_date='today'),
                stabilized=random.choice(['Y', 'N', 'S']), # Added 'S' for Stabilizing
                statement_type=random.choice(['Annual', 'Quarterly', 'Monthly', 'Pro-Forma']),
                snc_indicator=random.choice(['Y', 'N', None]), # Allow None
                key_bank_percentage=float(key_bank_percentage),
                global_commitment=float(global_commitment),
                key_bank_commitment=float(key_bank_commitment),
                key_bank_outstandings=float(key_bank_outstandings),
                global_operating_income=float(global_operating_income),
                operating_expense=float(operating_expense),
                net_operating_income=float(net_operating_income),
                appraisal_value=float(appraisal_value),
                cap_rate=float(cap_rate),
                ltv=float(ltv)
 
            )
            profile = crud.create_facility_profile(db=db, profile=profile_data)
            facility_profiles_db.append(profile)
    print(f"- Created {len(facility_profiles_db)} facility profiles.")
    
    db.commit() # Commit base data population
    print("Base data population finished.")
    return obligors_db, all_facilities_db # Return for potential use in rating population


def populate_rating_data(db: Session, num_rating_records_to_create: int):
    print("Starting RatingRecord, ORR, and LRR data population...")

    # Fetch obligor profiles that don't already have an ORR rating and have associated facilities/profiles
    # This query ensures we only pick obligor profiles that can actually have ORR and LRR ratings created.
    eligible_obligor_profiles = db.query(models.ObligorProfile).join(
        models.Obligor, models.ObligorProfile.obligor_id == models.Obligor.obligor_id
    ).join(
        models.ObligorFacility, models.Obligor.obligor_id == models.ObligorFacility.obligor_id
    ).join(
        models.Facility, models.ObligorFacility.facility_id == models.Facility.facility_id
    ).join(
        models.FacilityProfile, models.Facility.facility_id == models.FacilityProfile.facility_id
    ).outerjoin(
        models.OrrRating, models.ObligorProfile.obligor_profile_id == models.OrrRating.obligor_profile_id
    ).filter(
        models.OrrRating.orr_rating_id == None # No existing ORR rating for this obligor profile
    ).options(
        joinedload(models.ObligorProfile.obligor)
            .subqueryload(models.Obligor.facilities)
            .subqueryload(models.Facility.profiles) # Eager load facility profiles
    ).distinct().order_by(models.ObligorProfile.obligor_profile_id).limit(num_rating_records_to_create * 2).all() # Fetch a bit more to have choices

    if not eligible_obligor_profiles:
        print("! No eligible ObligorProfiles found for rating creation. Ensure base data (obligors, facilities, profiles) exists and meets criteria.")
        db.close()
        return

    print(f"- Fetched {len(eligible_obligor_profiles)} eligible ObligorProfiles to process for rating creation.")
    random.shuffle(eligible_obligor_profiles) # Randomize selection

    rating_records_created_count = 0
    orr_ratings_created_count = 0
    lrr_ratings_created_count = 0
    dots_printed_on_line = 0
    PROGRESS_DOTS_PER_LINE = 50

    print("Creating rating sets (RatingRecord, ORR, LRR(s)). One dot per set: ")

    for ob_profile in eligible_obligor_profiles:
        if rating_records_created_count >= num_rating_records_to_create:
            break

        if not ob_profile.obligor: # Should be loaded, but double-check
            print(f"  - ObligorProfile ID {ob_profile.obligor_profile_id} has no parent obligor. Skipping.")
            continue
        
        obligor = ob_profile.obligor
        
        facility_profiles_to_rate = []
        if hasattr(obligor, 'facilities') and obligor.facilities:
            for facility in obligor.facilities:
                if hasattr(facility, 'profiles') and facility.profiles:
                    latest_facility_profile = sorted(facility.profiles, key=lambda p: p.as_of_date, reverse=True)[0]
                    facility_profiles_to_rate.append(latest_facility_profile)

        if not facility_profiles_to_rate:
            print(f"  - Obligor ID {obligor.obligor_id} (Profile ID {ob_profile.obligor_profile_id}) has no valid facility profiles. Skipping.")
            continue

        # Double check again for existing ORR, as the initial query might not be perfect with limits and shuffles
        existing_orr_check = db.query(models.OrrRating).filter(models.OrrRating.obligor_profile_id == ob_profile.obligor_profile_id).first()
        if existing_orr_check:
            print(f"  - ObligorProfile ID {ob_profile.obligor_profile_id} already has an ORR. Skipping (race condition or re-run).")
            continue

        try:
            # 1. Create a RatingRecord
            rating_record_data = schemas.RatingRecordCreate(
                obligor_id=obligor.obligor_id,
                effective_date=date.today(),
                submitted=fake.boolean(chance_of_getting_true=30),
                credit_officer=ob_profile.credit_officer or fake.name() # Use profile's CO or fake one
            )
            db_rating_record = crud.create_rating_record(db=db, rating_record=rating_record_data)
            if not db_rating_record:
                print(f"\n  [WARN] Failed to create RatingRecord for ObligorProfile ID {ob_profile.obligor_profile_id}. Skipping.")
                db.rollback() # Rollback potential partial commit from create_rating_record
                continue
            
            # 2. Create one OrrRating for this RatingRecord
            orr_json_inputs = {
                "industry_risk": round(random.uniform(1, 5), 2), "business_position": round(random.uniform(1, 5), 2),
                "financial_profile": round(random.uniform(1, 5), 2), "parent_support": round(random.uniform(0, 1), 2),
                "country_risk": round(random.uniform(1, 5), 2), "note": "Populated by script for ORR"
            }
            orr_rating_data = schemas.OrrRatingCreate(
                rating_record_id=db_rating_record.rating_record_id,
                obligor_profile_id=ob_profile.obligor_profile_id,
                json_inputs=orr_json_inputs,
                assigned_orr=round(random.uniform(1, 10), 1),
                assigned_pd=round(random.uniform(0.001, 0.25), 4), # Increased max PD
                comment=fake.sentence(nb_words=10)
            )
            
            db_orr_rating = crud.create_orr_rating(db=db, orr_rating=orr_rating_data)
            if not db_orr_rating: 
                print(f"\n  [WARN] Failed to create or retrieve OrrRating for ObligorProfile ID {ob_profile.obligor_profile_id}. Rolling back RatingRecord {db_rating_record.rating_record_id}.")
                db.rollback() # Rollback RatingRecord and other potential changes in this transaction
                continue 
            
            # 3. Create LrrRatings for the facilities of this obligor
            random.shuffle(facility_profiles_to_rate)
            MAX_LRR_PER_RECORD = min(random.randint(1,3), len(facility_profiles_to_rate)) # 1 to 3 LRRs
            
            lrr_created_for_this_record = 0
            for fac_profile in facility_profiles_to_rate[:MAX_LRR_PER_RECORD]:
                lrr_json_inputs = {
                    "collateral_quality": round(random.uniform(1, 5), 2), "facility_structure": round(random.uniform(1, 5), 2),
                    "third_party_support": round(random.uniform(0, 1), 2), "recovery_expectations": round(random.uniform(1, 5), 2),
                    "market_conditions": round(random.uniform(1, 5), 2), "note": "Populated by script for LRR"
                }
                lrr_rating_data = schemas.LrrRatingCreate(
                    rating_record_id=db_rating_record.rating_record_id,
                    facility_id=fac_profile.facility_id,
                    facility_profile_id=fac_profile.facility_profile_id,
                    json_inputs=lrr_json_inputs,
                    assigned_lrr=round(random.uniform(1, 10), 1),
                    assigned_lgd=round(random.uniform(0.05, 0.75), 2),
                    comment=fake.sentence(nb_words=10)
                )
                db_lrr_rating = crud.create_lrr_rating(db=db, lrr_rating=lrr_rating_data)
                if db_lrr_rating:
                    lrr_ratings_created_count += 1
                    lrr_created_for_this_record +=1
                else:
                    print(f"\n  [WARN] Failed to create LrrRating for FacilityProfile ID {fac_profile.facility_profile_id} (RatingRecord {db_rating_record.rating_record_id})")
            
            if lrr_created_for_this_record == 0:
                print(f"\n  [WARN] No LRR Ratings could be created for RatingRecord ID {db_rating_record.rating_record_id}. Rolling back this record set.")
                db.rollback()
                continue

            db.commit() # Commit the full set: RatingRecord, ORR, and its LRRs
            
            # Increment counts after successful commit of the set
            rating_records_created_count += 1
            orr_ratings_created_count += 1 # Assuming one ORR per RatingRecord
            # lrr_ratings_created_count is already incremented per LRR

            print(".", end="", flush=True)
            dots_printed_on_line += 1
            if dots_printed_on_line >= PROGRESS_DOTS_PER_LINE:
                print() # Newline
                dots_printed_on_line = 0

        except Exception as e:
            print(f"\n  [ERROR] An unexpected error occurred while processing ObligorProfile ID {ob_profile.obligor_profile_id}: {e}. Rolling back.")
            db.rollback()
            continue

    if dots_printed_on_line > 0: # Ensure cursor moves to next line if dots were printed
        print()

    print(f"- Successfully created {rating_records_created_count} RatingRecords with {orr_ratings_created_count} ORRs and {lrr_ratings_created_count} LRRs.")
    db.close()
    print("Rating data population script finished.")

def populate_all_data(num_obligors: int, num_rating_records: int):
    """Main function to orchestrate data population."""
    db = get_db_session()
    
    # Initialize Database: Drop and Create Tables
    print("Initializing database...")
    print("Dropping existing tables (if any)...")
    models.Base.metadata.drop_all(bind=engine)
    print("Existing tables dropped.")
    models.Base.metadata.create_all(bind=engine)
    print("Database tables ensured/created.")
    
    # Populate Base Data
    populate_base_data(db, num_obligors)
    
    # Populate Rating Data
    # Re-fetch a session for rating population as populate_base_data closes its session.
    # This also ensures that the base data is committed and available.
    db_for_ratings = get_db_session()
    populate_rating_data(db_for_ratings, num_rating_records)
    
    print("All data population tasks finished.")

if __name__ == "__main__":
    print("Starting comprehensive data population script...")
    
    # Use the configuration variables from the top of the script
    populate_all_data(
        num_obligors=NUM_OBLIGORS_TO_CREATE,
        num_rating_records=MAX_RATING_RECORDS_TO_CREATE
    )
    
    print("Script execution complete.") 