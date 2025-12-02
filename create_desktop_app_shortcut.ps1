# PowerShell script to create desktop shortcut for NFL Parlay Generator Pro
#
# Run this script to create a clickable desktop icon

$desktopPath = [Environment]::GetFolderPath("Desktop")
$shortcutPath = Join-Path $desktopPath "NFL Parlay Generator Pro.lnk"
$targetPath = Join-Path $PSScriptRoot "launch_parlay_pro.bat"
$iconPath = Join-Path $PSScriptRoot "nfl_icon.ico"

# Create shortcut
$WScriptShell = New-Object -ComObject WScript.Shell
$shortcut = $WScriptShell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = $targetPath
$shortcut.WorkingDirectory = $PSScriptRoot
$shortcut.Description = "NFL Parlay Generator Pro - Desktop Edition"

# Set icon if available
if (Test-Path $iconPath) {
    $shortcut.IconLocation = $iconPath
}

$shortcut.Save()

Write-Host "✅ Desktop shortcut created successfully!" -ForegroundColor Green
Write-Host "📍 Location: $shortcutPath" -ForegroundColor Cyan
Write-Host ""
Write-Host "🏈 Double-click 'NFL Parlay Generator Pro' on your desktop to launch!" -ForegroundColor Yellow

# Keep window open
Read-Host "Press Enter to close"
