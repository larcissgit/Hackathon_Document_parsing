from abc import ABC, abstractmethod
from typing import Dict, Any
from src.models import Document, CheckResult, CheckStatus


class BaseCheck(ABC):
    """Абстрактный базовый класс для ВСЕХ проверок ГОСТ"""

    def __init__(self, check_id: str, check_name: str):
        self.check_id = check_id  # Например, "section_check"
        self.check_name = check_name  # Например, "Проверка разделов"
        self.rules = None  # Правила для этой проверки

    def set_rules(self, rules: Dict[str, Any]):
        """Загружает правила проверки из конфига"""
        self.rules = rules

    @abstractmethod
    def run(self, document: Document) -> CheckResult:
        """
        Главный метод, который выполняет проверку.
        Каждый конкретный чекер ДОЛЖЕН его реализовать.
        """
        pass

    def _create_result(self, status: CheckStatus, errors: list = None) -> CheckResult:
        """Вспомогательный метод для создания результата"""
        return CheckResult(
            check_id=self.check_id,
            check_name=self.check_name,
            status=status,
            errors=errors or []  # Если errors=None, подставляем пустой список
        )