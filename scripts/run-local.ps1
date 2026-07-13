param(
    [Parameter(Position = 0)]
    [string] $Question,
    [switch] $Ollama,
    [int] $TopK = 5
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $Root ".venv\Scripts\python.exe"

if (-not (Test-Path $Python)) {
    throw "NO .venv. Create it: py -3.12 -m venv .venv; .\.venv\Scripts\python.exe -m pip install -r requirements.txt"
}

$Arguments = @((Join-Path $Root "scripts\run-local.py"), "--top-k", $TopK)
if ($Question) { $Arguments += $Question }
if ($Ollama) { $Arguments += "--ollama" }

& $Python @Arguments

