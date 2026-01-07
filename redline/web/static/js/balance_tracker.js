/**
 * VarioSync Global Subscription Tracker
 * Tracks and displays subscription status across all pages
 */

(function() {
    'use strict';

    // Configuration
    const API_BASE = '/payments';
    const REFRESH_INTERVAL = 60000; // 1 minute
    const CACHE_STORAGE = 'variosync_subscription_cache';
    const CACHE_TTL = 30000; // 30 seconds cache

    // State
    let refreshInterval = null;
    let lastUpdate = null;
    let updateInterval = null;
    let currentSubscription = null;

    /**
     * Check if user is authenticated
     */
    function isAuthenticated() {
        const token = localStorage.getItem('variosync_auth_token');
        return !!token;
    }

    /**
     * Get auth token
     */
    function getAuthToken() {
        return localStorage.getItem('variosync_auth_token');
    }

    /**
     * Format time elapsed since last update
     */
    function formatTimeElapsed(seconds) {
        if (seconds < 60) {
            return `${Math.floor(seconds)}s ago`;
        } else if (seconds < 3600) {
            const minutes = Math.floor(seconds / 60);
            return `${minutes}m ago`;
        } else {
            const hours = Math.floor(seconds / 3600);
            const minutes = Math.floor((seconds % 3600) / 60);
            return `${hours}h ${minutes > 0 ? minutes + 'm' : ''} ago`.trim();
        }
    }

    /**
     * Update subscription display in navbar
     */
    function updateSubscriptionDisplay(data, updateTimestamp = true) {
        if (!data) return;

        const subscription = data.subscription;
        const usage = data.usage;

        if (updateTimestamp) {
            lastUpdate = Date.now();
        } else if (!lastUpdate) {
            lastUpdate = Date.now();
        }

        // Determine status
        const status = subscription ? subscription.status : 'none';
        const isActive = ['active', 'trialing'].includes(status);

        let statusClass = 'text-muted';
        let statusIcon = 'fa-circle';
        let statusText = 'No Subscription';

        if (isActive) {
            statusClass = 'text-success';
            statusIcon = 'fa-check-circle';
            statusText = status === 'trialing' ? 'Trial Active' : 'Active';
        } else if (status === 'past_due') {
            statusClass = 'text-warning';
            statusIcon = 'fa-exclamation-circle';
            statusText = 'Past Due';
        } else if (status === 'canceled') {
            statusClass = 'text-danger';
            statusIcon = 'fa-times-circle';
            statusText = 'Canceled';
        }

        // Create navbar indicator (if container exists)
        const container = document.getElementById('subscriptionStatusIndicator');
        if (container) {
            const usageText = usage && usage.total_usage > 0
                ? `${usage.total_usage.toLocaleString()} records`
                : 'No usage';

            container.innerHTML = `
                <span class="navbar-text ${statusClass}" style="cursor: pointer;"
                      onclick="window.location.href='/payments/subscription'"
                      title="Click to manage subscription">
                    <i class="fas ${statusIcon} me-1"></i>${statusText}
                    <small class="d-none d-lg-inline ms-2 text-muted">(${usageText})</small>
                </span>
            `;
        }

        // Store in cache
        try {
            localStorage.setItem(CACHE_STORAGE, JSON.stringify({
                data: data,
                timestamp: Date.now()
            }));
        } catch (e) {
            console.warn('Failed to cache subscription data:', e);
        }

        // Start time elapsed updater
        startTimeElapsedUpdater();
    }

    /**
     * Load subscription status from cache
     */
    function loadFromCache() {
        try {
            const cached = localStorage.getItem(CACHE_STORAGE);
            if (!cached) return null;

            const { data, timestamp } = JSON.parse(cached);
            const age = Date.now() - timestamp;

            // Check if cache is still valid
            if (age < CACHE_TTL) {
                lastUpdate = timestamp;
                return data;
            }
        } catch (e) {
            console.warn('Failed to load subscription cache:', e);
        }
        return null;
    }

    /**
     * Load subscription status from API
     */
    function loadSubscription(silent = false) {
        if (!isAuthenticated()) {
            stopRefresh();
            return;
        }

        const token = getAuthToken();

        fetch(`${API_BASE}/balance`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        })
        .then(response => {
            if (response.status === 401) {
                // Unauthorized - clear auth and redirect
                localStorage.removeItem('variosync_auth_token');
                localStorage.removeItem('variosync_user_data');
                stopRefresh();
                return null;
            }
            return response.json();
        })
        .then(data => {
            if (data) {
                currentSubscription = data;
                updateSubscriptionDisplay(data, true);
            }
        })
        .catch(error => {
            if (!silent) {
                console.error('Error loading subscription:', error);
            }
        });
    }

    /**
     * Start automatic refresh
     */
    function startRefresh() {
        stopRefresh();

        if (isAuthenticated()) {
            refreshInterval = setInterval(function() {
                if (isAuthenticated()) {
                    loadSubscription(true); // Silent refresh
                } else {
                    stopRefresh();
                }
            }, REFRESH_INTERVAL);
        }
    }

    /**
     * Stop automatic refresh
     */
    function stopRefresh() {
        if (refreshInterval) {
            clearInterval(refreshInterval);
            refreshInterval = null;
        }
        stopTimeElapsedUpdater();
    }

    /**
     * Update time elapsed display
     */
    function updateTimeElapsed() {
        if (!lastUpdate) return;

        const elapsed = (Date.now() - lastUpdate) / 1000;
        const elements = document.querySelectorAll('.subscription-time-elapsed');

        elements.forEach(el => {
            el.textContent = formatTimeElapsed(elapsed);
        });
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
     * Initialize subscription tracker
     */
    function init() {
        if (!isAuthenticated()) {
            console.log('User not authenticated - subscription tracker disabled');
            return;
        }

        // Try loading from cache first
        const cached = loadFromCache();
        if (cached) {
            updateSubscriptionDisplay(cached, false);
        }

        // Load fresh data
        loadSubscription(false);

        // Start auto-refresh
        startRefresh();

        // Listen for auth changes
        window.addEventListener('authTokenUpdated', function(e) {
            if (e.detail && e.detail.token) {
                init();
            } else {
                stopRefresh();
            }
        });

        console.log('✅ Subscription tracker initialized');
    }

    // Initialize on page load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Cleanup on page unload
    window.addEventListener('beforeunload', function() {
        stopRefresh();
    });

    // Expose functions globally
    window.VARIOSYNC = window.VARIOSYNC || {};
    window.VARIOSYNC.subscriptionTracker = {
        refresh: function() { loadSubscription(false); },
        start: startRefresh,
        stop: stopRefresh
    };

})();
