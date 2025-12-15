# scripts/smoke_test.ps1
# Smoke test básico de OpsCopilot (Windows PowerShell)
# - Frontend (3000)
# - API ping (8000/_debug/ping)
# - Postgres dentro del contenedor (pg_isready)

$ErrorActionPreference = "Stop"

function Test-HttpOk {
  param(
    [Parameter(Mandatory=$true)][string]$Url,
    [int]$TimeoutSec = 8
  )
  try {
    $res = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec $TimeoutSec
    if ($res.StatusCode -ge 200 -and $res.StatusCode -lt 400) {
      Write-Host "OK  $Url  ($($res.StatusCode))"
      return $true
    }
    Write-Host "FAIL $Url  ($($res.StatusCode))"
    return $false
  } catch {
    Write-Host "FAIL $Url  ($($_.Exception.Message))"
    return $false
  }
}

Write-Host "== OpsCopilot Smoke Test =="

# 1) Frontend
$okFrontend = Test-HttpOk -Url "http://localhost:3000"

# 2) API ping
$okApi = Test-HttpOk -Url "http://localhost:8000/_debug/ping"

# 3) Postgres ready (dentro del contenedor)
$okDb = $false
try {
  $out = docker compose exec -T db pg_isready -U postgres -d ops_copilot_dev 2>$null
  if ($LASTEXITCODE -eq 0) {
    Write-Host "OK  db pg_isready"
    $okDb = $true
  } else {
    Write-Host "FAIL db pg_isready ($out)"
  }
} catch {
  Write-Host "FAIL db pg_isready ($($_.Exception.Message))"
}

Write-Host "---------------------------"
if ($okFrontend -and $okApi -and $okDb) {
  Write-Host "SMOKE TEST PASSED"
  exit 0
} else {
  Write-Host "SMOKE TEST FAILED"
  exit 1
}
