# src/checks/base_check.py
from abc import ABC, abstractmethod
from typing import Dict, Any
from ..models import Document, CheckResult, CheckStatus


class BaseCheck(ABC):
    """Абстрактный базовый класс для ВСЕХ проверок ГОСТ"""

    def __init__(self, check_id: str, check_name: str):
        self.check_id = check_id
        self.check_name = check_name
        self.rules = None

    def set_rules(self, rules: Dict[str, Any]):
        """
        Загружает правила проверки из конфига.
        Должен быть переопределён в дочерних классах для извлечения специфичных правил.
        """
        self.rules = rules

    @abstractmethod
    def run(self, document: Document) -> CheckResult:
        """Главный метод, который выполняет проверку"""
        pass

    def _create_result(self, status: CheckStatus, errors: list = None) -> CheckResult:
        """Вспомогательный метод для создания результата"""
        return CheckResult(
            check_id=self.check_id,
            check_name=self.check_name,
            status=status,
            errors=errors or []
        )

    def _safe_get_rule(self, rule_path: str, default: Any = None) -> Any:
        """
        Безопасно извлекает правило из конфига по пути.
        Пример: _safe_get_rule('gost_2_105.required_sections', [])
        """
        if not self.rules:
            return default

        keys = rule_path.split('.')
        value = self.rules

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value