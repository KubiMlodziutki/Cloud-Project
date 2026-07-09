param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]] $PytestArgs
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

$env:PYTHONPATH = Join-Path $Root "src"

$env:S3_BUCKET_NAME = if ($env:S3_BUCKET_NAME) { $env:S3_BUCKET_NAME } else { "local-test-bucket" }
$env:SNOWFLAKE_ACCOUNT = if ($env:SNOWFLAKE_ACCOUNT) { $env:SNOWFLAKE_ACCOUNT } else { "local-test-account" }
$env:SNOWFLAKE_USER = if ($env:SNOWFLAKE_USER) { $env:SNOWFLAKE_USER } else { "local-test-user" }
$env:SNOWFLAKE_PASSWORD = if ($env:SNOWFLAKE_PASSWORD) { $env:SNOWFLAKE_PASSWORD } else { "local-test-password" }

$PythonCandidates = @(
    (Join-Path $Root ".venv\Scripts\python.exe"),
    "python",
    "python3",
    "py"
)

$Python = $null
foreach ($Candidate in $PythonCandidates) {
    $Command = Get-Command $Candidate -ErrorAction SilentlyContinue
    if ($Command) {
        try {
            $VersionOutput = & $Command.Source --version 2>&1
            if ($LASTEXITCODE -eq 0 -and $VersionOutput) {
                $Python = $Command.Source
                break
            }
        } catch {
            continue
        }
    }
}

if (-not $Python) {
    throw "No working Python launcher found. Install Python or create .venv, then run: python -m pip install -r requirements.txt"
}

& $Python -m pytest tests @PytestArgs
