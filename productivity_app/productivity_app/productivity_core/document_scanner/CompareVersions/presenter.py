"""
Compare Versions Presenter - Logic for comparing document versions
"""
from PySide6.QtCore import QObject
from PySide6.QtWidgets import QFileDialog, QMessageBox
from productivity_core.document_scanner.CompareVersions.view import CompareVersionsView
from productivity_core.document_scanner.CompareVersions.config_dialog import ComparisonConfigDialog
from productivity_core.document_scanner.document_store import DocumentStore
from typing import Dict, Any, Optional
import pandas as pd


class CompareVersionsPresenter(QObject):
    """Presenter for comparing document versions"""

    def __init__(self, context, model):
        super().__init__()
        self.context = context
        self.model = model
        self.view = CompareVersionsView()
        self.document_store = DocumentStore()

        # Track current state
        self.current_document_id = None
        self.current_versions = []
        self.custom_file1_path = None
        self.custom_file2_path = None

        # Cached data
        self.data1 = None
        self.data2 = None
        self.comparison_config = None
        self.full_results = None  # Store unfiltered results
        self.filtered_mode = False

        # Connect view signals
        self.view.document_selected.connect(self.on_document_selected)
        self.view.version1_selected.connect(self.on_version1_selected)
        self.view.version2_selected.connect(self.on_version2_selected)
        self.view.custom_file1_dropped.connect(self.on_custom_file1_dropped)
        self.view.custom_file2_dropped.connect(self.on_custom_file2_dropped)
        self.view.compare_requested.connect(self.on_compare_requested)
        self.view.filter_changes_requested.connect(self.on_filter_changes)
        self.view.export_requested.connect(self.on_export_results)

    def start_loading(self):
        """Initialize the compare versions tab"""
        print("Compare Versions: Loading...")

        # Load documents from store
        documents_by_project = self.document_store.get_all_documents()
        self.view.populate_documents(documents_by_project)

        print(
            f"Compare Versions: Loaded {sum(len(docs) for docs in documents_by_project.values())} documents")

    def on_document_selected(self, document_id: str):
        """Handle document selection

        Args:
            document_id: Selected document ID
        """
        print(f"Document selected: {document_id}")
        self.current_document_id = document_id

        # Clear custom files when selecting a document
        self.custom_file1_path = None
        self.custom_file2_path = None
        self.view.drop_area1.clear()
        self.view.drop_area2.clear()

        if document_id == "custom":
            # Custom document - only drag-drop available
            self.view.populate_versions([])
            self.view.update_status("Drop custom files to compare", "blue")
        else:
            # Load versions for this document
            versions = self._get_document_versions(document_id)
            self.current_versions = versions
            self.view.populate_versions(versions)
            self.view.update_status(
                f"Loaded {len(versions)} versions", "green")

    def on_version1_selected(self, version: str):
        """Handle version 1 selection"""
        print(f"Version 1 selected: {version}")
        if version != "Custom":
            self.custom_file1_path = None
            self.view.drop_area1.clear()

    def on_version2_selected(self, version: str):
        """Handle version 2 selection"""
        print(f"Version 2 selected: {version}")
        if version != "Custom":
            self.custom_file2_path = None
            self.view.drop_area2.clear()

    def on_custom_file1_dropped(self, file_path: str):
        """Handle custom file dropped for version 1"""
        print(f"Custom file 1: {file_path}")
        self.custom_file1_path = file_path
        self.view.version1_combo.setCurrentText("Custom")

    def on_custom_file2_dropped(self, file_path: str):
        """Handle custom file dropped for version 2"""
        print(f"Custom file 2: {file_path}")
        self.custom_file2_path = file_path
        self.view.version2_combo.setCurrentText("Custom")

    def on_compare_requested(self):
        """Handle compare button clicked"""
        try:
            # Load data for both versions
            self.data1 = self._load_version_data(
                self.view.get_selected_version1(),
                self.custom_file1_path,
                "Version 1"
            )

            self.data2 = self._load_version_data(
                self.view.get_selected_version2(),
                self.custom_file2_path,
                "Version 2"
            )

            if self.data1 is None or self.data2 is None:
                return

            # Get common columns
            common_columns = list(set(self.data1.columns)
                                  & set(self.data2.columns))

            if not common_columns:
                QMessageBox.warning(
                    self.view,
                    "No Common Columns",
                    "The two versions have no columns in common. Cannot compare."
                )
                return

            # Show configuration dialog
            dialog = ComparisonConfigDialog(common_columns, self.view)
            if dialog.exec_() != dialog.accepted:
                return

            self.comparison_config = dialog.get_config()

            # Perform comparison
            results_df = self._compare_versions(
                self.data1,
                self.data2,
                self.comparison_config
            )

            # Store full results
            self.full_results = results_df
            self.filtered_mode = False

            # Display results
            self.view.display_comparison_results(results_df)

        except Exception as e:
            QMessageBox.critical(
                self.view,
                "Comparison Error",
                f"Error comparing versions:\n{str(e)}"
            )
            import traceback
            traceback.print_exc()

    def on_filter_changes(self):
        """Toggle between showing all rows and only changed rows"""
        if self.full_results is None:
            return

        if self.filtered_mode:
            # Show all rows
            self.view.display_comparison_results(self.full_results)
            self.view.filter_changes_btn.setText("🔍 Filter Changes Only")
            self.filtered_mode = False
        else:
            # Filter to show only changes
            if "Verdict" in self.full_results.columns:
                filtered = self.full_results[self.full_results["Verdict"]
                                             == "Different"]
                self.view.display_comparison_results(filtered)
                self.view.filter_changes_btn.setText("📋 Show All Rows")
                self.filtered_mode = True
            else:
                QMessageBox.information(
                    self.view,
                    "No Verdict Column",
                    "Cannot filter changes - no verdict column found."
                )

    def on_export_results(self):
        """Export comparison results to file"""
        if self.full_results is None:
            QMessageBox.warning(
                self.view,
                "No Results",
                "No comparison results to export."
            )
            return

        # Get file path from user
        file_path, _ = QFileDialog.getSaveFileName(
            self.view,
            "Export Comparison Results",
            "comparison_results.csv",
            "CSV Files (*.csv);;Excel Files (*.xlsx)"
        )

        if not file_path:
            return

        try:
            # Determine what to export (filtered or all)
            if self.filtered_mode:
                data_to_export = self.full_results[self.full_results["Verdict"] == "Different"]
                export_type = "changes"
            else:
                data_to_export = self.full_results
                export_type = "all rows"

            # Export based on file extension
            if file_path.endswith('.xlsx'):
                data_to_export.to_excel(file_path, index=False)
            else:
                data_to_export.to_csv(file_path, index=False)

            QMessageBox.information(
                self.view,
                "Export Successful",
                f"Exported {len(data_to_export)} rows ({export_type}) to:\n{file_path}"
            )

        except Exception as e:
            QMessageBox.critical(
                self.view,
                "Export Error",
                f"Error exporting results:\n{str(e)}"
            )

    def _get_document_versions(self, document_id: str) -> list:
        """Get available versions for a document

        Args:
            document_id: Document identifier

        Returns:
            List of version strings
        """
        # Search through all projects for this document
        documents_by_project = self.document_store.get_all_documents()

        for project, documents in documents_by_project.items():
            for doc in documents:
                if doc["id"] == document_id:
                    return doc.get("versions", [])

        return []

    def _load_version_data(self, version: str, custom_path: Optional[str], label: str) -> Optional[pd.DataFrame]:
        """Load data for a specific version

        Args:
            version: Version string or "Custom"
            custom_path: Path to custom file (if version is "Custom")
            label: Label for error messages

        Returns:
            DataFrame with version data, or None on error
        """
        try:
            if version == "Custom":
                if not custom_path:
                    QMessageBox.warning(
                        self.view,
                        f"No Custom File for {label}",
                        f"Please drop a custom file for {label} or select a version."
                    )
                    return None

                # Load custom file
                print(f"Loading custom file for {label}: {custom_path}")
                return self.document_store.get_custom_document_data(custom_path)

            else:
                # Load from document store
                if not self.current_document_id:
                    QMessageBox.warning(
                        self.view,
                        "No Document Selected",
                        "Please select a document first."
                    )
                    return None

                print(
                    f"Loading {label}: {self.current_document_id} @ {version}")
                return self.document_store.get_document_data(self.current_document_id, version)

        except Exception as e:
            QMessageBox.critical(
                self.view,
                f"Error Loading {label}",
                f"Failed to load {label}:\n{str(e)}"
            )
            return None

    def _compare_versions(self, df1: pd.DataFrame, df2: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """Compare two dataframes based on configuration

        Args:
            df1: First version dataframe
            df2: Second version dataframe
            config: Comparison configuration with keys:
                - key_column: Column to use as key
                - compare_columns: Columns to compare
                - show_columns: Columns to show in results

        Returns:
            DataFrame with comparison results
        """
        key_col = config['key_column']
        compare_cols = config['compare_columns']
        show_cols = config['show_columns']

        # Ensure key column and compare columns exist in both dataframes
        for col in [key_col] + compare_cols:
            if col not in df1.columns:
                raise ValueError(f"Column '{col}' not found in Version 1")
            if col not in df2.columns:
                raise ValueError(f"Column '{col}' not found in Version 2")

        # Set key column as index
        df1_indexed = df1.set_index(key_col)
        df2_indexed = df2.set_index(key_col)

        # Find all keys (union of both versions)
        all_keys = set(df1_indexed.index) | set(df2_indexed.index)

        results = []

        for key in all_keys:
            row_result = {key_col: key}

            # Check if key exists in both versions
            in_v1 = key in df1_indexed.index
            in_v2 = key in df2_indexed.index

            if not in_v1:
                row_result['Verdict'] = "Only in Version 2"
                # Add Version 2 data
                for col in show_cols:
                    if col != key_col and col in df2_indexed.columns:
                        row_result[f"{col}_V2"] = df2_indexed.loc[key, col]

            elif not in_v2:
                row_result['Verdict'] = "Only in Version 1"
                # Add Version 1 data
                for col in show_cols:
                    if col != key_col and col in df1_indexed.columns:
                        row_result[f"{col}_V1"] = df1_indexed.loc[key, col]

            else:
                # Key exists in both - compare columns
                differences = []

                for col in compare_cols:
                    if col == key_col:
                        continue

                    val1 = df1_indexed.loc[key, col]
                    val2 = df2_indexed.loc[key, col]

                    # Convert to string for comparison (handles NaN, None, etc.)
                    str1 = str(val1) if pd.notna(val1) else ""
                    str2 = str(val2) if pd.notna(val2) else ""

                    if str1 != str2:
                        differences.append(col)

                # Set verdict
                if differences:
                    row_result['Verdict'] = "Different"
                    row_result['Changed_Columns'] = ", ".join(differences)
                else:
                    row_result['Verdict'] = "Same"

                # Add data from both versions for show columns
                for col in show_cols:
                    if col == key_col:
                        continue

                    if col in df1_indexed.columns:
                        row_result[f"{col}_V1"] = df1_indexed.loc[key, col]
                    if col in df2_indexed.columns:
                        row_result[f"{col}_V2"] = df2_indexed.loc[key, col]

            results.append(row_result)

        # Convert to DataFrame
        results_df = pd.DataFrame(results)

        # Reorder columns: Key, Verdict, Changed_Columns (if exists), then data columns
        ordered_cols = [key_col, 'Verdict']
        if 'Changed_Columns' in results_df.columns:
            ordered_cols.append('Changed_Columns')

        # Add remaining columns
        remaining_cols = [
            col for col in results_df.columns if col not in ordered_cols]
        ordered_cols.extend(remaining_cols)

        results_df = results_df[ordered_cols]

        return results_df
