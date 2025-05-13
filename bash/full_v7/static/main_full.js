const { createApp, ref, watch, onMounted, computed, nextTick, reactive, provide, inject } = Vue;
const { createVuetify } = Vuetify;
const { createRouter, createWebHistory } = VueRouter;

const vuetify = createVuetify({
    theme: {
        defaultTheme: 'light'
    },
    icons: {
        defaultSet: 'mdi',
    }
});

// Create a shared state across all views
const createSharedState = () => {
    const state = reactive({
        // Table data
        processedItems: [],
        totalProcessedItems: 0,
        combinedLoading: false,
        dataLoaded: false, // Flag to track if data has been loaded

        // Selected obligor data
        selectedObligor: null,
        selectedObligorId: null,
        selectedObligorProfiles: [],
        selectedObligorProfilesLoading: false,
        selectedFacilityId: null,
        expandedFacilityId: null,
        expandedRows: [],
        facilityProfiles: {},
        
        // Load obligors list data
        async loadObligorData(options = {}) {
            if (state.dataLoaded && !options.forceReload) {
                return; // Skip loading if data is already loaded
            }
            
            const API_BASE_URL = 'http://127.0.0.1:8000';
            state.combinedLoading = true;
            
            try {
                const params = {
                    skip: options.skip || 0,
                    limit: options.limit || 10,
                };
                if (options.nameContains) params.name_contains = options.nameContains;
                if (options.sortBy) {
                    params.sort_by = options.sortBy.replace('data.','');
                    params.sort_desc = options.sortDesc || false;
                }

                const response = await axios.get(`${API_BASE_URL}/obligors/`, { params });
                
                if (response.data && typeof response.data.total === 'number' && Array.isArray(response.data.items)) {
                    state.processedItems = response.data.items.map(obligor => ({
                        type: 'obligor',
                        id: obligor.obligor_id, 
                        data: { 
                            ...obligor,
                            facilities: []
                        },          
                        loadingFacilities: false,
                    }));
                    state.totalProcessedItems = response.data.total;
                    state.dataLoaded = true; // Mark data as loaded
                } else {
                    console.warn('Unexpected response structure for obligors:', response.data);
                    state.processedItems = [];
                    state.totalProcessedItems = 0;
                }
            } catch (error) {
                console.error('Error fetching obligor data:', error);
                state.processedItems = [];
                state.totalProcessedItems = 0;
            } finally {
                state.combinedLoading = false;
            }
        },
        
        // API function to fetch obligor details
        async fetchObligorDetails(obligorId) {
            if (!obligorId) return;
            const API_BASE_URL = 'http://127.0.0.1:8000';
            
            state.selectedObligorProfilesLoading = true;
            try {
                // Fetch detailed obligor info
                const response = await axios.get(`${API_BASE_URL}/obligors/${obligorId}`);
                state.selectedObligor = response.data;
                state.selectedObligorId = obligorId;
                
                // Fetch profiles
                const profilesResponse = await axios.get(`${API_BASE_URL}/obligors/${obligorId}/profiles`);
                state.selectedObligorProfiles = profilesResponse.data || [];
                
                // Fetch facilities
                const facilitiesResponse = await axios.get(`${API_BASE_URL}/facilities/`, {
                    params: { obligor_id: obligorId }
                });
                if (facilitiesResponse.data && facilitiesResponse.data.items) {
                    state.selectedObligor.facilities = facilitiesResponse.data.items;
                }
            } catch (error) {
                console.error(`Error fetching details for obligor ${obligorId}:`, error);
                state.selectedObligor = null;
                state.selectedObligorProfiles = [];
            } finally {
                state.selectedObligorProfilesLoading = false;
            }
        },
        
        // API function to fetch facility profiles
        async fetchFacilityProfiles(facilityId) {
            if (!facilityId) return;
            if (state.facilityProfiles[facilityId]) return; // Already loaded
            
            const API_BASE_URL = 'http://127.0.0.1:8000';
            try {
                const response = await axios.get(`${API_BASE_URL}/facilities/${facilityId}/profiles/`);
                state.facilityProfiles[facilityId] = response.data || [];
            } catch (error) {
                state.facilityProfiles[facilityId] = [];
                console.error(`Error fetching profiles for facility ${facilityId}:`, error);
            }
        },
        
        // Clear selection
        clearSelection() {
            state.selectedObligor = null;
            state.selectedObligorId = null;
            state.selectedObligorProfiles = [];
            state.expandedFacilityId = null;
            state.expandedRows = [];
        },
        
        // Clear all data (for search)
        clearAll() {
            state.clearSelection();
            state.processedItems = [];
            state.totalProcessedItems = 0;
            state.dataLoaded = false;
        },
        
        // Handle expanding/collapsing facility rows
        async updateExpandedRows(newExpanded) {
            // Find newly expanded rows (those in newExpanded but not in state.expandedRows)
            const newlyExpanded = newExpanded.filter(id => !state.expandedRows.includes(id));
            
            // Set the expanded state
            state.expandedRows = newExpanded;
            
            // Fetch profiles for any newly expanded facilities
            if (newlyExpanded.length > 0) {
                for (const facilityId of newlyExpanded) {
                    await state.fetchFacilityProfiles(facilityId);
                }
            }
        }
    });
    
    return state;
};

