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
    
    // Initialize on page load
    document.addEventListener('DOMContentLoaded', function() {
        initializePayments();
    });
    
    /**
     * Initialize payment system
     */
    function initializePayments() {
        // Load saved license key
        const savedKey = localStorage.getItem(LICENSE_KEY_STORAGE);
        if (savedKey) {
            document.getElementById('licenseKey').value = savedKey;
            currentLicenseKey = savedKey;
        }
        
        // Load packages
        loadPackages();
        
        // Load balance if license key exists
        if (currentLicenseKey) {
            loadBalance();
        }
        
        // Setup event listeners
        setupEventListeners();
    }
    
    /**
     * Setup event listeners
     */
    function setupEventListeners() {
        // License key input
        const licenseKeyInput = document.getElementById('licenseKey');
        if (licenseKeyInput) {
            licenseKeyInput.addEventListener('change', function() {
                currentLicenseKey = this.value.trim();
                if (currentLicenseKey) {
                    localStorage.setItem(LICENSE_KEY_STORAGE, currentLicenseKey);
                    loadBalance();
                }
            });
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
     */
    function loadBalance() {
        if (!currentLicenseKey) {
            document.getElementById('balanceInfo').innerHTML = 
                '<p class="text-muted">Enter your license key to view balance</p>';
            return;
        }
        
        fetch(`${API_BASE}/balance?license_key=${encodeURIComponent(currentLicenseKey)}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    balance = data;
                    displayBalance();
                } else {
                    document.getElementById('balanceInfo').innerHTML = 
                        `<p class="text-danger">${data.error || 'Failed to load balance'}</p>`;
                }
            })
            .catch(error => {
                console.error('Error loading balance:', error);
                document.getElementById('balanceInfo').innerHTML = 
                    '<p class="text-danger">Failed to load balance</p>';
            });
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
            </div>
            <div class="small text-muted">
                <div>Purchased: ${purchasedHours.toFixed(2)} hours</div>
                <div>Used: ${usedHours.toFixed(2)} hours</div>
            </div>
            <button class="btn btn-sm btn-outline-primary mt-3" onclick="loadBalance()">
                <i class="fas fa-sync me-1"></i>Refresh
            </button>
        `;
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
        
        // Stats
        if (data.stats) {
            html += '<div class="col-12"><h6>Statistics (Last 30 Days)</h6>';
            html += `<p>Total API Calls: ${data.stats.total_api_calls || 0}</p>`;
            html += `<p>Total Hours Used: ${(data.stats.total_hours_used || 0).toFixed(2)}</p>`;
            if (data.stats.top_endpoints && data.stats.top_endpoints.length > 0) {
                html += '<p>Most Used Endpoints:</p><ul>';
                data.stats.top_endpoints.slice(0, 5).forEach(ep => {
                    html += `<li>${ep.endpoint}: ${ep.count} calls</li>`;
                });
                html += '</ul>';
            }
            html += '</div>';
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
    
    // Expose functions globally
    window.loadBalance = loadBalance;
    window.loadHistory = loadHistory;
    
})();

