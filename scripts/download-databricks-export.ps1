param(
    [string] $Profile = "ekp-free",
    [string] $Destination = "data/export/gold"
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$VolumePath = terraform -chdir="$Root/terraform/databricks" output -raw gold_export_path
if ($LASTEXITCODE -ne 0) { throw "Could not read the Databricks Terraform output." }

$DestinationPath = Join-Path $Root $Destination
New-Item -ItemType Directory -Force -Path $DestinationPath | Out-Null
databricks fs cp -r "dbfs:$VolumePath" $DestinationPath --overwrite --profile $Profile
if ($LASTEXITCODE -ne 0) { throw "Databricks export download failed." }

Write-Output "Downloaded $VolumePath to $DestinationPath"
