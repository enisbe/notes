I am working within @full_v5  full_v5/ folder app. Only working within full_v5/ folder. Do not look at any other folders other then folder full_v5/.  Its a vue app (in static folder) with fastapi on the backend. First step is to learn the app structure without making any changes. Then I will make changes to the app. 


I want to split this application into three frontend view. First view is existing view. We'll call this summary view. Second view will be the same but only with Obligor profiles. We'll call this ORR view. Third view will be LRR view. both ORR and LRR views will have same starting point (Searhc obligors)but then Obligor detail LRR will display Obligor profiles. While ORR will display Facilities and faciliy profiles. This is would be just break the existing view in three components. 

## Project Overview

This is a Vue.js frontend application with a FastAPI backend, located in the full_v5/ folder. The application manages credit risk data including Obligors, Facilities, and their associated profiles and ratings.

## Application Structure

The application will be split into three main views:

1. **Summary View** 
   - The existing comprehensive view showing both Obligor and Facility data
   - Displays full relationship between Obligors and their Facilities
   - Serves as a complete overview dashboard

2. **ORR (Obligor Risk Rating) View**
   - Focuses on Obligor profiles and ratings
   - Starts with Obligor search functionality
   - After selecting an Obligor, displays:
     - Obligor details
     - Associated Facilities and their profiles
     - ORR-specific metrics and data

3. **LRR (Loss Risk Rating) View** 
   - Focuses on Loss Risk assessment
   - Starts with Obligor search functionality
   - After selecting an Obligor, displays:
     - Obligor details
     - Obligor profiles
     - LRR-specific metrics and data

## Implementation Plan

1. Refactor existing view into reusable components
2. Create new route structure for three views
3. Implement view-specific data filtering
4. Maintain consistent search and selection behavior across views
5. Ensure proper data relationships are maintained in each view

The goal is to break down the existing comprehensive view into three focused, purpose-specific views while maintaining consistent functionality and user experience.



