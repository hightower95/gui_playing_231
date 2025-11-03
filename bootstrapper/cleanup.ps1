# Bootstrap Cleanup Tool - PowerShell Wrapper
# Provides easy access to the cleanup tool with better error handling

Write-Host ""
Write-Host "Bootstrap Cleanup Tool" -ForegroundColor Cyan
Write-Host "=====================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python detected: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Error: Python not found in PATH!" -ForegroundColor Red
    Write-Host "Please install Python or add it to your PATH" -ForegroundColor Yellow
    pause
    exit 1
}

# Check if cleanup.py exists
$cleanupScript = Join-Path $PSScriptRoot "cleanup.py"
if (-not (Test-Path $cleanupScript)) {
    Write-Host "Error: cleanup.py not found!" -ForegroundColor Red
    Write-Host "Expected location: $cleanupScript" -ForegroundColor Yellow
    pause
    exit 1
}

Write-Host "Choose cleanup mode:" -ForegroundColor White
Write-Host "1. GUI Mode (recommended)" -ForegroundColor Yellow
Write-Host "2. Console Mode" -ForegroundColor Yellow  
Write-Host "3. Exit" -ForegroundColor Gray
Write-Host ""

do {
    $choice = Read-Host "Enter your choice (1-3)"
    
    switch ($choice) {
        "1" {
            Write-Host "Starting GUI cleanup tool..." -ForegroundColor Green
            try {
                python $cleanupScript
            } catch {
                Write-Host "Error starting GUI mode: $_" -ForegroundColor Red
                Write-Host "Falling back to console mode..." -ForegroundColor Yellow
                python $cleanupScript --console
            }
            $validChoice = $true
        }
        "2" {
            Write-Host "Starting console cleanup tool..." -ForegroundColor Green
            python $cleanupScript --console
            $validChoice = $true
        }
        "3" {
            Write-Host "Goodbye!" -ForegroundColor Green
            $validChoice = $true
        }
        default {
            Write-Host "Invalid choice! Please enter 1, 2, or 3." -ForegroundColor Red
            $validChoice = $false
        }
    }
} while (-not $validChoice)

if ($choice -ne "3") {
    Write-Host ""
    Write-Host "Press any key to exit..." -ForegroundColor Gray
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}