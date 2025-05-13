from sqlalchemy import create_engine, Column, Integer, String, Date, Float, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class ObligorFacility(Base):
    __tablename__ = "obligor_facility"
    obligor_facility_id = Column(Integer, primary_key=True, index=True)
    obligor_id = Column(Integer, ForeignKey("obligor.obligor_id"))
    facility_id = Column(Integer, ForeignKey("facility.facility_id"))

class Obligor(Base):
    __tablename__ = "obligor"

    obligor_id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    address = Column(String)

    profiles = relationship("ObligorProfile", back_populates="obligor")
    facilities = relationship("Facility", secondary="obligor_facility", back_populates="obligors")
    rating_records = relationship("RatingRecord", back_populates="obligor")

class ObligorProfile(Base):
    __tablename__ = "obligor_profile"

    obligor_profile_id = Column(Integer, primary_key=True, index=True)
    obligor_id = Column(Integer, ForeignKey("obligor.obligor_id"))
    as_of_date = Column(Date)
    custom = Column(Boolean)
    commitment = Column(Float)
    moody_rating = Column(Float)

    obligor = relationship("Obligor", back_populates="profiles")
    lrr_rating = relationship("LrrRating", back_populates="obligor_profile", uselist=False)  # 1:1 with LrrRating

class Facility(Base):
    __tablename__ = "facility"

    facility_id = Column(Integer, primary_key=True, index=True)
    description = Column(String)
    name = Column(String)
    address = Column(String)
    property_type = Column(String)

    profiles = relationship("FacilityProfile", back_populates="facility")
    obligors = relationship("Obligor", secondary="obligor_facility", back_populates="facilities")

class FacilityProfile(Base):
    __tablename__ = "facility_profile"

    facility_profile_id = Column(Integer, primary_key=True, index=True)
    facility_id = Column(Integer, ForeignKey("facility.facility_id"))
    as_of_date = Column(Date)
    loan_amount = Column(Float)
    collateral_amount = Column(Float)
    custom = Column(Boolean)
    ltv = Column(Float)
    cap_rate = Column(Float)
    workout_cost = Column(Float)

    facility = relationship("Facility", back_populates="profiles")
    orr_ratings = relationship("OrrRating", back_populates="facility_profile")  # 1:N with OrrRating

class RatingRecord(Base):
    __tablename__ = "rating_record"

    rating_record_id = Column(Integer, primary_key=True, index=True)
    obligor_id = Column(Integer, ForeignKey("obligor.obligor_id"))
    effective_date = Column(Date)
    submitted = Column(Boolean)

    obligor = relationship("Obligor", back_populates="rating_records")
    lrr_rating = relationship("LrrRating", back_populates="rating_record", uselist=False)  # 1:1 with LrrRating
    orr_ratings = relationship("OrrRating", back_populates="rating_record")  # 1:N with OrrRating

class LrrRating(Base):
    __tablename__ = "lrr_rating"

    lrr_rating_id = Column(Integer, primary_key=True, index=True)
    rating_record_id = Column(Integer, ForeignKey("rating_record.rating_record_id"), unique=True)  # Added unique=True for 1:1
    obligor_profile_id = Column(Integer, ForeignKey("obligor_profile.obligor_profile_id"), unique=True)  # 1:1 with ObligorProfile
    data = Column(Float)
    rating = Column(Float)
    pd = Column(Float)

    rating_record = relationship("RatingRecord", back_populates="lrr_rating")  # 1:1 with RatingRecord
    obligor_profile = relationship("ObligorProfile", back_populates="lrr_rating")

class OrrRating(Base):
    __tablename__ = "orr_rating"

    orr_rating_id = Column(Integer, primary_key=True, index=True)
    rating_record_id = Column(Integer, ForeignKey("rating_record.rating_record_id"))  # Removed unique=True for N:1
    facility_profile_id = Column(Integer, ForeignKey("facility_profile.facility_profile_id"))  # Removed unique=True for N:1
    data = Column(Float)
    json_inputs = Column(JSON)
    rating = Column(Float)
    lgd = Column(Float)

    rating_record = relationship("RatingRecord", back_populates="orr_ratings")  # N:1 with RatingRecord
    facility_profile = relationship("FacilityProfile", back_populates="orr_ratings")  # N:1 with FacilityProfile

# Example of how to create the engine (adjust as needed for your setup)
# DATABASE_URL = "sqlite:///./your_database.db"
# engine = create_engine(DATABASE_URL)

# Base.metadata.create_all(bind=engine) # To create tables

# For Pydantic models and FastAPI, you would typically define them in separate files
# and import these SQLAlchemy models. 