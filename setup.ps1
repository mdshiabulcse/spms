# One-time setup: create .venv and install packages
Set-Location $PSScriptRoot

if (-not (Test-Path ".\.venv\Scripts\python.exe")) {
    Write-Host "Creating .venv ..."
    python -m venv .venv
}

Write-Host "Installing packages ..."
& ".\.venv\Scripts\python.exe" -m pip install --upgrade pip
& ".\.venv\Scripts\python.exe" -m pip install -r requirements.txt

Write-Host "Running migrations ..."
& ".\.venv\Scripts\python.exe" manage.py migrate

Write-Host ""
Write-Host "Done. Next steps:"
Write-Host "  .\migrate.ps1          # migrate again later"
Write-Host "  .\.venv\Scripts\python.exe manage.py createsuperuser"
Write-Host "  .\run.ps1              # start server"
