# src/checks/section_numbering_checker.py
import re
from src.checks.base_checker import BaseCheck
from src.models import Document, CheckResult, CheckStatus, ValidationError


class SectionNumberingCheck(BaseCheck):
    """Проверка 2: Нумерация разделов и подразделов"""

    def __init__(self):
        super().__init__(
            check_id="section_numbering",
            check_name="Нумерация разделов и подразделов"
        )
        # ЗНАЧЕНИЕ ПО УМОЛЧАНИЮ - строка, а не None!
        self.numbering_pattern = r'^\d+(\.\d+)*\s+.+$'
        self.max_level = 3

    def set_rules(self, rules: dict):
        """Загружает правила для проверки из конфига"""
        super().set_rules(rules)
        # Безопасное извлечение с fallback на значения по умолчанию
        self.numbering_pattern = self._safe_get_rule(
            'gost_2_105.section_numbering.pattern',
            self.numbering_pattern
        )
        self.max_level = self._safe_get_rule(
            'gost_2_105.section_numbering.max_level',
            self.max_level
        )

    def run(self, document: Document) -> CheckResult:
        """Проверяет сквозную нумерацию арабскими цифрами (1, 1.1, 1.1.1)"""
        errors = []

        # Проверяем, что pattern является строкой
        if not isinstance(self.numbering_pattern, str):
            return self._create_result(CheckStatus.ERROR, [ValidationError(
                check_name=self.check_name,
                description="Паттерн для проверки нумерации не является строкой",
                recommendation="Проверьте конфигурационный файл",
                gost_reference="ГОСТ 2.105"
            )])

        # Анализируем разделы, найденные парсером
        for section in document.sections:
            title = section.get('title', '')

            # Пропускаем разделы без нумерации (например, "Введение")
            if not re.match(r'^\d', title):
                continue

            # Проверяем соответствие паттерну ГОСТ
            if not re.match(self.numbering_pattern, title):
                errors.append(ValidationError(
                    check_name=self.check_name,
                    description=f"Некорректный формат нумерации раздела: '{title}'",
                    recommendation="Используйте формат: '1. Название', '1.1. Подраздел' (арабские цифры)",
                    gost_reference="ГОСТ 2.105, раздел 4.2"
                ))

            # Проверяем уровень вложенности
            level = title.count('.') + 1 if '.' in title else 1
            if level > self.max_level:
                errors.append(ValidationError(
                    check_name=self.check_name,
                    description=f"Превышена максимальная глубина вложенности ({level} > {self.max_level}): '{title}'",
                    recommendation=f"Упростите структуру, максимальный уровень: {self.max_level}",
                    gost_reference="ГОСТ 2.105, раздел 4.2"
                ))

        status = CheckStatus.FAILED if errors else CheckStatus.PASSED
        return self._create_result(status, errors)