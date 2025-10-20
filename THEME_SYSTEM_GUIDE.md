# REDLINE Theme System Guide

## Overview
The REDLINE web application now includes a comprehensive theme system that allows users to switch between different color schemes. All themes are designed to be color-blind friendly and accessible.

## Available Themes

### 1. Default Theme (`theme-default`)
- **Colors**: Blue-based color palette
- **Description**: Default color-blind friendly theme
- **Best for**: General use, professional environments
- **Accessibility**: Tested for all color vision types

### 2. High Contrast Theme (`theme-high-contrast`)
- **Colors**: High contrast black, white, and primary colors
- **Description**: High contrast theme for better visibility
- **Best for**: Users with visual impairments, low-light environments
- **Accessibility**: Maximum contrast ratios for better readability

### 3. Ocean Theme (`theme-ocean`)
- **Colors**: Ocean-inspired blues and teals
- **Description**: Ocean-inspired blue theme
- **Best for**: Users who prefer cool color tones
- **Accessibility**: Blue tones are distinguishable for all color vision types

### 4. Forest Theme (`theme-forest`)
- **Colors**: Nature-inspired greens and earth tones
- **Description**: Nature-inspired green theme
- **Best for**: Users who prefer natural, calming colors
- **Accessibility**: Green tones are distinct from red/orange for red-green colorblind users

### 5. Sunset Theme (`theme-sunset`)
- **Colors**: Warm sunset colors with oranges and reds
- **Description**: Warm sunset colors
- **Best for**: Users who prefer warm, energetic colors
- **Accessibility**: Orange tones are distinct from green for colorblind users

### 6. Monochrome Theme (`theme-monochrome`)
- **Colors**: Black, white, and grayscale tones
- **Description**: Black and white theme
- **Best for**: Users who prefer minimal, clean designs
- **Accessibility**: Works perfectly for all color vision types

### 7. Dark Theme (`theme-dark`)
- **Colors**: Dark backgrounds with light text
- **Description**: Dark mode theme
- **Best for**: Low-light environments, users who prefer dark interfaces
- **Accessibility**: High contrast between dark backgrounds and light text

## How to Use the Theme System

### Via Web Interface
1. Click the **Theme** button in the navigation bar
2. Select your preferred theme from the dropdown menu
3. The theme will be applied immediately
4. Your preference will be saved in browser localStorage

### Via API
```javascript
// Get available themes
fetch('/api/themes')
  .then(response => response.json())
  .then(data => console.log(data.themes));

// Set a theme
fetch('/api/theme', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({ theme: 'theme-ocean' })
})
  .then(response => response.json())
  .then(data => console.log(data.message));

// Get current theme
fetch('/api/theme')
  .then(response => response.json())
  .then(data => console.log(data.theme));
```

### Via JavaScript
```javascript
// Using the REDLINE global object
REDLINE.themeSystem.setTheme('theme-dark');

// Get current theme
const currentTheme = REDLINE.themeSystem.getCurrentTheme();

// Listen for theme changes
$(document).on('themeChanged', function(event, theme) {
  console.log('Theme changed to:', theme);
});
```

## Technical Implementation

### CSS Variables
Each theme defines CSS custom properties that override the default colors:

```css
.theme-ocean {
    --primary-color: #0369a1;
    --secondary-color: #64748b;
    --success-color: #0d9488;
    --warning-color: #f59e0b;
    --danger-color: #dc2626;
    --info-color: #0891b2;
    /* ... more variables */
}
```

### Theme Application
Themes are applied by adding CSS classes to the `<body>` element:
```html
<body class="theme-ocean">
```

### Local Storage
Theme preferences are automatically saved to browser localStorage:
```javascript
localStorage.setItem('redline-theme', 'theme-ocean');
```

## File Structure

```
redline/web/
├── static/
│   ├── css/
│   │   ├── main.css          # Main styles with theme variables
│   │   └── themes.css        # Theme definitions
│   └── js/
│       └── main.js           # Theme system JavaScript
├── templates/
│   └── base.html             # Base template with theme switcher
└── routes/
    └── api.py                # Theme API endpoints
```

## API Endpoints

### GET /api/themes
Returns all available themes with their metadata.

**Response:**
```json
{
  "themes": {
    "theme-default": {
      "name": "Default",
      "description": "Default color-blind friendly theme",
      "icon": "fas fa-circle",
      "color": "primary"
    }
  },
  "default": "theme-default"
}
```

### POST /api/theme
Sets the user's theme preference.

**Request:**
```json
{
  "theme": "theme-ocean"
}
```

**Response:**
```json
{
  "message": "Theme preference updated",
  "theme": "theme-ocean"
}
```

### GET /api/theme
Gets the current theme preference.

**Response:**
```json
{
  "theme": "theme-default"
}
```

## Accessibility Features

### Color-Blind Friendly Design
- All themes are tested for protanopia, deuteranopia, and tritanopia
- Colors are chosen to be distinguishable for all color vision types
- Never relies on color alone to convey information

### High Contrast Options
- High Contrast theme provides maximum contrast ratios
- Dark theme offers excellent contrast for low-light environments
- All themes meet WCAG AA compliance standards

### Consistent Color Usage
- Success actions always use the theme's success color
- Warning messages always use the theme's warning color
- Error states always use the theme's danger color
- Information always uses the theme's info color

## Browser Support

### Local Storage
- Modern browsers (Chrome, Firefox, Safari, Edge)
- IE11+ with polyfill support

### CSS Custom Properties
- Chrome 49+, Firefox 31+, Safari 9.1+, Edge 16+
- Graceful degradation for older browsers

## Future Enhancements

### Planned Features
- **Custom Themes**: Allow users to create their own color schemes
- **Theme Sharing**: Share custom themes with other users
- **System Integration**: Auto-detect system dark/light mode preference
- **Advanced Customization**: Fine-tune individual color values

### User Preferences
- **Per-User Themes**: Store themes in user accounts
- **Device Sync**: Sync theme preferences across devices
- **Time-Based Themes**: Automatically switch themes based on time of day

## Troubleshooting

### Theme Not Applying
1. Check browser console for JavaScript errors
2. Verify localStorage is enabled
3. Clear browser cache and reload

### Theme Not Persisting
1. Check if localStorage is available
2. Verify theme name is valid
3. Check browser privacy settings

### Performance Issues
1. Themes are lightweight and should not impact performance
2. If experiencing issues, try clearing browser cache
3. Check for conflicting CSS rules

## Contributing

### Adding New Themes
1. Add theme CSS class to `themes.css`
2. Define color variables for the theme
3. Add theme metadata to API endpoint
4. Test theme with color blindness simulators
5. Update documentation

### Testing Themes
1. Use color blindness simulators (Coblis, Color Oracle)
2. Test with different screen sizes and resolutions
3. Verify contrast ratios meet accessibility standards
4. Test theme switching functionality

## Resources

### Color Blindness Testing
- [Coblis Color Blindness Simulator](https://www.color-blindness.com/coblis-color-blindness-simulator/)
- [Color Oracle](https://colororacle.org/)
- [Chrome DevTools Accessibility](https://developers.google.com/web/tools/chrome-devtools/accessibility)

### Accessibility Guidelines
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [WebAIM Color Contrast Checker](https://webaim.org/resources/contrastchecker/)
- [Colour Blind Awareness](https://www.colourblindawareness.org/)

### CSS Custom Properties
- [MDN CSS Custom Properties](https://developer.mozilla.org/en-US/docs/Web/CSS/Using_CSS_custom_properties)
- [CSS Custom Properties Browser Support](https://caniuse.com/css-variables)
