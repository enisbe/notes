


# Rating Record Implementation Plan

## Database Schema
The rating system uses the following related tables:

RATING_RECORD - Main rating record
- rating_record_id (int, primary key)  
- effective_date (date)
- submitted (boolean)

LRR_RATING - Loss Risk Rating, one per rating record
- lrr_rating_id (int, primary key)
- rating_record_id (int, foreign key)
- obligor_profile_id (int, foreign key) 
- data (float)
- rating (float)
- pd (float)

ORR_RATING - Obligor Risk Rating, many per rating record
- orr_rating_id (int, primary key)
- rating_record_id (int, foreign key)
- facility_profile_id (int, foreign key)
- data (float) 
- json_inputs (json)
- rating (float)
- lgd (float)

## Implementation Tasks

1. Add Rating Record Components
   - Create rating record placeholder components for all three views
   - Only enable adding/editing in LRR and ORR views
   - Summary view will display aggregated rating data

2. Add Rating Creation UI
   - Add "+" button next to rating records to trigger creation modal
   - Modal should allow creating new rating record entry
   - For LRR view: Create LRR rating entry
   - For ORR view: Create ORR rating entry

3. Implement Facility Selection
   - Add facility selection dropdown in rating modal
   - Populate with available facilities and their profiles
   - Link selected facility profile ID to ORR rating

4. Set Default Values
   For new ORR ratings:
   - data: 100000
   - json_inputs: {"a": 1, "b": 2}
   - rating: 1
   - lgd: 1

5. Handle Data Flow
   - Ensure proper relationship between rating record and ratings
   - Validate required fields before submission
   - Update UI to reflect new rating entries
