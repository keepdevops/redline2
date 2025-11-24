// REDLINE Web GUI Main JavaScript

// Global variables
let currentData = null;
let currentFilters = {};
let isLoading = false;

// License key management (persistent across all pages)
const LICENSE_KEY_STORAGE = 'redline_license_key';

// Get stored license key
function getStoredLicenseKey() {
    // Use global getLicenseKey if available (from base.html)
    if (typeof window.getLicenseKey === 'function') {
        return window.getLicenseKey();
    }
    // Fallback to direct localStorage access
    return localStorage.getItem(LICENSE_KEY_STORAGE) || window.REDLINE_LICENSE_KEY;
}

// Save license key to localStorage
function saveLicenseKey(licenseKey) {
    if (licenseKey && licenseKey.trim()) {
        localStorage.setItem(LICENSE_KEY_STORAGE, licenseKey.trim());
        // Dispatch custom event so other scripts can listen
        window.dispatchEvent(new CustomEvent('licenseKeyUpdated', { detail: { licenseKey: licenseKey.trim() } }));
    }
}

// Remove license key (logout)
function removeLicenseKey() {
    localStorage.removeItem(LICENSE_KEY_STORAGE);
    window.dispatchEvent(new CustomEvent('licenseKeyUpdated', { detail: { licenseKey: null } }));
}

// Utility functions
const utils = {
    // Format file size
    formatFileSize: function(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },

    // Format date
    formatDate: function(timestamp) {
        return new Date(timestamp * 1000).toLocaleDateString();
    },

    // Format number with commas
    formatNumber: function(num) {
        return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    },

    // Debounce function
    debounce: function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    // Validate email
    validateEmail: function(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    },

    // Validate ticker symbol
    validateTicker: function(ticker) {
        const re = /^[A-Z]{1,5}$/;
        return re.test(ticker);
    }
};

