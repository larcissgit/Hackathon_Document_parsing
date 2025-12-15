# Makefile
.PHONY: help install test run docker-build docker-run docker-test clean

help:
 @echo "Команды:"
 @echo "  install     Установить зависимости"
 @echo "  test        Запустить тесты"
 @echo "  run         Запустить приложение"
 @echo "  docker-build Собрать Docker образ"
 @echo "  docker-run   Запустить в Docker"
 @echo "  clean       Очистить кэш"

install:
 pip install -r requirements.txt
 pip install -e .

test:
 pytest tests/ -v

run:
 python -m src.main --help

docker-build:
 docker build -f docker/Dockerfile -t autoverifier:latest .

docker-run:
 docker-compose -f docker/docker-compose.yml up

docker-test:
 docker-compose -f docker/docker-compose.yml run tests

clean:
 find . -type d -name "pycache" -exec rm -rf {} + 2>/dev/null || true
 find . -type f -name "*.pyc" -delete
 rm -rf .pytest_cache