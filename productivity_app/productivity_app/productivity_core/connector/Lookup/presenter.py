"""
Connector Lookup Presenter - Mediates between model and view
"""
from PySide6.QtCore import QObject, Signal, QSortFilterProxyModel, Qt, QTimer, QThread
from .view import LookupConnectorView
from .config import DEFAULT_VISIBLE_COLUMNS
from .filter_redux import ConnectorFilterRedux, FilterCommand, FilterState
from ...presenters.pandas_table_model import PandasTableModel
import pandas as pd


class SearchWorker(QObject):
    """Worker class for performing searches in a background thread"""

    finished = Signal(object)  # filtered DataFrame
    error = Signal(str)  # error message

    def __init__(self, df, filters):
        super().__init__()
        self.df = df
        self.filters = filters
        self._is_cancelled = False

    def cancel(self):
        """Cancel the search operation"""
        self._is_cancelled = True

    def run(self):
        """Execute the search in background thread"""
        try:
            if self._is_cancelled:
                return

            # Apply filters to dataframe
            filtered_df = self.df.copy()

            # Text search filter - supports comma-separated terms
            if self.filters.get('search_text'):
                search_text = self.filters['search_text'].strip()

                # Check if comma-separated (multiple search terms)
                if ',' in search_text:
                    # Split by comma and trim each term
                    search_terms = [term.strip().lower()
                                    for term in search_text.split(',') if term.strip()]

                    # Create OR condition - match any term
                    mask = pd.Series([False] * len(filtered_df),
                                     index=filtered_df.index)
                    for term in search_terms:
                        term_mask = filtered_df.apply(lambda row: row.astype(
                            str).str.lower().str.contains(term, regex=False).any(), axis=1)
                        mask = mask | term_mask

                    filtered_df = filtered_df[mask]
                else:
                    # Single search term
                    search_text = search_text.lower()
                    mask = filtered_df.apply(lambda row: row.astype(
                        str).str.lower().str.contains(search_text, regex=False).any(), axis=1)
                    filtered_df = filtered_df[mask]

            # Standard (Family) filter - multiple selections
            if self.filters.get('standard'):
                standards = [s for s in self.filters['standard'] if s.strip()]
                if standards:
                    filtered_df = filtered_df[filtered_df['Family'].isin(
                        standards)]

            # Shell Type filter - multiple selections
            if self.filters.get('shell_type'):
                shell_types = [
                    st for st in self.filters['shell_type'] if st.strip()]
                if shell_types:
                    filtered_df = filtered_df[filtered_df['Shell Type'].isin(
                        shell_types)]

            # Material filter - multiple selections
            if self.filters.get('material'):
                materials = [m for m in self.filters['material'] if m.strip()]
                if materials:
                    filtered_df = filtered_df[filtered_df['Material'].isin(
                        materials)]

            # Shell Size filter - multiple selections
            if self.filters.get('shell_size'):
                shell_sizes = [
                    ss for ss in self.filters['shell_size'] if ss.strip()]
                if shell_sizes:
                    filtered_df = filtered_df[filtered_df['Shell Size'].isin(
                        shell_sizes)]

            # Insert Arrangement filter - multiple selections
            if self.filters.get('insert_arrangement'):
                insert_arrangements = [
                    ia for ia in self.filters['insert_arrangement'] if ia.strip()]
                if insert_arrangements:
                    filtered_df = filtered_df[filtered_df['Insert Arrangement'].isin(
                        insert_arrangements)]

            # Socket Type filter - multiple selections
            if self.filters.get('socket_type'):
                socket_types = [
                    st for st in self.filters['socket_type'] if st.strip()]
                if socket_types:
                    filtered_df = filtered_df[filtered_df['Socket Type'].isin(
                        socket_types)]

            # Keying filter - multiple selections
            if self.filters.get('keying'):
                keyings = [k for k in self.filters['keying'] if k.strip()]
                if keyings:
                    filtered_df = filtered_df[filtered_df['Keying'].isin(
                        keyings)]

            if self._is_cancelled:
                return

            self.finished.emit(filtered_df)

        except Exception as e:
            self.error.emit(f"Search failed: {str(e)}")


