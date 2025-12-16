import pytest
from src.core.parser import Parser
from src.core.validator import Validator
from src.checks import get_all_checks


def test_all_checks_integration():
    """Тест интеграции всех 7 проверок"""

    # 1. Подготовка
    parser = Parser()
    validator = Validator()

    # 2. Создаем документ с ошибками для всех проверок
    test_text = """Введение
1.1 Назначение (ошибка: должен быть 1., а не 1.1)
Таблица 1 Основные параметры (ошибка: без точки)
Рисунок 2 Схема (ошибка: без номера версии)
Формула [1] (ошибка: должны быть круглые скобки)
ПРИЛОЖЕНИЕ А (правильно)
странице 1 (ошибка: первая страница не нумеруется)"""

    # 3. Запускаем все проверки
    checks = get_all_checks()
    for check in checks:
        validator.register_check(check)

    # 4. Парсим и проверяем
    document = parser.parse_text(test_text)
    results = validator.validate(document)

    # 5. Проверяем, что все проверки сработали
    assert len(results) == 8
    print(f"\nПрошло проверок: {sum(1 for r in results if r.status.value == 'PASSED')}/8")

    for result in results:
        print(f"{result.check_name}: {result.status.value} (ошибок: {len(result.errors)})")