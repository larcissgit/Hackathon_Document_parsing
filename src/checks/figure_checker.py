import re
from src.checks.base_checker import BaseCheck
from src.models import Document, CheckResult, CheckStatus, ValidationError


class FigureCheck(BaseCheck):
    def __init__(self):
        super().__init__(
            check_id="figure_format",
            check_name="Проверка оформления рисунков")

    def run(self, document: Document) -> CheckResult:
        """Проверяет нумерацию и оформление рисунков"""
        errors = []
        text = document.raw_text

        # Ищем подписи рисунков
        figure_pattern = r'(?i)рисунок\s+(\d+(\.\d+)*)'
        figure_matches = list(re.finditer(figure_pattern, text))

        # Проверяем формат "Рисунок X.Y"
        for match in figure_matches:
            full_match = match.group(0)
            # Проверяем, что после номера есть текст (наименование)
            end_pos = match.end()
            if end_pos < len(text) and text[end_pos:end_pos + 20].strip() == "":
                errors.append(ValidationError(
                    check_name=self.check_name,
                    description=f"Рисунок без наименования: '{full_match}'",
                    recommendation="Добавьте наименование после номера рисунка",
                    gost_reference="ГОСТ 2.105, раздел 5.4"
                ))

        status = CheckStatus.FAILED if errors else CheckStatus.PASSED
        return self._create_result(status, errors)