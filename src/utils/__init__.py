SUPPORTED_FORMATS = [".docx", ".pdf", ".txt"]
SUPPORTED_ENCODINGS = ['utf-8', 'utf-8-sig', 'utf-16', 'cp1251', 'windows-1251']

from .config_loader import ConfigLoader
from .file_reader import FileReader

__all__ = [ConfigLoader, FileReader]
