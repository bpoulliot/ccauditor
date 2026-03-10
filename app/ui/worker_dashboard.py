import redis
import streamlit as st
from celery import Celery
from prometheus_client import generate_latest

from app.auth.rbac import require_role
from app.config.settings import settings


celery_app = Celery(
    "ccauditor",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

redis_client = redis.Redis.from_url(settings.REDIS_URL)


def get_worker_stats():

    inspect = celery_app.control.inspect()

    stats = inspect.stats() or {}
    active = inspect.active() or {}
    reserved = inspect.reserved() or {}

    workers = []

    for name, data in stats.items():

        workers.append(
            {
                "name": name,
                "pool": data.get("pool", {}).get("max-concurrency"),
                "tasks_processed": data.get("total"),
                "active_tasks": len(active.get(name, [])),
                "reserved_tasks": len(reserved.get(name, [])),
            }
        )

    return workers


def get_queue_stats():

    queues = {}

    for q in ["scans", "ai", "hygiene"]:

        key = f"celery:{q}"

        try:
            size = redis_client.llen(key)
        except Exception:
            size = 0

        queues[q] = size

    return queues


def get_running_tasks():

    inspect = celery_app.control.inspect()

    active = inspect.active() or {}

    tasks = []

    for worker, task_list in active.items():

        for t in task_list:

            tasks.append(
                {
                    "worker": worker,
                    "task": t.get("name"),
                    "id": t.get("id"),
                }
            )

    return tasks


def get_prometheus_metrics():

    try:
        return generate_latest().decode("utf-8")
    except Exception:
        return "Metrics unavailable"


def show_worker_dashboard(user_id):

    require_role(user_id, ["admin"])

    st.title("Worker Monitoring Dashboard")

    st.write("Operational monitoring for Celery workers and queues.")

    st.divider()

    # ------------------------------
    # Worker Status
    # ------------------------------

    st.subheader("Worker Status")

    workers = get_worker_stats()

    if not workers:
        st.warning("No workers detected.")
    else:

        for w in workers:

            col1, col2, col3, col4 = st.columns(4)

            col1.metric("Worker", w["name"])
            col2.metric("Concurrency", w["pool"])
            col3.metric("Active Tasks", w["active_tasks"])
            col4.metric("Reserved Tasks", w["reserved_tasks"])

    st.divider()

    # ------------------------------
    # Queue Monitoring
    # ------------------------------

    st.subheader("Queue Monitoring")

    queues = get_queue_stats()

    col1, col2, col3 = st.columns(3)

    col1.metric("Scan Queue", queues["scans"])
    col2.metric("AI Queue", queues["ai"])
    col3.metric("Hygiene Queue", queues["hygiene"])

    st.divider()

    # ------------------------------
    # Active Tasks
    # ------------------------------

    st.subheader("Active Tasks")

    tasks = get_running_tasks()

    if tasks:

        for t in tasks:

            st.write(f"{t['task']} running on {t['worker']} (id: {t['id']})")

    else:

        st.info("No active tasks")

    st.divider()

    # ------------------------------
    # Prometheus Metrics
    # ------------------------------

    st.subheader("Prometheus Metrics")

    metrics = get_prometheus_metrics()

    st.code(metrics[:5000], language="text")

    st.divider()

    # ------------------------------
    # Admin Queue Controls
    # ------------------------------

    st.subheader("Queue Controls")

    queue = st.selectbox("Queue", ["scans", "ai", "hygiene"])

    if st.button("Purge Queue"):

        celery_app.control.purge()

        st.success(f"{queue} queue purged")