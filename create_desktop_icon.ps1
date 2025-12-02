# PowerShell script to create desktop shortcut for NFL Parlay Generator Pro

$WshShell = New-Object -comObject WScript.Shell
$Desktop = [System.Environment]::GetFolderPath('Desktop')
$ShortcutPath = Join-Path $Desktop "NFL Parlay Pro.lnk"
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)

# Set the target to the batch file
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Shortcut.TargetPath = Join-Path $ScriptDir "launch_pro_desktop.bat"
$Shortcut.WorkingDirectory = $ScriptDir
$Shortcut.Description = "NFL Parlay Generator Pro - Quantitative Analytics"
$Shortcut.IconLocation = "shell32.dll,134"  # Football icon from Windows

$Shortcut.Save()

Write-Host "✓ Desktop shortcut created successfully!" -ForegroundColor Green
Write-Host "  Location: $ShortcutPath" -ForegroundColor Cyan
Write-Host ""
Write-Host "You can now double-click 'NFL Parlay Pro' on your desktop to launch the app!" -ForegroundColor Yellow
Read-Host "Press Enter to exit"
