# Grayscale Theme Guide

## Overview

The REDLINE Web Application now includes a **Grayscale Theme** option that provides a monochrome color scheme optimized for accessibility and professional presentation.

## Features

### 🎨 **Color Palette**
The grayscale theme uses a carefully selected palette of grays, whites, and subtle accent colors:

- **Primary Colors**: Muted grays (#4a5568, #718096)
- **Background**: Clean whites and light grays (#f7fafc)
- **Text**: High-contrast dark grays (#2d3748, #4a5568)
- **Accent Colors**: Subtle variations for success, warning, danger, and info states

### 🔧 **Font Colors**
The theme includes 12 customizable font color variables:

- `--text-primary`: Main text color (#2d3748)
- `--text-secondary`: Secondary text (#4a5568)
- `--text-muted`: Muted text (#718096)
- `--text-light`: Light text (#a0aec0)
- `--text-dark`: Dark text (#1a202c)
- `--text-white`: White text (#ffffff)
- `--text-success`: Success messages (#38a169)
- `--text-warning`: Warning messages (#d69e2e)
- `--text-danger`: Error messages (#e53e3e)
- `--text-info`: Info messages (#3182ce)
- `--text-link`: Link colors (#4a5568)
- `--text-link-hover`: Link hover (#2d3748)

## How to Use

### 1. **Access the Theme**
- Click the **Theme** dropdown in the navigation bar
- Select **Grayscale** from the available options
- The theme will be applied immediately

### 2. **Customize Font Colors**
- Click the floating palette button (🎨) in the bottom-right corner
- Select the **Grayscale** preset from the font color presets
- Or customize individual font colors using the color picker

### 3. **Persistent Settings**
- Theme and font color preferences are automatically saved
- Settings persist across browser sessions
- Changes apply to all pages in the application

## Benefits

### ♿ **Accessibility**
- High contrast ratios for better readability
- Reduced visual noise for users with visual sensitivities
- Compatible with screen readers and assistive technologies

### 💼 **Professional Use**
- Clean, professional appearance
- Suitable for presentations and reports
- Reduces eye strain during long work sessions

### 🖨️ **Print-Friendly**
- Optimized for black and white printing
- Clear distinction between different UI elements
- Maintains readability in grayscale

## Technical Details

### **CSS Implementation**
The grayscale theme is implemented using CSS custom properties (variables):

```css
.theme-grayscale {
    --primary-color: #4a5568;
    --secondary-color: #718096;
    /* ... additional color variables ... */
}
```

### **API Integration**
The theme is available through the font color presets API:

```javascript
GET /api/font-color-presets
```

Returns the grayscale preset along with all other available themes.

### **Theme Switching**
The theme can be switched dynamically using JavaScript:

```javascript
// Apply grayscale theme
document.body.className = 'theme-grayscale';
```

## Comparison with Other Themes

| Feature | Grayscale | Monochrome | High Contrast |
|---------|-----------|------------|---------------|
| Color Count | Limited | Very Limited | High Contrast |
| Professional Look | ✅ Excellent | ✅ Good | ⚠️ Bold |
| Accessibility | ✅ High | ✅ High | ✅ Very High |
| Print Friendly | ✅ Excellent | ✅ Good | ⚠️ Moderate |

## Browser Compatibility

The grayscale theme is compatible with all modern browsers that support:
- CSS Custom Properties (CSS Variables)
- Modern CSS Grid and Flexbox layouts
- JavaScript ES6+ features

## Support

For questions or issues with the grayscale theme:
1. Check the browser console for any JavaScript errors
2. Verify that CSS custom properties are supported
3. Clear browser cache if theme changes aren't applying
4. Contact support with specific error details

---

**Note**: The grayscale theme is designed to work seamlessly with all existing REDLINE features including data visualization, file conversion, and analysis tools.
