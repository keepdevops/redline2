#!/bin/bash
# Windows Installer Package Creator
# Creates Windows installer packages for USB distribution

set -e

echo "🪟 Creating Windows Installer Packages..."

# Get project root and version
PROJECT_ROOT=$(cd "$(dirname "$0")" && pwd)
cd "$PROJECT_ROOT"

VERSION=$(python -c "import sys; sys.path.insert(0, '.'); from redline.__version__ import __version__; print(__version__)")
PACKAGE_NAME="REDLINE-${VERSION}-Windows"
PACKAGE_DIR="dist/windows-package"

# Clean and create package directory
echo "📦 Creating Windows package directory..."
rm -rf "$PACKAGE_DIR"
mkdir -p "$PACKAGE_DIR"

# Create package structure
mkdir -p "$PACKAGE_DIR/NSIS"
mkdir -p "$PACKAGE_DIR/MSI"
mkdir -p "$PACKAGE_DIR/Executables"
mkdir -p "$PACKAGE_DIR/Scripts"

echo "✅ Package structure created"

# Copy Windows executables
echo "🪟 Copying Windows executables..."
if [[ -f "dist/executables/redline-gui-windows-x64.exe" ]] && [[ -f "dist/executables/redline-web-windows-x64.exe" ]]; then
    cp dist/executables/redline-gui-windows-x64.exe "$PACKAGE_DIR/Executables/"
    cp dist/executables/redline-web-windows-x64.exe "$PACKAGE_DIR/Executables/"
    echo "✅ Windows x64 executables copied"
else
    echo "⚠️ Windows x64 executables not found, skipping..."
fi

if [[ -f "dist/executables/redline-gui-windows-arm64.exe" ]] && [[ -f "dist/executables/redline-web-windows-arm64.exe" ]]; then
    cp dist/executables/redline-gui-windows-arm64.exe "$PACKAGE_DIR/Executables/"
    cp dist/executables/redline-web-windows-arm64.exe "$PACKAGE_DIR/Executables/"
    echo "✅ Windows ARM64 executables copied"
else
    echo "⚠️ Windows ARM64 executables not found, skipping..."
fi

# Create NSIS installer script
echo "📝 Creating NSIS installer script..."
cat > "$PACKAGE_DIR/NSIS/redline.nsi" << 'EOF'
; REDLINE Windows Installer Script
; NSIS (Nullsoft Scriptable Install System)

!define APPNAME "REDLINE"
!define COMPANYNAME "REDLINE Development Team"
!define DESCRIPTION "Professional Financial Data Analysis Platform"
!define VERSIONMAJOR 1
!define VERSIONMINOR 0
!define VERSIONBUILD 0
!define HELPURL "https://github.com/keepdevops/redline2"
!define UPDATEURL "https://github.com/keepdevops/redline2/releases"
!define ABOUTURL "https://github.com/keepdevops/redline2"
!define INSTALLSIZE 500000

RequestExecutionLevel admin
InstallDir "$PROGRAMFILES64\${APPNAME}"
Name "${APPNAME}"
outFile "REDLINE-${VERSION}-Setup.exe"

!include LogicLib.nsh
!include x64.nsh
!include WinVer.nsh

; Architecture detection function
Function .onInit
  ; Check if running on ARM64
  System::Call "kernel32::GetCurrentProcess() i .r0"
  System::Call "kernel32::IsWow64Process(i r0, *i .r1)"
  ${If} $1 == 1
    ; Running under WOW64, check if it's ARM64
    System::Call "kernel32::GetNativeSystemInfo(*i .r0)"
    ${If} $0 == 9  ; PROCESSOR_ARCHITECTURE_ARM64
      StrCpy $R0 "arm64"
    ${Else}
      StrCpy $R0 "x64"
    ${EndIf}
  ${Else}
    ; Not running under WOW64, check architecture
    ${If} ${RunningX64}
      StrCpy $R0 "x64"
    ${Else}
      StrCpy $R0 "x86"
    ${EndIf}
  ${EndIf}
  
  ; Set architecture-specific install directory
  ${If} $R0 == "arm64"
    StrCpy $INSTDIR "$PROGRAMFILES64\REDLINE"
  ${ElseIf} $R0 == "x64"
    StrCpy $INSTDIR "$PROGRAMFILES64\REDLINE"
  ${Else}
    StrCpy $INSTDIR "$PROGRAMFILES\REDLINE"
  ${EndIf}
