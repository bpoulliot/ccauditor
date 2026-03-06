# CCAuditor – Canvas Course Accessibility Auditor

CCAuditor is a scalable accessibility auditing platform for Canvas LMS courses. It analyzes course content across multiple accessibility domains—including HTML structure, files, media, and external links—to identify potential WCAG-related issues and provide actionable remediation insights.

The system is designed to operate across **large institutional environments**, supporting thousands of courses through asynchronous workers, distributed task queues, and observability tooling.

---

# Project Credits

**Originally developed by:**  
Riley O'Shea  
University of Colorado Colorado Springs

**Re-factored and redeveloped by:**  
Brandon Poulliot  
University of Colorado Colorado Springs

**Contact:**  
bpoullio@uccs.edu

---

# Overview

CCAuditor provides automated auditing and reporting capabilities for Canvas courses with a focus on identifying accessibility issues that impact compliance with accessibility standards such as **WCAG 2.1 AA**.

The platform scans course content using the Canvas API and performs analysis on:

- HTML pages
- Assignments
- Discussions
- Modules
- Uploaded files
- Video content
- External links
- Duplicate course content
- Caption availability

The system generates metrics and dashboards that help instructional designers and accessibility teams understand accessibility risk across departments, terms, and courses.

---

# Key Features

## Accessibility Scanning
The system analyzes course content for accessibility issues including:

- Missing image alt text
- Heading structure violations
- Broken links
- Duplicate content
- Missing video captions
- Caption remediation workload
- File accessibility issues
- WCAG-related content issues

## Caption Workload Estimation
Video detection and caption availability checks allow the system to estimate:

- total video duration
- caption remediation time
- caption remediation hours by department or course

## Duplicate Content Detection
CCAuditor identifies duplicate content including:

- duplicate files
- duplicate pages
- duplicate assignments
- duplicate quiz questions

This helps reduce redundant content and improve course quality.

## Department and Term Analytics
Metrics are aggregated to support institutional analysis:

- accessibility risk score by course
- accessibility issues by department
- caption backlog by department
- risk trends by academic term

## Real-Time Monitoring
The system includes operational dashboards showing:

- worker health
- task queue depth
- scan progress
- failure rates
- scan throughput

## Administrative Controls
Administrators can:

- launch scans for entire terms
- scan individual courses
- pause scans
- resume scans
- cancel scans
- monitor worker activity

---

# Architecture

CCAuditor uses a distributed architecture designed for scalability.

```
Canvas LMS
     │
     ▼
CCAuditor Scanner Engine
     │
     ▼
Celery Workers (scans / ai / hygiene queues)
     │
     ▼
Redis Task Queue
     │
     ▼
PostgreSQL + pgvector
     │
     ▼
Prometheus Metrics
     │
     ▼
Grafana Dashboards
```

---

# Technology Stack

## Application Layer

- Python
- Streamlit
- Canvas API (canvasapi)

## Background Processing

- Celery
- Redis

## Database

- PostgreSQL
- pgvector (for embeddings and similarity analysis)

## Observability

- Prometheus
- Grafana

## Containerization

- Docker
- Docker Compose

---

# Repository Structure

```
app/
  auth/
  canvas/
  scanner/
  observability/
  security/
  tasks/
  ui/

grafana/
  dashboards/
  provisioning/

prometheus/
  prometheus.yml

docker-compose.yml
```

---

# Installation

## Prerequisites

- Docker
- Docker Compose
- Canvas API Token
- Python 3.12 (for development)

---

## Clone the Repository

```bash
git clone https://github.com/bpoulliot/ccauditor.git
cd ccauditor
```

---

## Configure Environment Variables

Create a `.env` file based on `.env.example`.

Example configuration:

```
CANVAS_BASE_URL=https://canvas.yourschool.edu
CANVAS_API_TOKEN=your_token_here

REDIS_URL=redis://redis:6379/0
DATABASE_URL=postgresql://ccauditor:password@postgres:5432/ccauditor

SESSION_TIMEOUT=3600
SCAN_INCREMENTAL_ENABLED=true
```

---

# Running the Platform

Start all services:

```bash
docker compose up -d --build
```

This launches:

- Streamlit UI
- Celery workers
- Celery scheduler
- Redis
- PostgreSQL
- Prometheus
- Grafana

---

# Accessing the Platform

Streamlit UI:

```
http://localhost:49152
```

Grafana:

```
http://localhost:3000
```

Prometheus:

```
http://localhost:9090
```

---

# Worker Queues

Workers are separated by task type to prevent resource contention.

```
scans      → course scanning
ai         → AI analysis tasks
hygiene    → duplicate content detection
```

---

# Observability

CCAuditor exports Prometheus metrics including:

- scan throughput
- scan failures
- scan duration
- accessibility issues
- caption remediation backlog
- department risk scores
- Redis queue depth
- worker activity

These metrics power Grafana dashboards including:

- Scan Monitoring
- Accessibility Analytics
- Accessibility Heatmaps
- Worker Health

---

# Authentication

The system supports:

- username/password login
- Argon2 password hashing
- role-based access control
- Redis-backed sessions
- password reset tokens
- login attempt throttling

---

# Security

Security features include:

- Redis-backed session management
- password reset tokens with expiration
- login throttling
- audit logging
- role-based page access

---

# Contributing

Contributions are welcome. Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

All pull requests should include:

- code changes
- documentation updates
- testing instructions

---

# License

This project is intended for academic and institutional use.  
License details may vary depending on institutional policies.

---

# Contact

For questions, collaboration, or institutional deployment support:

**Brandon Poulliot**  
University of Colorado Colorado Springs  
Email: bpoullio@uccs.edu

---

# Acknowledgments

Special thanks to the instructional design and accessibility teams at:

**University of Colorado Colorado Springs**

for their work supporting accessible course development.