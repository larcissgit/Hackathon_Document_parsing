import yaml
from typing import Dict, Any


class ConfigLoader:
    """Загрузчик конфигурационных файлов"""

    @staticmethod
    def load_yaml(config_path: str) -> Dict[str, Any]:
        """Загружает конфигурацию из YAML файла"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"[Config] Файл {config_path} не найден. Использую настройки по умолчанию.")
            return ConfigLoader._get_default_config()
        except yaml.YAMLError as e:
            print(f"[Config] Ошибка в YAML файле: {e}")
            return ConfigLoader._get_default_config()

    @staticmethod
    def _get_default_config() -> Dict[str, Any]:
        """Возвращает конфигурацию по умолчанию"""
        return {
            "gost_2_105": {
                "required_sections": ["Введение", "Назначение", "Технические характеристики"],
                "page_numbering": {"skip_pages": 2, "style": "арабские"}
            }
        }
