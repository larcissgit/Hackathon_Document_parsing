from dataclasses import dataclass, field
from typing import List, Optional, Any
from enum import Enum

class CheckStatus(Enum):
    PASSED = "PASSED"
    FAILED = "FAILED"
    ERROR = "ERROR"

@dataclass
class ValidationError:
    """Класс для описания одной ошибки"""
    check_name: str
    description: str
    page: Optional[int] = None
    element: Optional[str] = None
    recommendation: str = ""
    gost_reference: str = ""

@dataclass
class CheckResult:
    """Результат выполнения одной проверки"""
    check_id: str
    check_name: str
    status: CheckStatus
    errors: List[ValidationError] = field(default_factory=list)

@dataclass
class Document:
    """Представление загруженного документа"""
    file_path: str
    pages: List[Any] = field(default_factory=list)  # Позже заменим на реальные данные
    sections: List[dict] = field(default_factory=list)
    tables: List[dict] = field(default_factory=list)
    figures: List[dict] = field(default_factory=list)
    raw_text: str = ""