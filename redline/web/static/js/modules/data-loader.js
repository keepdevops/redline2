/**
 * Data Loader Module
 * Handles loading data from files
 */
class DataLoader {
    constructor(apiBaseUrl = '') {
        this.apiBaseUrl = apiBaseUrl;
        this.currentData = null;
        this.currentFilename = null;
        this.onDataLoaded = null;
        this.onError = null;
    }

    /**
     * Load data from a file
     */
    async loadData(filename) {
        try {
            console.log(`DataLoader: Loading data for file: ${filename}`);
            
            // Get license key from localStorage
            const licenseKey = localStorage.getItem('redline_license_key') || window.REDLINE_LICENSE_KEY;
            
            const headers = {
                'Content-Type': 'application/json',
            };
            
            // Add license key to headers
            if (licenseKey) {
                headers['X-License-Key'] = licenseKey;
            }
            
            const response = await fetch(`${this.apiBaseUrl}/data/load`, {
                method: 'POST',
                headers: headers,
                body: JSON.stringify({ filename: filename, license_key: licenseKey })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.data && Array.isArray(data.data)) {
                this.currentData = data.data;
                this.currentFilename = filename;
                
                console.log(`DataLoader: Loaded ${data.total_rows} rows, ${data.columns.length} columns`);
                
                if (this.onDataLoaded) {
                    this.onDataLoaded({
                        data: this.currentData,
                        filename: this.currentFilename,
                        totalRows: data.total_rows,
                        columns: data.columns,
                        fileSize: data.file_size
                    });
                }
                
                return data;
            } else {
                throw new Error('Invalid response format');
            }
            
        } catch (error) {
            console.error(`DataLoader: Error loading data for ${filename}:`, error);
            
            if (this.onError) {
                this.onError(error, filename);
            }
            
            throw error;
        }
    }

    /**
     * Get current data
     */
    getCurrentData() {
        return this.currentData;
    }

    /**
     * Get current filename
     */
    getCurrentFilename() {
        return this.currentFilename;
    }

    /**
     * Set callback for when data is loaded
     */
    setOnDataLoaded(callback) {
        this.onDataLoaded = callback;
    }

    /**
     * Set callback for errors
     */
    setOnError(callback) {
        this.onError = callback;
    }
}

// Export for use in other modules
window.DataLoader = DataLoader;
