param([switch]$NoOpen)

$ErrorActionPreference = 'SilentlyContinue'
Set-Location -Path $PSScriptRoot

function Test-ServerUp {
    try {
        $r = Invoke-WebRequest -Uri "http://127.0.0.1:5000/" -UseBasicParsing -TimeoutSec 2
        return $r.StatusCode -eq 200
    } catch {
        return $false
    }
}

if (Test-ServerUp) {
    if (-not $NoOpen) {
        Start-Process "http://127.0.0.1:5000"
    }
    exit
}

python -c "import flask, requests, bs4" 2>$null
if ($LASTEXITCODE -ne 0) {
    python -m pip install --quiet --disable-pip-version-check flask requests beautifulsoup4
}

Start-Process -FilePath "pythonw" -ArgumentList "app.py" -WindowStyle Hidden

$ok = $false
for ($i = 0; $i -lt 30; $i++) {
    Start-Sleep -Milliseconds 500
    if (Test-ServerUp) { $ok = $true; break }
}

if ($ok) {
    if (-not $NoOpen) {
        Start-Process "http://127.0.0.1:5000"
    }
} else {
    Add-Type -AssemblyName System.Windows.Forms
    [System.Windows.Forms.MessageBox]::Show(
        "Server se nepodarilo spustit. Zkuste v terminalu spustit 'python app.py' rucne, aby se zobrazila chyba.",
        "Chyba - Archiv inzeratu"
    )
}
