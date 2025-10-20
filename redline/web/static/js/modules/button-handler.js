/**
 * Button Handler Module
 * Handles button interactions and state management
 */
class ButtonHandler {
    constructor(buttonId) {
        this.buttonId = buttonId;
        this.buttonElement = document.getElementById(buttonId);
        this.isEnabled = false;
        this.onClick = null;
        this.onStateChanged = null;
    }

    /**
     * Enable the button
     */
    enable() {
        if (this.buttonElement) {
            this.buttonElement.disabled = false;
            this.buttonElement.classList.remove('disabled');
            this.isEnabled = true;
            
            console.log(`ButtonHandler: Button ${this.buttonId} enabled`);
            
            if (this.onStateChanged) {
                this.onStateChanged(true);
            }
        }
    }

    /**
     * Disable the button
     */
    disable() {
        if (this.buttonElement) {
            this.buttonElement.disabled = true;
            this.buttonElement.classList.add('disabled');
            this.isEnabled = false;
            
            console.log(`ButtonHandler: Button ${this.buttonId} disabled`);
            
            if (this.onStateChanged) {
                this.onStateChanged(false);
            }
        }
    }

    /**
     * Set button text
     */
    setText(text) {
        if (this.buttonElement) {
            this.buttonElement.textContent = text;
        }
    }

    /**
     * Set button loading state
     */
    setLoading(loading, loadingText = 'Loading...') {
        if (this.buttonElement) {
            if (loading) {
                this.buttonElement.disabled = true;
                this.buttonElement.innerHTML = `<i class="fas fa-spinner fa-spin me-2"></i>${loadingText}`;
            } else {
                this.buttonElement.disabled = !this.isEnabled;
                this.buttonElement.innerHTML = this.getOriginalText();
            }
        }
    }

    /**
     * Get original button text
     */
    getOriginalText() {
        // Default text if not set
        return 'Load File';
    }

    /**
     * Check if button is enabled
     */
    isButtonEnabled() {
        return this.isEnabled;
    }

    /**
     * Set up click event handler
     */
    setupClickHandler() {
        if (!this.buttonElement) {
            console.error('ButtonHandler: Button element not found:', this.buttonId);
            return;
        }

        this.buttonElement.addEventListener('click', (event) => {
            event.preventDefault();
            
            if (!this.isEnabled) {
                console.log('ButtonHandler: Button clicked but disabled');
                return;
            }

            console.log(`ButtonHandler: Button ${this.buttonId} clicked`);
            
            if (this.onClick) {
                this.onClick(event);
            }
        });

        console.log(`ButtonHandler: Click handler set up for ${this.buttonId}`);
    }

    /**
     * Set click callback
     */
    setOnClick(callback) {
        this.onClick = callback;
    }

    /**
     * Set state change callback
     */
    setOnStateChanged(callback) {
        this.onStateChanged = callback;
    }

    /**
     * Simulate button click (for testing)
     */
    click() {
        if (this.buttonElement && this.isEnabled) {
            this.buttonElement.click();
        }
    }
}

// Export for use in other modules
window.ButtonHandler = ButtonHandler;
