# Start the development server (uses project .venv — no activate needed)
Set-Location $PSScriptRoot
& ".\.venv\Scripts\python.exe" manage.py runserver @args
