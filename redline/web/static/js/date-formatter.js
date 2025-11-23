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
/**
 * Format time value (HHMMSS format to HH:MM:SS)
 * Handles formats like: 90500, 90,500, 090500, etc.
 */
function formatTimeValue(value, header) {
    if (value === null || value === undefined || value === '') {
        return '';
    }
    
    // Check if header indicates this is a time column
    const isTimeColumn = header && (
        header.toLowerCase().includes('time') ||
        header === '<TIME>' ||
        header === 'TIME'
    );
    
    if (!isTimeColumn) {
        return value;
    }
    
    // Debug logging (can be removed later)
    if (typeof console !== 'undefined' && console.log) {
        console.log('formatTimeValue called:', { value: value, header: header, type: typeof value });
    }
    
    // Convert to string, remove commas, dots, spaces, and any non-numeric characters
    let timeStr = String(value).trim();
    // Remove all non-numeric characters (commas, dots, spaces, etc.)
    timeStr = timeStr.replace(/[^0-9]/g, '');
    
    // Handle different time formats
    if (timeStr.length === 5) {
        // 5 digits (e.g., "90500" -> "09:05:00")
        timeStr = '0' + timeStr; // Pad with leading zero
    }
    
    if (timeStr.length === 6) {
        // HHMMSS format (e.g., "090500" -> "09:05:00")
        const hours = timeStr.substring(0, 2);
        const minutes = timeStr.substring(2, 4);
        const seconds = timeStr.substring(4, 6);
        return hours + ':' + minutes + ':' + seconds;
    } else if (timeStr.length === 4) {
        // HHMM format (e.g., "0905" -> "09:05")
        return timeStr.substring(0, 2) + ':' + timeStr.substring(2, 4);
    } else if (timeStr.length === 2) {
        // HH format (e.g., "09" -> "09:00:00")
        return timeStr + ':00:00';
    } else if (timeStr.length === 0) {
        return '';
    }
    
    // If it doesn't match expected format, return as-is
    return value;
}

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

