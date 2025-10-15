"""
EPD Model - Data management for EPD analysis
"""
from typing import Dict, List, Any, Optional
from ..core.base_model import BaseModel
from ..core.app_context import AppContext
import pandas as pd

from app.core.base_model import BaseModel


class EpdModel(BaseModel):
    def __init__(self, context):
        super().__init__(context)
        # In real life, this would load from Excel or a database
        self.data = pd.DataFrame([
            {"EPD": "EPD-001", "Description": "Main harness",
                "Cable": "Cable 100", "AWG": 20},
            {"EPD": "EPD-002", "Description": "Sensor branch",
                "Cable": "Cable 200", "AWG": 22},
            {"EPD": "EPD-003", "Description": "Power loom",
                "Cable": "Cable 100", "AWG": 18},
        ])

    def get_all(self):
        """Return full dataset."""
        return self.data.copy()

    def filter(self, text: str):
        """Return filtered rows matching text in any column."""
        if not text:
            return self.get_all()
        mask = self.data.apply(lambda row: row.astype(
            str).str.contains(text, case=False).any(), axis=1)
        return self.data[mask]
# class EpdModel(BaseModel):
#     """Model for managing EPD (Electronic Parts Data) analysis data"""

#     def __init__(self, context: AppContext):
#         super().__init__(context)
#         self.current_breakout_wire = None
#         self.current_connection = None

#     def _initialize_data(self):
#         """Initialize EPD model data"""
#         # Initialize with sample breakout wire data
#         self._data = {
#             'breakout_wires': {
#                 'BreakoutWire1': {
#                     'name': 'BreakoutWire1',
#                     'connections': {
#                         'Connection1': {
#                             'name': 'Connection1',
#                             'pin_data': {},
#                             'wire_color': 'Red',
#                             'signal_type': 'Power'
#                         },
#                         'Connection2': {
#                             'name': 'Connection2',
#                             'pin_data': {},
#                             'wire_color': 'Blue',
#                             'signal_type': 'Data'
#                         },
#                         'Connection3': {
#                             'name': 'Connection3',
#                             'pin_data': {},
#                             'wire_color': 'Green',
#                             'signal_type': 'Ground'
#                         }
#                     },
#                     'pin_data': {
#                         'pin_count': 25,
#                         'pins': {}
#                     },
#                     'status': 'Active',
#                     'manufacturer': 'Generic',
#                     'part_number': 'BW001'
#                 },
#                 'BreakoutWire2': {
#                     'name': 'BreakoutWire2',
#                     'connections': {
#                         'Connection1': {
#                             'name': 'Connection1',
#                             'pin_data': {},
#                             'wire_color': 'Yellow',
#                             'signal_type': 'Signal'
#                         },
#                         'Connection2': {
#                             'name': 'Connection2',
#                             'pin_data': {},
#                             'wire_color': 'Orange',
#                             'signal_type': 'Control'
#                         },
#                         'Connection3': {
#                             'name': 'Connection3',
#                             'pin_data': {},
#                             'wire_color': 'Purple',
#                             'signal_type': 'Data'
#                         }
#                     },
#                     'pin_data': {
#                         'pin_count': 15,
#                         'pins': {}
#                     },
#                     'status': 'Active',
#                     'manufacturer': 'Generic',
#                     'part_number': 'BW002'
#                 }
#             },
#             'gys_data': {
#                 'enabled': True,
#                 'data_points': {}
#             }
#         }

#         # Initialize additional breakout wires
#         for i in range(3, 6):
#             breakout_wire_name = f'BreakoutWire{i}'
#             self._data['breakout_wires'][breakout_wire_name] = {
#                 'name': breakout_wire_name,
#                 'connections': {
#                     f'Connection{j}': {
#                         'name': f'Connection{j}',
#                         'pin_data': {},
#                         'wire_color': f'Color{j}',
#                         'signal_type': f'Type{j}'
#                     } for j in range(1, 4)
#                 },
#                 'pin_data': {
#                     'pin_count': 9,
#                     'pins': {}
#                 },
#                 'status': 'Active',
#                 'manufacturer': 'Generic',
#                 'part_number': f'BW00{i}'
#             }

#     def get_breakout_wire_list(self) -> List[str]:
#         """Get list of all breakout wire names"""
#         return list(self._data.get('breakout_wires', {}).keys())

#     def get_breakout_wire_data(self, breakout_wire_name: str) -> Optional[Dict]:
#         """Get data for a specific breakout wire"""
#         return self._data.get('breakout_wires', {}).get(breakout_wire_name)