FunctionEnd

page directory
page instfiles

section "Main Application" SEC01
  SetOutPath "$INSTDIR"
  SetOverwrite ifnewer
  
  ; Copy executables based on architecture
  ${If} $R0 == "arm64"
    ; ARM64 executables
    File "Executables\redline-gui-windows-arm64.exe"
    File "Executables\redline-web-windows-arm64.exe"
    
    ; Rename executables
    Rename "$INSTDIR\redline-gui-windows-arm64.exe" "$INSTDIR\redline-gui.exe"
    Rename "$INSTDIR\redline-web-windows-arm64.exe" "$INSTDIR\redline-web.exe"
  ${ElseIf} $R0 == "x64"
    ; x64 executables
    File "Executables\redline-gui-windows-x64.exe"
    File "Executables\redline-web-windows-x64.exe"
    
    ; Rename executables
    Rename "$INSTDIR\redline-gui-windows-x64.exe" "$INSTDIR\redline-gui.exe"
    Rename "$INSTDIR\redline-web-windows-x64.exe" "$INSTDIR\redline-web.exe"
  ${Else}
    ; x86 executables (fallback)
    File "Executables\redline-gui-windows-x64.exe"
    File "Executables\redline-web-windows-x64.exe"
    
    ; Rename executables
    Rename "$INSTDIR\redline-gui-windows-x64.exe" "$INSTDIR\redline-gui.exe"
    Rename "$INSTDIR\redline-web-windows-x64.exe" "$INSTDIR\redline-web.exe"
  ${EndIf}
  
  ; Create desktop shortcuts
  CreateShortCut "$DESKTOP\REDLINE.lnk" "$INSTDIR\redline-gui.exe"
  CreateShortCut "$DESKTOP\REDLINE Web.lnk" "$INSTDIR\redline-web.exe"
  
  ; Create Start Menu shortcuts
  CreateDirectory "$SMPROGRAMS\${APPNAME}"
  CreateShortCut "$SMPROGRAMS\${APPNAME}\REDLINE.lnk" "$INSTDIR\redline-gui.exe"
  CreateShortCut "$SMPROGRAMS\${APPNAME}\REDLINE Web.lnk" "$INSTDIR\redline-web.exe"
  CreateShortCut "$SMPROGRAMS\${APPNAME}\Uninstall.lnk" "$INSTDIR\uninstall.exe"
  
  ; Write uninstaller
  WriteUninstaller "$INSTDIR\uninstall.exe"
  
  ; Write registry keys
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayName" "${APPNAME}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "UninstallString" "$INSTDIR\uninstall.exe"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "InstallLocation" "$INSTDIR"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayIcon" "$INSTDIR\redline-gui.exe"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "Publisher" "${COMPANYNAME}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "HelpLink" "${HELPURL}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "URLUpdateInfo" "${UPDATEURL}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "URLInfoAbout" "${ABOUTURL}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayVersion" "${VERSIONMAJOR}.${VERSIONMINOR}.${VERSIONBUILD}"
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "VersionMajor" ${VERSIONMAJOR}
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "VersionMinor" ${VERSIONMINOR}
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "NoRepair" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\Windows\CurrentVersion\Uninstall\${APPNAME}" "EstimatedSize" ${INSTALLSIZE}
sectionEnd

