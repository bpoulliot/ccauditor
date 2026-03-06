from prometheus_client import Counter, Histogram


SCAN_COUNTER = Counter(
    "ccauditor_course_scans_total",
    "Total number of course scans"
)

SCAN_FAILURES = Counter(
    "ccauditor_scan_failures_total",
    "Total number of failed scans"
)

SCAN_DURATION = Histogram(
    "ccauditor_scan_duration_seconds",
    "Time spent scanning courses"
)

API_ERRORS = Counter(
    "ccauditor_api_errors_total",
    "External API errors"
)