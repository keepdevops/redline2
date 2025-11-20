/**
 * REDLINE Global Balance Tracker
 * Tracks and displays hours remaining balance across all pages
 */

(function() {
    'use strict';
    
    // Configuration
    const API_BASE = '/payments';
    const LICENSE_KEY_STORAGE = 'redline_license_key';
    const BALANCE_REFRESH_INTERVAL = 60000; // 1 minute
    const BALANCE_STORAGE = 'redline_balance_cache';
    const BALANCE_CACHE_TTL = 30000; // 30 seconds cache
    
    // State
    let balanceRefreshInterval = null;
    let lastBalanceUpdate = null;
    let balanceUpdateInterval = null;
    let currentBalance = null;
    
    /**
     * Get stored license key
     */
    function getLicenseKey() {
        if (typeof window.getLicenseKey === 'function') {
            return window.getLicenseKey();
        }
        return localStorage.getItem(LICENSE_KEY_STORAGE) || window.REDLINE_LICENSE_KEY;
    }
    
    /**
     * Format time elapsed since last update
     */
    function formatTimeElapsed(seconds) {
        if (seconds < 60) {
            return `${Math.floor(seconds)}s ago`;
        } else if (seconds < 3600) {
            const minutes = Math.floor(seconds / 60);
            const secs = Math.floor(seconds % 60);
            if (secs === 0) {
                return `${minutes}m ago`;
            }
            return `${minutes}m ${secs}s ago`;
        } else {
            const hours = Math.floor(seconds / 3600);
            const minutes = Math.floor((seconds % 3600) / 60);
            let result = `${hours}h`;
            if (minutes > 0) {
                result += ` ${minutes}m`;
            }
            return result + ' ago';
        }
    }
    
    /**
     * Update balance display in navbar
     * @param {boolean} updateTimestamp - If true, update lastBalanceUpdate timestamp (default: true)
     */
    function updateBalanceDisplay(balance, updateTimestamp = true) {
        if (!balance) return;
        
        const hoursRemaining = balance.hours_remaining || 0;
        const usedHours = balance.used_hours || 0;
        const purchasedHours = balance.purchased_hours || 0;
        
        // Update last balance update time only if explicitly requested
        // This allows preserving timestamp when loading from cache
        if (updateTimestamp) {
            lastBalanceUpdate = Date.now();
        } else if (!lastBalanceUpdate) {
            // If no timestamp exists, set it now
            lastBalanceUpdate = Date.now();
        }
        
        // Determine status color
        let statusClass = 'text-success';
        let statusIcon = 'fa-clock';
        if (hoursRemaining < 1) {
            statusClass = 'text-danger';
            statusIcon = 'fa-exclamation-triangle';
        } else if (hoursRemaining < 5) {
            statusClass = 'text-warning';
            statusIcon = 'fa-exclamation-circle';
        }
        
        // Find or create balance display element
        let balanceDisplay = document.getElementById('globalBalanceDisplay');
        if (!balanceDisplay) {
            // Create balance display element in navbar
            // Try multiple selectors to find navbar
            let navbarNav = document.querySelector('.navbar-nav:last-child');
            if (!navbarNav) {
                navbarNav = document.querySelector('.navbar-nav');
            }
            if (!navbarNav) {
                // Try to find any navbar nav
                const navbar = document.querySelector('nav.navbar');
                if (navbar) {
                    navbarNav = navbar.querySelector('.navbar-nav');
                }
            }
            
            if (navbarNav) {
                const balanceItem = document.createElement('li');
                balanceItem.className = 'nav-item';
                balanceItem.id = 'globalBalanceDisplay';
                balanceItem.innerHTML = `
                    <div class="nav-link" id="balanceWidget" style="cursor: pointer;" title="Click to refresh - Used: ${usedHours.toFixed(2)}h">
                        <i class="fas ${statusIcon} ${statusClass} me-1"></i>
                        <span class="balance-hours ${statusClass}" id="balanceHours">${hoursRemaining.toFixed(2)}</span>
                        <small class="text-muted ms-1" id="balanceTime">Just now</small>
                        <small class="text-muted ms-2" id="usedHours" style="font-size: 0.75em;">Used: ${usedHours.toFixed(2)}h</small>
                    </div>
                `;
                
                // Insert before last item (usually "Online" status) or append
                if (navbarNav.children.length > 0) {
                    navbarNav.insertBefore(balanceItem, navbarNav.lastChild);
                } else {
                    navbarNav.appendChild(balanceItem);
                }
                
                // Add click handler to refresh balance
                const widget = balanceItem.querySelector('#balanceWidget');
                if (widget) {
                    widget.addEventListener('click', function() {
                        loadBalance(false);
                    });
                }
                
                balanceDisplay = balanceItem;
            } else {
                console.warn('Balance tracker: Navbar not found, cannot create balance display');
                return; // Navbar not found
            }
        }
        
        // Update balance display
        const balanceHoursEl = document.getElementById('balanceHours');
        const balanceTimeEl = document.getElementById('balanceTime');
        const usedHoursEl = document.getElementById('usedHours');
        const balanceWidget = document.getElementById('balanceWidget');
        
        if (balanceHoursEl) {
            balanceHoursEl.textContent = hoursRemaining.toFixed(2);
            balanceHoursEl.className = `balance-hours ${statusClass}`;
        }
        
        if (usedHoursEl) {
            // Always update used hours display
            usedHoursEl.textContent = `Used: ${usedHours.toFixed(2)}h`;
            console.log('Updated used hours display:', usedHours.toFixed(2));
        } else if (balanceWidget) {
            // Create used hours element if it doesn't exist
            const usedEl = document.createElement('small');
            usedEl.className = 'text-muted ms-2';
            usedEl.id = 'usedHours';
            usedEl.style.fontSize = '0.75em';
            usedEl.textContent = `Used: ${usedHours.toFixed(2)}h`;
            balanceWidget.appendChild(usedEl);
        }
        
        // Update tooltip
        if (balanceWidget) {
            balanceWidget.title = `Click to refresh - Used: ${usedHours.toFixed(2)}h / Purchased: ${purchasedHours.toFixed(2)}h`;
            const icon = balanceWidget.querySelector('i');
            if (icon) {
                icon.className = `fas ${statusIcon} ${statusClass} me-1`;
            }
        }
        
        // Start time elapsed updater
        startTimeElapsedUpdater();
        
        // Store balance in cache
        try {
            localStorage.setItem(BALANCE_STORAGE, JSON.stringify({
                balance: balance,
                timestamp: Date.now()
            }));
        } catch (e) {
            console.warn('Failed to cache balance:', e);
        }
    }
    
    /**
     * Update time elapsed display
     */
    function updateTimeElapsed() {
        if (!lastBalanceUpdate) return;
        
        const elapsed = (Date.now() - lastBalanceUpdate) / 1000; // seconds
        const balanceTimeEl = document.getElementById('balanceTime');
        if (balanceTimeEl) {
            balanceTimeEl.textContent = formatTimeElapsed(elapsed);
        }
    }
    
    /**
     * Start time elapsed updater
     */
    function startTimeElapsedUpdater() {
        // Stop existing interval
        if (balanceUpdateInterval) {
            clearInterval(balanceUpdateInterval);
        }
        
        // Update every second
        balanceUpdateInterval = setInterval(updateTimeElapsed, 1000);
    }
    
    /**
     * Stop time elapsed updater
     */
    function stopTimeElapsedUpdater() {
        if (balanceUpdateInterval) {
            clearInterval(balanceUpdateInterval);
            balanceUpdateInterval = null;
        }
    }
    
    /**
     * Load balance from server
     * @param {boolean} silent - If true, don't show errors (for auto-refresh)
     */
    function loadBalance(silent = true) {
        const licenseKey = getLicenseKey();
        if (!licenseKey) {
            // Hide balance display if no license key
            const balanceDisplay = document.getElementById('globalBalanceDisplay');
            if (balanceDisplay) {
                balanceDisplay.style.display = 'none';
            }
            return;
        }
        
        // Show balance display
        const balanceDisplay = document.getElementById('globalBalanceDisplay');
        if (balanceDisplay) {
            balanceDisplay.style.display = '';
        }
        
        fetch(`${API_BASE}/balance?license_key=${encodeURIComponent(licenseKey)}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                return response.json();
            })
            .then(data => {
                // Ensure data has required fields with defaults
                if (!data.purchased_hours && data.purchased_hours !== 0) {
                    data.purchased_hours = 0.0;
                }
                if (!data.hours_remaining && data.hours_remaining !== 0) {
                    data.hours_remaining = 0.0;
                }
                if (!data.used_hours && data.used_hours !== 0) {
                    data.used_hours = 0.0;
                }
                
                if (data.success || (data.hours_remaining !== undefined) || data.error) {
                    // Accept both {success: true, ...} and {hours_remaining: ...} formats
                    // Also handle error responses that include balance fields
                    currentBalance = data;
                    // Always update timestamp when fetching from server
                    updateBalanceDisplay(data, true);
                    
                    // Dispatch custom event for other scripts
                    window.dispatchEvent(new CustomEvent('balanceUpdated', { 
                        detail: { balance: data } 
                    }));
                    
                    // Log error if present but still display balance
                    if (data.error && !silent) {
                        console.warn('Balance loaded with error:', data.error);
                    }
                } else {
                    if (!silent) {
                        console.error('Failed to load balance:', data.error || data);
                    }
                    // Show error in display
                    const balanceHoursEl = document.getElementById('balanceHours');
                    if (balanceHoursEl) {
                        balanceHoursEl.textContent = 'Error';
                        balanceHoursEl.className = 'balance-hours text-danger';
                    }
                }
            })
            .catch(error => {
                console.error('Error loading balance:', error);
                if (!silent) {
                    console.error('Failed to load balance:', error);
                }
                // Show error in display
                const balanceHoursEl = document.getElementById('balanceHours');
                if (balanceHoursEl) {
                    balanceHoursEl.textContent = 'Error';
                    balanceHoursEl.className = 'balance-hours text-danger';
                }
            });
    }
    
    /**
     * Load balance from cache if available
     */
    function loadBalanceFromCache() {
        try {
            const cached = localStorage.getItem(BALANCE_STORAGE);
            if (cached) {
                const { balance, timestamp } = JSON.parse(cached);
                const age = Date.now() - timestamp;
                
                // Use cache if less than TTL old
                if (age < BALANCE_CACHE_TTL && balance) {
                    currentBalance = balance;
                    // Preserve the original timestamp, don't reset it
                    lastBalanceUpdate = timestamp;
                    updateBalanceDisplay(balance, false); // Don't reset timestamp
                    return true;
                }
            }
        } catch (e) {
            // Ignore cache errors
        }
        return false;
    }
    
    /**
     * Start automatic balance refresh
     * @param {boolean} skipInitialLoad - If true, skip immediate load (for cache-first initialization)
     */
    function startBalanceRefresh(skipInitialLoad = false) {
        // Stop any existing interval
        stopBalanceRefresh();
        
        const licenseKey = getLicenseKey();
        if (!licenseKey) {
            return;
        }
        
        // Load balance immediately unless we're skipping (cache already loaded)
        if (!skipInitialLoad) {
            loadBalance(true);
        }
        
        // Start refresh interval
        balanceRefreshInterval = setInterval(function() {
            const currentKey = getLicenseKey();
            if (currentKey) {
                loadBalance(true); // Silent refresh
            } else {
                stopBalanceRefresh();
            }
        }, BALANCE_REFRESH_INTERVAL);
    }
    
    /**
     * Stop automatic balance refresh
     */
    function stopBalanceRefresh() {
        if (balanceRefreshInterval) {
            clearInterval(balanceRefreshInterval);
            balanceRefreshInterval = null;
        }
    }
    
    /**
     * Initialize balance tracker
     */
    function init() {
        const licenseKey = getLicenseKey();
        if (!licenseKey) {
            displayNoLicenseState();
            return;
        }
        
        // Load balance from cache first (for instant display)
        const cacheLoaded = loadBalanceFromCache();
        
        // Always load balance immediately, even if cache was loaded
        // This ensures fresh data and updates the display
        loadBalance(false); // false = not silent, show errors
        
        // Start balance refresh (skip initial load since we just loaded)
        startBalanceRefresh(true); // true = skip initial load
        
        // Ensure display is visible - create placeholder if needed
        let balanceDisplay = document.getElementById('globalBalanceDisplay');
        if (!balanceDisplay) {
            // Create a placeholder display element if it doesn't exist
            // This ensures the display area exists even before balance loads
            const navbarNav = document.querySelector('.navbar-nav:last-child') || 
                             document.querySelector('.navbar-nav') ||
                             (document.querySelector('nav.navbar')?.querySelector('.navbar-nav'));
            
            if (navbarNav) {
                const placeholder = document.createElement('li');
                placeholder.className = 'nav-item';
                placeholder.id = 'globalBalanceDisplay';
                placeholder.innerHTML = `
                    <div class="nav-link" id="balanceWidget" style="cursor: pointer;">
                        <i class="fas fa-clock text-muted me-1"></i>
                        <span class="balance-hours text-muted" id="balanceHours">Loading...</span>
                        <small class="text-muted ms-1" id="balanceTime"></small>
                        <small class="text-muted ms-2" id="usedHours" style="font-size: 0.75em;"></small>
                    </div>
                `;
                
                if (navbarNav.children.length > 0) {
                    navbarNav.insertBefore(placeholder, navbarNav.lastChild);
                } else {
                    navbarNav.appendChild(placeholder);
                }
                
                balanceDisplay = placeholder;
            }
        }
        
        // Ensure display is visible
        if (balanceDisplay) {
            balanceDisplay.style.display = '';
        }
        
        // Listen for license key updates
        window.addEventListener('licenseKeyUpdated', function(event) {
            const licenseKey = event.detail.licenseKey;
            if (licenseKey) {
                startBalanceRefresh();
            } else {
                stopBalanceRefresh();
                const balanceDisplay = document.getElementById('globalBalanceDisplay');
                if (balanceDisplay) {
                    balanceDisplay.style.display = 'none';
                }
            }
        });
        
        // Listen for storage changes (for multi-tab support)
        window.addEventListener('storage', function(event) {
            if (event.key === LICENSE_KEY_STORAGE) {
                // License key changed in another tab
                startBalanceRefresh();
            }
        });
        
        // Cleanup on page unload
        window.addEventListener('beforeunload', function() {
            stopBalanceRefresh();
            stopTimeElapsedUpdater();
        });
    }
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        // DOM already loaded
        init();
    }
    
    /**
     * Display no license state
     */
    function displayNoLicenseState() {
        const balanceDisplay = document.getElementById('globalBalanceDisplay');
        if (balanceDisplay) {
            balanceDisplay.style.display = 'none';
        }
    }
    
    // Expose global functions
    window.REDLINE_BALANCE = {
        loadBalance: function() { loadBalance(false); },
        getBalance: function() { return currentBalance; },
        refresh: function() { loadBalance(false); }
    };
    
})();