section "Uninstall"
  ; Remove files
  Delete "$INSTDIR\redline-gui.exe"
  Delete "$INSTDIR\redline-web.exe"
  Delete "$INSTDIR\uninstall.exe"
  
  ; Remove shortcuts
  Delete "$DESKTOP\REDLINE.lnk"
  Delete "$DESKTOP\REDLINE Web.lnk"
  Delete "$SMPROGRAMS\${APPNAME}\REDLINE.lnk"
  Delete "$SMPROGRAMS\${APPNAME}\REDLINE Web.lnk"
  Delete "$SMPROGRAMS\${APPNAME}\Uninstall.lnk"
  RMDir "$SMPROGRAMS\${APPNAME}"
  
  ; Remove registry keys
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}"
  
  ; Remove installation directory
  RMDir "$INSTDIR"
sectionEnd
EOF

# Create MSI installer script (WiX format)
echo "📝 Creating MSI installer script..."
cat > "$PACKAGE_DIR/MSI/redline.wxs" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<Wix xmlns="http://schemas.microsoft.com/wix/2006/wi">
  <Product Id="*" Name="REDLINE" Language="1033" Version="1.0.0" Manufacturer="REDLINE Development Team" UpgradeCode="PUT-GUID-HERE">
    <Package InstallerVersion="200" Compressed="yes" InstallScope="perMachine" />
    
    <MajorUpgrade DowngradeErrorMessage="A newer version of [ProductName] is already installed." />
    <MediaTemplate />
    
    <Feature Id="ProductFeature" Title="REDLINE" Level="1">
      <ComponentGroupRef Id="ProductComponents" />
    </Feature>
    
    <Directory Id="TARGETDIR" Name="SourceDir">
      <Directory Id="ProgramFiles64Folder">
        <Directory Id="INSTALLFOLDER" Name="REDLINE" />
      </Directory>
      <Directory Id="ProgramMenuFolder">
        <Directory Id="ApplicationProgramsFolder" Name="REDLINE"/>
      </Directory>
      <Directory Id="DesktopFolder" Name="Desktop"/>
    </Directory>
    
    <ComponentGroup Id="ProductComponents" Directory="INSTALLFOLDER">
      <Component Id="MainExecutable" Guid="*">
        <File Id="redline-gui.exe" Name="redline-gui.exe" Source="Executables\redline-gui-windows-x64.exe" KeyPath="yes" />
        <File Id="redline-web.exe" Name="redline-web.exe" Source="Executables\redline-web-windows-x64.exe" />
      </Component>
    </ComponentGroup>
    
    <DirectoryRef Id="ApplicationProgramsFolder">
      <Component Id="ApplicationShortcut" Guid="*">
        <Shortcut Id="ApplicationStartMenuShortcut" Directory="ApplicationProgramsFolder" WorkingDirectory="INSTALLFOLDER" Icon="redline-gui.exe" IconIndex="0" Advertise="yes" />
        <RemoveFolder Id="ApplicationProgramsFolder" On="uninstall" />
        <RegistryValue Root="HKCU" Key="Software\REDLINE" Name="installed" Type="integer" Value="1" KeyPath="yes" />
      </Component>
    </DirectoryRef>
    
    <DirectoryRef Id="DesktopFolder">
      <Component Id="DesktopShortcut" Guid="*">
        <Shortcut Id="DesktopShortcut" Directory="DesktopFolder" WorkingDirectory="INSTALLFOLDER" Icon="redline-gui.exe" IconIndex="0" Advertise="yes" />
        <RemoveFolder Id="DesktopFolder" On="uninstall" />
        <RegistryValue Root="HKCU" Key="Software\REDLINE" Name="installed" Type="integer" Value="1" KeyPath="yes" />
      </Component>
    </DirectoryRef>
  </Product>
</Wix>
EOF

# Create installation instructions
echo "📝 Creating installation instructions..."
cat > "$PACKAGE_DIR/INSTALL.txt" << EOF
REDLINE Windows Installation Instructions
========================================

Version: ${VERSION}
Date: $(date)

OVERVIEW:
REDLINE is a professional financial data analysis platform with both
desktop GUI and web-based interfaces.

INSTALLATION OPTIONS:

1. NSIS INSTALLER (Recommended):
   - File: REDLINE-${VERSION}-Setup.exe
   - Auto-detects system architecture (x64/ARM64)
   - Creates desktop and Start Menu shortcuts
   - Includes uninstaller
   - Requires: Windows 10 or later

