ccauditor/
├ docker-compose.yml
├ Makefile
├ bootstrap.sh
├ requirements.in
├ requirements.txt
├ .env.example
├ docker/
│   ├ Dockerfile
│   └ worker.Dockerfile
├ scripts/
│   └ wait_for_dependencies.py
├ alembic/
│   ├ env.py
│   ├ script.py.mako
│   └ versions/
│       └ 0001_initial_schema.py
├ alembic.ini
├ app/
│   ├ main.py
│   ├ celery_app.py
│   ├ config/settings.py
│   ├ auth/auth.py
│   ├ database/db.py
│   ├ database/models.py
│   ├ database/init_db.py
│   ├ canvas/client.py
│   ├ ai/client.py
│   └ utils/logger.py
└ .github/workflows/ci.yml