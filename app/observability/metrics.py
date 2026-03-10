from prometheus_client import Counter, Gauge, Histogram

COURSE_SCANS_TOTAL = Counter(
    "ccauditor_course_scans_total", "Total number of course scans executed"
)

SCAN_FAILURES_TOTAL = Counter("ccauditor_scan_failures_total", "Total scan failures")

SCAN_DURATION_SECONDS = Histogram(
    "ccauditor_scan_duration_seconds", "Time spent scanning courses"
)

COURSE_RISK_SCORE = Histogram(
    "ccauditor_course_risk_score", "Distribution of accessibility risk scores"
)

ACCESSIBILITY_ISSUES_TOTAL = Counter(
    "ccauditor_accessibility_issues_total",
    "Accessibility issues discovered",
    ["issue_type"],
)

BROKEN_LINKS_TOTAL = Counter("ccauditor_broken_links_total", "Broken links detected")

FILE_ACCESSIBILITY_ISSUES_TOTAL = Counter(
    "ccauditor_file_accessibility_issues_total",
    "Accessibility issues in uploaded files",
)

VIDEOS_TOTAL = Counter("ccauditor_videos_total", "Videos detected")

VIDEOS_MISSING_CAPTIONS_TOTAL = Counter(
    "ccauditor_videos_missing_captions_total", "Videos missing captions"
)

CAPTION_REMEDIATION_HOURS = Gauge(
    "ccauditor_caption_remediation_hours", "Estimated caption remediation hours"
)

DUPLICATE_CONTENT_TOTAL = Counter(
    "ccauditor_duplicate_content_total", "Duplicate content detected"
)

DEPARTMENT_RISK_SCORE = Gauge(
    "ccauditor_department_risk_score", "Risk score per department", ["department"]
)

DEPARTMENT_ACCESSIBILITY_ISSUES = Counter(
    "ccauditor_department_accessibility_issues_total",
    "Accessibility issues per department",
    ["department", "issue_type"],
)

DEPARTMENT_CAPTION_BACKLOG = Gauge(
    "ccauditor_department_caption_backlog_hours",
    "Caption backlog per department",
    ["department"],
)

TERM_RISK_SCORE = Gauge("ccauditor_term_risk_score", "Risk score by term", ["term_id"])

TERM_SCAN_PROGRESS = Gauge(
    "ccauditor_term_scan_progress", "Scan progress per term", ["term_id"]
)

REDIS_QUEUE_LENGTH = Gauge("redis_queue_length", "Length of Celery queues", ["queue"])

WORKER_COUNT = Gauge("celery_workers_active", "Number of Celery workers")
