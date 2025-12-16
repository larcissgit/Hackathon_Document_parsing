from src.checks.base_checker import BaseCheck
from src.models import Document, CheckResult, CheckStatus, ValidationError


class SectionCheck(BaseCheck):
    """Проверка 1: Наличие и порядок обязательных разделов"""

    def __init__(self):
        super().__init__(
            check_id="required_sections",
            check_name="Наличие и порядок разделов"
        )
        # Значения по умолчанию на случай отсутствия конфига
        self.required_sections = ["Введение", "Назначение", "Технические характеристики"]

    def set_rules(self, rules: dict):
        """Загружает правила для проверки из конфига"""
        super().set_rules(rules)
        # Безопасное извлечение правил с fallback на значения по умолчанию
        self.required_sections = self._safe_get_rule(
            'gost_2_105.required_sections',
            self.required_sections
        )

    def run(self, document: Document) -> CheckResult:
        """Проверяет наличие обязательных разделов в нужной последовательности"""
        errors = []
        text = document.raw_text.lower()
        lines = document.raw_text.split('\n')

        # Проверяем наличие каждого раздела
        found_sections = {}
        for section in self.required_sections:
            if section.lower() in text:
                # Находим позицию раздела
                for i, line in enumerate(lines):
                    if section.lower() in line.lower():
                        found_sections[section] = i
                        break

        # Проверяем, все ли разделы найдены
        for section in self.required_sections:
            if section not in found_sections:
                errors.append(ValidationError(
                    check_name=self.check_name,
                    description=f"Отсутствует обязательный раздел: '{section}'",
                    recommendation=f"Добавьте раздел '{section}' в документ",
                    gost_reference="ГОСТ 2.105, раздел 4.1"
                ))

        # Проверяем порядок разделов (если все найдены)
        if len(found_sections) == len(self.required_sections):
            sections_in_order = sorted(found_sections.items(), key=lambda x: x[1])
            expected_order = list(zip(self.required_sections, range(len(self.required_sections))))

            for (found_name, pos), (expected_name, _) in zip(sections_in_order, expected_order):
                if found_name != expected_name:
                    errors.append(ValidationError(
                        check_name=self.check_name,
                        description=f"Нарушен порядок разделов. '{found_name}' найден до '{expected_name}'",
                        recommendation=f"Расположите разделы в порядке: {', '.join(self.required_sections)}",
                        gost_reference="ГОСТ 2.105, раздел 4.1"
                    ))
                    break

        status = CheckStatus.FAILED if errors else CheckStatus.PASSED
        return self._create_result(status, errors)