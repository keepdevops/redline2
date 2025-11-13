/**
 * REDLINE Payment Management JavaScript
 * Handles payment processing, balance checking, and hour purchases
 */

(function() {
    'use strict';
    
    // Configuration
    const API_BASE = '/payments';
    const LICENSE_KEY_STORAGE = 'redline_license_key';
    
    // State
    let currentLicenseKey = null;
    let packages = [];
    let balance = null;
    let balanceRefreshInterval = null;
    let lastBalanceUpdate = null;
    let balanceUpdateInterval = null;
    const BALANCE_REFRESH_INTERVAL = 60000; // 1 minute (60 seconds)
    
    // Initialize on page load
    document.addEventListener('DOMContentLoaded', function() {
        initializePayments();
    });
    
    // Cleanup on page unload
    window.addEventListener('beforeunload', function() {
        stopBalanceRefresh();
        stopTimeElapsedUpdater();
    });
    
    /**
     * Initialize payment system
     */
    function initializePayments() {
        // Load saved license key
        const savedKey = localStorage.getItem(LICENSE_KEY_STORAGE);
        const licenseKeyInput = document.getElementById('licenseKey');
        
        if (savedKey && licenseKeyInput) {
            licenseKeyInput.value = savedKey;
            currentLicenseKey = savedKey;
            window.REDLINE_LICENSE_KEY = savedKey; // Also set global
            
            // Show saved status
            const licenseKeyStatus = document.getElementById('licenseKeyStatus');
            if (licenseKeyStatus) {
                licenseKeyStatus.innerHTML = '<small class="text-success"><i class="fas fa-check-circle me-1"></i>License key loaded from storage</small>';
            }
        } else if (licenseKeyInput) {
            // Show prompt if no key found
            const licenseKeyStatus = document.getElementById('licenseKeyStatus');
            if (licenseKeyStatus) {
                licenseKeyStatus.innerHTML = '<div class="alert alert-warning alert-sm py-2 mb-0"><i class="fas fa-exclamation-triangle me-1"></i><strong>No license key found.</strong> Please enter your license key above or <a href="/register" class="alert-link">register for a new one</a>.</div>';
            }
        }
        
        // Load packages
        loadPackages();
        
        // Load balance if license key exists
        if (currentLicenseKey) {
            loadBalance();
            startBalanceRefresh();
            loadHistory();
        }
        
        // Setup event listeners
        setupEventListeners();
    }
    
    /**
     * Start automatic balance refresh
     */
    function startBalanceRefresh() {
        // Stop any existing interval
        stopBalanceRefresh();
        
        // Start new interval
        if (currentLicenseKey) {
            balanceRefreshInterval = setInterval(function() {
                if (currentLicenseKey) {
                    loadBalance(true); // Silent refresh (don't show errors)
                } else {
                    stopBalanceRefresh();
                }
            }, BALANCE_REFRESH_INTERVAL);
        }
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
     * Setup event listeners
     */
    function setupEventListeners() {
        // License key input
        const licenseKeyInput = document.getElementById('licenseKey');
        const saveLicenseKeyBtn = document.getElementById('saveLicenseKeyBtn');
        const licenseKeyStatus = document.getElementById('licenseKeyStatus');
        
        if (licenseKeyInput) {
            // Save on change (blur)
            licenseKeyInput.addEventListener('change', function() {
                saveLicenseKey();
            });
            
            // Save on Enter key
            licenseKeyInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    saveLicenseKey();
                }
            });
            
            // Save button click
            if (saveLicenseKeyBtn) {
                saveLicenseKeyBtn.addEventListener('click', function() {
                    saveLicenseKey();
                });
            }
            
            // Show status when typing
            licenseKeyInput.addEventListener('input', function() {
                const key = this.value.trim();
                if (key && key.length > 10) {
                    if (licenseKeyStatus) {
                        licenseKeyStatus.innerHTML = '<small class="text-success"><i class="fas fa-check-circle me-1"></i>Press Enter or click Save to store license key</small>';
                    }
                } else if (key.length > 0) {
                    if (licenseKeyStatus) {
                        licenseKeyStatus.innerHTML = '<small class="text-warning"><i class="fas fa-exclamation-triangle me-1"></i>License key seems too short</small>';
                    }
                } else {
                    if (licenseKeyStatus) {
                        licenseKeyStatus.innerHTML = '';
                    }
                }
            });
        }
        
        function saveLicenseKey() {
            const key = licenseKeyInput.value.trim();
            if (key) {
                localStorage.setItem(LICENSE_KEY_STORAGE, key);
                currentLicenseKey = key;
                window.REDLINE_LICENSE_KEY = key; // Also set global
                
                // Dispatch event for other scripts
                window.dispatchEvent(new CustomEvent('licenseKeyUpdated', { detail: { licenseKey: key } }));
                
                if (licenseKeyStatus) {
                    licenseKeyStatus.innerHTML = '<small class="text-success"><i class="fas fa-check-circle me-1"></i>License key saved! Loading balance...</small>';
                }
                
                loadBalance();
                startBalanceRefresh();
                loadHistory();
                
                // Clear status after 3 seconds
                setTimeout(function() {
                    if (licenseKeyStatus) {
                        licenseKeyStatus.innerHTML = '<small class="text-muted"><i class="fas fa-check-circle me-1"></i>License key saved</small>';
                    }
                }, 3000);
            } else {
                if (licenseKeyStatus) {
                    licenseKeyStatus.innerHTML = '<small class="text-danger"><i class="fas fa-exclamation-circle me-1"></i>Please enter a valid license key</small>';
                }
            }
        }
        
        // Custom hours purchase
        const customHoursInput = document.getElementById('customHours');
        const purchaseCustomBtn = document.getElementById('purchaseCustomBtn');
        
        if (customHoursInput && purchaseCustomBtn) {
            customHoursInput.addEventListener('input', function() {
                updateCustomPrice();
            });
            
            purchaseCustomBtn.addEventListener('click', function() {
                const hours = parseFloat(customHoursInput.value);
                if (hours > 0) {
                    purchaseHours(hours);
                } else {
                    showMessage('Please enter a valid number of hours', 'warning');
                }
            });
        }
    }
    
    /**
     * Load available packages
     */
    function loadPackages() {
        fetch(`${API_BASE}/packages`)
            .then(response => response.json())
            .then(data => {
                packages = data.packages || [];
                displayPackages();
            })
            .catch(error => {
                console.error('Error loading packages:', error);
                showMessage('Failed to load packages', 'error');
            });
    }
    
    /**
     * Display packages
     */
    function displayPackages() {
        const container = document.getElementById('packagesContainer');
        if (!container) return;
        
        if (packages.length === 0) {
            container.innerHTML = '<div class="col-12 text-muted">No packages available</div>';
            return;
        }
        
        container.innerHTML = packages.map(pkg => `
            <div class="col-md-6 mb-3">
                <div class="card h-100">
                    <div class="card-body">
                        <h5 class="card-title">${pkg.name}</h5>
                        <p class="card-text">
                            <strong>${pkg.hours} hours</strong><br>
                            <span class="text-muted">$${pkg.price.toFixed(2)}</span><br>
                            <small>$${pkg.price_per_hour.toFixed(2)} per hour</small>
                        </p>
                        <button class="btn btn-primary w-100" onclick="purchasePackage('${pkg.id}')">
                            <i class="fas fa-shopping-cart me-2"></i>Purchase
                        </button>
                    </div>
                </div>
            </div>
        `).join('');
    }
    
    /**
     * Purchase a package
     */
    window.purchasePackage = function(packageId) {
        console.log('purchasePackage called:', packageId);
        console.log('Current license key:', currentLicenseKey);
        console.log('Available packages:', packages);
        
        // Try to get license key from input if not set
        const licenseKeyInput = document.getElementById('licenseKey');
        if (licenseKeyInput && licenseKeyInput.value.trim() && !currentLicenseKey) {
            currentLicenseKey = licenseKeyInput.value.trim();
            localStorage.setItem(LICENSE_KEY_STORAGE, currentLicenseKey);
            console.log('License key loaded from input:', currentLicenseKey);
        }
        
        if (!currentLicenseKey) {
            showMessage('Please enter your license key first', 'warning');
            if (licenseKeyInput) licenseKeyInput.focus();
            return;
        }
        
        const pkg = packages.find(p => p.id === packageId);
        if (!pkg) {
            console.error('Package not found:', packageId);
            showMessage('Package not found', 'error');
            return;
        }
        
        console.log('Purchasing package:', pkg);
        purchaseHours(pkg.hours, packageId);
    };
    
    /**
     * Purchase hours
     */
    function purchaseHours(hours, packageId = null) {
        console.log('purchaseHours called:', { hours, packageId, currentLicenseKey });
        
        if (!currentLicenseKey) {
            const licenseKeyInput = document.getElementById('licenseKey');
            if (licenseKeyInput && licenseKeyInput.value.trim()) {
                currentLicenseKey = licenseKeyInput.value.trim();
                localStorage.setItem(LICENSE_KEY_STORAGE, currentLicenseKey);
            } else {
                showMessage('Please enter your license key first', 'warning');
                if (licenseKeyInput) licenseKeyInput.focus();
                return;
            }
        }
        
        if (hours <= 0) {
            showMessage('Please enter a valid number of hours', 'warning');
            return;
        }
        
        console.log('Creating checkout session with:', {
            hours,
            package_id: packageId,
            license_key: currentLicenseKey
        });
        
        showMessage('Creating checkout session...', 'info');
        
        fetch(`${API_BASE}/create-checkout`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                hours: hours,
                package_id: packageId,
                license_key: currentLicenseKey
            })
        })
        .then(response => {
            console.log('Checkout response status:', response.status);
            return response.json();
        })
        .then(data => {
            console.log('Checkout response data:', data);
            if (data.checkout_url) {
                // Redirect to Stripe checkout
                console.log('Redirecting to:', data.checkout_url);
                window.location.href = data.checkout_url;
            } else if (data.error) {
                console.error('Checkout error:', data.error);
                showMessage(data.error, 'error');
            } else {
                console.error('Unexpected response:', data);
                showMessage('Unexpected response from server', 'error');
            }
        })
        .catch(error => {
            console.error('Error creating checkout:', error);
            showMessage('Failed to create checkout session: ' + error.message, 'error');
        });
    }
    
    /**
     * Load balance
     * @param {boolean} silent - If true, don't show error messages (for auto-refresh)
     */
    function loadBalance(silent = false) {
        if (!currentLicenseKey) {
            if (!silent) {
                document.getElementById('balanceInfo').innerHTML = 
                    '<p class="text-muted">Enter your license key to view balance</p>';
            }
            return;
        }
        
        fetch(`${API_BASE}/balance?license_key=${encodeURIComponent(currentLicenseKey)}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    balance = data;
                    displayBalance();
                } else {
                    if (!silent) {
                        document.getElementById('balanceInfo').innerHTML = 
                            `<p class="text-danger">${data.error || 'Failed to load balance'}</p>`;
                    }
                }
            })
            .catch(error => {
                console.error('Error loading balance:', error);
                if (!silent) {
                    document.getElementById('balanceInfo').innerHTML = 
                        '<p class="text-danger">Failed to load balance</p>';
                }
            });
    }
    
    /**
     * Format time elapsed since last update
     */
    function formatTimeElapsed(seconds) {
        if (seconds < 60) {
            return `${Math.floor(seconds)} second${Math.floor(seconds) !== 1 ? 's' : ''} ago`;
        } else if (seconds < 3600) {
            const minutes = Math.floor(seconds / 60);
            const secs = Math.floor(seconds % 60);
            if (secs === 0) {
                return `${minutes} minute${minutes !== 1 ? 's' : ''} ago`;
            }
            return `${minutes} minute${minutes !== 1 ? 's' : ''} ${secs} second${secs !== 1 ? 's' : ''} ago`;
        } else {
            const hours = Math.floor(seconds / 3600);
            const minutes = Math.floor((seconds % 3600) / 60);
            const secs = Math.floor(seconds % 60);
            let result = `${hours} hour${hours !== 1 ? 's' : ''}`;
            if (minutes > 0) {
                result += ` ${minutes} minute${minutes !== 1 ? 's' : ''}`;
            }
            if (secs > 0 && hours < 2) {
                result += ` ${secs} second${secs !== 1 ? 's' : ''}`;
            }
            return result + ' ago';
        }
    }
    
    /**
     * Update time elapsed display
     */
    function updateTimeElapsed() {
        if (!lastBalanceUpdate) return;
        
        const elapsed = (Date.now() - lastBalanceUpdate) / 1000; // seconds
        const timeElapsedEl = document.getElementById('timeElapsed');
        if (timeElapsedEl) {
            timeElapsedEl.textContent = formatTimeElapsed(elapsed);
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
     * Display balance
     */
    function displayBalance() {
        const container = document.getElementById('balanceInfo');
        if (!container || !balance) return;
        
        const hoursRemaining = balance.hours_remaining || 0;
        const usedHours = balance.used_hours || 0;
        const purchasedHours = balance.purchased_hours || 0;
        
        // Update last balance update time
        lastBalanceUpdate = Date.now();
        
        // Determine status color
        let statusClass = 'text-success';
        if (hoursRemaining < 1) {
            statusClass = 'text-danger';
        } else if (hoursRemaining < 5) {
            statusClass = 'text-warning';
        }
        
        container.innerHTML = `
            <div class="mb-3">
                <h2 class="${statusClass}">${hoursRemaining.toFixed(2)}</h2>
                <p class="text-muted mb-0">Hours Remaining</p>
                <small class="text-muted" id="timeElapsed">Just now</small>
            </div>
            <div class="small text-muted">
                <div>Purchased: ${purchasedHours.toFixed(2)} hours</div>
                <div>Used: ${usedHours.toFixed(2)} hours</div>
            </div>
            <button class="btn btn-sm btn-outline-primary mt-3" onclick="loadBalance()">
                <i class="fas fa-sync me-1"></i>Refresh Now
            </button>
            <div class="mt-2">
                <small class="text-muted">
                    <i class="fas fa-info-circle me-1"></i>Auto-refreshes every minute
                </small>
            </div>
        `;
        
        // Start time elapsed updater
        startTimeElapsedUpdater();
    }
    
    /**
     * Update custom price display
     */
    function updateCustomPrice() {
        const hoursInput = document.getElementById('customHours');
        const priceDisplay = document.getElementById('customPrice');
        
        if (!hoursInput || !priceDisplay) return;
        
        const hours = parseFloat(hoursInput.value);
        if (hours > 0) {
            // Calculate price (default: $5 per hour)
            const price = hours * 5;
            priceDisplay.textContent = `Estimated cost: $${price.toFixed(2)}`;
        } else {
            priceDisplay.textContent = '';
        }
    }
    
    /**
     * Show message
     */
    function showMessage(message, type = 'info') {
        const container = document.getElementById('paymentMessages');
        if (!container) return;
        
        const alertClass = {
            'info': 'alert-info',
            'success': 'alert-success',
            'warning': 'alert-warning',
            'error': 'alert-danger'
        }[type] || 'alert-info';
        
        const alert = document.createElement('div');
        alert.className = `alert ${alertClass} alert-dismissible fade show`;
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        container.appendChild(alert);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            alert.remove();
        }, 5000);
    }
    
    /**
     * Load usage history
     */
    function loadHistory() {
        if (!currentLicenseKey) {
            document.getElementById('usageHistory').innerHTML = 
                '<p class="text-muted">Enter your license key to view history</p>';
            return;
        }
        
        fetch(`${API_BASE}/history?license_key=${encodeURIComponent(currentLicenseKey)}&type=all`)
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    document.getElementById('usageHistory').innerHTML = 
                        `<p class="text-danger">${data.error}</p>`;
                    return;
                }
                
                displayHistory(data);
            })
            .catch(error => {
                console.error('Error loading history:', error);
                document.getElementById('usageHistory').innerHTML = 
                    '<p class="text-danger">Failed to load history</p>';
            });
    }
    
    /**
     * Display usage history
     */
    function displayHistory(data) {
        const container = document.getElementById('usageHistory');
        if (!container) return;
        
        let html = '<div class="row">';
        
        // Usage History
        if (data.usage_history && data.usage_history.length > 0) {
            html += '<div class="col-md-6 mb-3"><h6>Recent Usage</h6><table class="table table-sm"><thead><tr><th>Date</th><th>Hours</th><th>Remaining</th></tr></thead><tbody>';
            data.usage_history.slice(0, 10).forEach(entry => {
                const date = new Date(entry.deduction_time).toLocaleString();
                html += `<tr><td>${date}</td><td>${entry.hours_deducted.toFixed(4)}</td><td>${entry.hours_remaining_after ? entry.hours_remaining_after.toFixed(2) : 'N/A'}</td></tr>`;
            });
            html += '</tbody></table></div>';
        } else {
            html += '<div class="col-md-6 mb-3"><h6>Recent Usage</h6><p class="text-muted">No usage history available</p></div>';
        }
        
        // Payment History
        if (data.payment_history && data.payment_history.length > 0) {
            html += '<div class="col-md-6 mb-3"><h6>Payment History</h6><table class="table table-sm"><thead><tr><th>Date</th><th>Hours</th><th>Amount</th></tr></thead><tbody>';
            data.payment_history.slice(0, 10).forEach(entry => {
                const date = new Date(entry.payment_date).toLocaleString();
                html += `<tr><td>${date}</td><td>${entry.hours_purchased}</td><td>$${entry.amount_paid.toFixed(2)}</td></tr>`;
            });
            html += '</tbody></table></div>';
        } else {
            html += '<div class="col-md-6 mb-3"><h6>Payment History</h6><p class="text-muted">No payment history available</p></div>';
        }
        
        // Totals
        if (data.totals) {
            html += '<div class="col-12 mt-3"><div class="card"><div class="card-body"><h6>Summary</h6>';
            html += `<p><strong>Total Hours Used:</strong> ${(data.totals.total_hours_used || 0).toFixed(2)} hours</p>`;
            html += `<p><strong>Total Hours Purchased:</strong> ${(data.totals.total_hours_purchased || 0).toFixed(2)} hours</p>`;
            html += `<p><strong>Total Payments:</strong> ${data.totals.total_payments || 0}</p>`;
            html += `<p><strong>Total Sessions:</strong> ${data.totals.total_sessions || 0}</p>`;
            html += '</div></div></div>';
        }
        
        html += '</div>';
        container.innerHTML = html || '<p class="text-muted">No history available</p>';
    }
    
    // Check for payment success on page load
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('session_id')) {
        // Payment success - reload balance and history
        setTimeout(() => {
            if (currentLicenseKey) {
                loadBalance();
                loadHistory();
                startBalanceRefresh(); // Restart auto-refresh after payment
            }
        }, 1000);
    }
    
    // Load history when license key changes
    const licenseKeyInput = document.getElementById('licenseKey');
    if (licenseKeyInput) {
        licenseKeyInput.addEventListener('change', function() {
            if (this.value.trim()) {
                loadHistory();
            }
        });
    }
    
    // Expose functions globally for onclick handlers
    window.loadBalance = function() {
        loadBalance(false);
    };
    window.loadHistory = loadHistory;
    
})();

