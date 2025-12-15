# src/core/validator.py
from typing import List
from src.models import Document, CheckResult
from src.checks.base_check import BaseCheck


class Validator:
    """Главный двигатель проверок. Управляет всеми чекерами."""

    def __init__(self):
        self.checks: List[BaseCheck] = []  # Список зарегистрированных проверок

    def register_check(self, check: BaseCheck):
        """Добавляет проверку в систему"""
        self.checks.append(check)
        print(f"[Валидатор] Зарегистрирована проверка: {check.check_name}")

    def validate(self, document: Document) -> List[CheckResult]:
        """Запускает ВСЕ зарегистрированные проверки для документа"""
        print(f"[Валидатор] Запуск проверок для: {document.file_path}")
        results = []

        for check in self.checks:
            result = check.run(document)
            results.append(result)
            status_icon = "✅" if result.status.value == "PASSED" else "❌"
            print(f"  {status_icon} {check.check_name}: {result.status.value}")

        return results