// Create reusable data and methods for all views
const createBaseViewModel = (sharedState) => {
    // --- Local reactive state ---
    const combinedSearch = ref('');
    const showObligorSearchModal = ref(false);
    const expandedGroups = ref([]);

    const combinedHeaders = [
        { title: 'Obligor ID', key: 'data.obligor_id', value: 'data.obligor_id', sortable: true, align: 'start' },
        { title: 'Obligor Name', key: 'data.name', value: 'data.name', sortable: true, align: 'start' },
        { title: 'Address', key: 'data.address', value: 'data.address', sortable: false, align: 'start' },
    ];

    // --- Methods ---
    const loadCombinedData = async (options = {}) => {
        // Use the shared state loading function instead
        await sharedState.loadObligorData({
            skip: (options.page - 1) * (options.itemsPerPage || 10) || 0,
            limit: options.itemsPerPage || 10,
            nameContains: combinedSearch.value,
            sortBy: options.sortBy && options.sortBy.length > 0 ? options.sortBy[0].key : null,
            sortDesc: options.sortBy && options.sortBy.length > 0 ? options.sortBy[0].order === 'desc' : false,
            forceReload: options.forceReload || false
        });
    };

    // Add expand all facilities function
    const expandAllFacilities = () => {
        if (sharedState.selectedObligor && sharedState.selectedObligor.facilities) {
            const allFacilityIds = sharedState.selectedObligor.facilities.map(f => f.facility_id);
            sharedState.updateExpandedRows(allFacilityIds);
        }
    };

    // Add collapse all facilities function
    const collapseAllFacilities = () => {
        sharedState.updateExpandedRows([]);
    };

    const fetchFacilitiesForObligor = async (obligorItem) => {
        if (!obligorItem || !obligorItem.id) return;

        const itemInProcessed = sharedState.processedItems.find(p => p.id === obligorItem.id);
        if (!itemInProcessed) return;

        itemInProcessed.loadingFacilities = true;
        const API_BASE_URL = 'http://127.0.0.1:8000';
        try {
            const response = await axios.get(`${API_BASE_URL}/facilities/`, {
                params: { obligor_id: itemInProcessed.id }
            });

            if (response.data && Array.isArray(response.data.items)) {
                itemInProcessed.data.facilities = response.data.items;
            } else {
                itemInProcessed.data.facilities = [];
                console.warn(`Unexpected facility data structure for obligor ${itemInProcessed.id}:`, response.data);
            }
        } catch (error) {
            console.error(`Error fetching facilities for obligor ${itemInProcessed.id}:`, error);
            itemInProcessed.data.facilities = [];
        } finally {
            itemInProcessed.loadingFacilities = false;
        }
    };

    // Debounced search handler 
    const debouncedCombinedLoad = _.debounce((options) => {
        sharedState.clearAll(); // Clear all data for new search
        loadCombinedData({ ...options, page: 1, forceReload: true });
    }, 300); // Reduced debounce time for better responsiveness

    // Search change watcher
    watch(combinedSearch, () => {
        debouncedCombinedLoad({ itemsPerPage: 10 });
    });

    // Row click handler - updated to use shared state
    const handleObligorRowClick = async (obligorData, internalItem) => {
        if (!obligorData || obligorData.obligor_id === undefined) return;
        const clickedObligorId = obligorData.obligor_id;

        if (sharedState.selectedObligorId === clickedObligorId) {
            sharedState.clearSelection();
        } else {
            // Fetch obligor details through shared state
            await sharedState.fetchObligorDetails(clickedObligorId);
        }
    };

    // Legacy handler - kept for backward compatibility
    const handleFacilityRowClick = async (facility) => {
        if (!facility || !facility.facility_id) return;
        
        // Add or remove from expanded rows
        const facilityId = facility.facility_id;
        if (sharedState.expandedRows.includes(facilityId)) {
            sharedState.expandedRows = sharedState.expandedRows.filter(id => id !== facilityId);
        } else {
            sharedState.expandedRows.push(facilityId);
            await sharedState.fetchFacilityProfiles(facilityId);
        }
    };

    // Initial data load on component mount - only if not already loaded
    onMounted(() => {
        if (!sharedState.dataLoaded) {
            loadCombinedData({ page: 1, itemsPerPage: 10 });
        }
    });

    return {
        // Local state
        combinedSearch,
        showObligorSearchModal,
        combinedHeaders,
        expandedGroups,

        // Methods
        loadCombinedData,
        fetchFacilitiesForObligor,
        debouncedCombinedLoad,
        handleObligorRowClick,
        handleFacilityRowClick,
        expandAllFacilities,
        collapseAllFacilities,
        
        // Access to shared state
        processedItems: computed(() => sharedState.processedItems),
        combinedLoading: computed(() => sharedState.combinedLoading),
        totalProcessedItems: computed(() => sharedState.totalProcessedItems),
        selectedObligor: computed(() => sharedState.selectedObligor),
        selectedObligorId: computed(() => sharedState.selectedObligorId),
        selectedObligorProfiles: computed(() => sharedState.selectedObligorProfiles),
        selectedObligorProfilesLoading: computed(() => sharedState.selectedObligorProfilesLoading),
        selectedFacilityId: computed(() => sharedState.selectedFacilityId),
        expandedFacilityId: computed(() => sharedState.expandedFacilityId),
        expandedRows: computed(() => sharedState.expandedRows),
        facilityProfiles: computed(() => sharedState.facilityProfiles),
        updatedExpandedRows: sharedState.updateExpandedRows
    };
};

