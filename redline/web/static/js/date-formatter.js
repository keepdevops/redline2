/**
 * REDLINE Date Formatter
 * Unified date formatting function that works with both jQuery and vanilla JavaScript.
 * 
 * This function formats YYYYMMDD numeric dates (e.g., 20241118) to readable formats
 * based on user preference. It detects dates in numeric columns and applies formatting.
 * 
 * @param {any} value - The value to format (can be number, string, or date)
 * @param {string} header - Optional column header name (used for date detection)
 * @returns {string} - Formatted date string or original value if not a date
 */
function formatDateValue(value, header) {
    if (value === null || value === undefined || value === '') {
        return '';
    }
    
    // Get selected date format - works with both jQuery and vanilla JS
    let dateFormat = 'auto'; // Default
    
    // Try jQuery first (if available)
    if (typeof $ !== 'undefined' && $('#dateFormatSelect').length > 0) {
        dateFormat = $('#dateFormatSelect').val() || localStorage.getItem('redline-date-format') || 'auto';
    }
    // Fallback to vanilla JS
    else {
        const dateFormatSelect = document.getElementById('dateFormatSelect');
        dateFormat = dateFormatSelect ? dateFormatSelect.value : (localStorage.getItem('redline-date-format') || 'auto');
    }
    
    // If format is 'raw', return original value
    if (dateFormat === 'raw') {
        return value;
    }
    
    // Convert to string and remove any commas (thousands separators)
    const strValue = String(value).replace(/,/g, '');
    
    // Check if it's a numeric value that could be YYYYMMDD format
    // YYYYMMDD format: 8 digits, between 19000101 and 21001231
    let year = null, month = null, day = null;
    let isValidDate = false;
    
    if (/^\d{8}$/.test(strValue)) {
        const numValue = parseInt(strValue, 10);
        if (numValue >= 19000101 && numValue <= 21001231) {
            // Extract year, month, day
            year = Math.floor(numValue / 10000);
            month = Math.floor((numValue % 10000) / 100);
            day = numValue % 100;
            
            // Validate month and day
            if (month >= 1 && month <= 12 && day >= 1 && day <= 31) {
                // Check if the date is valid (e.g., not Feb 30)
                const dateObj = new Date(year, month - 1, day);
                if (dateObj.getFullYear() === year && dateObj.getMonth() === month - 1 && dateObj.getDate() === day) {
                    isValidDate = true;
                }
            }
        }
    }
    
    // Also check for column names that suggest dates
    if (!isValidDate) {
        const headerLower = String(header || '').toLowerCase();
        if (headerLower.includes('date') || headerLower.includes('time') || headerLower.includes('timestamp')) {
            // Try to parse as YYYYMMDD
            if (/^\d{8}$/.test(strValue)) {
                const numValue = parseInt(strValue, 10);
                if (numValue >= 19000101 && numValue <= 21001231) {
                    year = Math.floor(numValue / 10000);
                    month = Math.floor((numValue % 10000) / 100);
                    day = numValue % 100;
                    if (month >= 1 && month <= 12 && day >= 1 && day <= 31) {
                        const dateObj = new Date(year, month - 1, day);
                        if (dateObj.getFullYear() === year && dateObj.getMonth() === month - 1 && dateObj.getDate() === day) {
                            isValidDate = true;
                        }
                    }
                }
            }
        }
    }
    
    // If we have a valid date, format it according to user preference
    if (isValidDate && year && month && day) {
        const monthStr = String(month).padStart(2, '0');
        const dayStr = String(day).padStart(2, '0');
        const yearStr = String(year);
        
        switch (dateFormat) {
            case 'YYYY-MM-DD':
            case 'auto':  // Default to YYYY-MM-DD
                return `${yearStr}-${monthStr}-${dayStr}`;
            case 'MM/DD/YYYY':
                return `${monthStr}/${dayStr}/${yearStr}`;
            case 'DD/MM/YYYY':
                return `${dayStr}/${monthStr}/${yearStr}`;
            case 'YYYY/MM/DD':
                return `${yearStr}/${monthStr}/${dayStr}`;
            case 'DD-MM-YYYY':
                return `${dayStr}-${monthStr}-${yearStr}`;
            case 'MM-DD-YYYY':
                return `${monthStr}-${dayStr}-${yearStr}`;
            default:
                return `${yearStr}-${monthStr}-${dayStr}`;
        }
    }
    
    // Return original value if not a date
    return value;
}

