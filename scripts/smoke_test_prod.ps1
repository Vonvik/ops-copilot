# scripts/smoke_test_prod.ps1

$frontend = "https://opscopilot-frontend.onrender.com"
$apiBase  = "https://opscopilot-api.onrender.com"
$apiV1    = "$apiBase/api/v1"

function Test-HttpOk([string]$Url) {
  try {
    $r = Invoke-WebRequest -Uri $Url -Method GET -UseBasicParsing -TimeoutSec 20
    if ($r.StatusCode -ge 200 -and $r.StatusCode -lt 400) {
      Write-Host "OK   $Url ($($r.StatusCode))"
    } else {
      Write-Host "FAIL $Url ($($r.StatusCode))"
    }
  } catch {
    Write-Host "FAIL $Url ($($_.Exception.Message))"
  }
}

Write-Host "== OpsCopilot PROD Smoke Test =="

Test-HttpOk $frontend
Test-HttpOk $apiBase
Test-HttpOk "$apiBase/_debug/ping"
Test-HttpOk "$apiV1/processed/stats"