#     def get_connection_data(self, breakout_wire_name: str, connection_name: str) -> Optional[Dict]:
#         """Get data for a specific connection"""
#         breakout_wire = self.get_breakout_wire_data(breakout_wire_name)
#         if breakout_wire:
#             return breakout_wire.get('connections', {}).get(connection_name)
#         return None

#     def set_current_breakout_wire(self, breakout_wire_name: str):
#         """Set the currently selected breakout wire"""
#         self.current_breakout_wire = breakout_wire_name
#         self.set_data('current_breakout_wire', breakout_wire_name)

#     def set_current_connection(self, breakout_wire_name: str, connection_name: str):
#         """Set the currently selected connection"""
#         self.current_breakout_wire = breakout_wire_name
#         self.current_connection = connection_name
#         self.set_data('current_breakout_wire', breakout_wire_name)
#         self.set_data('current_connection', connection_name)

#     def update_breakout_wire_pin_data(self, breakout_wire_name: str, pin_data: Dict):
#         """Update pin data for a breakout wire"""
#         if breakout_wire_name in self._data.get('breakout_wires', {}):
#             self._data['breakout_wires'][breakout_wire_name]['pin_data'].update(pin_data)
#             self.data_updated.emit({
#                 'breakout_wire': breakout_wire_name,
#                 'pin_data': pin_data
#             })
#         else:
#             raise ValueError(f"Breakout wire '{breakout_wire_name}' not found")

#     def update_connection_data(self, breakout_wire_name: str, connection_name: str, connection_data: Dict):
#         """Update data for a specific connection"""
#         breakout_wire = self.get_breakout_wire_data(breakout_wire_name)
#         if breakout_wire and connection_name in breakout_wire.get('connections', {}):
#             breakout_wire['connections'][connection_name].update(connection_data)
#             self.data_updated.emit({
#                 'breakout_wire': breakout_wire_name,
#                 'connection': connection_name,
#                 'connection_data': connection_data
#             })
#         else:
#             raise ValueError(f"Connection '{connection_name}' not found in breakout wire '{breakout_wire_name}'")

#     def add_breakout_wire(self, breakout_wire_name: str, breakout_wire_data: Dict):
#         """Add a new breakout wire"""
#         if breakout_wire_name in self._data.get('breakout_wires', {}):
#             raise ValueError(f"Breakout wire '{breakout_wire_name}' already exists")

#         if 'breakout_wires' not in self._data:
#             self._data['breakout_wires'] = {}

#         self._data['breakout_wires'][breakout_wire_name] = breakout_wire_data
#         self.data_updated.emit({
#             'action': 'add_breakout_wire',
#             'breakout_wire': breakout_wire_name,
#             'data': breakout_wire_data
#         })

#     def remove_breakout_wire(self, breakout_wire_name: str):
#         """Remove a breakout wire"""
#         if breakout_wire_name not in self._data.get('breakout_wires', {}):
#             raise ValueError(f"Breakout wire '{breakout_wire_name}' not found")

#         del self._data['breakout_wires'][breakout_wire_name]
#         self.data_updated.emit({
#             'action': 'remove_breakout_wire',
#             'breakout_wire': breakout_wire_name
#         })

#     def get_gys_data(self) -> Dict:
#         """Get GYS data"""
#         return self._data.get('gys_data', {})

#     def update_gys_data(self, gys_data: Dict):
#         """Update GYS data"""
#         if 'gys_data' not in self._data:
#             self._data['gys_data'] = {}

#         self._data['gys_data'].update(gys_data)
#         self.data_updated.emit({
#             'action': 'update_gys_data',
#             'gys_data': gys_data
#         })

#     def toggle_gys_data_visibility(self, visible: bool):
#         """Toggle GYS data visibility"""
#         if 'gys_data' not in self._data:
#             self._data['gys_data'] = {}

#         self._data['gys_data']['enabled'] = visible
#         self.data_updated.emit({
#             'action': 'toggle_gys_visibility',
#             'visible': visible
#         })

#     def validate_breakout_wire_data(self, breakout_wire_name: str) -> Dict:
#         """Validate breakout wire data"""
#         breakout_wire = self.get_breakout_wire_data(breakout_wire_name)
#         if not breakout_wire:
#             return {'valid': False, 'errors': [f'Breakout wire {breakout_wire_name} not found']}

#         errors = []

#         # Check if connections exist
#         connections = breakout_wire.get('connections', {})
#         if not connections:
#             errors.append('No connections defined')

#         # Check pin data
#         pin_data = breakout_wire.get('pin_data', {})
#         if not pin_data.get('pin_count'):
#             errors.append('Pin count not defined')

#         return {
#             'valid': len(errors) == 0,
#             'errors': errors,
#             'warnings': []
#         }
