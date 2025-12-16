from . import SUPPORTED_FORMATS, SUPPORTED_ENCODINGS
from pathlib import Path
from typing import Optional


class FileReader:
    @staticmethod
    def read_file(file_path: str) -> Optional[str]:
        """Основной метод для чтения файла любого поддерживаемого формата"""
        path = Path(file_path)

        if not path.exists():
            print(f"[FileReader] Файл не найден: {file_path}")
            print("[FileReader] Создан тестовый файл для проверки")
            return FileReader.create_demo_text()

        suffix = path.suffix.lower()
        if suffix in SUPPORTED_FORMATS:
            if suffix == '.txt':
                return FileReader._read_text_file(file_path)
            elif suffix == '.docx':
                return FileReader._read_docx_file(file_path)
            elif suffix == '.pdf':
                return FileReader._read_pdf_file(file_path)
            else:
                print(f"[FileReader] Поддержка формата ещё не добавлена: {suffix}")
                print("[FileReader] Создан тестовый файл для проверки")
                return FileReader.create_demo_text()
        else:
            print(f"[FileReader] Неподдерживаемый формат: {suffix}")
            print("[FileReader] Создан тестовый файл для проверки")
            return FileReader.create_demo_text()

    @staticmethod
    def _read_text_file(file_path: str) -> str:
        """Чтение текстовых файлов с автоопределением кодировки"""

        for encoding in SUPPORTED_ENCODINGS:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                    print(f"[FileReader] Текстовый файл прочитан в кодировке {encoding}")
                    return content
            except UnicodeDecodeError:
                continue

        print("[FileReader] Не удалось определить кодировку файла")
        print("[FileReader] Создан тестовый файл для проверки")
        return FileReader.create_demo_text()

    @staticmethod
    def _read_docx_file(file_path: str) -> str:
        """Чтение DOCX файлов"""
        try:
            # Ленивый импорт - библиотека может быть не установлена
            from docx import Document as DocxDocument

            doc = DocxDocument(file_path)
            full_text = []

            # Извлекаем текст из всех параграфов
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    full_text.append(paragraph.text)

            # Извлекаем текст из таблиц
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        if cell.text.strip():
                            full_text.append(cell.text)

            result = '\n'.join(full_text)
            print(f"[FileReader] DOCX файл прочитан, символов: {len(result)}")
            return result

        except ImportError:
            print("[FileReader] Библиотека 'python-docx' не установлена")
            print("[FileReader] Создан тестовый файл для проверки")
            return FileReader.create_demo_text()
        except Exception as e:
            print(f"[FileReader] Ошибка чтения DOCX: {e}")
            print("[FileReader] Создан тестовый файл для проверки")
            return FileReader.create_demo_text()

    @staticmethod
    def _read_pdf_file(file_path: str) -> str:
        """Чтение PDF файлов"""
        try:
            import pdfplumber

            full_text = []
            with pdfplumber.open(file_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    if text and text.strip():
                        # Добавляем маркер страницы для отладки
                        full_text.append(f"--- Страница {i + 1} ---")
                        full_text.append(text.strip())

            result = '\n'.join(full_text)
            print(f"[FileReader] PDF файл прочитан, страниц: {len(pdf.pages)}, символов: {len(result)}")
            return result
        except ImportError:
            print("[FileReader] Библиотека 'pdfplumber' не установлена")
            print("[FileReader] Создан тестовый файл для проверки")
            return FileReader.create_demo_text()
        except Exception as e:
            print(f"[FileReader] Ошибка чтения PDF: {e}")
            print("[FileReader] Создан тестовый файл для проверки")
            return FileReader.create_demo_text()


    @staticmethod
    def create_demo_text() -> str:
        """Создаёт демонстрационный текст для тестирования"""
        return (
            "Введение\n"
            "Это введение к документу.\n\n"
            "Назначение\n"
            "Цель данного документа - тестирование авто-верификатора.\n\n"
            "Технические характеристики\n"
            "Здесь должны быть параметры и характеристики изделия.\n\n"
            "Таблица 1.1: Основные параметры\n"
            "Рисунок 2.1: Структурная схема\n\n"
            "Заключение\n"
            "Выводы по проведённой работе."
        )