import pandas as pd
import chardet
from pathlib import Path
from loguru import logger

def detect_encoding(file_path):
    """Detect file encoding"""
    with open(file_path, 'rb') as f:
        raw_data = f.read()
    return chardet.detect(raw_data)['encoding']

def safe_read_csv(file_path, **kwargs):
    """Safely read CSV file with automatic encoding detection"""
    try:
        return pd.read_csv(file_path, **kwargs)
    except UnicodeDecodeError:
        encoding = detect_encoding(file_path)
        logger.info(f"Detected encoding: {encoding} for file {file_path}")
        return pd.read_csv(file_path, encoding=encoding, **kwargs)

def safe_read_json(file_path, **kwargs):
    """Safely read JSON file with automatic encoding handling"""
    try:
        return pd.read_json(file_path, **kwargs)
    except UnicodeDecodeError:
        encoding = detect_encoding(file_path)
        logger.info(f"Detected encoding: {encoding} for file {file_path}")
        return pd.read_json(file_path, encoding=encoding, **kwargs)

def safe_read_excel(file_path, **kwargs):
    """Safely read Excel file"""
    try:
        return pd.read_excel(file_path, **kwargs)
    except Exception as e:
        logger.error(f"Error reading Excel file {file_path}: {e}")
        raise