"""Quick test to verify config paths"""
import sys
sys.path.insert(0, 'swiss_army_tool')

from app.core.config_manager import ConfigManager, DocumentScannerConfig

print("="*60)
print("CONFIG PATH TEST")
print("="*60)
print(f"CONFIG_DIR: {ConfigManager.CONFIG_DIR}")
print(f"CONFIG_DIR (absolute): {ConfigManager.CONFIG_DIR.absolute()}")
print(f"DOCUMENT_SCANNER_CONFIG: {ConfigManager.DOCUMENT_SCANNER_CONFIG}")
print(f"Full path: {ConfigManager.get_config_path(ConfigManager.DOCUMENT_SCANNER_CONFIG).absolute()}")
print(f"File exists: {ConfigManager.config_exists(ConfigManager.DOCUMENT_SCANNER_CONFIG)}")

print("\n" + "="*60)
print("TESTING SAVE/LOAD")
print("="*60)

# Test save
test_docs = [
    {
        'file_name': 'test.csv',
        'file_path': 'C:/test.csv',
        'header_row': 0,
        'search_columns': ['Col1'],
        'return_columns': ['Col1', 'Col2']
    }
]

print("\nSaving test document...")
result = DocumentScannerConfig.save_documents(test_docs)
print(f"Save result: {result}")

print("\nLoading documents...")
loaded = DocumentScannerConfig.load_documents()
print(f"Loaded {len(loaded)} document(s)")
if loaded:
    print(f"First document: {loaded[0]}")
