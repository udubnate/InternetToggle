# Load-Env.ps1
# PowerShell script to load environment variables from .env file

Write-Host "Loading environment variables from .env file..." -ForegroundColor Green

# Check if .env file exists
if (!(Test-Path -Path ".env")) {
    Write-Host "Error: .env file not found!" -ForegroundColor Red
    exit 1
}

# Read and process .env file
Get-Content .env | ForEach-Object {
    $line = $_.Trim()
    
    # Skip empty lines and comments
    if ($line -and !$line.StartsWith('#')) {
        $key, $value = $line -split '=', 2
        
        # Remove quotes if present
        $value = $value -replace '^"|"$', ''
        $value = $value -replace "^'|'$", ''
        
        # Set environment variable
        [Environment]::SetEnvironmentVariable($key, $value, 'Process')
        Write-Host "Set $key = $value" -ForegroundColor Cyan
    }
}

Write-Host "`nEnvironment variables loaded successfully." -ForegroundColor Green
Write-Host "You can now access them in this PowerShell session." -ForegroundColor Green
Write-Host "`nTo verify, try: `$env:INTERNET_IP" -ForegroundColor Yellow