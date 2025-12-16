from .section_checker import SectionCheck
from .section_numbering_checker import SectionNumberingCheck
from .page_numbering_checker import PageNumberingCheck
from .table_checker import TableCheck
from .figure_checker import FigureCheck
from .formula_checker import FormulaCheck
from .appendix_checker import AppendixCheck
from .format_checker import FormatCheck

# Все 7 основных проверок ГОСТ 2.105 + проверка формата
ALL_CHECKS = [
    SectionCheck,
    SectionNumberingCheck,
    PageNumberingCheck,
    TableCheck,
    FigureCheck,
    FormulaCheck,
    AppendixCheck,
    FormatCheck
]


def get_all_checks(config: dict = None):
    checks = []
    for CheckClass in ALL_CHECKS:
        check = CheckClass()
        if config:
            check.set_rules(config)
        checks.append(check)

    return checks