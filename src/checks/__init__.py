from .section_checker import SectionCheck
from .table_checker import TableCheck
from .numbering_checker import PageNumberingCheck
from .figure_checker import FigureCheck

__all__ = ['SectionCheck', 'TableCheck', 'PageNumberingCheck', 'FigureCheck']

def get_all_checks():
    """Фабрика для создания всех проверок"""
    return [
        SectionCheck(),
        TableCheck(),
        PageNumberingCheck(),
        FigureCheck()
    ]