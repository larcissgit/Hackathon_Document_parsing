# Установка и запуск авто-верификатора ГОСТ 2.105

## 📦 Быстрый старт (Docker)

### Предварительные требования
- Установленный [Docker](https://docs.docker.com/get-docker/)
- Установленный [Docker Compose](https://docs.docker.com/compose/install/)

### Шаги установки

1. Клонирование репозитория
```bash
  git clone https://github.com/larcissgit/Hackathon_Document_parsing
  cd Hackathon_Document_parsing
```
2. Сборка Docker образа
```bash
  docker build -t autoverifier-gost:latest .
``` 
3. Запуск контейнера
```bash
  # Базовая проверка
  docker run -v $(pwd)/документ.docx:/app/document.docx autoverifier-gost document.docx
  # С сохранением отчёта
  docker run -v $(pwd)/документ.docx:/app/document.docx -v $(pwd)/reports:/app/reports autoverifier-gost document.docx --output reports/validation.json
``` 
4. Использование docker-compose
```bash
  # Поместите документ в папку data/
  cp ваш_документ.docx data/
  # Запустите проверку
  docker-compose up
```
