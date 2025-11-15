"""
Connectors Presenter - Main coordinator for connector module (updated to new structure)
"""
from ..connector.connector_model import ConnectorModel
from ..connector.connector_tab import ConnectorModuleView
from ..core.base_presenter import BasePresenter


class ConnectorsPresenter(BasePresenter):
    """Presenter coordinating the connector module"""

    def __init__(self, context):
        # Create model
        self.model = ConnectorModel(context)

        # Create view (which contains sub-tabs)
        self.view = ConnectorModuleView(context, self.model)

        # Initialize base presenter
        super().__init__(context, self.view, self.model, title="Connectors")

        # Auto-load data on startup
        self._auto_load_data()

    def _auto_load_data(self):
        """Auto-load connector data with slight delay"""
        from PySide6.QtCore import QTimer
        QTimer.singleShot(150, self.view.start_loading)


# class ConnectorsPresenter(BasePresenter):
#     """Presenter for connector management functionality"""

#     def __init__(self, context: AppContext):
#         super().__init__(context)
#         self.model = ConnectorsModel(context)
#         self._connect_model_signals()

#     def _initialize(self):
#         """Initialize the connectors presenter"""
#         # Load initial connector data
#         self.model.load_data()
#         print("Connectors Presenter initialized")

#     def _connect_model_signals(self):
#         """Connect to model signals"""
#         self.model.data_updated.connect(self._on_model_data_updated)
#         self.model.data_loaded.connect(self._on_model_data_loaded)
#         self.model.data_saved.connect(self._on_model_data_saved)

#     def handle_connector_selection(self, connector_name: str):
#         """Handle connector selection from view"""
#         print(f"Connectors Presenter: Connector selected - {connector_name}")

#         # Get connector data from model
#         connector_data = self.model.get_connector_data(connector_name)

#         if connector_data:
#             self.data_changed.emit({
#                 'type': 'connector_selected',
#                 'connector': connector_name,
#                 'data': connector_data
#             })

#             # Update application state
#             self.context.set_state('current_connector', connector_name)

#             self.complete_operation(f"connector_selection_{connector_name}")
#         else:
#             self.handle_error(f"No data found for connector: {connector_name}")

#     def handle_connector_data_change(self, action: str, connector_data: dict):
#         """Handle connector data changes from view"""
#         print(f"Connectors Presenter: Connector data change - {action}")

#         try:
#             if action == 'add':
#                 self.add_connector(connector_data)
#             elif action == 'remove':
#                 self.remove_connector(connector_data.get('name'))
#             elif action == 'update':
#                 self.update_connector(connector_data)
#             else:
#                 self.handle_error(f"Unknown action: {action}")

#         except Exception as e:
#             self.handle_error(f"Failed to {action} connector: {str(e)}")

#     def add_connector(self, connector_data: dict):
#         """Add a new connector"""
#         connector_name = connector_data.get('name')
#         if not connector_name:
#             raise ValueError("Connector name is required")

#         # Validate connector data
#         if self.model.has_connector(connector_name):
#             raise ValueError(f"Connector '{connector_name}' already exists")

#         # Add to model
#         self.model.add_connector(connector_name, connector_data)

#         self.data_changed.emit({
#             'type': 'connector_added',
#             'connector': connector_name,
#             'data': connector_data
#         })

#         self.complete_operation(f"add_connector_{connector_name}")

#     def remove_connector(self, connector_name: str):
#         """Remove a connector"""
#         if not connector_name:
#             raise ValueError("Connector name is required")

#         if not self.model.has_connector(connector_name):
#             raise ValueError(f"Connector '{connector_name}' does not exist")

#         # Remove from model
#         self.model.remove_connector(connector_name)

#         self.data_changed.emit({
#             'type': 'connector_removed',
#             'connector': connector_name
#         })

#         self.complete_operation(f"remove_connector_{connector_name}")

#     def update_connector(self, connector_data: dict):
#         """Update an existing connector"""
#         connector_name = connector_data.get('name')
#         if not connector_name:
#             raise ValueError("Connector name is required")

#         if not self.model.has_connector(connector_name):
#             raise ValueError(f"Connector '{connector_name}' does not exist")

#         # Update in model
#         self.model.update_connector(connector_name, connector_data)

#         self.data_changed.emit({
#             'type': 'connector_updated',
#             'connector': connector_name,
#             'data': connector_data
#         })

#         self.complete_operation(f"update_connector_{connector_name}")

#     def get_connector_list(self):
#         """Get list of all connectors"""
#         return self.model.get_connector_list()

#     def validate_connector_configuration(self, connector_name: str):
#         """Validate a connector's pin configuration"""
#         print(f"Connectors Presenter: Validating configuration for {connector_name}")

#         try:
#             validation_result = self.model.validate_connector(connector_name)

#             self.data_changed.emit({
#                 'type': 'validation_result',
#                 'connector': connector_name,
#                 'result': validation_result
#             })

#             if validation_result.get('valid', False):
#                 self.complete_operation(f"validate_connector_{connector_name}_success")
#             else:
#                 self.handle_error(f"Validation failed for {connector_name}: {validation_result.get('errors', [])}")

#             return validation_result

#         except Exception as e:
#             self.handle_error(f"Failed to validate connector {connector_name}: {str(e)}")
#             return {'valid': False, 'errors': [str(e)]}

#     def auto_populate_connector(self, connector_name: str, connector_type: str):
#         """Auto-populate connector based on type"""
#         print(f"Connectors Presenter: Auto-populating {connector_name} as {connector_type}")

#         try:
#             self.model.auto_populate_connector(connector_name, connector_type)

#             self.data_changed.emit({
#                 'type': 'connector_auto_populated',
#                 'connector': connector_name,
#                 'connector_type': connector_type
#             })

#             self.complete_operation(f"auto_populate_{connector_name}_{connector_type}")

#         except Exception as e:
#             self.handle_error(f"Failed to auto-populate connector {connector_name}: {str(e)}")

#     def save_connector_configuration(self):
#         """Save all connector configurations"""
#         print("Connectors Presenter: Saving connector configurations")

#         try:
#             success = self.model.save_data()
#             if success:
#                 self.complete_operation("save_connector_configurations")
#             else:
#                 self.handle_error("Failed to save connector configurations")
#         except Exception as e:
#             self.handle_error(f"Error saving connector configurations: {str(e)}")

#     def _on_model_data_updated(self, data):
#         """Handle model data updates"""
#         print(f"Connectors Presenter: Model data updated - {list(data.keys())}")
#         self.data_changed.emit(data)

#     def _on_model_data_loaded(self, data):
#         """Handle model data loaded"""
#         print(f"Connectors Presenter: Model data loaded - {len(data)} connectors")
#         self.data_changed.emit({'type': 'data_loaded', 'data': data})

#     def _on_model_data_saved(self, success):
#         """Handle model data saved"""
#         if success:
#             print("Connectors Presenter: Model data saved successfully")
#             self.complete_operation("model_data_saved")
#         else:
#             self.handle_error("Failed to save model data")
