[CmdletBinding()]
param(
    [string]$BackendPath = $env:MEDUSA_BACKEND_DIR,
    [string]$FrameworkEnvFile = ".env",
    [switch]$SkipCustomer
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($BackendPath)) {
    $BackendPath = "D:\medusa_store_codebase\Backend\my-medusa-store"
}

$backendPackage = Join-Path $BackendPath "package.json"
$backendSeed = Join-Path $BackendPath "src\scripts\seed.ts"
if (-not (Test-Path -LiteralPath $backendPackage) -or -not (Test-Path -LiteralPath $backendSeed)) {
    throw "BackendPath must contain package.json and src\\scripts\\seed.ts. Received: $BackendPath"
}

$frameworkRoot = Split-Path -Parent $PSScriptRoot
$resolvedEnvFile = if ([System.IO.Path]::IsPathRooted($FrameworkEnvFile)) {
    $FrameworkEnvFile
} else {
    Join-Path $frameworkRoot $FrameworkEnvFile
}
if (-not (Test-Path -LiteralPath $resolvedEnvFile)) {
    throw "Create the framework .env from .env.example, then apply test-data\\storefront-default-seed.env. Missing: $resolvedEnvFile"
}

Write-Host "Running the Medusa native seed in $BackendPath"
Push-Location $BackendPath
try {
    npm run seed
    if ($LASTEXITCODE -ne 0) {
        throw "Medusa seed failed with exit code $LASTEXITCODE"
    }
} finally {
    Pop-Location
}

if (-not $SkipCustomer) {
    Write-Host "Creating or verifying the isolated storefront customer"
    uv run python (Join-Path $PSScriptRoot "create_test_customer.py") --env-file $resolvedEnvFile
    if ($LASTEXITCODE -ne 0) {
        throw "Customer setup failed with exit code $LASTEXITCODE"
    }
}

Write-Host "Baseline Medusa data is ready. The script does not enable RUN_E2E or start a storefront."
