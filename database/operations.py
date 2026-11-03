
from database.connection import get_connection
from psycopg.types.json import Jsonb


def save_assignment(assignment):

    connection = get_connection()

    try:
        with connection.cursor() as cursor:

            # Make sure the course exists
            cursor.execute(
                """
                INSERT INTO courses (course_id)
                VALUES (%s)
                ON CONFLICT (course_id) DO NOTHING
                """,
                (assignment["course_id"],)
            )

            # Save or update the assignment
            cursor.execute(
                """
                INSERT INTO assignments (
                    assignment_id,
                    course_id,
                    name,
                    published,
                    due_at,
                    unlock_at,
                    lock_at,
                    submission_types
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (assignment_id)
                DO UPDATE SET
                    name = EXCLUDED.name,
                    published = EXCLUDED.published,
                    due_at = EXCLUDED.due_at,
                    unlock_at = EXCLUDED.unlock_at,
                    lock_at = EXCLUDED.lock_at,
                    submission_types = EXCLUDED.submission_types
                """,
                (
                    assignment["assignment_id"],
                    assignment["course_id"],
                    assignment["name"],
                    assignment["published"],
                    assignment["due_at"],
                    assignment["unlock_at"],
                    assignment["lock_at"],
                    Jsonb(assignment["submission_types"])
                )
            )

        connection.commit()
        print("Assignment successfully saved!")

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def save_findings(assignment_id, findings):

    connection = get_connection()

    try:
        with connection.cursor() as cursor:

            # Create a new troubleshooting run
            cursor.execute(
                """
                INSERT INTO troubleshooting_runs (assignment_id)
                VALUES (%s)
                RETURNING run_id
                """,
                (assignment_id,)
            )

            run_id = cursor.fetchone()[0]

            # Save findings under this run
            for finding in findings:
                cursor.execute(
                    """
                    INSERT INTO troubleshooting_reports (
                        run_id,
                        assignment_id,
                        issue,
                        severity,
                        recommendation
                    )
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        run_id,
                        assignment_id,
                        finding["issue"],
                        finding["severity"],
                        finding["recommendation"]
                    )
                )

        connection.commit()
        print(f"Troubleshooting run {run_id} successfully saved!")

        return run_id

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def get_findings(run_id):

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT issue, severity, recommendation, created_at
                FROM troubleshooting_reports
                WHERE run_id = %s
                ORDER BY created_at DESC
                """,
                (run_id,)
            )

            rows = cursor.fetchall()

            findings = []

            for row in rows:
                findings.append({
                    "issue": row[0],
                    "severity": row[1],
                    "recommendation": row[2],
                    "created_at": row[3]
                })

            return findings

    finally:
        connection.close()


def get_troubleshooting_history(assignment_id):

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT run_id, created_at
                FROM troubleshooting_runs
                WHERE assignment_id = %s
                ORDER BY created_at DESC
                """,
                (assignment_id,)
            )

            rows = cursor.fetchall()

            history = []

            for row in rows:
                history.append({
                    "run_id": row[0],
                    "created_at": row[1]
                })

            return history

    finally:
        connection.close()
