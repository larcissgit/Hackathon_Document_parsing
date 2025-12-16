# src/core/validator.py
from typing import List
from src.models import Document, CheckResult
from src.checks.base_checker import BaseCheck


class Validator:
    """Главный двигатель проверок. Управляет всеми чекерами."""

    def __init__(self, config: dict = None):
        self.checks: List[BaseCheck] = []  # Список зарегистрированных проверок
        self.config = config  # Сохраняем конфиг

    def register_check(self, check: BaseCheck):
        """Добавляет проверку в систему и передаёт конфигурацию"""
        # Передаём конфиг проверке, если он есть
        if self.config:
            check.set_rules(self.config)

        self.checks.append(check)
        print("[Валидатор] Зарегистрирована проверка: ", end="")

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