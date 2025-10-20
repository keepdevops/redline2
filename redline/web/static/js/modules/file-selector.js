/**
 * File Selector Module
 * Handles file selection dropdown
 */
class FileSelector {
    constructor(selectId) {
        this.selectId = selectId;
        this.selectElement = document.getElementById(selectId);
        this.onFileSelected = null;
        this.onSelectionChanged = null;
    }

    /**
     * Populate dropdown with files
     */
    populateFiles(files) {
        if (!this.selectElement) {
            console.error('FileSelector: Select element not found:', this.selectId);
            return;
        }

        console.log(`FileSelector: Populating dropdown with ${files.length} files`);

        // Clear existing options
        this.selectElement.innerHTML = '';

        // Add default option
        const defaultOption = document.createElement('option');
        defaultOption.value = '';
        defaultOption.textContent = 'Select a file to load...';
        this.selectElement.appendChild(defaultOption);

        // Add file options
        files.forEach(file => {
            const option = document.createElement('option');
            option.value = file.name;
            option.textContent = this.formatFileName(file);
            this.selectElement.appendChild(option);
        });

        console.log('FileSelector: Dropdown populated successfully');
    }

    /**
     * Format file name for display
     */
    formatFileName(file) {
        const size = file.size || 0;
        const sizeStr = this.formatFileSize(size);
        return `${file.name} (${sizeStr})`;
    }

    /**
     * Format file size
     */
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    /**
     * Get selected file
     */
    getSelectedFile() {
        if (!this.selectElement) return null;
        return this.selectElement.value || null;
    }

    /**
     * Set selected file
     */
    setSelectedFile(filename) {
        if (this.selectElement) {
            this.selectElement.value = filename || '';
        }
    }

    /**
     * Enable/disable the selector
     */
    setEnabled(enabled) {
        if (this.selectElement) {
            this.selectElement.disabled = !enabled;
        }
    }

    /**
     * Clear selection
     */
    clearSelection() {
        if (this.selectElement) {
            this.selectElement.value = '';
        }
    }

    /**
     * Show error state
     */
    showError(message = 'Error loading files') {
        if (this.selectElement) {
            this.selectElement.innerHTML = '';
            const option = document.createElement('option');
            option.value = '';
            option.textContent = message;
            this.selectElement.appendChild(option);
            this.selectElement.disabled = true;
        }
    }

    /**
     * Set up event handlers
     */
    setupEventHandlers() {
        if (!this.selectElement) return;

        this.selectElement.addEventListener('change', (event) => {
            const selectedFile = event.target.value;
            console.log('FileSelector: File selected:', selectedFile);

            if (this.onSelectionChanged) {
                this.onSelectionChanged(selectedFile);
            }

            if (this.onFileSelected && selectedFile) {
                this.onFileSelected(selectedFile);
            }
        });
    }

    /**
     * Set callback for file selection
     */
    setOnFileSelected(callback) {
        this.onFileSelected = callback;
    }

    /**
     * Set callback for selection change
     */
    setOnSelectionChanged(callback) {
        this.onSelectionChanged = callback;
    }
}

// Export for use in other modules
window.FileSelector = FileSelector;
