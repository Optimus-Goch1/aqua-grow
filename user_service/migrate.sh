#!/bin/bash
set -e

echo "Running database migrations..."
flask --app src.app db upgrade

echo "Migrations applied. Starting the service..."
python src.app