$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
Set-Location -LiteralPath $projectRoot
$pythonPath = Join-Path $projectRoot '.venv312\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $pythonPath)) { $pythonPath = Join-Path $projectRoot '.venv\Scripts\python.exe' }
if (-not (Test-Path -LiteralPath $pythonPath)) { throw 'Create a Python environment and install requirements first; see README.md.' }
New-Item -ItemType Directory -Force -Path (Join-Path $projectRoot '.runtime') | Out-Null
$pgCtl = Join-Path $projectRoot '.runtime\pgsql\bin\pg_ctl.exe'
$pgData = Join-Path $projectRoot '.runtime\pgdata'
if (Test-Path -LiteralPath $pgCtl) {
    & $pgCtl -D $pgData status *> $null
    if ($LASTEXITCODE -ne 0) { & $pgCtl -D $pgData -l (Join-Path $projectRoot '.runtime\postgresql.log') -o '-p 55432 -h 127.0.0.1' start }
}
if (-not (Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue)) {
    Start-Process -FilePath $pythonPath -ArgumentList 'scripts/serve_backend.py' -WorkingDirectory $projectRoot -WindowStyle Hidden -RedirectStandardOutput (Join-Path $projectRoot '.runtime\backend.log') -RedirectStandardError (Join-Path $projectRoot '.runtime\backend-error.log') | Out-Null
}
if (-not (Get-NetTCPConnection -LocalPort 5173 -State Listen -ErrorAction SilentlyContinue)) {
    $nodePath = (Get-Command node).Source
    Start-Process -FilePath $nodePath -ArgumentList 'node_modules/vite/bin/vite.js --host 127.0.0.1' -WorkingDirectory (Join-Path $projectRoot 'frontend') -WindowStyle Hidden -RedirectStandardOutput (Join-Path $projectRoot '.runtime\frontend.log') -RedirectStandardError (Join-Path $projectRoot '.runtime\frontend-error.log') | Out-Null
}
Write-Host 'ScaleeLapse: http://127.0.0.1:5173. Logs: .runtime/. Use README.md for demo accounts and setup.'
