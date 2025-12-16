import re
from src.checks.base_checker import BaseCheck
from src.models import Document, CheckResult, CheckStatus, ValidationError


class PageNumberingCheck(BaseCheck):
    """Проверка 3: Нумерация страниц"""

    def __init__(self):
        super().__init__(
            check_id="page_numbering",
            check_name="Нумерация страниц"
        )

    def run(self, document: Document) -> CheckResult:
        """
        Проверка сквозной нумерации,
        отсутствия номеров на титульном листе и содержании
        """
        errors = []
        text = document.raw_text

        # Эвристика: ищем упоминания страниц
        page_patterns = [
            r'страниц[ауе]\s+(\d+)',  # "странице 5"
            r'стр\.\s*(\d+)',  # "стр. 5"
            r'—\s*(\d+)\s*—',  # "— 5 —" (типично для колонтитулов)
        ]

        page_numbers = []
        for pattern in page_patterns:
            for match in re.finditer(pattern, text):
                try:
                    page_num = int(match.group(1))
                    page_numbers.append({
                        'number': page_num,
                        'context': text[max(0, match.start() - 20):match.end() + 20]
                    })
                except ValueError:
                    continue

        # Проверяем, что нет упоминания первых страниц (титульный, содержание)
        for page_info in page_numbers:
            if page_info['number'] <= 2:  # Первые 2 страницы не нумеруются
                errors.append(ValidationError(
                    check_name=self.check_name,
                    description=f"Упоминание страницы {page_info['number']} (первые 2 страницы не должны нумероваться)",
                    recommendation="Уберите нумерацию с титульного листа и содержания",
                    gost_reference="ГОСТ 2.105, раздел 6.1"
                ))

        # Проверяем последовательность (если нашли несколько номеров)
        if len(page_numbers) > 1:
            nums = sorted([p['number'] for p in page_numbers])
            for i in range(1, len(nums)):
                if nums[i] != nums[i - 1] + 1:
                    errors.append(ValidationError(
                        check_name=self.check_name,
                        description=f"Нарушена сквозная нумерация: {nums[i - 1]} → {nums[i]}",
                        recommendation="Убедитесь в сквозной последовательной нумерации",
                        gost_reference="ГОСТ 2.105, раздел 6.1"
                    ))

        status = CheckStatus.FAILED if errors else CheckStatus.PASSED
        return self._create_result(status, errors)