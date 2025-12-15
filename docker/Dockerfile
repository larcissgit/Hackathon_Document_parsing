FROM python:3.11-slim

WORKDIR /app

# Устанавливаем системные зависимости для работы с PDF/DOCX
RUN apt-get update && apt-get install -y \
    poppler-utils \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Копируем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код
COPY . .

# Создаем пользователя без привилегий root
RUN useradd -m -u 1000 user && chown -R user:user /app
USER user

# Точка входа
ENTRYPOINT ["python", "-m", "src.main"]
CMD ["--help"]