@echo off
setlocal

cd /d "%~dp0\.."

set "PYTHONPATH=%CD%\src"

if "%S3_BUCKET_NAME%"=="" set "S3_BUCKET_NAME=local-test-bucket"
if "%SNOWFLAKE_ACCOUNT%"=="" set "SNOWFLAKE_ACCOUNT=local-test-account"
if "%SNOWFLAKE_USER%"=="" set "SNOWFLAKE_USER=local-test-user"
if "%SNOWFLAKE_PASSWORD%"=="" set "SNOWFLAKE_PASSWORD=local-test-password"

if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" -m pytest tests %*
    exit /b %ERRORLEVEL%
)

python -m pytest tests %*
exit /b %ERRORLEVEL%