// API helper functions
const api = {
    // Generic API call
    call: function(url, options = {}) {
        const defaultOptions = {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        };

        // Auto-add license key to headers if available
        const licenseKey = getStoredLicenseKey();
        if (licenseKey) {
            defaultOptions.headers['X-License-Key'] = licenseKey;
        }

        const finalOptions = { ...defaultOptions, ...options };
        
        // Ensure license key header is set (don't override if explicitly provided)
        if (licenseKey && !finalOptions.headers['X-License-Key']) {
            finalOptions.headers['X-License-Key'] = licenseKey;
        }
        
        return fetch(url, finalOptions)
            .then(response => {
                if (!response.ok) {
                    // Safari-compatible error handling - use Promise chains instead of async/await
                    // Read response body once and parse it
                    return response.text().then(function(text) {
                        // Try to parse as JSON first
                        let errorMessage = null;
                        let errorData = null;
                        let jsonParsed = false;
                        
                        if (text && text.trim().length > 0 && !text.trim().startsWith('<')) {
                            // Not HTML, try to parse as JSON
                            if (text.trim().startsWith('{') || text.trim().startsWith('[')) {
                                try {
                                    errorData = JSON.parse(text);
                                    jsonParsed = true;
                                    if (errorData && typeof errorData === 'object') {
                                        if (errorData.error) {
                                            errorMessage = errorData.error;
                                        } else if (errorData.message) {
                                            errorMessage = errorData.message;
                                        } else {
                                            // Try to find any string value in the error object
                                            for (var key in errorData) {
                                                if (errorData.hasOwnProperty(key) && typeof errorData[key] === 'string' && errorData[key].length > 0) {
                                                    errorMessage = errorData[key];
                                                    break;
                                                }
                                            }
                                        }
                                    }
                                } catch (parseError) {
                                    // Not valid JSON, use text as error message
                                    errorMessage = text.substring(0, 200);
                                }
                            } else {
                                // Plain text error
                                errorMessage = text.substring(0, 200);
                            }
                        }
                        
                        // If we still don't have an error message, use fallback
                        if (!errorMessage) {
                            // Use status text or fallback message
                            if (response.statusText) {
                                errorMessage = response.statusText + ' (' + response.status + ')';
                            } else {
                                // Create user-friendly messages for common status codes
                                var statusMessages = {
                                    400: 'Bad request - please check your input',
                                    401: 'Unauthorized - please check your credentials',
                                    403: 'Access forbidden - insufficient permissions',
                                    404: 'Resource not found',
                                    429: 'Too many requests - please wait before trying again',
                                    500: 'Server error - please try again later',
                                    502: 'Bad gateway - service temporarily unavailable',
                                    503: 'Service unavailable - please try again later'
                                };
                                errorMessage = statusMessages[response.status] || 'HTTP error (' + response.status + ')';
                            }
                        }
                        
                        // Create error object with status code and message
                        var error = new Error(errorMessage);
                        error.status = response.status;
                        error.statusText = response.statusText;
                        
                        // Add Retry-After header if present (for 429 errors)
                        var retryAfter = response.headers.get('Retry-After');
                        if (retryAfter) {
                            error.retryAfter = retryAfter;
                        }
                        
                        // Try to extract additional fields from JSON response if available
                        if (jsonParsed && errorData && typeof errorData === 'object') {
                            // Copy useful fields from error response
                            if (errorData.retry_after !== undefined) {
                                error.retryAfter = errorData.retry_after;
                            }
                            if (errorData.ticker) {
                                error.ticker = errorData.ticker;
                            }
                            if (errorData.source) {
                                error.source = errorData.source;
                            }
                            if (errorData.suggestion) {
                                error.suggestion = errorData.suggestion;
                            }
                        }
                        
                        throw error;
                    });
                }
                return response.json();
            })
            .catch(error => {
                console.error('API call failed:', error);
                throw error;
            });
    },

    // GET request
    get: function(url) {
        return this.call(url);
    },

    // POST request
    post: function(url, data) {
        return this.call(url, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },

    // PUT request
    put: function(url, data) {
        return this.call(url, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    },

    // DELETE request
    delete: function(url) {
        return this.call(url, {
            method: 'DELETE'
        });
    }
};

// UI helper functions
const ui = {
    // Show loading overlay
    showLoading: function(text = 'Processing...') {
        $('.loading-text').text(text);
        $('#loading-overlay').show();
        isLoading = true;
    },

    // Hide loading overlay
    hideLoading: function() {
        $('#loading-overlay').hide();
        isLoading = false;
    },

    // Show toast notification
    showToast: function(message, type = 'info') {
        const toast = $('#toast');
        const icon = type === 'success' ? 'fas fa-check-circle text-success' : 
                    type === 'error' ? 'fas fa-exclamation-circle text-danger' : 
                    type === 'warning' ? 'fas fa-exclamation-triangle text-warning' :
                    'fas fa-info-circle text-primary';
        
        toast.find('.toast-header i').attr('class', icon);
        toast.find('.toast-body').text(message);
        
        const bsToast = new bootstrap.Toast(toast[0]);
        bsToast.show();
    },

    // Show modal
    showModal: function(title, content, size = '') {
        const modalHtml = `
            <div class="modal fade" id="dynamicModal" tabindex="-1">
                <div class="modal-dialog ${size}">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">${title}</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            ${content}
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        $('#dynamicModal').remove();
        $('body').append(modalHtml);
        $('#dynamicModal').modal('show');
    },

    // Confirm dialog
    confirm: function(message, callback) {
        const confirmHtml = `
            <div class="modal fade" id="confirmModal" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Confirm</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            ${message}
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                            <button type="button" class="btn btn-primary" id="confirmBtn">Confirm</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        $('#confirmModal').remove();
        $('body').append(confirmHtml);
        $('#confirmModal').modal('show');
        
        $('#confirmBtn').on('click', function() {
            $('#confirmModal').modal('hide');
            if (callback) callback();
        });
    },

    // Create data table
    createDataTable: function(container, data, columns, options = {}) {
        const tableId = 'dataTable_' + Math.random().toString(36).substr(2, 9);
        const defaultOptions = {
            pageLength: 25,
            searching: true,
            ordering: true,
            responsive: true,
            scrollX: true
        };
        
        const finalOptions = { ...defaultOptions, ...options };
        
        const tableHtml = `
            <table id="${tableId}" class="table table-striped table-hover">
                <thead>
                    <tr>
                        ${columns.map(col => `<th>${col.title || col.data}</th>`).join('')}
                    </tr>
                </thead>
                <tbody>
                    ${data.map(row => `
                        <tr>
                            ${columns.map(col => `<td>${row[col.data] || ''}</td>`).join('')}
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
        
        $(container).html(tableHtml);
        
        // Initialize DataTable if available
        if (typeof $.fn.DataTable !== 'undefined') {
            $(`#${tableId}`).DataTable(finalOptions);
        }
        
        return tableId;
    },

    // Update progress bar
    updateProgress: function(percent, text = '') {
        const progressBar = $('.progress-bar');
        progressBar.css('width', percent + '%');
        progressBar.attr('aria-valuenow', percent);
        
        if (text) {
            progressBar.text(text);
        }
    },

    // Clear form
    clearForm: function(formSelector) {
        $(formSelector)[0].reset();
        $(formSelector).find('.is-invalid').removeClass('is-invalid');
        $(formSelector).find('.invalid-feedback').remove();
    },

    // Validate form
    validateForm: function(formSelector) {
        let isValid = true;
        const form = $(formSelector);
        
        form.find('input[required], select[required], textarea[required]').each(function() {
            const field = $(this);
            const value = field.val().trim();
            
            if (!value) {
                field.addClass('is-invalid');
                if (!field.siblings('.invalid-feedback').length) {
                    field.after('<div class="invalid-feedback">This field is required.</div>');
                }
                isValid = false;
            } else {
                field.removeClass('is-invalid');
                field.siblings('.invalid-feedback').remove();
            }
        });
        
        return isValid;
    }
};

// Data management functions
const dataManager = {
    // Load data from API
    loadData: function(filename) {
        ui.showLoading('Loading data...');
        
        return api.post('/data/load', { filename: filename })
            .then(response => {
                currentData = response;
                ui.hideLoading();
                ui.showToast('Data loaded successfully', 'success');
                return response;
            })
            .catch(error => {
                ui.hideLoading();
                ui.showToast('Error loading data: ' + error.message, 'error');
                throw error;
            });
    },

    // Apply filters to data
    applyFilters: function(filename, filters) {
        ui.showLoading('Applying filters...');
        
        return api.post('/data/filter', {
            filename: filename,
            filters: filters
        })
            .then(response => {
                currentFilters = filters;
                ui.hideLoading();
                ui.showToast('Filters applied successfully', 'success');
                return response;
            })
            .catch(error => {
                ui.hideLoading();
                ui.showToast('Error applying filters: ' + error.message, 'error');
                throw error;
            });
    },

    // Export data
    exportData: function(filename, format, exportFilename, filters = {}) {
        ui.showLoading('Exporting data...');
        
        return api.post('/data/export', {
            filename: filename,
            format: format,
            export_filename: exportFilename,
            filters: filters
        })
            .then(response => {
                ui.hideLoading();
                ui.showToast('Data exported successfully', 'success');
                return response;
            })
            .catch(error => {
                ui.hideLoading();
                ui.showToast('Error exporting data: ' + error.message, 'error');
                throw error;
            });
    }
};

// File management functions
const fileManager = {
    // Upload file
    uploadFile: function(file, onProgress = null) {
        const formData = new FormData();
        formData.append('file', file);
        
        // Get license key and add to form data
        const licenseKey = getStoredLicenseKey();
        if (licenseKey) {
            formData.append('license_key', licenseKey);
        }
        
        const headers = {};
        if (licenseKey) {
            headers['X-License-Key'] = licenseKey;
        }
        
        return fetch('/api/upload', {
            method: 'POST',
            headers: headers,
            body: formData
        })
        .then(async response => {
            if (!response.ok) {
                // Use same error handling as main API call
                let errorMessage = `HTTP error! status: ${response.status}`;
                try {
                    const errorData = await response.json();
                    if (errorData && typeof errorData === 'object') {
                        if (errorData.error) {
                            errorMessage = errorData.error;
                        } else if (errorData.message) {
                            errorMessage = errorData.message;
                        }
                    } else if (typeof errorData === 'string') {
                        errorMessage = errorData;
                    }
                } catch (e) {
                    // JSON parsing failed, use status text
                    if (response.statusText) {
                        errorMessage = `${response.statusText} (${response.status})`;
                    }
                }
                const error = new Error(errorMessage);
                error.status = response.status;
                throw error;
            }
            return response.json();
        });
    },

    // List files
    listFiles: function() {
        return api.get('/api/files');
    },

    // Delete file
    deleteFile: function(filename) {
        return api.delete(`/api/files/${filename}`);
    }
};

// Chart helper functions
const chartHelper = {
    // Create line chart
    createLineChart: function(canvasId, data, options = {}) {
        const ctx = document.getElementById(canvasId).getContext('2d');
        const defaultOptions = {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: false
                }
            }
        };
        
        const finalOptions = { ...defaultOptions, ...options };
        
        return new Chart(ctx, {
            type: 'line',
            data: data,
            options: finalOptions
        });
    },

    // Create bar chart
    createBarChart: function(canvasId, data, options = {}) {
        const ctx = document.getElementById(canvasId).getContext('2d');
        const defaultOptions = {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        };
        
        const finalOptions = { ...defaultOptions, ...options };
        
        return new Chart(ctx, {
            type: 'bar',
            data: data,
            options: finalOptions
        });
    },

    // Create pie chart
    createPieChart: function(canvasId, data, options = {}) {
        const ctx = document.getElementById(canvasId).getContext('2d');
        const defaultOptions = {
            responsive: true,
            maintainAspectRatio: false
        };
        
        const finalOptions = { ...defaultOptions, ...options };
        
        return new Chart(ctx, {
            type: 'pie',
            data: data,
            options: finalOptions
        });
    }
};

