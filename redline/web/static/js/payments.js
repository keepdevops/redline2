/**
 * VarioSync Subscription Management JavaScript
 * Handles Stripe subscription management, usage tracking, and billing
 */

(function() {
    'use strict';

    // Configuration
    const API_BASE = '/payments';

    // State
    let subscription = null;
    let usage = null;
    let subscriptionRefreshInterval = null;
    let lastSubscriptionUpdate = null;
    let updateInterval = null;
    const REFRESH_INTERVAL = 60000; // 1 minute

    // Initialize on page load
    document.addEventListener('DOMContentLoaded', function() {
        initializeSubscriptions();
    });

    // Cleanup on page unload
    window.addEventListener('beforeunload', function() {
        stopSubscriptionRefresh();
        stopTimeElapsedUpdater();
    });

    /**
     * Initialize subscription system
     */
    function initializeSubscriptions() {
        // Check if user is authenticated
        if (!window.VARIOSYNC || !window.VARIOSYNC.isAuthenticated()) {
            showAuthRequired();
            return;
        }

        // Load subscription status
        loadSubscription();
        startSubscriptionRefresh();

        // Setup event listeners
        setupEventListeners();

        // Check for subscription success/cancel in URL
        checkSubscriptionStatus();
    }

    /**
     * Show authentication required message
     */
    function showAuthRequired() {
        const container = document.getElementById('subscriptionInfo');
        if (container) {
            container.innerHTML = `
                <div class="alert alert-warning">
                    <i class="fas fa-lock me-2"></i>
                    Please <a href="/auth/login?redirect=${encodeURIComponent(window.location.pathname)}" class="alert-link">log in</a> to manage your subscription.
                </div>
            `;
        }
    }

    /**
     * Start automatic subscription refresh
     */
    function startSubscriptionRefresh() {
        stopSubscriptionRefresh();

        if (window.VARIOSYNC && window.VARIOSYNC.isAuthenticated()) {
            subscriptionRefreshInterval = setInterval(function() {
                if (window.VARIOSYNC.isAuthenticated()) {
                    loadSubscription(true); // Silent refresh
                } else {
                    stopSubscriptionRefresh();
                }
            }, REFRESH_INTERVAL);
        }
    }

    /**
     * Stop automatic subscription refresh
     */
    function stopSubscriptionRefresh() {
        if (subscriptionRefreshInterval) {
            clearInterval(subscriptionRefreshInterval);
            subscriptionRefreshInterval = null;
        }
    }

    /**
     * Setup event listeners
     */
    function setupEventListeners() {
        // Subscribe button
        const subscribeBtn = document.getElementById('subscribeBtn');
        if (subscribeBtn) {
            subscribeBtn.addEventListener('click', function() {
                createSubscriptionCheckout();
            });
        }

        // Cancel subscription button
        const cancelBtn = document.getElementById('cancelSubscriptionBtn');
        if (cancelBtn) {
            cancelBtn.addEventListener('click', function() {
                confirmCancelSubscription();
            });
        }

        // Manage subscription button (opens Stripe customer portal)
        const manageBtn = document.getElementById('manageSubscriptionBtn');
        if (manageBtn) {
            manageBtn.addEventListener('click', function() {
                openCustomerPortal();
            });
        }
    }

    /**
     * Load subscription status
     * @param {boolean} silent - If true, don't show error messages
     */
    function loadSubscription(silent = false) {
        if (!window.VARIOSYNC || !window.VARIOSYNC.isAuthenticated()) {
            if (!silent) showAuthRequired();
            return;
        }

        const token = window.VARIOSYNC.getToken();

        fetch(`${API_BASE}/balance`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            subscription = data.subscription || null;
            usage = data.usage || null;
            displaySubscription();
        })
        .catch(error => {
            console.error('Error loading subscription:', error);
            if (!silent) {
                showMessage('Failed to load subscription status', 'error');
            }
        });
    }

    /**
     * Display subscription information
     */
    function displaySubscription() {
        const container = document.getElementById('subscriptionInfo');
        if (!container) return;

        // Update last update time
        lastSubscriptionUpdate = Date.now();
        startTimeElapsedUpdater();

        if (!subscription) {
            // No active subscription
            container.innerHTML = `
                <div class="card">
                    <div class="card-body text-center">
                        <i class="fas fa-info-circle fa-3x text-muted mb-3"></i>
                        <h5>No Active Subscription</h5>
                        <p class="text-muted">Subscribe to VarioSync to access data processing features</p>
                        <button class="btn btn-primary" id="subscribeBtn">
                            <i class="fas fa-credit-card me-2"></i>Subscribe Now
                        </button>
                    </div>
                </div>
            `;
            setupEventListeners();
            return;
        }

        // Determine status
        const status = subscription.status || 'unknown';
        const isActive = ['active', 'trialing'].includes(status);

        let statusBadge = '';
        let statusClass = '';

        switch(status) {
            case 'active':
                statusBadge = '<span class="badge bg-success">Active</span>';
                statusClass = 'text-success';
                break;
            case 'trialing':
                statusBadge = '<span class="badge bg-info">Trial</span>';
                statusClass = 'text-info';
                break;
            case 'past_due':
                statusBadge = '<span class="badge bg-warning">Past Due</span>';
                statusClass = 'text-warning';
                break;
            case 'canceled':
            case 'cancelled':
                statusBadge = '<span class="badge bg-danger">Canceled</span>';
                statusClass = 'text-danger';
                break;
            case 'incomplete':
                statusBadge = '<span class="badge bg-secondary">Incomplete</span>';
                statusClass = 'text-muted';
                break;
            default:
                statusBadge = `<span class="badge bg-secondary">${status}</span>`;
                statusClass = 'text-muted';
        }

        // Format dates
        const currentPeriodEnd = subscription.current_period_end
            ? new Date(subscription.current_period_end * 1000).toLocaleDateString()
            : 'N/A';

        // Usage information
        const totalUsage = usage ? usage.total_usage || 0 : 0;
        const usageDisplay = totalUsage > 0
            ? `${totalUsage.toLocaleString()} records processed`
            : 'No usage yet';

        container.innerHTML = `
            <div class="card">
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-start mb-3">
                        <div>
                            <h5 class="mb-1">Subscription Status</h5>
                            ${statusBadge}
                        </div>
                        <small class="text-muted" id="timeElapsed">Just now</small>
                    </div>

                    <div class="mb-3">
                        <h2 class="${statusClass}">${usageDisplay}</h2>
                        <p class="text-muted mb-0">Current billing period</p>
                    </div>

                    <div class="row text-start small">
                        <div class="col-md-6 mb-2">
                            <strong>Plan:</strong> VarioSync Metered
                        </div>
                        <div class="col-md-6 mb-2">
                            <strong>Billing Period Ends:</strong> ${currentPeriodEnd}
                        </div>
                        ${subscription.cancel_at_period_end ? `
                            <div class="col-12">
                                <div class="alert alert-warning py-2 mb-0 mt-2">
                                    <i class="fas fa-exclamation-triangle me-1"></i>
                                    Subscription will cancel on ${currentPeriodEnd}
                                </div>
                            </div>
                        ` : ''}
                    </div>

                    <div class="mt-3 d-flex gap-2">
                        <button class="btn btn-sm btn-outline-primary" onclick="loadSubscription()">
                            <i class="fas fa-sync me-1"></i>Refresh
                        </button>
                        <button class="btn btn-sm btn-outline-secondary" id="manageSubscriptionBtn">
                            <i class="fas fa-cog me-1"></i>Manage
                        </button>
                        ${isActive && !subscription.cancel_at_period_end ? `
                            <button class="btn btn-sm btn-outline-danger" id="cancelSubscriptionBtn">
                                <i class="fas fa-times me-1"></i>Cancel
                            </button>
                        ` : ''}
                    </div>

                    <div class="mt-3">
                        <small class="text-muted">
                            <i class="fas fa-info-circle me-1"></i>Auto-refreshes every minute
                        </small>
                    </div>
                </div>
            </div>
        `;

        setupEventListeners();
    }

    /**
     * Create subscription checkout session
     */
    function createSubscriptionCheckout() {
        if (!window.VARIOSYNC || !window.VARIOSYNC.isAuthenticated()) {
            showAuthRequired();
            return;
        }

        const token = window.VARIOSYNC.getToken();
        const user = window.VARIOSYNC.getUser();

        showMessage('Creating checkout session...', 'info');

        fetch(`${API_BASE}/create-subscription-checkout`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                email: user.email
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.checkout_url) {
                window.location.href = data.checkout_url;
            } else if (data.error) {
                showMessage(data.error, 'error');
            } else {
                showMessage('Unexpected response from server', 'error');
            }
        })
        .catch(error => {
            console.error('Error creating checkout:', error);
            showMessage('Failed to create checkout session: ' + error.message, 'error');
        });
    }

    /**
     * Confirm subscription cancellation
     */
    function confirmCancelSubscription() {
        if (window.VARIOSYNC && window.VARIOSYNC.confirm) {
            window.VARIOSYNC.confirm(
                'Are you sure you want to cancel your subscription? You will retain access until the end of your billing period.',
                function() {
                    cancelSubscription();
                }
            );
        } else {
            if (confirm('Are you sure you want to cancel your subscription?')) {
                cancelSubscription();
            }
        }
    }

    /**
     * Cancel subscription
     */
    function cancelSubscription() {
        if (!window.VARIOSYNC || !window.VARIOSYNC.isAuthenticated()) {
            showAuthRequired();
            return;
        }

        const token = window.VARIOSYNC.getToken();

        showMessage('Canceling subscription...', 'info');

        fetch(`${API_BASE}/cancel-subscription`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showMessage('Subscription canceled successfully', 'success');
                loadSubscription();
            } else {
                showMessage(data.error || 'Failed to cancel subscription', 'error');
            }
        })
        .catch(error => {
            console.error('Error canceling subscription:', error);
            showMessage('Failed to cancel subscription: ' + error.message, 'error');
        });
    }

    /**
     * Open Stripe Customer Portal
     */
    function openCustomerPortal() {
        if (!window.VARIOSYNC || !window.VARIOSYNC.isAuthenticated()) {
            showAuthRequired();
            return;
        }

        const token = window.VARIOSYNC.getToken();

        showMessage('Opening customer portal...', 'info');

        fetch(`${API_BASE}/customer-portal`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.portal_url) {
                window.location.href = data.portal_url;
            } else {
                showMessage(data.error || 'Failed to open customer portal', 'error');
            }
        })
        .catch(error => {
            console.error('Error opening portal:', error);
            showMessage('Failed to open customer portal: ' + error.message, 'error');
        });
    }

    /**
     * Check subscription status from URL parameters
     */
    function checkSubscriptionStatus() {
        const urlParams = new URLSearchParams(window.location.search);
        const sessionId = urlParams.get('session_id');
        const canceled = urlParams.get('canceled');

        if (sessionId) {
            // Subscription success
            showMessage('Subscription activated successfully!', 'success');
            setTimeout(() => {
                loadSubscription();
            }, 1000);

            // Clean URL
            window.history.replaceState({}, document.title, window.location.pathname);
        } else if (canceled === '1') {
            // Subscription canceled
            showMessage('Subscription checkout was canceled', 'warning');

            // Clean URL
            window.history.replaceState({}, document.title, window.location.pathname);
        }
    }

    /**
     * Format time elapsed
     */
    function formatTimeElapsed(seconds) {
        if (seconds < 60) {
            return `${Math.floor(seconds)} second${Math.floor(seconds) !== 1 ? 's' : ''} ago`;
        } else if (seconds < 3600) {
            const minutes = Math.floor(seconds / 60);
            return `${minutes} minute${minutes !== 1 ? 's' : ''} ago`;
        } else {
            const hours = Math.floor(seconds / 3600);
            return `${hours} hour${hours !== 1 ? 's' : ''} ago`;
        }
    }

    /**
     * Update time elapsed display
     */
    function updateTimeElapsed() {
        if (!lastSubscriptionUpdate) return;

        const elapsed = (Date.now() - lastSubscriptionUpdate) / 1000;
        const timeElapsedEl = document.getElementById('timeElapsed');
        if (timeElapsedEl) {
            timeElapsedEl.textContent = formatTimeElapsed(elapsed);
        }
    }

    /**
     * Start time elapsed updater
     */
    function startTimeElapsedUpdater() {
        if (updateInterval) {
            clearInterval(updateInterval);
        }
        updateInterval = setInterval(updateTimeElapsed, 1000);
    }

    /**
     * Stop time elapsed updater
     */
    function stopTimeElapsedUpdater() {
        if (updateInterval) {
            clearInterval(updateInterval);
            updateInterval = null;
        }
    }

    /**
     * Show message
     */
    function showMessage(message, type = 'info') {
        // Use VARIOSYNC toast if available
        if (window.VARIOSYNC && window.VARIOSYNC.showToast) {
            window.VARIOSYNC.showToast(message, type);
            return;
        }

        // Fallback to custom alert
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

        setTimeout(() => {
            alert.remove();
        }, 5000);
    }

    // Expose functions globally for onclick handlers
    window.loadSubscription = function() {
        loadSubscription(false);
    };

    window.createSubscriptionCheckout = createSubscriptionCheckout;
    window.cancelSubscription = confirmCancelSubscription;
    window.openCustomerPortal = openCustomerPortal;

})();
