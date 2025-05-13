# Credit Risk Dashboard Application - Refactored Structure

This document outlines the refactored structure of the Credit Risk Dashboard application, which now features three distinct views as required.

## Application Overview

The application has been refactored to include three main views, each accessible through the navigation tabs at the top of the application:

1. **Summary View** - A comprehensive dashboard showing both Obligor and Facility data
2. **ORR (Obligor Risk Rating) View** - Focused on Obligor profiles and their ORR ratings
3. **LRR (Loss Risk Rating) View** - Focused on Obligor profiles and their LRR ratings

## Technical Implementation

### Routing

The application now uses Vue Router to handle navigation between the three views. Routes are defined in `main_full.js`:

```javascript
const routes = [
    { path: '/', component: SummaryView },
    { path: '/orr', component: OrrView },
    { path: '/lrr', component: LrrView }
];
```

### Component Structure

Each view is implemented as a separate Vue component with its own template in `index.html`:

- Summary View: `#summary-template`
- ORR View: `#orr-template`
- LRR View: `#lrr-template`

### Shared Functionality

To avoid code duplication, common functionality has been extracted into a factory function `createBaseViewModel()` which provides:

- Data fetching for obligors and facilities
- Search functionality
- Selection handling for obligors and facilities
- Profile data loading

Each view component uses this shared foundation but presents the data differently according to its purpose.

## View-Specific Features

### Summary View
- Displays comprehensive obligor information
- Shows all facilities linked to an obligor
- Displays profiles for both obligors and facilities

### ORR View
- Focuses on Obligor Risk Rating metrics
- Emphasizes facility data and associated ORR ratings
- ORR-specific columns in the facilities table

### LRR View
- Focuses on Loss Risk Rating metrics
- Emphasizes obligor profiles and their LRR ratings
- Displays probability of default (PD) data
- LRR-specific columns in the obligor profiles table

## Running the Application

The application structure and backend remain unchanged. Follow the original run instructions:

1. Start the FastAPI server from the backend directory:
   ```
   uvicorn app.db.playgroud.full_v5.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. Access the application in your browser at:
   `http://127.0.0.1:8000/`

## Implementation Notes

- The refactoring maintains all existing functionality while organizing it into focused views
- URL-based navigation enables bookmarking specific views
- The common data model ensures consistent data handling across all views
- Each view focuses on its specific use case while maintaining a consistent UI/UX 