from typing import Any

from src.checks.base_check import BaseCheck
from src.models import Document, CheckResult, CheckStatus, ValidationError


class SectionCheck(BaseCheck):
    """Проверка наличия обязательных разделов в документе"""

    def __init__(self):
        super().__init__(
            check_id="required_sections",
            check_name="Проверка обязательных разделов"
        )
        self.required_sections = []

    def set_rules(self, rules: dict):
        """Загружает правила для проверки из конфига"""
        super().set_rules(rules)
        # Извлекаем конкретные правила для этой проверки
        if rules and 'checks' in rules:
            gost_rules = rules['checks']
            check: dict = gost_rules.get('required_sections', {'enabled': True,
                'sections': ["Введение", "Назначение", "Технические характеристики"]})
            if check.get('enabled', True):
                self.required_sections = check.get('required_sections', [
                "Введение", "Назначение", "Технические характеристики"])
            print(self.required_sections)

    def run(self, document: Document) -> CheckResult:
        """Ищет обязательные разделы в тексте документа"""
        errors = []

        # Проверяем, загружены ли правила
        if not hasattr(self, 'required_sections'):
            error = ValidationError(
                check_name=self.check_name,
                description="Правила проверки не загружены",
                recommendation="Проверьте конфигурационный файл",
                gost_reference="ГОСТ 2.105"
            )
            return self._create_result(CheckStatus.ERROR, [error])

        # Простейшая логика: ищем подстроки в тексте
        for section in self.required_sections:
            print(section)
            if section not in document.raw_text:
                error = ValidationError(
                    check_name=self.check_name,
                    description=f"Отсутствует обязательный раздел: '{section}'",
                    recommendation=f"Добавьте раздел '{section}' в соответствии с ГОСТ 2.105",
                    gost_reference="ГОСТ 2.105, разделы 4.1-4.3"
                )
                errors.append(error)

        status = CheckStatus.FAILED if errors else CheckStatus.PASSED
        return self._create_result(status, errors)