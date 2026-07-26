import os
from pathlib import Path

import pandas as pd
import pytest
import snowflake.connector

from ekp.storage.snowflake import snowflake_connection_options


pytestmark = pytest.mark.cloud_integration
EXPECTED_DOCUMENT = "aws-caf-security-perspective.pdf"


@pytest.mark.skipif(
    os.getenv("RUN_CLOUD_INTEGRATION") != "1",
    reason="set RUN_CLOUD_INTEGRATION=1 after downloading and transferring the export",
)
def test_sample_document_passed_through_databricks_and_snowflake() -> None:
    export_path = Path(os.getenv("DATABRICKS_EXPORT_PATH", "data/export/gold"))
    assert export_path.exists(), "download the Databricks gold export first"

    frame = pd.read_parquet(export_path)
    document_rows = frame[frame["document_name"] == EXPECTED_DOCUMENT]
    assert not document_rows.empty
    assert document_rows["embedding"].map(len).eq(384).all()

    with snowflake.connector.connect(**snowflake_connection_options()) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT COUNT(*), MIN(VECTOR_L2_DISTANCE(embedding, embedding))
                FROM document_chunks
                WHERE document_id = %s
                """,
                (EXPECTED_DOCUMENT,),
            )
            count, minimum_self_distance = cursor.fetchone()

    assert count == len(document_rows)
    assert minimum_self_distance == pytest.approx(0.0, abs=1e-7)
