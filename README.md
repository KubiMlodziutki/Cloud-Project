# Enterprise Knowledge Platform

This project implements a small RAG pipeline with local Python, Databricks Free
Edition serverless compute, Unity Catalog managed storage, and Snowflake.

The active no-AWS flow is:

```text
sample PDF -> Unity Catalog volume -> Databricks parse -> chunk -> embeddings
           -> local Parquet download -> local Snowflake transfer -> vector search
```

The legacy AWS S3 Terraform and ingestion code remain available under
`terraform/aws` and `src/ekp/ingest`, but they are not required by this workflow.

## 1. Local environment

Use Python 3.12 from PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Run local tests and the cloud-free RAG pipeline:

```powershell
.\scripts\test-local.ps1 -q
.\scripts\run-local.ps1 "How do I secure access to S3?"
```

## 2. Snowflake infrastructure

Create a Snowflake trial account and fill the Snowflake values in `.env` for the
local transfer. Supply Terraform credentials as environment variables so the
password is not committed:

```powershell
$env:TF_VAR_snowflake_organization_name = "organization"
$env:TF_VAR_snowflake_account_name = "account"
$env:TF_VAR_snowflake_user = "terraform-user"
$env:TF_VAR_snowflake_password = Read-Host "Snowflake password"
$env:TF_VAR_snowflake_role = "ACCOUNTADMIN"

terraform -chdir=terraform/snowflake init
terraform -chdir=terraform/snowflake validate
terraform -chdir=terraform/snowflake plan -out snowflake.tfplan
terraform -chdir=terraform/snowflake apply snowflake.tfplan
```

Terraform provisions:

- `EKP_DB.RAG`;
- `RAW_DOCUMENT_CHUNKS_STG` and `DOCUMENT_CHUNKS`;
- an initially suspended `XSMALL` warehouse with 60-second auto-suspend;
- a one-credit monthly resource monitor with immediate suspension at 90%;
- the restricted `EKP_ROLE` and its grants.

The table resource is currently a preview feature in the Snowflake Terraform
provider and is explicitly enabled in `provider.tf`.

## 3. Databricks Free Edition infrastructure

Create a Free Edition workspace and install current Terraform and Databricks CLI
versions. Authenticate interactively with OAuth:

```powershell
databricks auth login --host "https://YOUR-WORKSPACE" --profile ekp-free
databricks current-user me --profile ekp-free
$env:TF_VAR_databricks_host = "https://YOUR-WORKSPACE"
```

Free Edition normally provides an existing catalog and schema. Defaults are
`workspace.default`; override them when the names shown in Catalog Explorer are
different:

```powershell
$env:TF_VAR_catalog_name = "workspace"
$env:TF_VAR_schema_name = "default"
```

Deploy the managed volume, source files, sample PDF, and three-task serverless job:

```powershell
terraform -chdir=terraform/databricks init
terraform -chdir=terraform/databricks validate
terraform -chdir=terraform/databricks plan -out databricks.tfplan
terraform -chdir=terraform/databricks apply databricks.tfplan
```

Run it:

```powershell
$jobId = terraform -chdir=terraform/databricks output -raw job_id
databricks jobs run-now $jobId --profile ekp-free
```

The job has exactly three serverless tasks: parse, chunk, and embeddings. It uses
`STANDARD` performance mode and a batch size of 16 to favor efficient test runs.
Free Edition has daily fair-use quotas and restricted outbound network access. The
embedding task must be able to download the configured model; if its model host is
blocked, upload a compatible model or dependency artifact to the volume instead.

## 4. Local Databricks-to-Snowflake transfer

After the job succeeds, download the gold Parquet files:

```powershell
.\scripts\download-databricks-export.ps1
```

Load them into Snowflake and require continuity of the supplied sample document:

```powershell
.\.venv\Scripts\python.exe .\scripts\transfer-databricks-to-snowflake.py `
  .\data\export\gold `
  --expected-document aws-caf-security-perspective.pdf
```

The command validates the export schema and every 384-dimensional embedding,
truncates both test tables, inserts staging rows, and casts valid arrays into
Snowflake vectors. Pass `--append` only when duplicate rows are acceptable.

## 5. Cross-system integration test

After download and transfer, run the opt-in live test:

```powershell
$env:RUN_CLOUD_INTEGRATION = "1"
.\scripts\test-local.ps1 -m cloud_integration -vv
```

It confirms that the same sample PDF exists in the downloaded Databricks gold
artifact and Snowflake, that row counts match, that embeddings have 384 dimensions,
and that Snowflake can execute vector distance operations. Normal unit-test runs
skip this live test.

## 6. Cost cleanup

Snowflake compute automatically suspends after 60 seconds, but verify it after the
test. When the environment is disposable, review and apply destroy plans:

```powershell
terraform -chdir=terraform/databricks plan -destroy
terraform -chdir=terraform/snowflake plan -destroy
```

Databricks Free Edition is quota-limited rather than billed. Snowflake trial credits
are consumed while its warehouse runs, so keep the dataset small and retain the
short auto-suspend and resource-monitor settings.
