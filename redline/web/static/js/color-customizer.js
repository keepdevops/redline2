/**
 * Font Color Customization System
 * Allows users to customize font colors throughout the application
 */

class ColorCustomizer {
    constructor() {
        this.isOpen = false;
        this.currentTheme = this.getCurrentTheme();
        this.customColors = {};
        this.presetSchemes = {
            'default': {
                'text-primary': '#1e293b',
                'text-secondary': '#64748b',
                'text-muted': '#94a3b8',
                'text-light': '#cbd5e1',
                'text-dark': '#0f172a',
                'text-white': '#ffffff',
                'text-success': '#059669',
                'text-warning': '#d97706',
                'text-danger': '#dc2626',
                'text-info': '#0891b2',
                'text-link': '#2563eb',
                'text-link-hover': '#1d4ed8'
            },
            'high-contrast': {
                'text-primary': '#000000',
                'text-secondary': '#404040',
                'text-muted': '#808080',
                'text-light': '#c0c0c0',
                'text-dark': '#000000',
                'text-white': '#ffffff',
                'text-success': '#008000',
                'text-warning': '#ff8000',
                'text-danger': '#ff0000',
                'text-info': '#0080ff',
                'text-link': '#0000ff',
                'text-link-hover': '#0000cc'
            },
            'ocean': {
                'text-primary': '#0f172a',
                'text-secondary': '#475569',
                'text-muted': '#64748b',
                'text-light': '#94a3b8',
                'text-dark': '#020617',
                'text-white': '#ffffff',
                'text-success': '#0d9488',
                'text-warning': '#f59e0b',
                'text-danger': '#dc2626',
                'text-info': '#0891b2',
                'text-link': '#0369a1',
                'text-link-hover': '#075985'
            },
            'forest': {
                'text-primary': '#14532d',
                'text-secondary': '#365314',
                'text-muted': '#4b5563',
                'text-light': '#9ca3af',
                'text-dark': '#052e16',
                'text-white': '#ffffff',
                'text-success': '#16a34a',
                'text-warning': '#ca8a04',
                'text-danger': '#dc2626',
                'text-info': '#0891b2',
                'text-link': '#166534',
                'text-link-hover': '#15803d'
            },
            'sunset': {
                'text-primary': '#431407',
                'text-secondary': '#9a3412',
                'text-muted': '#a16207',
                'text-light': '#d97706',
                'text-dark': '#292524',
                'text-white': '#ffffff',
                'text-success': '#16a34a',
                'text-warning': '#f59e0b',
                'text-danger': '#dc2626',
                'text-info': '#0891b2',
                'text-link': '#ea580c',
                'text-link-hover': '#c2410c'
            },
            'monochrome': {
                'text-primary': '#111827',
                'text-secondary': '#374151',
                'text-muted': '#6b7280',
                'text-light': '#9ca3af',
                'text-dark': '#000000',
                'text-white': '#ffffff',
                'text-success': '#059669',
                'text-warning': '#d97706',
                'text-danger': '#dc2626',
                'text-info': '#0891b2',
                'text-link': '#374151',
                'text-link-hover': '#1f2937'
            },
            'grayscale': {
                'text-primary': '#2d3748',
                'text-secondary': '#4a5568',
                'text-muted': '#718096',
                'text-light': '#a0aec0',
                'text-dark': '#1a202c',
                'text-white': '#ffffff',
                'text-success': '#38a169',
                'text-warning': '#d69e2e',
                'text-danger': '#e53e3e',
                'text-info': '#3182ce',
                'text-link': '#4a5568',
                'text-link-hover': '#2d3748'
            },
            'dark': {
                'text-primary': '#f9fafb',
                'text-secondary': '#d1d5db',
                'text-muted': '#9ca3af',
                'text-light': '#6b7280',
                'text-dark': '#ffffff',
                'text-white': '#ffffff',
                'text-success': '#10b981',
                'text-warning': '#f59e0b',
                'text-danger': '#ef4444',
                'text-info': '#06b6d4',
                'text-link': '#3b82f6',
                'text-link-hover': '#2563eb'
            }
        };
        
        this.init();
    }
    
    init() {
        this.createToggleButton();
        this.createCustomizerInterface();
        this.loadSavedColors();
        this.bindEvents();
        this.listenForThemeChanges();
    }
    
    getCurrentTheme() {
        // Get current theme from body class or localStorage
        const bodyTheme = document.body.className.match(/theme-\w+/);
        if (bodyTheme) {
            return bodyTheme[0];
        }
        return localStorage.getItem('redline-theme') || 'theme-default';
    }
    
