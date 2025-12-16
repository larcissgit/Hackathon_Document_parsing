import re
from src.checks.base_checker import BaseCheck
from src.models import Document, CheckResult, CheckStatus, ValidationError


class FormulaCheck(BaseCheck):
    """Проверка 6: Оформление формул"""

    def __init__(self):
        super().__init__(
            check_id="formulas",
            check_name="Оформление формул"
        )
        # Значения по умолчанию
        self.numbering_pattern = r'^\((\d+(\.\d+)*)\)$'
        self.require_reference = True

    def set_rules(self, rules: dict):
        """Загружает правила для проверки формул из конфига"""
        super().set_rules(rules)
        # Безопасное извлечение правил
        self.numbering_pattern = self._safe_get_rule(
            'gost_2_105.formulas.numbering_pattern',
            self.numbering_pattern
        )
        self.require_reference = self._safe_get_rule(
            'gost_2_105.formulas.require_reference',
            self.require_reference
        )

    def run(self, document: Document) -> CheckResult:
        """Улучшенная проверка формул с фильтрацией ложных срабатываний"""
        errors = []
        text = document.raw_text

        # 1. Ищем формулы по строгому ГОСТ-паттерну
        gost_formula_pattern = r'\((\d+(\.\d+)*)\)'  # Только круглые скобки
        gost_matches = list(re.finditer(gost_formula_pattern, text))

        # 2. Фильтруем ложные срабатывания
        real_formulas = []
        for match in gost_matches:
            formula = match.group(0)
            position = match.start()

            # Контекст вокруг формулы
            start_ctx = max(0, position - 30)
            end_ctx = min(len(text), position + 30)
            context = text[start_ctx:end_ctx].lower()

            # ПРИЗНАКИ РЕАЛЬНОЙ ФОРМУЛЫ:
            # - Упоминание "формула" рядом
            # - Математические символы вокруг: =, +, -, *, /, ^, Σ, ∫
            # - Наличие переменных: x, y, z, a, b, c
            # - Отсутствие слов "год", "рисунок", "страница", "пункт"

            is_likely_formula = (
                    'формул' in context or
                    any(math_char in context for math_char in ['=', '+', '-', '*', '/', '^'])
            )

            is_likely_false_positive = any(
                false_word in context for false_word in ['год', 'рис', 'стр', 'пункт', 'см.']
            )

            if is_likely_formula and not is_likely_false_positive:
                real_formulas.append({
                    'formula': formula,
                    'number': match.group(1),
                    'position': position,
                    'context': context
                })

        print(f"[FormulaCheck] Найдено формул по ГОСТ: {len(gost_matches)}")
        print(f"[FormulaCheck] Отфильтровано реальных формул: {len(real_formulas)}")

        # 3. Проверяем формулы в неправильных скобках
        wrong_brackets_patterns = [
            (r'\[(\d+(\.\d+)*)\]', 'квадратных'),
            (r'\{(\d+(\.\d+)*)\}', 'фигурных')
        ]

        for pattern, bracket_type in wrong_brackets_patterns:
            for match in re.finditer(pattern, text):
                # Проверяем контекст - это действительно формула?
                context_start = max(0, match.start() - 20)
                context_end = min(len(text), match.end() + 20)
                context = text[context_start:context_end].lower()

                if 'формул' in context or 'уравнен' in context:
                    errors.append(ValidationError(
                        check_name=self.check_name,
                        description=f"Формула {match.group(0)} в {bracket_type} скобках",
                        recommendation=f"Исправьте на круглые скобки: ({match.group(1)})",
                        gost_reference="ГОСТ 2.105, раздел 5.6"
                    ))

        # 4. Проверяем ссылки для реальных формул
        for formula_info in real_formulas:
            formula_num = formula_info['number']
            ref_patterns = [
                rf'формул[аеуы]\s*\({formula_num}\)',
                rf'по формуле\s*\({formula_num}\)',
                rf'ф-ла\s*\({formula_num}\)',
                rf'ф\.\s*\({formula_num}\)',
                rf'\(\({formula_num}\)\)',  # Двойные скобки - частый стиль ссылок
            ]

            ref_found = False
            for pattern in ref_patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    ref_found = True
                    break

            if not ref_found:
                # Проверяем, есть ли хоть какая-то ссылка
                simple_ref = re.search(rf'\({formula_num}\)', text)
                if simple_ref and simple_ref.start() != formula_info['position']:
                    # Есть упоминание, но не в форме "формула (X)"
                    pass  # Не считаем ошибкой - возможно, контекст иной
                else:
                    errors.append(ValidationError(
                        check_name=self.check_name,
                        description=f"Не найдена ссылка на формулу {formula_info['formula']}",
                        recommendation=f"Добавьте в текст: '... по формуле {formula_info['formula']} ...'",
                        gost_reference="ГОСТ 2.105, раздел 5.6"
                    ))

        print(f"[FormulaCheck] Итоговое количество ошибок: {len(errors)}")

        status = CheckStatus.FAILED if errors else CheckStatus.PASSED
        return self._create_result(status, errors)

    def _check_formula_references(self, text: str, formulas: list, errors: list):
        """Проверяет наличие ссылок на формулы в тексте"""
        for formula in formulas:
            # Ищем ссылки вида "формула (1)" или "по формуле (1.5)"
            ref_patterns = [
                rf'[Фф]ормул[аеуы]\s*[\(\[]?{re.escape(formula["number"])}[\)\]]?',
                rf'[Пп]о\s+формуле\s*[\(\[]?{re.escape(formula["number"])}[\)\]]?',
                rf'\([\(\[]?{re.escape(formula["number"])}[\)\]]?\)',
            ]

            ref_found = False
            for pattern in ref_patterns:
                if re.search(pattern, text):
                    ref_found = True
                    break

            if not ref_found:
                errors.append(ValidationError(
                    check_name=self.check_name,
                    description=f"Отсутствует ссылка на формулу ({formula['number']}) в тексте",
                    recommendation=f"Добавьте ссылку: '... по формуле ({formula['number']}) ...'",
                    gost_reference="ГОСТ 2.105, раздел 5.6"
                ))