/**
 * Data Tab Controller
 * Orchestrates all modules for the data tab functionality
 */
class DataTabController {
    constructor(options = {}) {
        this.apiBaseUrl = options.apiBaseUrl || '';
        this.fileSelectId = options.fileSelectId || 'fileSelect';
        this.loadButtonId = options.loadButtonId || 'loadFileBtn';
        this.refreshButtonId = options.refreshButtonId || 'refreshFilesBtn';
        this.dataContainerId = options.dataContainerId || 'dataTableContainer';
        
        // Initialize modules
        this.fileLoader = new FileLoader(this.apiBaseUrl);
        this.dataLoader = new DataLoader(this.apiBaseUrl);
        this.fileSelector = new FileSelector(this.fileSelectId);
        this.dataDisplay = new DataDisplay(this.dataContainerId);
        this.loadButtonHandler = new ButtonHandler(this.loadButtonId);
        this.refreshButtonHandler = new ButtonHandler(this.refreshButtonId);
        
        // State
        this.currentFile = null;
        this.currentData = null;
        
        this.init();
    }

    /**
     * Initialize the controller
     */
    init() {
        console.log('DataTabController: Initializing...');
        
        try {
            this.setupModules();
            this.setupEventHandlers();
            this.loadInitialData();
            
            console.log('DataTabController: Initialized successfully');
        } catch (error) {
            console.error('DataTabController: Initialization error:', error);
        }
    }

    /**
     * Setup module callbacks
     */
    setupModules() {
        // File loader callbacks
        this.fileLoader.setOnFilesLoaded((files) => {
            console.log(`DataTabController: Files loaded: ${files.length}`);
            this.fileSelector.populateFiles(files);
        });

        this.fileLoader.setOnError((error) => {
            console.error('DataTabController: File loading error:', error);
            this.fileSelector.showError('Error loading files');
        });

        // Data loader callbacks
        this.dataLoader.setOnDataLoaded((dataInfo) => {
            console.log(`DataTabController: Data loaded: ${dataInfo.totalRows} rows`);
            this.currentData = dataInfo.data;
            this.currentFile = dataInfo.filename;
            this.dataDisplay.displayData(dataInfo.data);
        });

        this.dataLoader.setOnError((error, filename) => {
            console.error(`DataTabController: Data loading error for ${filename}:`, error);
            this.dataDisplay.showError(`Error loading data: ${error.message}`);
        });

        // File selector callbacks
        this.fileSelector.setOnSelectionChanged((filename) => {
            console.log(`DataTabController: File selection changed: ${filename}`);
            this.currentFile = filename;
            this.loadButtonHandler.setText(filename ? 'Load File' : 'Select a file first');
            
            if (filename) {
                this.loadButtonHandler.enable();
            } else {
                this.loadButtonHandler.disable();
            }
        });

        // Button handlers
        this.loadButtonHandler.setOnClick(() => {
            if (this.currentFile) {
                this.loadFileData(this.currentFile);
            }
        });

        this.refreshButtonHandler.setOnClick(() => {
            this.refreshFiles();
        });
    }

    /**
     * Setup event handlers
     */
    setupEventHandlers() {
        // Setup button click handlers
        this.loadButtonHandler.setupClickHandler();
        this.refreshButtonHandler.setupClickHandler();
        
        // Setup file selector change handler
        this.fileSelector.setupEventHandlers();
    }

    /**
     * Load initial data
     */
    async loadInitialData() {
        console.log('DataTabController: Loading initial data...');
        
        try {
            await this.refreshFiles();
        } catch (error) {
            console.error('DataTabController: Error loading initial data:', error);
        }
    }

    /**
     * Refresh files list
     */
    async refreshFiles() {
        console.log('DataTabController: Refreshing files...');
        
        try {
            this.dataDisplay.showLoading('Loading files...');
            await this.fileLoader.loadFiles();
        } catch (error) {
            console.error('DataTabController: Error refreshing files:', error);
            this.dataDisplay.showError('Error loading files');
        }
    }

    /**
     * Load file data
     */
    async loadFileData(filename) {
        console.log(`DataTabController: Loading data for file: ${filename}`);
        
        try {
            this.loadButtonHandler.setLoading(true, 'Loading data...');
            this.dataDisplay.showLoading('Loading data...');
            
            await this.dataLoader.loadData(filename);
            
            console.log('DataTabController: File data loaded successfully');
        } catch (error) {
            console.error(`DataTabController: Error loading file data for ${filename}:`, error);
            this.dataDisplay.showError(`Error loading data: ${error.message}`);
        } finally {
            this.loadButtonHandler.setLoading(false);
        }
    }

    /**
     * Get current state
     */
    getState() {
        return {
            currentFile: this.currentFile,
            currentData: this.currentData,
            filesLoaded: this.fileLoader.getFiles().length,
            loadButtonEnabled: this.loadButtonHandler.isButtonEnabled()
        };
    }

    /**
     * Reset state
     */
    reset() {
        this.currentFile = null;
        this.currentData = null;
        this.fileSelector.clearSelection();
        this.loadButtonHandler.disable();
        this.dataDisplay.clear();
    }
}

// Export for use in other modules
window.DataTabController = DataTabController;
