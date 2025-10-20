# Load Button Debug Guide 🔍

## 🎯 **Issue to Debug**

The "Load File" button in the Data tab is not working - nothing loads when clicked.

## 🔧 **Debugging Steps Added**

I've added debugging alerts to help identify the issue:

### **1. Added Alert to loadFileList Function**
```javascript
function loadFileList() {
    console.log('loadFileList called - starting AJAX request to /data/files');
    alert('loadFileList function called');  // ← NEW DEBUG ALERT
    // ... rest of function
}
```

### **2. Added Alert to loadData Function**
```javascript
function loadData(filename) {
    console.log('Loading data for file:', filename);
    alert('loadData function called with filename: ' + filename);  // ← NEW DEBUG ALERT
    // ... rest of function
}
```

## 🧪 **Testing Instructions**

### **Step 1: Test Page Load**
1. Go to http://localhost:8082/data/
2. **Expected**: You should see an alert "loadFileList function called"
3. **If you see this alert**: The JavaScript is executing correctly
4. **If you don't see this alert**: There's a JavaScript error preventing execution

### **Step 2: Test File Selection**
1. After the page loads, check if the dropdown has files
2. **Expected**: Dropdown should contain 37 files
3. **If dropdown is empty**: The loadFileList function isn't working
4. **If dropdown has files**: The file loading is working

### **Step 3: Test Load Button**
1. Select a file from the dropdown
2. Click the "Load File" button
3. **Expected**: You should see an alert "loadData function called with filename: [filename]"
4. **If you see this alert**: The button click is working, issue is in the data loading
5. **If you don't see this alert**: The button click event isn't working

## 🔍 **Possible Issues and Solutions**

### **Issue 1: No Alert on Page Load**
- **Problem**: JavaScript not executing
- **Solution**: Check browser console for errors
- **Likely Cause**: Syntax error or missing function

### **Issue 2: Alert on Page Load, But Empty Dropdown**
- **Problem**: loadFileList function executing but API call failing
- **Solution**: Check network tab in browser dev tools
- **Likely Cause**: API endpoint not responding

### **Issue 3: Files in Dropdown, But No Alert on Button Click**
- **Problem**: Button click event not attached
- **Solution**: Check if button is disabled
- **Likely Cause**: Event handler not properly attached

### **Issue 4: Alert on Button Click, But No Data Loading**
- **Problem**: loadData function executing but API call failing
- **Solution**: Check network tab for failed requests
- **Likely Cause**: API endpoint error or data processing issue

## 🚀 **Quick Test**

**Open the debug page**: `debug_data_tab.html` in your browser to test the functionality in isolation.

## 📋 **What to Report**

Please test the Data tab and report:

1. **Do you see the "loadFileList function called" alert when the page loads?**
2. **Does the dropdown contain files?**
3. **Do you see the "loadData function called" alert when clicking Load File?**
4. **Any error messages in the browser console?**

This will help identify exactly where the issue is occurring.
