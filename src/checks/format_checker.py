from pathlib import Path

from src.checks.base_checker import BaseCheck
from src.models import Document, CheckResult, CheckStatus, ValidationError


class FormatCheck(BaseCheck):
    """Проверка наличия обязательных разделов в документе"""

    def __init__(self):
        super().__init__(
            check_id="required_format",
            check_name="Проверка формата файла")
        self.required_format = {}

    def set_rules(self, rules: dict):
        """Загружает правила для проверки из конфига"""
        super().set_rules(rules)
        # Извлекаем конкретные правила для этой проверки
        if rules and 'system' in rules:
            self.required_format = rules.get('system', {
                'allowed_formats': [".docx", ".pdf", ".rtf"],
                'max_file_size_mb': 50
            })


    def run(self, document: Document) -> CheckResult:
        """Проверяет формат файла на соответствие требованиям"""
        errors = []

        # Проверяем, загружены ли правила
        if not hasattr(self, 'required_format'):
            error = ValidationError(
                check_name=self.check_name,
                description="Правила проверки не загружены",
                recommendation="Проверьте конфигурационный файл",
                gost_reference="ГОСТ 2.105"
            )
            return self._create_result(CheckStatus.ERROR, [error])

        # Проверяем суффикс файла и размер
        file_path = document.file_path
        path = Path(file_path)
        if not path.exists():
            error = ValidationError(
                check_name=self.check_name,
                description="Используется тестовый файл",
                recommendation="Проверьте наличие реального файла для верификации",
                gost_reference="ГОСТ 2.105"
            )
            errors.append(error)
        else:
            suffix = path.suffix.lower()
            if suffix not in self.required_format['allowed_formats']:
                error = ValidationError(
                    check_name=self.check_name,
                    description=f"Формат файла ({suffix}) не соответсвует стандарту ",
                    recommendation=f"Используйте следующие разрешения файлов: {self.required_format['allowed_formats']}",
                    gost_reference="ГОСТ 2.105"
                )
                errors.append(error)
            file_size = path.stat().st_size
            if file_size > self.required_format['max_file_size_mb'] * 1024 * 1024:
                error = ValidationError(
                    check_name=self.check_name,
                    description="Размер файла превышает допустимый",
                    recommendation="Уменьшите размер проверяемого файла до <=50 мб",
                    gost_reference="ГОСТ 2.105"
                )
                errors.append(error)

        status = CheckStatus.FAILED if errors else CheckStatus.PASSED
        return self._create_result(status, errors)