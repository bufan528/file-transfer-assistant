$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  File Transfer Assistant APK Downloader" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$artifactUrl = "https://github.com/bufan528/file-transfer-assistant/actions/runs/24287827607/artifacts/6387145305"
$outputZip = "d:\文件传输助手\file-transfer-assistant-apk.zip"
$outputDir = "d:\文件传输助手"
$apkFile = "$outputDir\*.apk"

Write-Host "[1/4] Opening browser for download..." -ForegroundColor Green
Start-Process $artifactUrl

Write-Host ""
Write-Host "[2/4] Waiting for you to complete download in browser..." -ForegroundColor Green
Write-Host "Please click the download button in the browser window that opened" -ForegroundColor Yellow
Write-Host "File will be saved to: $env:USERPROFILE\Downloads\" -ForegroundColor Yellow
Write-Host ""
Write-Host "Waiting for download (max 120 seconds)..." -ForegroundColor Gray

$timeout = 120
$elapsed = 0
$downloaded = $false

while ($elapsed -lt $timeout) {
    Start-Sleep -Seconds 5
    $elapsed += 5
    
    $zipFiles = Get-ChildItem "$env:USERPROFILE\Downloads" -Filter "*.zip" | Where-Object { $_.LastWriteTime -gt (Get-Date).AddMinutes(-5) }
    
    if ($zipFiles.Count -gt 0) {
        $downloaded = $true
        Write-Host ""
        Write-Host "Download detected!" -ForegroundColor Green
        break
    }
    
    Write-Host "`r  Elapsed: ${elapsed} seconds..." -NoNewline
}

if (-not $downloaded) {
    Write-Host ""
    Write-Host "Timeout - no download detected" -ForegroundColor Red
    Write-Host "Please manually check: $env:USERPROFILE\Downloads" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "[3/4] Extracting APK file..." -ForegroundColor Green

$latestZip = (Get-ChildItem "$env:USERPROFILE\Downloads" -Filter "*.zip" | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName

Expand-Archive -Path $latestZip -DestinationPath $outputDir -Force

Write-Host ""
Write-Host "[4/4] Checking APK file..." -ForegroundColor Green

$apkFiles = Get-ChildItem $apkFile -ErrorAction SilentlyContinue

if ($apkFiles.Count -gt 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  SUCCESS! APK downloaded and extracted!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    foreach ($file in $apkFiles) {
        $sizeMB = [math]::Round($file.Length / 1MB, 2)
        Write-Host "  File: $($file.Name)" -ForegroundColor White
        Write-Host "  Path: $($file.FullName)" -ForegroundColor White
        Write-Host "  Size: ${sizeMB} MB" -ForegroundColor White
        Write-Host ""
    }
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "1. Transfer APK to your Android phone" -ForegroundColor Gray
    Write-Host "2. Install APK on phone (may need to enable 'Unknown sources' in settings)" -ForegroundColor Gray
    Write-Host "3. Open and use the File Transfer Assistant app!" -ForegroundColor Gray
} else {
    Write-Host ""
    Write-Host "APK file not found in ZIP" -ForegroundColor Red
    Write-Host "Please check ZIP contents manually" -ForegroundColor Yellow
}
