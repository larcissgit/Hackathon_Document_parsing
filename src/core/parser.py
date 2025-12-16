from . import SUPPORTED_FORMATS
from src.models import Document
import codecs  # Добавляем модуль для работы с кодировками


class Parser:
    def __init__(self):
        self.supported_formats = SUPPORTED_FORMATS
        self.supported_encodings = ['utf-8', 'utf-16', 'cp1251']

    def _read_text_file(self, file_path: str) -> str:
        encodings_to_try = self.supported_encodings
        for encoding in encodings_to_try:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                print(f"[Парсер] Не удалось прочитать как {encoding}, пробую следующую...")
                continue
            except Exception as e:
                print(f"[Парсер] Ошибка при чтении файла: {e}")
                break

        # Если ни одна кодировка не подошла, возвращаем заглушку
        print(f"[Парсер] Не удалось определить кодировку файла. Использую заглушку.")
        return f"Содержимое файла {file_path} не удалось прочитать."

    def parse(self, file_path: str) -> Document:
        print(f"[Парсер] Чтение файла: {file_path}")

        # ПРОСТАЯ РЕАЛИЗАЦИЯ ДЛЯ TXT ФАЙЛОВ
        if any([file_path.endswith(supported_format) for supported_format in self.supported_formats]):
            if file_path.endswith('.txt'):
                try:
                    text = self._read_text_file(file_path)
                    print(f"[Парсер] Файл успешно прочитан. Символов: {len(text)}")
                except FileNotFoundError:
                    print(f"[Парсер] Файл не найден! Создаю демо-текст.")
                    text = (
                        "Введение\nЭто введение.\n\n"
                        "Назначение\nЦель документа.\n\n"
                        "Основная часть\nЗдесь должен быть раздел 'Технические характеристики'."
                    )
            elif file_path.endswith('.docx'):
                try:
                    text = self._read_text_file(file_path)
                except FileNotFoundError:
                    print(f"[Парсер] Файл не найден! Создаю демо-текст.")
                    text = (
                        "Введение\nЭто введение.\n\n"
                        "Назначение\nЦель документа.\n\n"
                        "Основная часть\nЗдесь должен быть раздел 'Технические характеристики'."
                    )
            else:
                # Для других форматов пока возвращаем заглушку
                text = f"[Файл {file_path} в будущем будет парситься]"
                print(f"[Парсер] Формат не поддерживается, используется заглушка.")
        else:
            text = f"[Файл {file_path} в будущем будет парситься]"
            print(f"[Парсер] Формат не поддерживается, используется заглушка.")
        return Document(file_path=file_path, raw_text=text)