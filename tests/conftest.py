import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


LOCAL_TEST_ENV = {
    "S3_BUCKET_NAME": "local-test-bucket",
    "SNOWFLAKE_ACCOUNT": "local-test-account",
    "SNOWFLAKE_USER": "local-test-user",
    "SNOWFLAKE_PASSWORD": "local-test-password",
}

for key, value in LOCAL_TEST_ENV.items():
    os.environ.setdefault(key, value)