2. MSI PACKAGE:
   - File: REDLINE-${VERSION}.msi
   - Enterprise deployment friendly
   - Group Policy compatible
   - Requires: Windows 10 or later

3. MANUAL INSTALLATION:
   - Copy executables from Executables/ folder
   - Run redline-gui.exe for desktop interface
   - Run redline-web.exe for web interface

ARCHITECTURE SUPPORT:
- x64 (Intel/AMD): Primary support
- ARM64 (Qualcomm/Apple): Full support
- Auto-detection: Installer automatically selects correct version

SYSTEM REQUIREMENTS:
- Windows 10 or later
- 4GB RAM minimum
- 500MB free disk space
- Internet connection for web interface

FEATURES:
- REDLINE GUI: Desktop application with full functionality
- REDLINE Web: Web-based interface (runs on localhost:8080)
- Multi-architecture support
- Professional financial analysis tools

INSTALLATION STEPS:

For NSIS Installer:
1. Right-click REDLINE-${VERSION}-Setup.exe
2. Select "Run as administrator"
3. Follow the installation wizard
4. Launch from desktop shortcut or Start Menu

For MSI Package:
1. Right-click REDLINE-${VERSION}.msi
2. Select "Install"
3. Follow the installation wizard
4. Launch from Start Menu

For Manual Installation:
1. Copy redline-gui.exe and redline-web.exe to desired folder
2. Run redline-gui.exe for desktop interface
3. Run redline-web.exe for web interface
4. Visit http://localhost:8080 for web interface

TROUBLESHOOTING:
- If installer fails, try running as administrator
- Check Windows Defender for blocked files
- Ensure sufficient disk space (500MB minimum)
- For web interface, check firewall settings

UNINSTALLATION:
- Use "Add or Remove Programs" in Windows Settings
- Or run uninstall.exe from installation directory
- Or use Start Menu uninstall shortcut

SUPPORT:
- GitHub: https://github.com/keepdevops/redline2
- Issues: https://github.com/keepdevops/redline2/issues
- Documentation: See Documentation/ folder

SECURITY:
- All security vulnerabilities have been fixed
- No hardcoded secrets or passwords
- Environment variable configuration
- Secure API key management

Thank you for using REDLINE!
EOF

# Create build scripts
echo "📝 Creating build scripts..."

# NSIS build script
cat > "$PACKAGE_DIR/Scripts/build_nsis.bat" << 'EOF'
@echo off
echo Building REDLINE NSIS Installer...

REM Check if NSIS is installed
where makensis >nul 2>nul
if %errorlevel% neq 0 (
    echo NSIS is not installed or not in PATH
    echo Please install NSIS from https://nsis.sourceforge.io/
    pause
    exit /b 1
)

REM Build the installer
makensis NSIS\redline.nsi

if %errorlevel% equ 0 (
    echo NSIS installer built successfully!
    echo Output: REDLINE-1.0.0-Setup.exe
) else (
    echo NSIS build failed!
    pause
    exit /b 1
)

pause
EOF

# MSI build script
cat > "$PACKAGE_DIR/Scripts/build_msi.bat" << 'EOF'
@echo off
echo Building REDLINE MSI Package...

REM Check if WiX Toolset is installed
where candle >nul 2>nul
if %errorlevel% neq 0 (
    echo WiX Toolset is not installed or not in PATH
    echo Please install WiX Toolset from https://wixtoolset.org/
    pause
    exit /b 1
)

REM Compile WiX source
candle MSI\redline.wxs -out redline.wixobj

if %errorlevel% neq 0 (
    echo WiX compilation failed!
    pause
    exit /b 1
)

REM Link MSI package
light redline.wixobj -out REDLINE-1.0.0.msi

if %errorlevel% equ 0 (
    echo MSI package built successfully!
    echo Output: REDLINE-1.0.0.msi
    del redline.wixobj
) else (
    echo MSI linking failed!
    pause
    exit /b 1
)

pause
EOF

