"""
Searchable Document - Pre-loaded document for fast searching
"""
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any
from app.document_scanner.search_result import SearchResult


class SearchableDocument:
    """A document that's loaded into memory for fast searching"""

    def __init__(self, config: Dict[str, Any]):
        """Initialize searchable document

        Args:
            config: Document configuration dictionary
        """
        self.config = config
        self.file_path = Path(config['file_path'])
        self.file_name = config['file_name']
        self.doc_type = config['doc_type']
        self.header_row = config['header_row']
        self.search_columns = config['search_columns']
        self.return_columns = config['return_columns']
        self.precondition_enabled = config.get('precondition_enabled', False)
        self.precondition = config.get('precondition', '')

        self.df = None  # Will hold the loaded DataFrame
        self.load_error = None

        # Load the document immediately
        self._load()

    def _load(self):
        """Load the document into memory"""
        try:
            if not self.file_path.exists():
                self.load_error = "File not found"
                print(f"  ❌ ERROR: File not found: {self.file_path}")
                return

            # Load based on file type
            if self.file_path.suffix.lower() in ['.xlsx', '.xls']:
                self.df = pd.read_excel(self.file_path, header=self.header_row)
            else:
                # Try CSV first
                try:
                    self.df = pd.read_csv(
                        self.file_path, header=self.header_row)
                except Exception:
                    # Fall back to tab-separated
                    self.df = pd.read_csv(
                        self.file_path, sep='\t', header=self.header_row)

            print(
                f"  ✓ Loaded '{self.file_name}': {len(self.df)} rows, {len(self.df.columns)} columns")

        except Exception as e:
            self.load_error = str(e)
            print(f"  ❌ ERROR loading '{self.file_name}': {e}")
            import traceback
            traceback.print_exc()

    def is_loaded(self) -> bool:
        """Check if document loaded successfully"""
        return self.df is not None and self.load_error is None

    def check_precondition(self, search_term: str) -> bool:
        """Check if search meets precondition

        Args:
            search_term: The search term

        Returns:
            True if precondition is met or not enabled
        """
        if not self.precondition_enabled or not self.precondition:
            return True

        try:
            result = eval(self.precondition, {"__builtins__": {}}, {
                          "search_term": search_term})
            return bool(result)
        except Exception as e:
            print(
                f"  ⚠️  Error evaluating precondition '{self.precondition}': {e}")
            return False

    def search(self, search_term: str) -> List[SearchResult]:
        """Search this document for the given term

        Args:
            search_term: Term to search for

        Returns:
            List of SearchResult objects
        """
        results = []

        if not self.is_loaded():
            print(f"  ⏭️  Skipped '{self.file_name}': {self.load_error}")
            return results

        # Check precondition
        if not self.check_precondition(search_term):
            print(f"  ⏭️  Skipped '{self.file_name}': Precondition not met")
            return results

        print(f"  🔎 Searching '{self.file_name}'...")

        # Search in each search column
        for search_col in self.search_columns:
            if search_col not in self.df.columns:
                print(f"     ❌ Column '{search_col}' not found!")
                continue

            # Find matches (case-insensitive contains)
            matches = self.df[self.df[search_col].astype(
                str).str.contains(search_term, case=False, na=False)]

            if len(matches) > 0:
                print(f"     Found {len(matches)} match(es) in '{search_col}'")

            # Create results for each match
            for idx, row in matches.iterrows():
                # Extract return column data
                matched_data = {}
                for return_col in self.return_columns:
                    if return_col in self.df.columns:
                        matched_data[return_col] = row[return_col]

                result = SearchResult(
                    search_term=search_term,
                    document_name=self.file_name,
                    document_type=self.doc_type,
                    matched_row_data=matched_data
                )

                results.append(result)

        return results

    def reload(self):
        """Reload the document from disk"""
        self.df = None
        self.load_error = None
        self._load()

    def get_info(self) -> str:
        """Get document information string"""
        if self.is_loaded():
            return f"{self.file_name} ({len(self.df)} rows, {len(self.df.columns)} cols)"
        else:
            return f"{self.file_name} (Error: {self.load_error})"
