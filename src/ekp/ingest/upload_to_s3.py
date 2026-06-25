from pathlib import Path

import boto3

from ekp.config import settings


RAW_DOCUMENTS_PREFIX = "raw/documents/"
PROJECT_ROOT = Path(__file__).resolve().parents[3]
SAMPLE_DOCS_DIR = PROJECT_ROOT / "data" / "sample_docs"


def iter_sample_documents(sample_docs_dir: Path = SAMPLE_DOCS_DIR):
    for path in sorted(sample_docs_dir.rglob("*")):
        if path.is_file() and not path.name.startswith("."):
            yield path


def upload_sample_documents() -> int:
    s3_client = boto3.client("s3", region_name=settings.aws_region)
    uploaded_count = 0

    if not SAMPLE_DOCS_DIR.exists():
        raise FileNotFoundError(f"Sample docs directory does not exist: {SAMPLE_DOCS_DIR}")

    for file_path in iter_sample_documents():
        relative_path = file_path.relative_to(SAMPLE_DOCS_DIR).as_posix()
        s3_key = f"{RAW_DOCUMENTS_PREFIX}{relative_path}"

        s3_client.upload_file(str(file_path), settings.s3_bucket_name, s3_key)
        uploaded_count += 1
        print(f"Uploaded {file_path} to s3://{settings.s3_bucket_name}/{s3_key}")

    return uploaded_count


def main():
    uploaded_count = upload_sample_documents()
    print(f"Uploaded {uploaded_count} file(s).")


if __name__ == "__main__":
    main()
