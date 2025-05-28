from sqlalchemy import create_engine, Column, DateTime, DECIMAL, Integer, String, Date, Float, Boolean, ForeignKey, JSON, MetaData, UniqueConstraint
from sqlalchemy.orm import relationship, declarative_base, joinedload
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from .database import Base


# Base = declarative_base()
# Base.metadata.schema = "cre_lrr"

class ObligorFacility(Base):
    __tablename__ = "obligor_facility"
    
    obligor_facility_id = Column(Integer, primary_key=True, index=True)
    obligor_id = Column(Integer, ForeignKey('obligor.obligor_id', ondelete="CASCADE"), index=True)
    facility_id = Column(Integer, ForeignKey('facility.facility_id', ondelete="CASCADE"), index=True)

class Obligor(Base):
    __tablename__ = "obligor"
    
    obligor_id = Column(Integer, primary_key=True, index=True)
    
    src_arng_num = Column(String(100), nullable=True)
    name = Column(String)
    created = Column(DateTime, nullable=False, server_default=func.now())
    modified = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    address = Column(String)

    profiles = relationship("ObligorProfile", back_populates="obligor", cascade="all, delete-orphan")
    facilities = relationship("Facility", secondary=ObligorFacility.__table__, back_populates="obligors", cascade="all")
    rating_records = relationship("RatingRecord", back_populates="obligor", cascade="all, delete-orphan")


class ObligorProfile(Base):
    __tablename__ = "obligor_profile"
    
    obligor_profile_id = Column(Integer, primary_key=True, index=True)
    obligor_id = Column(Integer, ForeignKey('obligor.obligor_id', ondelete="CASCADE"), nullable=True)
    as_of_date = Column(Date, nullable=True)
    credit_officer = Column(String(500), nullable=True)
    comment = Column(String(5000), nullable=True)

    insert_datetime = Column(DateTime, nullable=True, server_default=func.now())
    update_datetime = Column(DateTime, nullable=True, server_default=func.now(), onupdate=func.now())
    
    obligor = relationship("Obligor", back_populates="profiles", passive_deletes=True)
    orr_ratings = relationship("OrrRating", back_populates="obligor_profile", uselist=False, cascade="all, delete-orphan")

class Facility(Base):
    __tablename__ = "facility"
    
    facility_id = Column(Integer, primary_key=True, index=True)
    
    description = Column(String)
    name = Column(String)
    src_facility_num = Column(String(100), nullable=True)
    
    address = Column(String)
    property_type = Column(String(100), nullable=True) # consilder changing to facility type or enum to standardize
    insert_datetime = Column(DateTime, nullable=True, server_default=func.now())
    update_datetime = Column(DateTime, nullable=True, server_default=func.now(), onupdate=func.now())
    
    profiles = relationship("FacilityProfile", back_populates="facility", cascade="all, delete-orphan")
    obligors = relationship("Obligor", secondary=ObligorFacility.__table__, back_populates="facilities", cascade="all")

class FacilityProfile(Base):
    __tablename__ = "facility_profile"
    
    facility_profile_id = Column(Integer, primary_key=True, index=True)
    facility_id = Column(Integer, ForeignKey('facility.facility_id', ondelete="CASCADE"))

    as_of_date = Column(Date, nullable=True)
    rec_web_deal_number = Column(Integer, nullable=False)
    statement_date = Column(Date, nullable=True)
    stabilized = Column(String(5), nullable=True)
    statement_type = Column(String(100), nullable=True)
    snc_indicator = Column(String(5), nullable=True)
    key_bank_percentage = Column(DECIMAL(18, 5), nullable=True)
    global_commitment = Column(DECIMAL(18, 5), nullable=True)
    key_bank_commitment = Column(DECIMAL(18, 5), nullable=True)
    key_bank_outstandings = Column(DECIMAL(18, 5), nullable=True)
    global_operating_income = Column(DECIMAL(18, 5), nullable=True)
    operating_expense = Column(DECIMAL(18, 5), nullable=True)
    net_operating_income = Column(DECIMAL(18, 5), nullable=True)
    appraisal_value = Column(DECIMAL(18, 5), nullable=True)
    cap_rate = Column(DECIMAL(18, 5), nullable=True)
    ltv = Column(DECIMAL(18, 5), nullable=True)
 
    
    insert_datetime = Column(DateTime, nullable=True, server_default=func.now())
    update_datetime = Column(DateTime, nullable=True, server_default=func.now(), onupdate=func.now())
    
    facility = relationship("Facility", back_populates="profiles", passive_deletes=True)
    lrr_ratings = relationship("LrrRating", back_populates="facility_profile", cascade="all, delete-orphan")

