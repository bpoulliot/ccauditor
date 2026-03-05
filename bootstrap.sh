#!/usr/bin/env bash

set -e

echo "Bootstrapping Canvas Accessibility Platform..."

if [ ! -f ".env" ]; then
    cp .env.example .env
    echo ".env file created"
fi

pip install --upgrade pip
pip install pip-tools

echo "Bootstrap complete."

echo "Next steps:"
echo "docker compose up --build"