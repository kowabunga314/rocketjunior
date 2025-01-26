#!/usr/bin/env bash

# Hint: Ensure that docker, docker-compose, and direnv are installed
echo "Checking dependencies..."
for cmd in docker; do
  if ! command -v $cmd &> /dev/null; then
    echo -e "\033[31m $cmd is not installed. Please install it before proceeding.\033[0m"
    echo "Examples:"
    echo "  brew install [package]"
    echo "  apt-get install [package]"
    echo "  yum install [package]"
    exit 1
  fi
done

echo ""
echo "===================================================="
echo ""
echo "Setup complete!"
echo "You can now build and start the project with:"
echo "  make build"
echo ""
echo "Execute tests:"
echo "  make test"
echo ""
echo "Stop application:"
echo "  make stop"
echo ""
echo "Restart application:"
echo "  make start"
