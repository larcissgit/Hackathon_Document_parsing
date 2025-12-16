import re
from src.models import Document
from src.utils.file_reader import FileReader


class Parser:
    """Парсер документов. Извлекает структуру из текста."""

    def __init__(self):
        self.file_reader = FileReader()
        print("[Parser] Инициализирован парсер документов")

    def parse(self, file_path: str) -> Document:
        """Основной метод: читает файл и парсит его структуру"""
        print(f"[Parser] Начинаю обработку файла: {file_path}")

        # 1. Чтение файла
        text, error_message = self.file_reader.read_file(file_path)

        # 2. Если файл не найден или не прочитан, создаём демо-текст
        if text is None or text == "":
            if error_message:
                print(f"[Parser] Ошибка чтения файла: {error_message}")
            print("[Parser] Не удалось экспортировать текст из файла, использую демо-текст")
            text = self.file_reader.create_demo_text()

        # 3. Извлечение структуры
        print("[Parser] Извлекаю структуру документа...")
        sections = self._extract_sections(text)
        tables = self._extract_tables(text)
        figures = self._extract_figures(text)

        print(f"[Parser] Найдено: {len(sections)} разделов, {len(tables)} таблиц, {len(figures)} рисунков")

        # 4. Создание объекта документа
        document = Document(
            file_path=file_path,
            raw_text=text,
            sections=sections,
            tables=tables,
            figures=figures
        )

        return document

    @staticmethod
    def _extract_sections(text: str) -> list:
        """Извлекает разделы документа по заголовкам"""
        sections = []
        lines = text.split('\n')

        for i, line in enumerate(lines):
            line_stripped = line.strip()

            # Пропускаем пустые строки
            if not line_stripped:
                continue

            # Паттерны заголовков
            patterns = [
                # "1. Введение" или "1.1. Подраздел"
                (r'^(\d+(\.\d+)*)[\.\s]+([А-Я].*)$', 1),
                # "Глава 1. Название"
                (r'^(Глава|Раздел|Часть)\s+(\d+)[\.\s]+(.+)$', 2),
                # "ВВЕДЕНИЕ" (все заглавные)
                (r'^[А-ЯЁ]{3,}$', 3)
            ]

            for pattern, level in patterns:
                match = re.match(pattern, line_stripped)
                if match:
                    # Извлекаем название раздела
                    if level == 1:
                        title = match.group(3)
                    elif level == 2:
                        title = f"{match.group(1)} {match.group(2)}. {match.group(3)}"
                    else:
                        title = line_stripped

                    sections.append({
                        'title': title,
                        'level': level,
                        'line_number': i,
                        'original_text': line_stripped
                    })
                    break

        return sections

    @staticmethod
    def _extract_tables(text: str) -> list:
        """Извлекает информацию о таблицах"""
        tables = []

        # Ищем "Таблица X.Y: Название" или "Таблица X.Y Название"
        pattern = r'(?i)таблица\s+(\d+(\.\d+)*)[\s:]*([^\n]+)'

        for match in re.finditer(pattern, text):
            # Находим начало и конец строки с таблицей
            start_pos = match.start()
            end_of_line = text.find('\n', start_pos)
            if end_of_line == -1:
                end_of_line = len(text)

            full_line = text[start_pos:end_of_line].strip()

            tables.append({
                'id': match.group(1),  # Номер: "1.1"
                'caption': match.group(3).strip() if match.group(3) else "без названия",
                'full_text': full_line,
                'position': start_pos
            })

        return tables

    @staticmethod
    def _extract_figures(text: str) -> list:
        """Извлекает информацию о рисунках"""
        figures = []

        # Ищем "Рисунок X.Y: Название" или "Рисунок X.Y Название"
        pattern = r'(?i)рисунок\s+(\d+(\.\d+)*)[\s:]*([^\n]+)'

        for match in re.finditer(pattern, text):
            # Находим начало и конец строки с рисунком
            start_pos = match.start()
            end_of_line = text.find('\n', start_pos)
            if end_of_line == -1:
                end_of_line = len(text)

            full_line = text[start_pos:end_of_line].strip()

            figures.append({
                'id': match.group(1),  # Номер: "2.1"
                'caption': match.group(3).strip() if match.group(3) else "без названия",
                'full_text': full_line,
                'position': start_pos
            })

        return figures

    def parse_text(self, text: str) -> Document:
        """Парсит уже готовый текст (без чтения файла)"""
        print("[Parser] Парсинг готового текста...")

        sections = self._extract_sections(text)
        tables = self._extract_tables(text)
        figures = self._extract_figures(text)

        return Document(
            file_path="text_input",
            raw_text=text,
            sections=sections,
            tables=tables,
            figures=figures
        )