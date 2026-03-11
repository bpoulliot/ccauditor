from prometheus_client import Counter, Gauge, Histogram

# --------------------------------------------------
# Scan Execution Metrics
# --------------------------------------------------

COURSE_SCANS_TOTAL = Counter(
    "ccauditor_course_scans_total",
    "Total number of course scans executed",
)

SCAN_FAILURES_TOTAL = Counter(
    "ccauditor_scan_failures_total",
    "Total scan failures",
)

SCAN_DURATION_SECONDS = Histogram(
    "ccauditor_scan_duration_seconds",
    "Time spent scanning courses",
    buckets=(
        1,
        2,
        5,
        10,
        20,
        30,
        60,
        120,
        300,
    ),
)

# --------------------------------------------------
# Course Risk Distribution
# --------------------------------------------------
# NOTE:
# Histogram must NOT use course_id labels
# otherwise cardinality explodes and Prometheus breaks.

COURSE_RISK_SCORE = Histogram(
    "ccauditor_course_risk_score",
    "Distribution of course accessibility risk scores",
    buckets=(
        0,
        1,
        2,
        5,
        10,
        20,
        50,
        100,
    ),
)

# --------------------------------------------------
# Accessibility Issue Metrics
# --------------------------------------------------

ACCESSIBILITY_ISSUES_TOTAL = Counter(
    "ccauditor_accessibility_issues_total",
    "Accessibility issues discovered",
    ["issue_type"],
)

BROKEN_LINKS_TOTAL = Counter(
    "ccauditor_broken_links_total",
    "Broken links detected",
)

FILE_ACCESSIBILITY_ISSUES_TOTAL = Counter(
    "ccauditor_file_accessibility_issues_total",
    "Accessibility issues in uploaded files",
)

# --------------------------------------------------
# Video Accessibility Metrics
# --------------------------------------------------

VIDEOS_TOTAL = Counter(
    "ccauditor_videos_total",
    "Videos detected",
)

VIDEOS_MISSING_CAPTIONS_TOTAL = Counter(
    "ccauditor_videos_missing_captions_total",
    "Videos missing captions",
)

CAPTION_REMEDIATION_HOURS = Gauge(
    "ccauditor_caption_remediation_hours",
    "Estimated caption remediation hours",
)

PANOPTO_VIDEOS_TOTAL = Counter(
    "ccauditor_panopto_videos_total",
    "Panopto videos detected"
)

PANOPTO_MISSING_CAPTIONS_TOTAL = Counter(
    "ccauditor_panopto_missing_captions_total",
    "Panopto videos missing captions"
)

VIMEO_VIDEOS_TOTAL = Counter(
    "ccauditor_vimeo_videos_total",
    "Total Vimeo videos detected"
)

VIMEO_MISSING_CAPTIONS_TOTAL = Counter(
    "ccauditor_vimeo_missing_captions_total",
    "Vimeo videos missing captions"
)

FOD_VIDEOS_TOTAL = Counter(
    "ccauditor_fod_videos_total",
    "Films On Demand videos detected"
)

FOD_MISSING_CAPTIONS_TOTAL = Counter(
    "ccauditor_fod_missing_captions_total",
    "Films On Demand videos missing captions"
)

# --------------------------------------------------
# Content Hygiene Metrics
# --------------------------------------------------

DUPLICATE_CONTENT_TOTAL = Counter(
    "ccauditor_duplicate_content_total",
    "Duplicate content detected",
)

# --------------------------------------------------
# Department Analytics
# --------------------------------------------------

DEPARTMENT_RISK_SCORE = Gauge(
    "ccauditor_department_risk_score",
    "Average accessibility risk score per department",
    ["department"],
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

# --------------------------------------------------
# Term-Level Metrics
# --------------------------------------------------

TERM_RISK_SCORE = Gauge(
    "ccauditor_term_risk_score",
    "Average risk score by term",
    ["term_id"],
)

TERM_SCAN_PROGRESS = Gauge(
    "ccauditor_term_scan_progress",
    "Scan progress per term",
    ["term_id"],
)

# --------------------------------------------------
# Infrastructure Metrics
# --------------------------------------------------

REDIS_QUEUE_LENGTH = Gauge(
    "ccauditor_redis_queue_length",
    "Length of Celery queues",
    ["queue"],
)

WORKER_COUNT = Gauge(
    "ccauditor_celery_workers_active",
    "Number of Celery workers",
)