import re
from src.checks.base_checker import BaseCheck
from src.models import Document, CheckResult, CheckStatus, ValidationError


class AppendixCheck(BaseCheck):
    """Проверка 7: Оформление приложений"""

    def __init__(self):
        super().__init__(
            check_id="appendices",
            check_name="Оформление приложений"
        )
        # Значения по умолчанию
        self.appendix_pattern = r'^ПРИЛОЖЕНИЕ\s+[А-Я]$'
        self.require_reference = True
        self.allowed_types = None
        self.max_designation_length = None
        self.require_uppercase = True
        self.require_space = True
        self.allow_dot_after = True
        self.allow_parentheses = True

    def set_rules(self, rules: dict):
        """Загружает правила для проверки приложений из конфига"""
        super().set_rules(rules)

        # Безопасное извлечение правил со значениями по умолчанию
        config = self._safe_get_rule('gost_2_105.appendices', {})

        # Паттерн для поиска
        self.appendix_pattern = config.get('pattern', r'^ПРИЛОЖЕНИЕ\s+[А-ЯA-Z\d]')

        # Допустимые типы обозначений
        self.allowed_types = config.get('allowed_designations', {}).get('types',
                                                                        ["cyrillic", "latin", "numeric"])

        # Максимальная длина обозначения
        self.max_designation_length = config.get('allowed_designations', {}).get('max_length', 2)

        # Настройки строгости
        self.require_uppercase = config.get('validation', {}).get('require_uppercase', True)
        self.require_space = config.get('validation', {}).get('require_space', True)
        self.allow_dot_after = config.get('validation', {}).get('allow_dot_after', True)
        self.allow_parentheses = config.get('validation', {}).get('allow_parentheses', True)

        # Общие настройки
        self.require_reference = config.get('require_reference', True)

        print(f"[AppendixCheck] Настройки: типы={self.allowed_types}, "
              f"макс.длина={self.max_designation_length}")

    def run(self, document: Document) -> CheckResult:
        """Улучшенная проверка приложений с поддержкой разных форматов"""
        errors = []
        text = document.raw_text
        lines = text.split('\n')

        found_appendix_lines = []

        print(f"\n[AppendixCheck] Поиск приложений в документе...")

        for i, line in enumerate(lines):
            line_stripped = line.strip()

            # Проверяем, начинается ли строка с "ПРИЛОЖЕНИЕ" (регистронезависимо)
            if line_stripped.upper().startswith('ПРИЛОЖЕНИЕ'):

                # Извлекаем обозначение приложения
                designation = self._extract_appendix_designation(line_stripped)

                if designation:
                    # Определяем тип обозначения
                    designation_type = self._get_designation_type(designation)

                    # Проверяем, разрешён ли такой тип
                    is_allowed_type = designation_type in self.allowed_types

                    # Проверяем длину
                    is_valid_length = len(designation) <= self.max_designation_length

                    # Проверяем другие критерии
                    validation_result = self._validate_appendix_format(line_stripped, designation)

                    found_appendix_lines.append({
                        'line_num': i,
                        'original': line_stripped,
                        'designation': designation,
                        'type': designation_type,
                        'is_allowed_type': is_allowed_type,
                        'is_valid_length': is_valid_length,
                        'validation': validation_result
                    })

                    print(f"  Строка {i + 1}: '{line_stripped}'")
                    print(f"    Обозначение: '{designation}' (тип: {designation_type})")
                    print(f"    Разрешённый тип: {'✓' if is_allowed_type else '✗'}")
                    print(f"    Валидная длина: {'✓' if is_valid_length else '✗'}")

        print(f"\n[AppendixCheck] Найдено приложений: {len(found_appendix_lines)}")

        # 2. Проверяем каждое найденное приложение
        for appendix in found_appendix_lines:
            appendix_errors = []

            # Проверка типа обозначения
            if not appendix['is_allowed_type']:
                allowed_types_str = ', '.join(self.allowed_types)
                appendix_errors.append(f"Тип обозначения '{appendix['type']}' не разрешён. "
                                       f"Допустимые типы: {allowed_types_str}")

            # Проверка длины
            if not appendix['is_valid_length']:
                appendix_errors.append(f"Обозначение '{appendix['designation']}' слишком длинное. "
                                       f"Максимум: {self.max_designation_length} символов")

            # Дополнительные проверки формата
            if appendix['validation'].get('has_space_issue'):
                appendix_errors.append("Отсутствует или лишний пробел после 'ПРИЛОЖЕНИЕ'")

            if appendix['validation'].get('has_case_issue'):
                appendix_errors.append("Используйте заглавные буквы для 'ПРИЛОЖЕНИЕ'")

            # Если есть ошибки - добавляем в общий список
            if appendix_errors:
                errors.append(ValidationError(
                    check_name=self.check_name,
                    description=f"Проблемы с оформлением приложения: '{appendix['original']}'",
                    recommendation="; ".join(appendix_errors),
                    gost_reference="ГОСТ 2.105, раздел 6",
                    element=appendix['original'],
                    page=self._estimate_page_number(appendix['line_num'])
                ))
            else:
                print(f"  ✓ Приложение '{appendix['original']}' - корректно")

        # 3. Проверяем ссылки (если требуется)
        if self.require_reference and found_appendix_lines:
            self._check_appendix_references(text, found_appendix_lines, errors)

        status = CheckStatus.FAILED if errors else CheckStatus.PASSED
        return self._create_result(status, errors)



    @staticmethod
    def _is_strict_gost_format(line_upper: str, designation: str) -> bool:
        """Проверяет строгое соответствие ГОСТ"""
        # Строгий формат: "ПРИЛОЖЕНИЕ А"
        strict_pattern = r'^ПРИЛОЖЕНИЕ\s+[А-Я]$'

        if re.match(strict_pattern, line_upper):
            return True

        # Допустимый формат: "ПРИЛОЖЕНИЕ А" с возможными точками, двоеточиями после
        relaxed_pattern = r'^ПРИЛОЖЕНИЕ\s+[А-Я][\.:]?\s*'
        if re.match(relaxed_pattern, line_upper):
            # Проверяем, что обозначение - одна буква кириллицы
            return len(designation) == 1 and designation in 'АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'

        return False

    @staticmethod
    def _extract_appendix_designation(line: str) -> str:
        """Извлекает обозначение приложения из строки"""
        # Приводим к верхнему регистру для анализа
        line_upper = line.upper()

        # Убираем слово "ПРИЛОЖЕНИЕ" и пробелы в начале
        if 'ПРИЛОЖЕНИЕ' in line_upper:
            # Находим позицию после слова "ПРИЛОЖЕНИЕ"
            start_pos = line_upper.find('ПРИЛОЖЕНИЕ') + len('ПРИЛОЖЕНИЕ')
            after_word = line_upper[start_pos:].strip()

            # Извлекаем обозначение (цифры, буквы, возможно с точкой)
            # Допустимые символы: буквы (кириллица/латиница), цифры, точка, тире
            match = re.match(r'^([А-ЯA-Z\d]+[.\-]?)', after_word)
            if match:
                designation = match.group(1)
                # Убираем точку в конце, если есть
                if designation.endswith('.'):
                    designation = designation[:-1]
                return designation

        return ""

    @staticmethod
    def _get_designation_type(designation: str) -> str:
        """Определяет тип обозначения приложения"""
        if not designation:
            return "unknown"

        # Проверяем, состоит ли только из цифр
        if designation.isdigit():
            return "numeric"

        # Проверяем, содержит ли кириллические буквы
        if any('А' <= ch <= 'Я' for ch in designation):
            return "cyrillic"

        # Проверяем, содержит ли латинские буквы
        if any('A' <= ch <= 'Z' for ch in designation):
            return "latin"

        # Смешанный тип
        return "mixed"

    def _validate_appendix_format(self, line: str, designation: str) -> dict:
        """Проверяет формат строки с приложением"""
        result = {
            'has_space_issue': False,
            'has_case_issue': False,
            'has_format_issue': False
        }

        line_upper = line.upper()

        # Проверка пробела после "ПРИЛОЖЕНИЕ"
        if self.require_space:
            # Паттерн: "ПРИЛОЖЕНИЕ" + пробел + обозначение
            if not re.match(r'^ПРИЛОЖЕНИЕ\s+', line_upper):
                result['has_space_issue'] = True

        # Проверка регистра слова "ПРИЛОЖЕНИЕ"
        if self.require_uppercase:
            if not line.startswith('ПРИЛОЖЕНИЕ'):
                result['has_case_issue'] = True

        # Проверка на наличие лишних символов
        # Допустимый паттерн: "ПРИЛОЖЕНИЕ" + пробел + обозначение + (точка/скобки/текст)
        pattern = r'^ПРИЛОЖЕНИЕ\s+' + re.escape(designation)
        if not re.match(pattern, line_upper):
            result['has_format_issue'] = True

        return result

    @staticmethod
    def _estimate_page_number(line_num: int) -> int:
        """Оценивает номер страницы по номеру строки"""
        # Примерная оценка: 50 строк на страницу
        return (line_num // 50) + 1

    def _check_appendix_references(self, text: str, appendices: list, errors: list):
        """Проверяет наличие ссылок на приложения в тексте"""
        text_lower = text.lower()

        for appendix in appendices:
            designation = appendix['designation']
            designation_lower = designation.lower()

            # ПРОСТОЙ ПОДХОД: ищем упоминания без сложных регулярных выражений

            # 1. Сначала проверяем явные ссылки со словом "приложение"
            explicit_ref_found = False

            # Варианты явных ссылок
            explicit_patterns = [
                f'приложени[еия] {designation_lower}',
                f'приложени[еия].{designation_lower}',  # без пробела
                f'приложение {designation_lower}',
                f'приложении {designation_lower}',
                f'прилож. {designation_lower}',
                f'прил. {designation_lower}',
            ]

            for pattern in explicit_patterns:
                if pattern in text_lower:
                    explicit_ref_found = True
                    break

            # 2. Если явных ссылок нет, проверяем простое упоминание обозначения
            if not explicit_ref_found:
                # Ищем обозначение в тексте (не в заголовке приложения)
                # Разделяем текст на слова и ищем обозначение отдельно

                # Простой способ: ищем обозначение, окружённое пробелами или знаками препинания
                words = re.findall(r'\b\w+\b', text_lower)
                if designation_lower in words:
                    # Нашли как отдельное слово - это может быть ссылка
                    pass
                else:
                    # Проверяем, есть ли обозначение в составе других конструкций
                    simple_pattern = rf'\b{re.escape(designation_lower)}\b'
                    if not re.search(simple_pattern, text_lower):
                        # Создаём ошибку только если обозначение совсем не упоминается
                        errors.append(ValidationError(
                            check_name=self.check_name,
                            description=f"Отсутствует ссылка на Приложение {designation}",
                            recommendation=f"Добавьте ссылку в текст: '... в Приложении {designation} ...'",
                            gost_reference="ГОСТ 2.105, раздел 6.2",
                            element=f"Приложение {designation}",
                            page=appendix.get('page')
                        ))
                    else:
                        # Обозначение упоминается, но не как "Приложение X"
                        # Можно добавить предупреждение или игнорировать
                        print(f"  ℹ️  Приложение {designation} упоминается, но не в стандартной форме")