// Theme System Functions
const themeSystem = {
    // Initialize theme system
    init: function() {
        // Load saved theme from localStorage
        const savedTheme = localStorage.getItem('redline-theme') || 'theme-default';
        this.applyTheme(savedTheme);
        
        // Handle theme selection
        $('.theme-option').on('click', function(e) {
            e.preventDefault();
            const theme = $(this).data('theme');
            themeSystem.applyTheme(theme);
            localStorage.setItem('redline-theme', theme);
            
            // Update active state
            $('.theme-option').removeClass('active');
            $(this).addClass('active');
            
            // Close dropdown
            $('#themeDropdown').dropdown('hide');
        });
        
        // Set active theme in dropdown
        $('.theme-option').each(function() {
            if ($(this).data('theme') === savedTheme) {
                $(this).addClass('active');
            }
        });
    },

    // Apply theme to body
    applyTheme: function(theme) {
        // Remove all theme classes
        $('body').removeClass('theme-default theme-high-contrast theme-ocean theme-forest theme-sunset theme-monochrome theme-dark theme-grayscale');
        
        // Apply new theme
        $('body').addClass(theme);
        
        // Update theme button text
        const themeNames = {
            'theme-default': 'Default',
            'theme-high-contrast': 'High Contrast',
            'theme-ocean': 'Ocean',
            'theme-forest': 'Forest',
            'theme-sunset': 'Sunset',
            'theme-monochrome': 'Monochrome',
            'theme-dark': 'Dark',
            'theme-grayscale': 'Grayscale'
        };
        
        $('#themeDropdown').html('<i class="fas fa-palette me-1"></i>' + themeNames[theme]);
        
        // Trigger theme change event
        $(document).trigger('themeChanged', [theme]);
        
        // Force widget color updates
        this.updateWidgetColors(theme);
    },
    
    // Update widget colors when theme changes
    updateWidgetColors: function(theme) {
        // Force re-render of charts and other dynamic widgets
        if (typeof chartHelper !== 'undefined' && chartHelper.updateTheme) {
            chartHelper.updateTheme(theme);
        }
        
        // Update any custom widgets
        $('.custom-widget').each(function() {
            $(this).css({
                'background-color': 'var(--light-color)',
                'color': 'var(--text-primary)'
            });
        });
        
        // Force CSS variable updates
        const root = document.documentElement;
        const computedStyle = getComputedStyle(root);
        
        // Trigger a reflow to ensure CSS variables are updated
        root.style.display = 'none';
        root.offsetHeight; // Trigger reflow
        root.style.display = '';
    },

    // Get current theme
    getCurrentTheme: function() {
        return localStorage.getItem('redline-theme') || 'theme-default';
    },

    // Set theme
    setTheme: function(theme) {
        localStorage.setItem('redline-theme', theme);
        this.applyTheme(theme);
    }
};