    listenForThemeChanges() {
        // Listen for theme change events
        $(document).on('themeChanged', (event, theme) => {
            const previousTheme = this.currentTheme;
            this.currentTheme = theme;
            // Clear saved colors when theme changes (user wants theme colors, not custom)
            this.updateColorsForTheme(theme, true);
        });
        
        // Also listen for direct theme class changes on body
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'attributes' && mutation.attributeName === 'class') {
                    const newTheme = this.getCurrentTheme();
                    if (newTheme !== this.currentTheme) {
                        const previousTheme = this.currentTheme;
                        this.currentTheme = newTheme;
                        // Clear saved colors when theme changes (user wants theme colors, not custom)
                        this.updateColorsForTheme(newTheme, true);
                    }
                }
            });
        });
        
        observer.observe(document.body, {
            attributes: true,
            attributeFilter: ['class']
        });
    }
    
    updateColorsForTheme(theme, clearSaved = false) {
        // Map theme class to preset name
        const themeToPreset = {
            'theme-default': 'default',
            'theme-high-contrast': 'high-contrast',
            'theme-ocean': 'ocean',
            'theme-forest': 'forest',
            'theme-sunset': 'sunset',
            'theme-monochrome': 'monochrome',
            'theme-grayscale': 'grayscale',
            'theme-dark': 'dark'
        };
        
        const presetName = themeToPreset[theme] || 'default';
        
        // Clear custom color overrides to let theme colors show
        this.clearCustomOverrides();
        
        // If theme changed (not initial load), clear saved custom colors
        if (clearSaved) {
            localStorage.removeItem('redline-custom-font-colors');
            this.customColors = {};
        }
        
        // Update color picker inputs to show theme defaults
        const presetColors = this.presetSchemes[presetName];
        if (presetColors && this.customizer) {
            Object.keys(presetColors).forEach(colorVar => {
                const input = this.customizer.querySelector(`[data-color="${colorVar}"]`);
                if (input) {
                    input.value = presetColors[colorVar];
                    this.updateColorPreview(input);
                }
            });
            
            // Update active preset indicator
            this.customizer.querySelectorAll('.preset-color').forEach(preset => {
                preset.classList.remove('active');
            });
            const activePreset = this.customizer.querySelector(`[data-preset="${presetName}"]`);
            if (activePreset) {
                activePreset.classList.add('active');
            }
        }
    }
    
    clearCustomOverrides() {
        // Remove inline style overrides from documentElement to let theme CSS variables take precedence
        const colorVars = [
            'text-primary', 'text-secondary', 'text-muted', 'text-light', 
            'text-dark', 'text-white', 'text-success', 'text-warning', 
            'text-danger', 'text-info', 'text-link', 'text-link-hover'
        ];
        
        colorVars.forEach(colorVar => {
            document.documentElement.style.removeProperty(`--${colorVar}`);
        });
        
        // Clear custom colors object
        this.customColors = {};
    }
    
    createToggleButton() {
        const toggleBtn = document.createElement('button');
        toggleBtn.className = 'color-picker-toggle';
        toggleBtn.innerHTML = '<i class="fas fa-palette"></i>';
        toggleBtn.title = 'Customize Font Colors';
        toggleBtn.addEventListener('click', () => this.toggleCustomizer());
        document.body.appendChild(toggleBtn);
        this.toggleButton = toggleBtn;
    }
    
    createCustomizerInterface() {
        const customizer = document.createElement('div');
        customizer.className = 'color-customizer';
        customizer.innerHTML = `
            <div class="color-customizer-header">
                <h4 class="color-customizer-title">Font Color Customizer</h4>
                <button class="color-customizer-close">&times;</button>
            </div>
            
            <div class="color-group">
                <label class="color-group-title">Text Colors</label>
                
                <div class="color-input-group">
                    <label class="color-input-label">Primary:</label>
                    <input type="color" class="color-input" data-color="text-primary" value="#1e293b">
                    <span class="color-preview" style="background-color: #1e293b"></span>
                </div>
                
                <div class="color-input-group">
                    <label class="color-input-label">Secondary:</label>
                    <input type="color" class="color-input" data-color="text-secondary" value="#64748b">
                    <span class="color-preview" style="background-color: #64748b"></span>
                </div>
                
                <div class="color-input-group">
                    <label class="color-input-label">Muted:</label>
                    <input type="color" class="color-input" data-color="text-muted" value="#94a3b8">
                    <span class="color-preview" style="background-color: #94a3b8"></span>
                </div>
                
                <div class="color-input-group">
                    <label class="color-input-label">Light:</label>
                    <input type="color" class="color-input" data-color="text-light" value="#cbd5e1">
                    <span class="color-preview" style="background-color: #cbd5e1"></span>
                </div>
                
                <div class="color-input-group">
                    <label class="color-input-label">Dark:</label>
                    <input type="color" class="color-input" data-color="text-dark" value="#0f172a">
                    <span class="color-preview" style="background-color: #0f172a"></span>
                </div>
            </div>
            
            <div class="color-group">
                <label class="color-group-title">Status Colors</label>
                
                <div class="color-input-group">
                    <label class="color-input-label">Success:</label>
                    <input type="color" class="color-input" data-color="text-success" value="#059669">
                    <span class="color-preview" style="background-color: #059669"></span>
                </div>
                
                <div class="color-input-group">
                    <label class="color-input-label">Warning:</label>
                    <input type="color" class="color-input" data-color="text-warning" value="#d97706">
                    <span class="color-preview" style="background-color: #d97706"></span>
                </div>
                
                <div class="color-input-group">
                    <label class="color-input-label">Danger:</label>
                    <input type="color" class="color-input" data-color="text-danger" value="#dc2626">
                    <span class="color-preview" style="background-color: #dc2626"></span>
                </div>
                
                <div class="color-input-group">
                    <label class="color-input-label">Info:</label>
                    <input type="color" class="color-input" data-color="text-info" value="#0891b2">
                    <span class="color-preview" style="background-color: #0891b2"></span>
                </div>
            </div>
            
            <div class="color-group">
                <label class="color-group-title">Link Colors</label>
                
                <div class="color-input-group">
                    <label class="color-input-label">Link:</label>
                    <input type="color" class="color-input" data-color="text-link" value="#2563eb">
                    <span class="color-preview" style="background-color: #2563eb"></span>
                </div>
                
                <div class="color-input-group">
                    <label class="color-input-label">Hover:</label>
                    <input type="color" class="color-input" data-color="text-link-hover" value="#1d4ed8">
                    <span class="color-preview" style="background-color: #1d4ed8"></span>
                </div>
            </div>
            
            <div class="color-group">
                <label class="color-group-title">Preset Schemes</label>
                <div class="preset-colors">
                    <div class="preset-color active" data-preset="default" style="background: linear-gradient(45deg, #1e293b 0%, #64748b 50%, #94a3b8 100%)" title="Default">
                        <span class="preset-color-label">Default</span>
                    </div>
                    <div class="preset-color" data-preset="high-contrast" style="background: linear-gradient(45deg, #000000 0%, #404040 50%, #808080 100%)" title="High Contrast">
                        <span class="preset-color-label">High Contrast</span>
                    </div>
                    <div class="preset-color" data-preset="ocean" style="background: linear-gradient(45deg, #0f172a 0%, #475569 50%, #64748b 100%)" title="Ocean">
                        <span class="preset-color-label">Ocean</span>
                    </div>
                    <div class="preset-color" data-preset="forest" style="background: linear-gradient(45deg, #14532d 0%, #365314 50%, #4b5563 100%)" title="Forest">
                        <span class="preset-color-label">Forest</span>
                    </div>
                    <div class="preset-color" data-preset="sunset" style="background: linear-gradient(45deg, #431407 0%, #9a3412 50%, #a16207 100%)" title="Sunset">
                        <span class="preset-color-label">Sunset</span>
                    </div>
                    <div class="preset-color" data-preset="monochrome" style="background: linear-gradient(45deg, #111827 0%, #374151 50%, #6b7280 100%)" title="Monochrome">
                        <span class="preset-color-label">Monochrome</span>
                    </div>
                    <div class="preset-color" data-preset="grayscale" style="background: linear-gradient(45deg, #2d3748 0%, #4a5568 50%, #718096 100%)" title="Grayscale">
                        <span class="preset-color-label">Grayscale</span>
                    </div>
                    <div class="preset-color" data-preset="dark" style="background: linear-gradient(45deg, #f9fafb 0%, #d1d5db 50%, #9ca3af 100%)" title="Dark">
                        <span class="preset-color-label">Dark</span>
                    </div>
                </div>
            </div>
            
            <div class="color-customizer-actions">
                <button class="color-customizer-btn" id="resetColors">Reset</button>
                <button class="color-customizer-btn primary" id="applyColors">Apply</button>
            </div>
        `;
        
        document.body.appendChild(customizer);
        this.customizer = customizer;
    }
    
    bindEvents() {
        // Close button
        this.customizer.querySelector('.color-customizer-close').addEventListener('click', () => {
            this.closeCustomizer();
        });
        
        // Color input changes
        this.customizer.querySelectorAll('.color-input').forEach(input => {
            input.addEventListener('input', (e) => {
                this.updateColorPreview(e.target);
                this.applyColorChange(e.target.dataset.color, e.target.value);
            });
        });
        
        // Preset color schemes
        this.customizer.querySelectorAll('.preset-color').forEach(preset => {
            preset.addEventListener('click', (e) => {
                this.selectPreset(e.target.dataset.preset);
            });
        });
        
        // Action buttons
        this.customizer.querySelector('#resetColors').addEventListener('click', () => {
            this.resetToDefault();
        });
        
        this.customizer.querySelector('#applyColors').addEventListener('click', () => {
            this.saveColors();
        });
        
        // Click outside to close
        document.addEventListener('click', (e) => {
            if (this.isOpen && !this.customizer.contains(e.target) && !this.toggleButton.contains(e.target)) {
                this.closeCustomizer();
            }
        });
    }
    
    toggleCustomizer() {
        if (this.isOpen) {
            this.closeCustomizer();
        } else {
            this.openCustomizer();
        }
    }
    
    openCustomizer() {
        this.customizer.classList.add('show');
        this.toggleButton.classList.add('active');
        this.isOpen = true;
    }
    
    closeCustomizer() {
        this.customizer.classList.remove('show');
        this.toggleButton.classList.remove('active');
        this.isOpen = false;
    }
    
    updateColorPreview(input) {
        const preview = input.parentNode.querySelector('.color-preview');
        if (preview) {
            preview.style.backgroundColor = input.value;
        }
    }
    
    applyColorChange(colorVar, value) {
        document.documentElement.style.setProperty(`--${colorVar}`, value);
        this.customColors[colorVar] = value;
    }
    
    selectPreset(presetName) {
        // Update active preset
        this.customizer.querySelectorAll('.preset-color').forEach(preset => {
            preset.classList.remove('active');
        });
        const activePreset = this.customizer.querySelector(`[data-preset="${presetName}"]`);
        if (activePreset) {
            activePreset.classList.add('active');
        }
        
        // Clear any existing custom overrides first
        this.clearCustomOverrides();
        
        // Apply preset colors
        const presetColors = this.presetSchemes[presetName];
        Object.keys(presetColors).forEach(colorVar => {
            const input = this.customizer.querySelector(`[data-color="${colorVar}"]`);
            if (input) {
                input.value = presetColors[colorVar];
                this.updateColorPreview(input);
                // Don't apply as custom override - let theme handle it
                // Only apply if user manually changes a color
            }
        });
        
        // Store preset colors but don't apply as overrides
        this.customColors = {};
    }
    
    resetToDefault() {
        // Reset to current theme's default colors
        const currentTheme = this.getCurrentTheme();
        this.updateColorsForTheme(currentTheme);
        // Clear saved custom colors
        localStorage.removeItem('redline-custom-font-colors');
        this.showNotification('Font colors reset to theme defaults', 'success');
    }
    
    saveColors() {
        localStorage.setItem('redline-custom-font-colors', JSON.stringify(this.customColors));
        this.showNotification('Font colors saved successfully!', 'success');
    }
    
    loadSavedColors() {
        // First, set colors to match current theme (don't clear saved colors on initial load)
        const currentTheme = this.getCurrentTheme();
        this.updateColorsForTheme(currentTheme, false);
        
        // Then, if user has custom colors saved, apply them (but only if they explicitly saved them)
        const savedColors = localStorage.getItem('redline-custom-font-colors');
        if (savedColors) {
            try {
                const parsedColors = JSON.parse(savedColors);
                // Only apply if user explicitly saved custom colors (not just theme defaults)
                const hasCustomColors = Object.keys(parsedColors).length > 0;
                if (hasCustomColors) {
                    this.customColors = parsedColors;
                    Object.keys(this.customColors).forEach(colorVar => {
                        const input = this.customizer.querySelector(`[data-color="${colorVar}"]`);
                        if (input) {
                            input.value = this.customColors[colorVar];
                            this.updateColorPreview(input);
                            this.applyColorChange(colorVar, this.customColors[colorVar]);
                        }
                    });
                }
            } catch (e) {
                console.warn('Failed to load saved font colors:', e);
            }
        }
    }
    
    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show`;
        notification.style.position = 'fixed';
        notification.style.top = '20px';
        notification.style.right = '20px';
        notification.style.zIndex = '1060';
        notification.style.minWidth = '300px';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 3 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 3000);
    }
}

// Initialize color customizer when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.colorCustomizer = new ColorCustomizer();
});

// Export for use in other scripts
window.ColorCustomizer = ColorCustomizer;
