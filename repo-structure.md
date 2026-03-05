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
├ app/
│   ├ main.py
│   ├ celery_app.py
│   ├ config/settings.py
│   ├ auth/auth.py
│   ├ database/db.py
│   ├ database/models.py
│   ├ canvas/client.py
│   ├ ai/client.py
│   └ utils/logger.py
└ .github/workflows/ci.yml