class RatingRecord(Base):
    __tablename__ = "rating_record"
    
    rating_record_id = Column(Integer, primary_key=True, index=True)
    obligor_id = Column(Integer, ForeignKey('obligor.obligor_id', ondelete="CASCADE"))

    effective_date = Column(Date)
    submitted = Column(Boolean)
    credit_officer = Column(String(500), nullable=True)
    insert_datetime = Column(DateTime, nullable=True, server_default=func.now())
    update_datetime = Column(DateTime, nullable=True, server_default=func.now(), onupdate=func.now())
    
    obligor = relationship("Obligor", back_populates="rating_records", passive_deletes=True)
    lrr_ratings = relationship("LrrRating", back_populates="rating_record", cascade="all, delete-orphan")
    orr_rating = relationship("OrrRating", back_populates="rating_record", uselist=False, cascade="all, delete-orphan")

class LrrRating(Base):
    __tablename__ = "lrr_rating"
    __table_args__ = (
        UniqueConstraint('rating_record_id', 'facility_id', name='uq_lrr_rating_record_facility'),
    )

    lrr_rating_id = Column(Integer, primary_key=True, index=True)
    rating_record_id = Column(Integer, ForeignKey("rating_record.rating_record_id", ondelete="CASCADE"))
    facility_profile_id = Column(Integer, ForeignKey("facility_profile.facility_profile_id", ondelete="CASCADE"))
    
    facility_id = Column(Integer, ForeignKey('facility.facility_id'), nullable=False) # needed to enforce unique constraint on rating_record_id and facility_id

    json_inputs = Column(JSON)
    assigned_lrr = Column(DECIMAL(7, 3), nullable=True)
    assigned_lgd = Column(DECIMAL(7, 3), nullable=True)
    comment = Column(String(5000), nullable=True)
    
    insert_datetime = Column(DateTime, nullable=True, server_default=func.now())
    update_datetime = Column(DateTime, nullable=True, server_default=func.now(), onupdate=func.now())

    rating_record = relationship("RatingRecord", back_populates="lrr_ratings")
    facility_profile = relationship("FacilityProfile", back_populates="lrr_ratings")
    
    facility = relationship("Facility", foreign_keys=[facility_id])

class OrrRating(Base):
    __tablename__ = "orr_rating"

    orr_rating_id = Column(Integer, primary_key=True, index=True)
    rating_record_id = Column(Integer, ForeignKey("rating_record.rating_record_id", ondelete="CASCADE"), unique=True)
    obligor_profile_id = Column(Integer, ForeignKey("obligor_profile.obligor_profile_id", ondelete="CASCADE"))

    json_inputs = Column(JSON)
    assigned_orr = Column(DECIMAL(7, 3), nullable=True)
    assigned_pd = Column(DECIMAL(7, 3), nullable=True)
    comment = Column(String(5000), nullable=True)
    
    insert_datetime = Column(DateTime, nullable=True, server_default=func.now())
    update_datetime = Column(DateTime, nullable=True, server_default=func.now(), onupdate=func.now())

    rating_record = relationship("RatingRecord", back_populates="orr_rating")
    obligor_profile = relationship("ObligorProfile", back_populates="orr_ratings", passive_deletes=True)

# Example of how to create the engine (adjust as needed for your setup)

if __name__ == "__main__":
    from database import engine  
    Base.metadata.create_all(bind=engine) # To create tables

# For Pydantic models and FastAPI, you would typically define them in separate files
# and import these SQLAlchemy models. 