class LookupConnectorPresenter(QObject):
    """Presenter for connector lookup functionality"""

    # Signals
    loading_started = Signal()
    loading_progress = Signal(int, str)
    loading_completed = Signal()
    loading_failed = Signal(str)
    data_loaded = Signal(object)

    def __init__(self, context, connector_model):
        super().__init__()
        self.context = context
        self.model = connector_model
        self.view = LookupConnectorView()

        # Data storage
        self.df = None
        self.filtered_df = None
        self.is_loading = False
        self.current_filters = {}  # Track current search filters

        # Redux state manager (dark release - runs parallel to view)
        self.filter_redux = ConnectorFilterRedux()

        # Search threading
        self._search_worker = None
        self._search_thread = None

        # UI Components
        self.table_model = None
        self.proxy = None

        # Connect model signals
        self._connect_model_signals()

        # Connect view signals
        self.view.search_requested.connect(self.on_search)
        self.view.standards_changed.connect(self.on_standards_changed)
        self.view.clear_filters_requested.connect(self.on_clear_filters)
        self.view.refresh_requested.connect(self.on_refresh)
        self.view.export_requested.connect(self.on_export)
        self.view.reset_requested.connect(self.on_reset)
        self.view.find_alternative_requested.connect(self.on_find_alternative)
        self.view.find_opposite_requested.connect(self.on_find_opposite)

        # Setup UI components
        self._setup_ui_components()

        # Connect internal signals
        self.data_loaded.connect(self._on_data_ready)

        # Connect loading signals to view
        self.loading_started.connect(lambda: self.view.show_loading(True))
        self.loading_progress.connect(self.view.update_loading_progress)
        self.loading_completed.connect(lambda: self.view.show_loading(False))
        self.loading_failed.connect(self.view.show_error)

        # Initialize Redux dark release monitoring (no view impact)
        self._initialize_redux_dark_release()

    def _connect_model_signals(self):
        """Connect to model signals"""
        try:
            if hasattr(self.model, 'data_loaded'):
                self.model.data_loaded.connect(self._on_model_data_loaded)

            if hasattr(self.model, 'loading_progress'):
                self.model.loading_progress.connect(
                    self._on_model_loading_progress)

            if hasattr(self.model, 'loading_failed'):
                self.model.loading_failed.connect(
                    self._on_model_loading_failed)

        except Exception as e:
            print(f"Error connecting model signals: {e}")

    def _on_model_data_loaded(self, data):
        """Handle data loaded from model"""
        print("Connector data loaded from model")
        self.df = self._convert_to_dataframe(data)
        self.data_loaded.emit(self.df)

    def _on_model_loading_progress(self, percent: int, message: str):
        """Forward loading progress"""
        self.loading_progress.emit(percent, message)

    def _on_model_loading_failed(self, error_message: str):
        """Forward loading failure"""
        self.loading_failed.emit(error_message)

    def _setup_ui_components(self):
        """Setup UI components"""
        # Create proxy model for sorting/filtering
        self.proxy = QSortFilterProxyModel()
        self.proxy.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.proxy.setFilterKeyColumn(-1)

        # Configure table view
        self.view.table.setModel(self.proxy)

    def _on_data_ready(self, data):
        """Handle when data is ready for UI"""
        # Create table model with loaded data
        self.table_model = PandasTableModel(data)
        self.proxy.setSourceModel(self.table_model)

        # Apply column visibility settings
        self._apply_column_visibility()

        # Connect selection signal
        if self.view.table.selectionModel():
            self.view.table.selectionModel().selectionChanged.connect(self.on_row_selected)
            self.view.table.selectionModel().selectionChanged.connect(self.on_selection_changed)

        # Update stats
        self._update_stats()

    def _apply_column_visibility(self):
        """Apply default column visibility settings"""
        if self.table_model is None:
            return

        # Get all columns from the dataframe
        all_columns = self.table_model._data.columns.tolist()

        # Hide columns that are not in DEFAULT_VISIBLE_COLUMNS
        for col_index, col_name in enumerate(all_columns):
            if col_name not in DEFAULT_VISIBLE_COLUMNS:
                self.view.table.setColumnHidden(col_index, True)
            else:
                self.view.table.setColumnHidden(col_index, False)

    def _convert_to_dataframe(self, data: dict) -> pd.DataFrame:
        """Convert connector data to DataFrame, limiting to first 100 results"""
        if not data or 'connectors' not in data:
            return pd.DataFrame()

        connectors = data['connectors']

        # Limit to 100 connectors to avoid sending too much data to GUI
        limited_connectors = connectors[:100]

        # Log if we're limiting
        if len(connectors) > 100:
            print(
                f"Limited connector data from {len(connectors)} to 100 records for initial display")

        # Connectors is now a list of dictionaries
        return pd.DataFrame(limited_connectors)

    def start_loading(self):
        """Start loading connector data"""
        if self.is_loading:
            return

        self.is_loading = True
        self.loading_started.emit()

        # Trigger model to load data
        if hasattr(self.model, 'load_async'):
            self.model.load_async()
        else:
            # Fallback
            data = self.model.get_all()
            if data:
                self._on_model_data_loaded(data)

    def on_standards_changed(self, selected_standards: list):
        """Handle change in selected standards - update available filter options

        Args:
            selected_standards: List of selected standard names (e.g., ['D38999', 'VG'])
        """
        print(f"Standards changed: {selected_standards}")

        # Get available filter options from model based on selected standards
        if hasattr(self.model, 'get_available_filter_options'):
            filter_options = self.model.get_available_filter_options(
                selected_standards)

            # Update view with new filter options
            self.view.update_filter_options(filter_options)

            # Dark release: Populate Redux with available options
            self._populate_redux_available_options(filter_options)

            # Dark release: Sync standard selection to Redux
            self._sync_redux_from_view_filters(
                {'standard': selected_standards},
                FilterCommand.STANDARD_CHANGED
            )

            print(f"Updated filter options: {filter_options}")
            data = self.model.get_all()
            if data:
                self._on_model_data_loaded(data)

    def on_search(self, filters: dict):
        """Handle search with filters - runs asynchronously"""
        print(f"Searching with filters: {filters}")

        if self.df is None:
            return

        # Store current filters for history tracking
        self.current_filters = filters.copy()

        # Dark release: Sync to Redux
        self._sync_redux_from_view_filters(filters, FilterCommand.SEARCH_BOX)

        # Cancel any existing search
        if self._search_worker is not None:
            self._search_worker.cancel()
            if self._search_thread is not None and self._search_thread.isRunning():
                self._search_thread.quit()
                self._search_thread.wait()

        # Create worker and thread for async search
        self._search_worker = SearchWorker(self.df, filters)
        self._search_thread = QThread()

        # Move worker to thread
        self._search_worker.moveToThread(self._search_thread)

        # Connect signals
        self._search_thread.started.connect(self._search_worker.run)
        self._search_worker.finished.connect(self._on_search_finished)
        self._search_worker.error.connect(self._on_search_error)
        self._search_worker.finished.connect(self._search_thread.quit)
        self._search_worker.error.connect(self._search_thread.quit)

        # Start search
        self._search_thread.start()

    def _on_search_finished(self, filtered_df):
        """Handle search completion"""
        self.filtered_df = filtered_df
        if self.table_model:
            self.table_model.update(filtered_df)
            self._update_stats()

            # Add to search history with first result info
            result_count = len(filtered_df)
            first_result = None
            if result_count > 0:
                # Get first row data
                first_row = filtered_df.iloc[0]
                first_result = {
                    'Part Number': first_row.get('Part Number', ''),
                    'Part Code': first_row.get('Part Code', '')
                }

            self.view.add_search_to_history(
                self.current_filters, result_count, first_result)

    def _on_search_error(self, error_message: str):
        """Handle search error"""
        self.view.show_error(error_message)

    def on_clear_filters(self):
        """Handle clear filters"""
        if self.df is not None:
            self.filtered_df = self.df.copy()
            if self.table_model:
                self.table_model.update(self.filtered_df)
                self._update_stats()

        # Dark release: Sync to Redux
        self.filter_redux.clear_filters()

    def on_reset(self):
        """Handle reset request - clear filters and show all results like initial state"""
        # Reset to show all data (like initial state)
        if self.df is not None:
            self.filtered_df = self.df.copy()
            if self.table_model:
                self.table_model.update(self.filtered_df)
                self._update_stats()

        # Clear context display
        self.view.context_box.clear()

        # Dark release: Reset Redux
        self.filter_redux.reset_all_filters()

    def on_refresh(self):
        """Handle refresh request"""
        self.start_loading()

    def on_export(self):
        """Handle export request"""
        print("Export requested")
        # To be implemented

    def on_row_selected(self, selected, deselected):
        """Handle row selection - update context display"""
        if not selected.indexes():
            return

        # Get selected row
        index = selected.indexes()[0]
        row = index.row()

        # Get data from model
        if self.table_model:
            row_data = self.table_model.get_record(row)
            self._update_context_display(row_data)

    def on_selection_changed(self, selected, deselected):
        """Handle selection change - update button states"""
        self.view.update_context_buttons_state()

    def on_find_alternative(self, part_code: str):
        """Handle find alternative request

        Args:
            part_code: The part code to find alternatives for
        """
        print(f"Presenter: Finding alternative for {part_code}")

        if self.df is None:
            return

        # Get the original record
        original_record = self.df[self.df['Part Code'] == part_code]
        if original_record.empty:
            print(f"Could not find original record for {part_code}")
            return

        # Call model method to get alternatives
        if hasattr(self.model, 'find_alternative'):
            alternatives = self.model.find_alternative(part_code)
            print(f"Found {len(alternatives)} alternatives")

            # Convert alternatives to DataFrame
            alternatives_df = pd.DataFrame(
                alternatives) if alternatives else pd.DataFrame()

            # Combine original record with alternatives
            # Original record first, then alternatives
            if not alternatives_df.empty:
                combined_df = pd.concat(
                    [original_record, alternatives_df], ignore_index=True)
            else:
                combined_df = original_record.copy()

            # Update table with combined results
            self.filtered_df = combined_df
            if self.table_model:
                self.table_model.update(combined_df)
                self._update_stats()

            # Add to search history with special description
            result_count = len(combined_df)
            first_result = None
            if result_count > 0:
                first_row = combined_df.iloc[0]
                first_result = {
                    'Part Number': first_row.get('Part Number', ''),
                    'Part Code': first_row.get('Part Code', '')
                }

            # Create special filters dict for history
            special_filters = {
                'search_text': f"Alternative to {part_code}",
                '_special_action': 'find_alternative'  # Mark as special action
            }

            self.view.add_search_to_history(
                special_filters, result_count, first_result)
        else:
            print("Model does not support find_alternative")

    def on_find_opposite(self, part_code: str):
        """Handle find opposite request

        Args:
            part_code: The part code to find opposite for
        """
        print(f"Presenter: Finding opposite for {part_code}")

        if self.df is None:
            return

        # Get the original record
        original_record = self.df[self.df['Part Code'] == part_code]
        if original_record.empty:
            print(f"Could not find original record for {part_code}")
            return

        # Call model method to get opposite
        if hasattr(self.model, 'find_opposite'):
            opposite = self.model.find_opposite(part_code)
            print(f"Found opposite: {opposite}")

            # Convert opposite to DataFrame
            if opposite:
                opposite_df = pd.DataFrame([opposite])
                # Combine original record with opposite
                combined_df = pd.concat(
                    [original_record, opposite_df], ignore_index=True)
            else:
                # No opposite found, just show original
                combined_df = original_record.copy()

            # Update table with combined results
            self.filtered_df = combined_df
            if self.table_model:
                self.table_model.update(combined_df)
                self._update_stats()

            # Add to search history with special description
            result_count = len(combined_df)
            first_result = None
            if result_count > 0:
                first_row = combined_df.iloc[0]
                first_result = {
                    'Part Number': first_row.get('Part Number', ''),
                    'Part Code': first_row.get('Part Code', '')
                }

            # Create special filters dict for history
            special_filters = {
                'search_text': f"Opposite to {part_code}",
                '_special_action': 'find_opposite'  # Mark as special action
            }

            self.view.add_search_to_history(
                special_filters, result_count, first_result)
        else:
            print("Model does not support find_opposite")

    def _update_context_display(self, row_data: dict):
        """Update context box with selected connector details

        Supports both text and inline images in the context display.
        Images can be referenced via:
        1. Image path in row_data['image_path'] - will display as separate label
        2. HTML img tags in formatted text
        """
        if not row_data:
            return

        # Generate formatted HTML text with details
        details_html = self._generate_context_html(row_data)

        # Set HTML content if available, otherwise use plain text
        if hasattr(self.view.context_box, 'setHtml'):
            self.view.context_box.setHtml(details_html)
        else:
            # Fallback for plain text widget
            self.view.context_box.setText(details_html)

        # Handle pinout image if present and enabled
        if self.view.pinout_image_label and 'image_path' in row_data:
            image_path = row_data.get('image_path')
            if image_path:
                self._load_image_to_label(
                    image_path, self.view.pinout_image_label)

    def _generate_context_html(self, row_data: dict) -> str:
        """Generate HTML-formatted context details with support for inline images

        Args:
            row_data: Dictionary containing connector data

        Returns:
            HTML string that can be displayed in QTextBrowser or QTextEdit

        Example row_data with image:
            {
                'Part Number': 'D38999/12',
                'Part Code': 'MSEK',
                'Material': 'Aluminum',
                'image_base64': 'data:image/png;base64,...' or 'image_url': 'http://...'
            }
        """
        # Check if we have image data embedded in row_data
        image_html = ""
        if 'image_base64' in row_data and row_data['image_base64']:
            # Base64 encoded image
            image_html = f'<img src="{row_data["image_base64"]}" style="width:150px; height:150px; border-radius:5px;" />'
        elif 'image_url' in row_data and row_data['image_url']:
            # URL-based image
            image_html = f'<img src="{row_data["image_url"]}" style="width:150px; height:150px; border-radius:5px;" />'
        else:
            # Placeholder image when none provided
            image_html = self._get_placeholder_image()

        # Build the HTML with optional image
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; color: #e0e0e0; background-color: transparent; margin: 0; padding: 0;">
            <div style="display: flex; gap: 15px; align-items: flex-start;">
                <div style="flex: 1;">
                    <h3 style="margin: 0 0 10px 0; color: #4a90e2;">Connector Details</h3>
                    <table style="width: 100%; border-collapse: collapse; font-size: 12px;">
                        <tr>
                            <td style="padding: 4px; font-weight: bold; color: #888;">Part Number:</td>
                            <td style="padding: 4px;">{row_data.get('Part Number', 'N/A')}</td>
                        </tr>
                        <tr>
                            <td style="padding: 4px; font-weight: bold; color: #888;">Part Code:</td>
                            <td style="padding: 4px;">{row_data.get('Part Code', 'N/A')}</td>
                        </tr>
                        <tr>
                            <td style="padding: 4px; font-weight: bold; color: #888;">Material:</td>
                            <td style="padding: 4px;">{row_data.get('Material', 'N/A')}</td>
                        </tr>
                        <tr>
                            <td style="padding: 4px; font-weight: bold; color: #888;">Database Status:</td>
                            <td style="padding: 4px;">{row_data.get('Database Status', 'N/A')}</td>
                        </tr>
                        <tr>
                            <td style="padding: 4px; font-weight: bold; color: #888;">Family:</td>
                            <td style="padding: 4px;">{row_data.get('Family', 'N/A')}</td>
                        </tr>
                        <tr>
                            <td style="padding: 4px; font-weight: bold; color: #888;">Shell Type:</td>
                            <td style="padding: 4px;">{row_data.get('Shell Type', 'N/A')}</td>
                        </tr>
                        <tr>
                            <td style="padding: 4px; font-weight: bold; color: #888;">Insert Arrangement:</td>
                            <td style="padding: 4px;">{row_data.get('Insert Arrangement', 'N/A')}</td>
                        </tr>
                        <tr>
                            <td style="padding: 4px; font-weight: bold; color: #888;">Socket Type:</td>
                            <td style="padding: 4px;">{row_data.get('Socket Type', 'N/A')}</td>
                        </tr>
                        <tr>
                            <td style="padding: 4px; font-weight: bold; color: #888;">Keying:</td>
                            <td style="padding: 4px;">{row_data.get('Keying', 'N/A')}</td>
                        </tr>
                    </table>
                </div>
                {'<div style=\"flex-shrink: 0;\">' + image_html + '</div>' if image_html else ''}
            </div>
        </body>
        </html>
        """
        return html.strip()

    def _load_image_to_label(self, image_path: str, label):
        """Load image from file path or URL to a QLabel

        Args:
            image_path: Path to image file or URL
            label: QLabel widget to display the image
        """
        from pathlib import Path
        from PySide6.QtGui import QPixmap

        try:
            if image_path.startswith(('http://', 'https://')):
                # URL-based image - would need urllib or requests to load
                print(f"Note: URL images not yet supported: {image_path}")
                label.setText("Image URL\n(Not loaded)")
            else:
                # File path
                path = Path(image_path)
                if path.exists() and path.is_file():
                    pixmap = QPixmap(str(path))
                    if not pixmap.isNull():
                        label.setPixmap(pixmap)
                    else:
                        label.setText("Invalid\nImage")
                else:
                    label.setText("Image not\nfound")
        except Exception as e:
            print(f"Error loading image: {e}")
            label.setText("Error loading\nimage")

    def _get_placeholder_image(self) -> str:
        """Generate a placeholder image as base64 SVG

        Returns:
            HTML img tag with base64-encoded placeholder SVG
        """
        # Simple SVG placeholder - gray rectangle with camera icon
        svg_placeholder = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 150 150" width="150" height="150">
            <rect width="150" height="150" fill="#333333" stroke="#555555" stroke-width="2" rx="5"/>
            <circle cx="75" cy="60" r="20" fill="none" stroke="#888888" stroke-width="2"/>
            <path d="M 45 85 L 45 130 L 105 130 L 105 85 Z" fill="none" stroke="#888888" stroke-width="2"/>
            <line x1="50" y1="95" x2="100" y2="120" stroke="#888888" stroke-width="1" opacity="0.5"/>
            <line x1="100" y1="95" x2="50" y2="120" stroke="#888888" stroke-width="1" opacity="0.5"/>
        </svg>'''

        import base64
        b64_svg = base64.b64encode(svg_placeholder.encode()).decode()
        return f'<img src="data:image/svg+xml;base64,{b64_svg}" style="width:150px; height:150px; border-radius:5px;" />'

    # ============================================================================
    # REDUX DARK RELEASE - Parallel filter state tracking (no view impact)
    # ============================================================================
    # These methods run in parallel with the existing view to validate Redux
    # implementation before fully integrating it. The Redux state mirrors all
    # filter operations but does not affect the view.

    def _initialize_redux_dark_release(self):
        """Initialize Redux dark release monitoring"""
        # Connect Redux signals to dark release handlers (logging/validation only)
        self.filter_redux.filters_changed.connect(
            self._on_redux_filters_changed)
        self.filter_redux.filters_cleared.connect(
            self._on_redux_filters_cleared)

    def _sync_redux_from_view_filters(self, filters: dict, command: FilterCommand) -> None:
        """
        Sync Redux state from view filter operations (dark release).
        This mirrors view filter changes into Redux without affecting the view.

        Args:
            filters: Filter dict from view (same format as current_filters)
            command: FilterCommand enum indicating source of change
        """
        # Extract filter values from the filters dict
        update_dict = {
            'search_text': filters.get('search_text', ''),
            'standard': filters.get('standard', []),
            'shell_type': filters.get('shell_type', []),
            'material': filters.get('material', []),
            'shell_size': filters.get('shell_size', []),
            'insert_arrangement': filters.get('insert_arrangement', []),
            'socket_type': filters.get('socket_type', []),
            'keying': filters.get('keying', [])
        }

        # Update Redux (no view impact)
        self.filter_redux.update_filters(update_dict, command)

    def _populate_redux_available_options(self, filter_options: dict) -> None:
        """
        Populate Redux with available filter options (dark release).
        Called when filter options are updated based on standards selection.

        Args:
            filter_options: Dict with keys like 'shell_types', 'materials', etc.
        """
        # Map view option keys to Redux option keys
        options_map = {
            'shell_types': 'shell_type',
            'materials': 'material',
            'shell_sizes': 'shell_size',
            'insert_arrangements': 'insert_arrangement',
            'socket_types': 'socket_type',
            'keyings': 'keying'
        }

        # Convert to Redux format and update
        redux_options = {}
        for view_key, redux_key in options_map.items():
            if view_key in filter_options:
                redux_options[redux_key] = filter_options[view_key]

        # Populate available options in Redux
        if redux_options:
            self.filter_redux.update_available_options(redux_options)

    def _on_redux_filters_changed(self, state: FilterState, command: FilterCommand, metadata: dict) -> None:
        """
        Dark release handler: Redux filter state changed.
        This is for monitoring/validation only - no view updates.

        Args:
            state: New FilterState from Redux
            command: FilterCommand that triggered the change
            metadata: Additional metadata about the change
        """
        # Log filter state change for validation
        # print(f"[REDUX DARK RELEASE] Filters changed via {command.value}")
        # print(f"  State: {state.to_dict()}")
        # Uncomment above lines to enable debug logging
        pass

    def _on_redux_filters_cleared(self) -> None:
        """
        Dark release handler: Redux filters were cleared.
        This is for monitoring/validation only - no view updates.
        """
        # Log filter clear event for validation
        # print(f"[REDUX DARK RELEASE] Filters cleared")
        # Uncomment above line to enable debug logging
        pass

    def get_redux_state(self) -> FilterState:
        """
        Get current Redux filter state (dark release).
        Useful for debugging and validation.

        Returns:
            Current FilterState from Redux
        """
        return self.filter_redux.state

    def get_redux_available_options(self, filter_key: str) -> list:
        """
        Get Redux available options for a filter (dark release).
        Useful for validation and debugging.

        Args:
            filter_key: The filter key (e.g., 'material')

        Returns:
            List of available options from Redux
        """
        return self.filter_redux.get_available_options(filter_key)

    def _update_stats(self):
        """Update statistics display"""
        if self.filtered_df is not None:
            count = len(self.filtered_df)
            total = len(self.df) if self.df is not None else 0
            self.view.record_count_label.setText(
                f"Showing {count} of {total} connectors from database")
