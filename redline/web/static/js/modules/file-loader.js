/**
 * File Loader Module
 * Handles loading file lists from the API
 */
class FileLoader {
    constructor(apiBaseUrl = '') {
        this.apiBaseUrl = apiBaseUrl;
        this.files = [];
        this.onFilesLoaded = null;
        this.onError = null;
    }

    /**
     * Load files from the API
     */
    async loadFiles() {
        try {
            console.log('FileLoader: Loading files from API...');

            // Get JWT token from localStorage
            const authToken = localStorage.getItem('variosync_auth_token');

            const headers = {
                'Content-Type': 'application/json'
            };

            if (authToken) {
                headers['Authorization'] = `Bearer ${authToken}`;
            }

            const url = `${this.apiBaseUrl}/data/files`;

            const response = await fetch(url, {
                method: 'GET',
                headers: headers
            });

            // Handle 401 Unauthorized
            if (response.status === 401) {
                localStorage.removeItem('variosync_auth_token');
                localStorage.removeItem('variosync_user_data');
                window.location.href = '/auth/login?redirect=' + encodeURIComponent(window.location.pathname);
                throw new Error('Session expired. Please log in again.');
            }

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.files && Array.isArray(data.files)) {
                this.files = data.files;
                console.log(`FileLoader: Loaded ${this.files.length} files`);
                
                if (this.onFilesLoaded) {
                    this.onFilesLoaded(this.files);
                }
                
                return this.files;
            } else {
                throw new Error('Invalid response format');
            }
            
        } catch (error) {
            console.error('FileLoader: Error loading files:', error);
            
            if (this.onError) {
                this.onError(error);
            }
            
            throw error;
        }
    }

    /**
     * Get files array
     */
    getFiles() {
        return this.files;
    }

    /**
     * Set callback for when files are loaded
     */
    setOnFilesLoaded(callback) {
        this.onFilesLoaded = callback;
    }

    /**
     * Set callback for errors
     */
    setOnError(callback) {
        this.onError = callback;
    }
}

// Export for use in other modules
window.FileLoader = FileLoader;
