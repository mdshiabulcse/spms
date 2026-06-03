# Run database migrations (uses project .venv — no activate needed)
Set-Location $PSScriptRoot
& ".\.venv\Scripts\python.exe" manage.py migrate @args
