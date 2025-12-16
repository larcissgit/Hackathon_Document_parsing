import sys
import argparse
from pathlib import Path

# Настройка пути для импортов
sys.path.insert(0, str(Path(__file__).parent.parent))


from src.utils import ConfigLoader
from src.core import Parser, Validator, Reporter
from src.checks import get_all_checks



def main():

    """Основная функция с поддержкой аргументов командной строки"""
    parser = argparse.ArgumentParser(
        description='Авто-верификатор конструкторской документации по ГОСТ 2.105',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
            Примеры использования:
            python src/main.py files/document.docx
            python src/main.py files/document.docx --config config/my_rules.yaml
            python src/main.py files/document.docx --output report/report_1.json --verbose
        """
    )

    parser.add_argument('document', help='Путь к проверяемому документу')
    parser.add_argument('--config', '-c', default='config/gost_2_105_rules.yaml',
                        help='Путь к конфигурационному файлу (по умолчанию: config/gost_rules.yaml)')
    parser.add_argument('--output', '-o', default='reports/validation_report.json',
                        help='Путь для сохранения отчета (по умолчанию: validation_report.json)')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Подробный вывод в консоль')

    args = parser.parse_args()



    if args.verbose:
        print("=== Авто-верификатор ГОСТ 2.105 ===")
        print(f"Документ: {args.document}")
        print(f"Конфиг: {args.config}")
        print(f"Вывод: {args.output}")

    # 1. ЗАГРУЗКА КОНФИГУРАЦИИ
    if args.verbose:
        print("\n[1] Загрузка конфигурации...")
    config = ConfigLoader.load_yaml(args.config)

    # 2. ИНИЦИАЛИЗАЦИЯ КОМПОНЕНТОВ
    if args.verbose:
        print("[2] Инициализация компонентов...")

    doc_parser = Parser()
    validator = Validator(config)

    # 3. РЕГИСТРАЦИЯ ВСЕХ ПРОВЕРОК
    if args.verbose:
        print("[3] Регистрация проверок...")

    # Автоматически создаем все 7 проверок
    checks = get_all_checks()
    for check in checks:
        validator.register_check(check)
        if args.verbose:
            status = "✓" if check.check_id in config.get('check_settings', {}).get('enabled_checks', []) else "✗"
            print(f"  {status} {check.check_name}")

    # 4. ПАРСИНГ ДОКУМЕНТА
    if args.verbose:
        print(f"[4] Парсинг документа: {args.document}")

    parsed_document = doc_parser.parse(args.document)

    # 5. ВАЛИДАЦИЯ
    if args.verbose:
        print("[5] Запуск проверок...")

    results = validator.validate(parsed_document)

    # 6. ГЕНЕРАЦИЯ И СОХРАНЕНИЕ ОТЧЕТА
    if args.verbose:
        print("[6] Генерация отчета...")

    report = Reporter.generate_report(document=parsed_document, results=results)
    Reporter.save_report(report_data=report, report_path=args.output)

    # 7. ВЫВОД СТАТИСТИКИ
    stats = report['summary']
    print(f"\n{'=' * 50}")
    print("ИТОГИ ПРОВЕРКИ:")
    print(f"  Документ: {Path(args.document).name}")
    print(f"  Всего проверок: {stats['total_checks']}")
    print(f"  ✓ Пройдено: {stats['passed']}")
    print(f"  ✗ Не пройдено: {stats['failed']}")
    print(f"  Успешность: {stats['success_rate']}")
    print(f"\nПодробный отчет сохранен в: {args.output}")
    print('=' * 50)


if __name__ == "__main__":
    main()