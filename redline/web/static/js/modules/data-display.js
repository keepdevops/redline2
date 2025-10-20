/**
 * Data Display Module
 * Handles displaying data in tables
 */
class DataDisplay {
    constructor(containerId) {
        this.containerId = containerId;
        this.container = document.getElementById(containerId);
        this.maxRows = 100; // Limit rows for performance
    }

    /**
     * Display data in a table
     */
    displayData(data, options = {}) {
        if (!this.container) {
            console.error('DataDisplay: Container not found:', this.containerId);
            return;
        }

        if (!data || !Array.isArray(data) || data.length === 0) {
            this.showMessage('No data to display');
            return;
        }

        console.log(`DataDisplay: Displaying ${data.length} rows of data`);

        try {
            const tableHtml = this.createTableHtml(data, options);
            this.container.innerHTML = tableHtml;
            console.log('DataDisplay: Data displayed successfully');
        } catch (error) {
            console.error('DataDisplay: Error displaying data:', error);
            this.showError('Error displaying data: ' + error.message);
        }
    }

    /**
     * Create HTML table from data
     */
    createTableHtml(data, options = {}) {
        const maxRows = options.maxRows || this.maxRows;
        const headers = Object.keys(data[0]);
        
        let html = '<div class="table-responsive">';
        html += '<table class="table table-striped table-hover">';
        
        // Header
        html += '<thead class="table-dark"><tr>';
        headers.forEach(header => {
            html += `<th>${this.escapeHtml(header)}</th>`;
        });
        html += '</tr></thead>';
        
        // Body
        html += '<tbody>';
        const rowsToShow = Math.min(data.length, maxRows);
        
        for (let i = 0; i < rowsToShow; i++) {
            html += '<tr>';
            headers.forEach(header => {
                const value = data[i][header];
                html += `<td>${this.escapeHtml(this.formatValue(value))}</td>`;
            });
            html += '</tr>';
        }
        
        html += '</tbody></table></div>';
        
        // Show row count info
        if (data.length > maxRows) {
            html += `<div class="text-center p-2"><small class="text-muted">Showing first ${maxRows} of ${data.length} rows</small></div>`;
        }
        
        return html;
    }

    /**
     * Format value for display
     */
    formatValue(value) {
        if (value === null || value === undefined) {
            return '';
        }
        
        if (typeof value === 'number') {
            return value.toLocaleString();
        }
        
        return String(value);
    }

    /**
     * Escape HTML to prevent XSS
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Show loading message
     */
    showLoading(message = 'Loading data...') {
        if (this.container) {
            this.container.innerHTML = `
                <div class="text-center p-4">
                    <i class="fas fa-spinner fa-spin me-2"></i>${message}
                </div>
            `;
        }
    }

    /**
     * Show error message
     */
    showError(message) {
        if (this.container) {
            this.container.innerHTML = `
                <div class="text-center p-4 text-danger">
                    <i class="fas fa-exclamation-triangle me-2"></i>${message}
                </div>
            `;
        }
    }

    /**
     * Show info message
     */
    showMessage(message) {
        if (this.container) {
            this.container.innerHTML = `
                <div class="text-center p-4">
                    <i class="fas fa-info-circle me-2"></i>${message}
                </div>
            `;
        }
    }

    /**
     * Clear display
     */
    clear() {
        if (this.container) {
            this.container.innerHTML = '';
        }
    }
}

// Export for use in other modules
window.DataDisplay = DataDisplay;
