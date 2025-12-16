import re
from src.checks.base_check import BaseCheck
from src.models import Document, CheckResult, CheckStatus, ValidationError


class PageNumberingCheck(BaseCheck):
    def __init__(self):
        super().__init__("page_numbering", "Проверка нумерации страниц")

    def run(self, document: Document) -> CheckResult:
        """Проверяет сквозную нумерацию, отсутствие номеров на титульном листе"""
        errors = []

        # Заглушка для демонстрации
        # TODO: Реальная логика анализа номеров страниц
        # 1. Проверить, что титульный лист не имеет номера
        # 2. Проверить сквозную последовательность
        # 3. Проверить, что содержание имеет отдельную нумерацию

        # Временная логика: ищем признаки неправильной нумерации в тексте
        if "страница 1" in document.raw_text.lower():
            errors.append(ValidationError(
                check_name=self.check_name,
                description="Номер '1' обнаружен в основном тексте. Титульный лист не должен нумероваться",
                recommendation="Убедитесь, что титульный лист не содержит номера страницы",
                gost_reference="ГОСТ 2.105, раздел 6.1"
            ))

        status = CheckStatus.FAILED if errors else CheckStatus.PASSED
        return self._create_result(status, errors)