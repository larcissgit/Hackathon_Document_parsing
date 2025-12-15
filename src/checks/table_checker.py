# src/checks/table_checker.py
from src.checks.base_check import BaseCheck
from src.models import Document, CheckResult, CheckStatus, ValidationError
import re


class TableCheck(BaseCheck):
    """Проверка оформления таблиц по ГОСТ"""

    def __init__(self):
        super().__init__(
            check_id="table_format",
            check_name="Проверка оформления таблиц"
        )
        self.table_pattern = r'Таблица\s+\d+[\.\d+]*'
        self.caption_prefix = ''
        self.must_be_referenced = True

    def set_rules(self, rules: dict):
        """Загружает правила для проверки таблиц"""
        super().set_rules(rules)
        if rules and 'gost_2_105' in rules:
            gost_rules = rules['gost_2_105']
            table_rules = gost_rules.get('tables', {})
            self.caption_prefix = table_rules.get('caption_prefix', 'Таблица')
            self.must_be_referenced = table_rules.get('must_be_referenced', True)

    def run(self, document: Document) -> CheckResult:
        """Проверяет оформление таблиц в документе"""
        errors = []

        # Ищем все упоминания таблиц в тексте
        table_matches = list(re.finditer(self.table_pattern, document.raw_text))

        if not table_matches:
            # Если таблиц нет - проверка пройдена
            return self._create_result(CheckStatus.PASSED)

        print(f"[Проверка таблиц] Найдено таблиц: {len(table_matches)}")

        # Проверяем каждую найденную таблицу
        for i, match in enumerate(table_matches):
            table_text = match.group(0)

            # Проверяем формат: "Таблица X.Y" или "Таблица X"
            if not re.match(r'Таблица\s+\d+(\.\d+)?$', table_text):
                error = ValidationError(
                    check_name=self.check_name,
                    description=f"Некорректный формат подписи таблицы: '{table_text}'",
                    recommendation="Используйте формат: 'Таблица X.Y' или 'Таблица X'",
                    gost_reference="ГОСТ 2.105, раздел 5.3",
                    element=table_text
                )
                errors.append(error)

        # Проверяем наличие подписей под таблицами
        lines = document.raw_text.split('\n')
        for i, line in enumerate(lines):
            if line.strip().startswith('Таблица'):
                # Проверяем, есть ли текст после подписи (название таблицы)
                if len(line.strip()) < len('Таблица 1.1') + 3:
                    error = ValidationError(
                        check_name=self.check_name,
                        description=f"Таблица без наименования: '{line.strip()}'",
                        recommendation="Добавьте наименование после номера таблицы",
                        gost_reference="ГОСТ 2.105, раздел 5.3",
                        element=line.strip()
                    )
                    errors.append(error)

        status = CheckStatus.FAILED if errors else CheckStatus.PASSED
        return self._create_result(status, errors)