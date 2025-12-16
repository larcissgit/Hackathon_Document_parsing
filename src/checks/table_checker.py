# src/checks/table_checker.py
import re
from src.checks.base_checker import BaseCheck
from src.models import Document, CheckResult, CheckStatus, ValidationError


class TableCheck(BaseCheck):
    """Проверка 4: Оформление таблиц"""

    def __init__(self):
        super().__init__(
            check_id="table_format",
            check_name="Оформление таблиц"
        )
        # Значения по умолчанию
        self.caption_pattern = r'^Таблица\s+\d+(\.\d+)*'
        self.require_caption = True

    def set_rules(self, rules: dict):
        super().set_rules(rules)
        self.caption_pattern = self._safe_get_rule(
            'gost_2_105.tables.caption_pattern',
            self.caption_pattern
        )
        self.require_caption = self._safe_get_rule(
            'gost_2_105.tables.require_caption',
            self.require_caption
        )

    def run(self, document: Document) -> CheckResult:
        """Проверяет формат подписи таблиц, наличие наименования и ссылок"""
        errors = []
        text = document.raw_text

        # Ищем все упоминания таблиц
        table_pattern = r'(?i)таблица\s+\d+(\.\d+)*'
        table_matches = list(re.finditer(table_pattern, text))

        if not table_matches:
            return self._create_result(CheckStatus.PASSED)

        # Проверяем каждую найденную таблицу
        for match in table_matches:
            table_text = match.group(0)

            # Проверяем формат подписи
            if not re.match(self.caption_pattern, table_text, re.IGNORECASE):
                errors.append(ValidationError(
                    check_name=self.check_name,
                    description=f"Некорректный формат подписи таблицы: '{table_text}'",
                    recommendation="Используйте формат: 'Таблица 1.1' или 'Таблица 1'",
                    gost_reference="ГОСТ 2.105, раздел 5.3"
                ))

            # Проверяем наличие наименования после номера
            end_pos = match.end()
            next_chars = text[end_pos:end_pos + 5].strip()
            if self.require_caption and (not next_chars or next_chars.startswith(('.', ','))):
                errors.append(ValidationError(
                    check_name=self.check_name,
                    description=f"Таблица без наименования: '{table_text}'",
                    recommendation="Добавьте наименование после номера таблицы через тире или двоеточие",
                    gost_reference="ГОСТ 2.105, раздел 5.3"
                ))

        # Проверяем наличие ссылок на таблицы в тексте (упрощённо)
        for match in table_matches:
            table_ref = match.group(0)
            # Ищем ссылки вида "таблице 1.1" или "см. таблицу 1.1"
            ref_pattern = rf'(?:см\.|в|по|из)\s+{re.escape(table_ref)}'
            if not re.search(ref_pattern, text, re.IGNORECASE):
                errors.append(ValidationError(
                    check_name=self.check_name,
                    description=f"Отсутствует ссылка на таблицу: '{table_ref}'",
                    recommendation=f"Добавьте в текст ссылку на таблицу: '... в {table_ref} ...'",
                    gost_reference="ГОСТ 2.105, раздел 5.3"
                ))

        status = CheckStatus.FAILED if errors else CheckStatus.PASSED
        return self._create_result(status, errors)