// Create shared state that will be used across all views
const sharedAppState = createSharedState();

// Define components for each view
const SummaryView = {
    template: '#summary-template',
    setup() {
        return createBaseViewModel(sharedAppState);
    }
};

const OrrView = {
    template: '#orr-template',
    setup() {
        return createBaseViewModel(sharedAppState);
    }
};

const LrrView = {
    template: '#lrr-template',
    setup() {
        return createBaseViewModel(sharedAppState);
    }
};

// Define routes with navigation guards to prevent unnecessary data loading
const routes = [
    { 
        path: '/', 
        component: SummaryView
    },
    { 
        path: '/orr', 
        component: OrrView
    },
    { 
        path: '/lrr', 
        component: LrrView
    }
];

// Create router 
const router = createRouter({
    history: createWebHistory(),
    routes
});

// Global navigation guard to preload data if needed
router.beforeEach(async (to, from, next) => {
    // If we're navigating between our main views and data is already loaded, just proceed
    if (from.path && ['/', '/orr', '/lrr'].includes(from.path) && sharedAppState.dataLoaded) {
        next();
        return;
    }
    
    // Otherwise, if data isn't loaded yet, load it before navigating
    if (!sharedAppState.dataLoaded) {
        await sharedAppState.loadObligorData();
    }
    
    next();
});

// Create Vue app
const app = createApp({
    setup() {
        const currentTab = ref('summary');
        
        // Watch route changes to update the selected tab
        watch(
            () => router.currentRoute.value.path,
            (path) => {
                if (path === '/') currentTab.value = 'summary';
                else if (path === '/orr') currentTab.value = 'orr';
                else if (path === '/lrr') currentTab.value = 'lrr';
            }
        );
        
        return {
            currentTab
        };
    }
});

// Register plugins
app.use(vuetify);
app.use(router);

// Mount the app
app.mount('#app'); 