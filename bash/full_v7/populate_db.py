import random
from datetime import date, timedelta
from faker import Faker
from decimal import Decimal

# Assuming these are in the same directory or path is configured correctly
from .database import SessionLocal, engine # Use relative import for sibling modules
from . import models, schemas, crud      # Use relative import for sibling modules

# Initialize Faker
fake = Faker()

# Helper function to get a DB session
def get_db_session():
    return SessionLocal()

def populate():
    db = get_db_session()
    print("Starting data population with Faker...")

    # 1. Create 100 obligors
    obligors_db = []
    for _ in range(100):
        obligor_data = schemas.ObligorCreate(
            name=fake.company(),
            address=fake.address()
        )
        obligor = crud.create_obligor(db=db, obligor=obligor_data)
        obligors_db.append(obligor)
    print(f"- Created {len(obligors_db)} obligors.")

    # 2. Create 2 facilities per obligor and link them (~200 facilities)
    all_facilities_db = []
    obligor_facility_map = {} # To keep track of primary obligor for each facility

    for obligor in obligors_db:
        for _ in range(2): # Create 2 facilities for this obligor
            facility_data = schemas.FacilityCreate(
                name=f"{fake.bs().capitalize()} {fake.word().capitalize()} Center",
                description=f"Property Type: {random.choice(['Office Building', 'Retail Space', 'Industrial Unit', 'Warehouse', 'Mixed-Use Complex'])} - {fake.catch_phrase()}",
                address=f"{fake.street_address()}, {fake.city()}",
                property_type=random.choice(['Commercial', 'Industrial', 'Mixed-Use', 'Retail', 'Residential High-Rise'])
            )
            facility = crud.create_facility(db=db, facility=facility_data)
            all_facilities_db.append(facility)
            # Link this facility to its primary obligor
            crud.create_obligor_facility_link(db=db, obligor_id=obligor.obligor_id, facility_id=facility.facility_id)
            obligor_facility_map[facility.facility_id] = obligor.obligor_id # Store primary obligor
    print(f"- Created {len(all_facilities_db)} facilities and linked 2 to each of the {len(obligors_db)} obligors.")

    # 3. Out of 200 facilities, 10 will have 2 obligors
    if len(all_facilities_db) >= 10 and len(obligors_db) >= 2:
        facilities_for_second_obligor = random.sample(all_facilities_db, 10)
        additional_links_created = 0
        for facility_to_share in facilities_for_second_obligor:
            primary_obligor_id = obligor_facility_map.get(facility_to_share.facility_id)
            # Find an obligor that is not the primary one for this facility
            potential_secondary_obligors = [o for o in obligors_db if o.obligor_id != primary_obligor_id]
            if potential_secondary_obligors:
                secondary_obligor = random.choice(potential_secondary_obligors)
                # Check if link already exists (e.g. from initial 2-per-obligor creation if that obligor owned this facility)
                # This is a simplified check; a more robust check would query the association table
                existing_links = [
                    link for link in getattr(secondary_obligor, 'facilities', [])
                    if link.facility_id == facility_to_share.facility_id
                ]
                if not existing_links:
                    crud.create_obligor_facility_link(db=db, obligor_id=secondary_obligor.obligor_id, facility_id=facility_to_share.facility_id)
                    additional_links_created += 1
        print(f"- Assigned a second, distinct obligor to {additional_links_created} facilities (target was 10).")
    else:
        print("- Skipped assigning second obligors to facilities due to insufficient facilities/obligors.")


    # 4. Create 5 borrower profiles for each obligor (500 profiles)
    obligor_profiles_db = []
    for obligor in obligors_db:
        for _ in range(5):
            profile_data = schemas.ObligorProfileCreate(
                obligor_id=obligor.obligor_id,
                as_of_date=fake.date_between(start_date='-2y', end_date='today'),
                custom=fake.boolean(),
                commitment=fake.pydecimal(right_digits=2, positive=True, min_value=50000, max_value=10000000),
                moody_rating=round(random.uniform(1, 20), 1) # Max 20 for typical Moody's scale
            )
            profile = crud.create_obligor_profile(db=db, profile=profile_data)
            obligor_profiles_db.append(profile)
    print(f"- Created {len(obligor_profiles_db)} obligor profiles ({len(obligor_profiles_db) // len(obligors_db) if obligors_db else 0} per obligor).")

    # 5. Create 5 profiles for each facility (1000 facility profiles)
    facility_profiles_db = []
    for facility in all_facilities_db:
        for _ in range(5):
            collateral = fake.pydecimal(right_digits=2, positive=True, min_value=100000, max_value=50000000)
            # Ensure multiplication is between Decimal types
            max_loan_for_facility = collateral * Decimal('0.85') 
            # Ensure min_value for loan is not greater than the calculated max_loan_for_facility
            # Since min_collateral (100k) * 0.85 = 85k, which is > min_loan (50k), this should be fine.
            loan = fake.pydecimal(right_digits=2, positive=True, min_value=50000, max_value=max_loan_for_facility)
            ltv_val = round(float(loan / collateral), 2) if collateral > 0 else round(random.uniform(0.5, 0.85), 2)

            profile_data = schemas.FacilityProfileCreate(
                facility_id=facility.facility_id,
                as_of_date=fake.date_between(start_date='-2y', end_date='today'),
                loan_amount=loan,
                collateral_amount=collateral,
                custom=fake.boolean(),
                ltv=ltv_val,
                cap_rate=round(random.uniform(0.03, 0.10), 3),
                workout_cost=fake.pydecimal(right_digits=2, positive=True, min_value=1000, max_value=75000)
            )
            profile = crud.create_facility_profile(db=db, profile=profile_data)
            facility_profiles_db.append(profile)
    print(f"- Created {len(facility_profiles_db)} facility profiles ({len(facility_profiles_db) // len(all_facilities_db) if all_facilities_db else 0} per facility).")

    db.commit() # Ensure all changes are committed
    db.close()
    print("Data population script finished.")

if __name__ == "__main__":
    print("Initializing database and populating data...")
    # Drop all existing tables first to ensure a clean slate
    print("Dropping existing tables...")
    models.Base.metadata.drop_all(bind=engine)
    print("Existing tables dropped.")
    # Ensure tables are created
    models.Base.metadata.create_all(bind=engine)
    print("Database tables ensured/created.")
    
    populate() 