## Scanner Improvements

- Improve `course_prioritizer` to use real accessibility risk indicators instead of simple course size heuristics.

Future prioritization signals may include:
- video count (caption remediation workload)
- number of files (PDF, DOCX, PPTX)
- presence of inaccessible file types
- historical risk scores
- AI-assisted course risk estimation

Goal:
Prioritize courses with the highest accessibility remediation impact so scans surface the most critical courses earlier.

## TODO – Worker Stability and Monitoring Improvements

Investigate and implement improved database session management for Celery workers under high concurrency.

Context:
Large scan jobs dispatch hundreds or thousands of `scan_course_task` executions. Under heavy load this can cause SQLAlchemy connection pool reuse issues, session rollback errors, or libpq state errors.

Goals:
- Ensure Celery workers use a fully isolated SQLAlchemy session lifecycle.
- Prevent connection reuse after rollback failures.
- Validate connection pool settings for long-running scan workloads.
- Confirm Postgres pool size and Celery concurrency are aligned.
- Add monitoring to detect DB connection pool exhaustion during scans.

Potential Areas to Review:
- `app/database/db.py`
- Celery worker concurrency configuration
- SQLAlchemy engine pool settings
- Session rollback / retry behavior in `scan_course_task`

Priority:
Medium — implement once scan pipeline stability is confirmed.