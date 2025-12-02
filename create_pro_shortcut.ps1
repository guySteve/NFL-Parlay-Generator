# PowerShell script to create desktop shortcut for NFL Parlay Generator Pro

$DesktopPath = [Environment]::GetFolderPath("Desktop")
$ScriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$ShortcutPath = "$DesktopPath\NFL Parlay Generator Pro.lnk"
$TargetPath = "$ScriptPath\launch_pro.bat"
$IconPath = "C:\Windows\System32\imageres.dll"

$WScriptShell = New-Object -ComObject WScript.Shell
$Shortcut = $WScriptShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $TargetPath
$Shortcut.WorkingDirectory = $ScriptPath
$Shortcut.IconLocation = "$IconPath,1"  # Football-ish icon
$Shortcut.Description = "NFL Parlay Generator Pro - Quantitative Analytics"
$Shortcut.Save()

Write-Host "Desktop shortcut created successfully at: $ShortcutPath" -ForegroundColor Green
Write-Host "You can now double-click 'NFL Parlay Generator Pro' on your desktop to launch the app!"
pause
