import json
from datetime import datetime
from typing import List
from src.models import Document, CheckResult
from typing import Dict, Any


class Reporter:
    """Формирует финальный отчёт в формате JSON"""

    @staticmethod
    def generate_report(*, document: Document, results: List[CheckResult]) -> dict:
        """Создаёт структуру данных для отчёта"""

        # Считаем статистику
        total = len(results)
        passed = sum(1 for r in results if r.status.value == "PASSED")

        report = {
            "document": document.file_path,
            "validation_date": datetime.now().isoformat(),
            "summary": {
                "total_checks": total,
                "passed": passed,
                "failed": total - passed,
                "success_rate": f"{(passed / total) * 100:.1f}%" if total > 0 else "0%"
            },
            "checks": []
        }

        # Добавляем детали по каждой проверке
        for result in results:
            check_info = {
                "id": result.check_id,
                "name": result.check_name,
                "status": result.status.value,
                "errors_count": len(result.errors),
                "errors": []
            }

            for error in result.errors:
                check_info["errors"].append({
                    "description": error.description,
                    "recommendation": error.recommendation,
                    "gost_reference": error.gost_reference
                })

            report["checks"].append(check_info)

        return report

    @staticmethod
    def save_report(*, report_data: Dict[str, Any], report_path: str):
        """Сохраняет отчет в JSON файл"""
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)