// Event handlers
$(document).ready(function() {
    // Listen for theme changes and update widgets
    $(document).on('themeChanged', function(event, theme) {
        // Update all widgets with theme-specific colors
        setTimeout(function() {
            // Force update of all dynamic content
            $('.table, .card, .form-control, .btn').each(function() {
                $(this).css('color', 'var(--text-primary)');
            });
            
            // Update data tables if they exist
            if (typeof dataTableHelper !== 'undefined' && dataTableHelper.updateTheme) {
                dataTableHelper.updateTheme(theme);
            }
            
            // Update charts if they exist
            if (typeof chartHelper !== 'undefined' && chartHelper.updateTheme) {
                chartHelper.updateTheme(theme);
            }
        }, 100);
    });
    
    // Initialize tooltips
    $('[data-bs-toggle="tooltip"]').tooltip();
    
    // Initialize popovers
    $('[data-bs-toggle="popover"]').popover();
    
    // Initialize theme system
    themeSystem.init();
    
    // Handle file upload drag and drop
    $('.file-upload-area').on('dragover', function(e) {
        e.preventDefault();
        $(this).addClass('dragover');
    });
    
    $('.file-upload-area').on('dragleave', function(e) {
        e.preventDefault();
        $(this).removeClass('dragover');
    });
    
    $('.file-upload-area').on('drop', function(e) {
        e.preventDefault();
        $(this).removeClass('dragover');
        
        const files = e.originalEvent.dataTransfer.files;
        if (files.length > 0) {
            handleFileUpload(files[0]);
        }
    });
    
    // Handle file input change
    $('input[type="file"]').on('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            handleFileUpload(file);
        }
    });
    
    // Handle form submissions
    $('form').on('submit', function(e) {
        e.preventDefault();
        
        if (ui.validateForm(this)) {
            const formData = new FormData(this);
            const action = $(this).attr('action');
            const method = $(this).attr('method') || 'POST';
            
            if (action) {
                submitForm(action, method, formData);
            }
        }
    });
    
    // Handle modal events
    $('.modal').on('hidden.bs.modal', function() {
        $(this).remove();
    });
    
    // Auto-refresh data every 5 minutes
    setInterval(function() {
        if (currentData) {
            refreshCurrentData();
        }
    }, 300000); // 5 minutes
});

