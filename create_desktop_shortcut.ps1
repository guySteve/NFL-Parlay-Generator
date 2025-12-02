# PowerShell script to create desktop shortcut for Multi-Sport Parlay Generator

$WScriptShell = New-Object -ComObject WScript.Shell
$Desktop = [System.Environment]::GetFolderPath('Desktop')
$ShortcutPath = Join-Path $Desktop "Multi-Sport Parlay Generator.lnk"
$TargetPath = Join-Path $PSScriptRoot "launch_multisport.bat"
$IconLocation = "C:\Windows\System32\shell32.dll,134"  # Trophy icon

$Shortcut = $WScriptShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $TargetPath
$Shortcut.WorkingDirectory = $PSScriptRoot
$Shortcut.IconLocation = $IconLocation
$Shortcut.Description = "Multi-Sport Parlay Generator - NFL, NBA, NHL"
$Shortcut.Save()

Write-Host "✅ Desktop shortcut created successfully!" -ForegroundColor Green
Write-Host "Location: $ShortcutPath" -ForegroundColor Cyan
Write-Host ""
Write-Host "You can now double-click the shortcut on your desktop to launch the app!" -ForegroundColor Yellow
Write-Host ""
pause
