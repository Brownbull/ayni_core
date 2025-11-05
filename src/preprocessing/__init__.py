"""
GabeDA Preprocessing Package

Modules:
- loaders: Data loading from CSV, Excel, DataFrame
- validators: Data validation (columns, quality) - NO date range validation
- transformers: Column mapping and type conversion
- schema: Schema processing coordinator
"""

from src.preprocessing.loaders import DataLoader
from src.preprocessing.validators import DataValidator, ValidationResult
from src.preprocessing.transformers import ColumnMapper, TypeConverter
from src.preprocessing.schema import SchemaProcessor, ProcessedSchema

__all__ = [
    'DataLoader',
    'DataValidator', 'ValidationResult',
    'ColumnMapper', 'TypeConverter',
    'SchemaProcessor', 'ProcessedSchema'
]