// Global event handlers
function handleFileUpload(file) {
    if (!file) return;
    
    ui.showLoading('Uploading file...');
    
    fileManager.uploadFile(file)
        .then(response => {
            ui.hideLoading();
            ui.showToast('File uploaded successfully', 'success');
            
            // Refresh file list if on appropriate page
            if (typeof refreshFileList === 'function') {
                refreshFileList();
            }
        })
        .catch(error => {
            ui.hideLoading();
            ui.showToast('Error uploading file: ' + error.message, 'error');
        });
}

function submitForm(action, method, formData) {
    ui.showLoading('Submitting form...');
    
    const options = {
        method: method,
        body: formData
    };
    
    fetch(action, options)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            ui.hideLoading();
            ui.showToast('Form submitted successfully', 'success');
            
            // Handle success response
            if (data.redirect) {
                window.location.href = data.redirect;
            } else if (data.reload) {
                location.reload();
            }
        })
        .catch(error => {
            ui.hideLoading();
            ui.showToast('Error submitting form: ' + error.message, 'error');
        });
}

function refreshCurrentData() {
    if (!currentData || !currentData.filename) return;
    
    dataManager.loadData(currentData.filename)
        .then(response => {
            // Update current data
            currentData = response;
            
            // Refresh display if function exists
            if (typeof refreshDataDisplay === 'function') {
                refreshDataDisplay(response);
            }
        })
        .catch(error => {
            console.error('Error refreshing data:', error);
        });
}

// Export global functions
window.REDLINE = {
    utils: utils,
    api: api,
    ui: ui,
    dataManager: dataManager,
    fileManager: fileManager,
    chartHelper: chartHelper,
    themeSystem: themeSystem,
    showLoading: ui.showLoading,
    hideLoading: ui.hideLoading,
    showToast: ui.showToast,
    showModal: ui.showModal,
    confirm: ui.confirm
};
