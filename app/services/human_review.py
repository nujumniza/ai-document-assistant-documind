
import json
from datetime import datetime, timezone
from uuid import uuid4

from app.services.incident_intelligence import get_connection


def review_incident(
    incident_id,
    decision,
    reviewer,
    edited_response=None
):
    if decision not in ("approved", "rejected"):
        raise ValueError("Decision must be approved or rejected.")

    with get_connection() as connection:

        incident = connection.execute(
            """
            SELECT analysis_json
            FROM incidents
            WHERE incident_id = ?
            """,
            (incident_id,)
        ).fetchone()

        if incident is None:
            raise ValueError("Incident not found.")

        analysis = json.loads(incident["analysis_json"])

        original_response = analysis.get(
            "customer_response_draft", ""
        )

        final_response = (
            edited_response
            if edited_response is not None
            else original_response
        )

        if decision == "approved" and not final_response.strip():
            raise ValueError("Cannot approve an empty response.")

        connection.execute("""
            CREATE TABLE IF NOT EXISTS incident_reviews (
                review_id TEXT PRIMARY KEY,
                incident_id TEXT NOT NULL,
                reviewer TEXT NOT NULL,
                decision TEXT NOT NULL,
                final_response TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

        review_id = str(uuid4())
        created_at = datetime.now(timezone.utc).isoformat()

        connection.execute(
            """
            INSERT INTO incident_reviews (
                review_id,
                incident_id,
                reviewer,
                decision,
                final_response,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                review_id,
                incident_id,
                reviewer,
                decision,
                final_response,
                created_at
            )
        )

    return {
        "review_id": review_id,
        "incident_id": incident_id,
        "reviewer": reviewer,
        "decision": decision,
        "final_response": final_response,
        "email_sent": False,
        "created_at": created_at
    }


def get_incident_reviews(incident_id):

    with get_connection() as connection:

        rows = connection.execute(
            """
            SELECT *
            FROM incident_reviews
            WHERE incident_id = ?
            ORDER BY created_at DESC
            """,
            (incident_id,)
        ).fetchall()

    return [dict(row) for row in rows]
