"""
Connectors Model - Data management for connector configurations
"""
from typing import Dict, List, Any, Optional
from ..core.base_model import BaseModel
from ..core.app_context import AppContext


class ConnectorsModel(BaseModel):
    """Model for managing connector configuration data"""

    def __init__(self, context: AppContext):
        super().__init__(context)
        # Initialize with sample connector data
        self._connectors_data = {
            'connectors': {
                'DB9_Male_1': {
                    'name': 'DB9_Male_1',
                    'type': 'DB9',
                    'gender': 'Male',
                    'pin_count': 9,
                    'manufacturer': 'Generic',
                    'part_number': 'DB9M-001',
                    'pins': {
                        '1': {'signal': 'DCD', 'wire_color': 'Brown', 'function': 'Data Carrier Detect'},
                        '2': {'signal': 'RXD', 'wire_color': 'Red', 'function': 'Receive Data'},
                        '3': {'signal': 'TXD', 'wire_color': 'Orange', 'function': 'Transmit Data'},
                        '4': {'signal': 'DTR', 'wire_color': 'Yellow', 'function': 'Data Terminal Ready'},
                        '5': {'signal': 'GND', 'wire_color': 'Green', 'function': 'Ground'},
                        '6': {'signal': 'DSR', 'wire_color': 'Blue', 'function': 'Data Set Ready'},
                        '7': {'signal': 'RTS', 'wire_color': 'Violet', 'function': 'Request To Send'},
                        '8': {'signal': 'CTS', 'wire_color': 'Grey', 'function': 'Clear To Send'},
                        '9': {'signal': 'RI', 'wire_color': 'White', 'function': 'Ring Indicator'}
                    }
                },
                'DB25_Female_1': {
                    'name': 'DB25_Female_1',
                    'type': 'DB25',
                    'gender': 'Female',
                    'pin_count': 25,
                    'manufacturer': 'Generic',
                    'part_number': 'DB25F-001',
                    'pins': {}  # Would be populated with 25 pins
                },
                'RJ45_1': {
                    'name': 'RJ45_1',
                    'type': 'RJ45',
                    'gender': 'Hermaphroditic',
                    'pin_count': 8,
                    'manufacturer': 'Generic',
                    'part_number': 'RJ45-001',
                    'pins': {
                        '1': {'signal': 'TX+', 'wire_color': 'White/Orange', 'function': 'Transmit Positive'},
                        '2': {'signal': 'TX-', 'wire_color': 'Orange', 'function': 'Transmit Negative'},
                        '3': {'signal': 'RX+', 'wire_color': 'White/Green', 'function': 'Receive Positive'},
                        '4': {'signal': 'Unused', 'wire_color': 'Blue', 'function': 'Unused'},
                        '5': {'signal': 'Unused', 'wire_color': 'White/Blue', 'function': 'Unused'},
                        '6': {'signal': 'RX-', 'wire_color': 'Green', 'function': 'Receive Negative'},
                        '7': {'signal': 'Unused', 'wire_color': 'White/Brown', 'function': 'Unused'},
                        '8': {'signal': 'Unused', 'wire_color': 'Brown', 'function': 'Unused'}
                    }
                }
            },
            'connector_templates': {
                'DB9': {
                    'pin_count': 9,
                    'standard_signals': ['DCD', 'RXD', 'TXD', 'DTR', 'GND', 'DSR', 'RTS', 'CTS', 'RI']
                },
                'DB15': {
                    'pin_count': 15,
                    'standard_signals': []  # Would be populated with VGA or other standards
                },
                'DB25': {
                    'pin_count': 25,
                    'standard_signals': []  # Would be populated with parallel port or serial standards
                },
                'RJ45': {
                    'pin_count': 8,
                    'standard_signals': ['TX+', 'TX-', 'RX+', 'Unused', 'Unused', 'RX-', 'Unused', 'Unused']
                },
                'USB-C': {
                    'pin_count': 24,
                    'standard_signals': []  # Would be populated with USB-C standard
                }
            }
        }

    def get_connector_list(self) -> List[str]:
        """Get list of all connector names"""
        return list(self._connectors_data.get('connectors', {}).keys())

    def get_connector_data(self, connector_name: str) -> Optional[Dict]:
        """Get data for a specific connector"""
        return self._connectors_data.get('connectors', {}).get(connector_name)

    def has_connector(self, connector_name: str) -> bool:
        """Check if a connector exists"""
        return connector_name in self._connectors_data.get('connectors', {})

    def add_connector(self, connector_name: str, connector_data: Dict):
        """Add a new connector"""
        if self.has_connector(connector_name):
            raise ValueError(f"Connector '{connector_name}' already exists")

        if 'connectors' not in self._connectors_data:
            self._connectors_data['connectors'] = {}

        # Ensure required fields
        connector_data.setdefault('name', connector_name)
        connector_data.setdefault('pins', {})

        self._connectors_data['connectors'][connector_name] = connector_data
        self.data_updated.emit({
            'action': 'add_connector',
            'connector': connector_name,
            'data': connector_data
        })

    def remove_connector(self, connector_name: str):
        """Remove a connector"""
        if not self.has_connector(connector_name):
            raise ValueError(f"Connector '{connector_name}' not found")

        del self._connectors_data['connectors'][connector_name]
        self.data_updated.emit({
            'action': 'remove_connector',
            'connector': connector_name
        })

    def update_connector(self, connector_name: str, connector_data: Dict):
        """Update an existing connector"""
        if not self.has_connector(connector_name):
            raise ValueError(f"Connector '{connector_name}' not found")

        self._connectors_data['connectors'][connector_name].update(
            connector_data)
        self.data_updated.emit({
            'action': 'update_connector',
            'connector': connector_name,
            'data': connector_data
        })

    def update_connector_pin(self, connector_name: str, pin_number: str, pin_data: Dict):
        """Update a specific pin in a connector"""
        connector = self.get_connector_data(connector_name)
        if not connector:
            raise ValueError(f"Connector '{connector_name}' not found")

        if 'pins' not in connector:
            connector['pins'] = {}

        connector['pins'][pin_number] = pin_data
        self.data_updated.emit({
            'action': 'update_pin',
            'connector': connector_name,
            'pin': pin_number,
            'pin_data': pin_data
        })

    def get_connector_template(self, connector_type: str) -> Optional[Dict]:
        """Get template data for a connector type"""
        return self._connectors_data.get('connector_templates', {}).get(connector_type)

    def auto_populate_connector(self, connector_name: str, connector_type: str):
        """Auto-populate a connector based on its type"""
        template = self.get_connector_template(connector_type)
        if not template:
            raise ValueError(
                f"No template found for connector type '{connector_type}'")

        connector = self.get_connector_data(connector_name)
        if not connector:
            raise ValueError(f"Connector '{connector_name}' not found")

        # Clear existing pins
        connector['pins'] = {}

        # Populate pins based on template
        standard_signals = template.get('standard_signals', [])
        pin_count = template.get('pin_count', len(standard_signals))

        for i in range(1, pin_count + 1):
            pin_number = str(i)
            signal = standard_signals[i-1] if i - \
                1 < len(standard_signals) else f'Pin{i}'

            connector['pins'][pin_number] = {
                'signal': signal,
                'wire_color': '',
                'function': f'Function for {signal}',
                'notes': '',
                'connected_to': ''
            }

        self.data_updated.emit({
            'action': 'auto_populate',
            'connector': connector_name,
            'connector_type': connector_type
        })

    def validate_connector(self, connector_name: str) -> Dict:
        """Validate a connector's configuration"""
        connector = self.get_connector_data(connector_name)
        if not connector:
            return {'valid': False, 'errors': [f'Connector {connector_name} not found']}

        errors = []
        warnings = []

        # Check required fields
        required_fields = ['name', 'type', 'pin_count']
        for field in required_fields:
            if not connector.get(field):
                errors.append(f'Missing required field: {field}')

        # Check pin configuration
        pins = connector.get('pins', {})
        expected_pin_count = connector.get('pin_count', 0)

        if len(pins) != expected_pin_count:
            warnings.append(
                f'Pin count mismatch: expected {expected_pin_count}, found {len(pins)}')

        # Check for duplicate signals
        signals = []
        for pin_num, pin_data in pins.items():
            signal = pin_data.get('signal', '')
            if signal and signal != 'Unused':
                if signal in signals:
                    errors.append(
                        f'Duplicate signal "{signal}" found on multiple pins')
                else:
                    signals.append(signal)

        # Check for empty signal names
        for pin_num, pin_data in pins.items():
            if not pin_data.get('signal'):
                warnings.append(f'Pin {pin_num} has no signal defined')

        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }

    def get_connector_types(self) -> List[str]:
        """Get list of available connector types"""
        return list(self._connectors_data.get('connector_templates', {}).keys())

    def export_connector_data(self, connector_name: str) -> Dict:
        """Export connector data for external use"""
        connector = self.get_connector_data(connector_name)
        if not connector:
            raise ValueError(f"Connector '{connector_name}' not found")

        return {
            'connector': connector.copy(),
            'export_timestamp': str(self.context.get_state('current_time', 'unknown')),
            'format_version': '1.0'
        }

    def import_connector_data(self, connector_data: Dict):
        """Import connector data from external source"""
        if 'connector' not in connector_data:
            raise ValueError('Invalid import data format')

        connector = connector_data['connector']
        connector_name = connector.get('name')

        if not connector_name:
            raise ValueError('Connector name is required in import data')

        if self.has_connector(connector_name):
            # Update existing connector
            self.update_connector(connector_name, connector)
        else:
            # Add new connector
            self.add_connector(connector_name, connector)
