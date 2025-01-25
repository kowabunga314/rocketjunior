#!/bin/bash

# Hint: Ensure that docker, docker-compose, and direnv are installed
echo "Checking dependencies..."
for cmd in docker docker-compose direnv; do
  if ! command -v $cmd &> /dev/null; then
    echo "$cmd is not installed. Please install it before proceeding."
    echo "Examples:"
    echo "  brew install [package]"
    echo "  apt-get install [package]"
    echo "  yum install [package]"
    exit 1
  fi
done

echo "Setting up environment..."
if [ ! -f .env ]; then
  echo "Creating .env file from .env.example..."
  cp .env.example .env
  echo -e "\033[31mIMPORTANT: Please edit the .env file with your secrets.\033[0m"
fi

echo "Allowing direnv..."
direnv allow || { echo "Failed to allow direnv. Ensure direnv is installed and configured."; exit 1; }

echo "Making scripts executable..."
chmod +x *.sh

echo "Setup complete! You can now start the project with:"
echo "  docker compose up -d --build"
echo ""
echo "Execute tests:"
echo "  docker compose exec api python manage.py test --parallel"