# PowerShell build script
cat > "$PACKAGE_DIR/Scripts/build_all.ps1" << 'EOF'
# REDLINE Windows Installer Build Script
# PowerShell script to build all Windows installers

Write-Host "Building REDLINE Windows Installers..." -ForegroundColor Green

# Check prerequisites
$prerequisites = @{
    "NSIS" = "makensis"
    "WiX Toolset" = "candle"
}

foreach ($tool in $prerequisites.GetEnumerator()) {
    $command = Get-Command $tool.Value -ErrorAction SilentlyContinue
    if (-not $command) {
        Write-Host "❌ $($tool.Key) is not installed or not in PATH" -ForegroundColor Red
        Write-Host "Please install $($tool.Key) and try again" -ForegroundColor Yellow
        exit 1
    } else {
        Write-Host "✅ $($tool.Key) found" -ForegroundColor Green
    }
}

# Build NSIS installer
Write-Host "Building NSIS installer..." -ForegroundColor Yellow
& makensis NSIS\redline.nsi
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ NSIS installer built successfully!" -ForegroundColor Green
} else {
    Write-Host "❌ NSIS build failed!" -ForegroundColor Red
    exit 1
}

# Build MSI package
Write-Host "Building MSI package..." -ForegroundColor Yellow
& candle MSI\redline.wxs -out redline.wixobj
if ($LASTEXITCODE -eq 0) {
    & light redline.wixobj -out REDLINE-1.0.0.msi
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ MSI package built successfully!" -ForegroundColor Green
        Remove-Item redline.wixobj
    } else {
        Write-Host "❌ MSI linking failed!" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "❌ WiX compilation failed!" -ForegroundColor Red
    exit 1
}

Write-Host "🎉 All Windows installers built successfully!" -ForegroundColor Green
Write-Host "Output files:" -ForegroundColor Cyan
Write-Host "  - REDLINE-1.0.0-Setup.exe (NSIS installer)" -ForegroundColor White
Write-Host "  - REDLINE-1.0.0.msi (MSI package)" -ForegroundColor White
EOF

# Create package info
cat > "$PACKAGE_DIR/PACKAGE_INFO.txt" << EOF
REDLINE Windows Installer Package Information
=============================================

Package Name: ${PACKAGE_NAME}
Version: ${VERSION}
Created: $(date)
Platform: Windows (x64 and ARM64)

Contents:
- NSIS/: NSIS installer script and resources
- MSI/: WiX MSI installer script
- Executables/: Windows executables (x64 and ARM64)
- Scripts/: Build scripts for Windows
- INSTALL.txt: Installation instructions
- PACKAGE_INFO.txt: This file

Prerequisites for Building:
- NSIS (Nullsoft Scriptable Install System)
- WiX Toolset (for MSI packages)
- Windows 10 or later

Build Instructions:
1. Install NSIS from https://nsis.sourceforge.io/
2. Install WiX Toolset from https://wixtoolset.org/
3. Run Scripts/build_all.ps1 (PowerShell)
   OR
4. Run Scripts/build_nsis.bat and Scripts/build_msi.bat separately

Output Files:
- REDLINE-${VERSION}-Setup.exe (NSIS installer)
- REDLINE-${VERSION}.msi (MSI package)

Architecture Support:
- x64 (Intel/AMD): Primary support
- ARM64 (Qualcomm/Apple): Full support
- Auto-detection: Installer automatically selects correct version

Features:
- Desktop shortcuts
- Start Menu integration
- Uninstaller included
- Registry integration
- Multi-architecture support

Security:
- All security vulnerabilities fixed
- No hardcoded secrets
- Environment variable configuration
- Secure API key management
EOF

echo "✅ Windows installer package created successfully!"
echo ""
echo "📁 Package location: $PACKAGE_DIR"
echo ""
echo "📊 Package contents:"
ls -la "$PACKAGE_DIR"
echo ""
echo "💾 Package size: $(du -sh "$PACKAGE_DIR" | cut -f1)"
echo ""
echo "🚀 Ready for Windows installer building!"
echo "   Copy to Windows system and run build scripts"
echo "   Requires NSIS and WiX Toolset for building"
