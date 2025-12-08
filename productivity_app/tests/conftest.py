"""
Pytest fixtures and configuration for productivity_app tests
"""
import pytest
import pandas as pd
from typing import Dict, List, Any


@pytest.fixture
def sample_connector_data() -> List[Dict[str, Any]]:
    """Sample connector data matching the actual data structure"""
    return [
        {
            'Part Number': 'D38999/26WA35PN',
            'Part Code': 'D38999-26WA35PN',
            'Minified Part Code': 'D3899926WA35PN',
            'Material': 'Aluminum',
            'Database Status': 'Active',
            'Family': 'D38999',
            'Shell Type': '26 - Plug',
            'Shell Size': '10',
            'Insert Arrangement': 'A - 1',
            'Socket Type': 'Type A',
            'Keying': 'A'
        },
        {
            'Part Number': 'D38999/24WB35SN',
            'Part Code': 'D38999-24WB35SN',
            'Minified Part Code': 'D3899924WB35SN',
            'Material': 'Stainless Steel',
            'Database Status': 'Active',
            'Family': 'D38999',
            'Shell Type': '24 - Receptacle',
            'Shell Size': '12',
            'Insert Arrangement': 'B - 2',
            'Socket Type': 'Type B',
            'Keying': 'B'
        },
        {
            'Part Number': 'D38999/20WC10PN',
            'Part Code': 'D38999-20WC10PN',
            'Minified Part Code': 'D3899920WC10PN',
            'Material': 'Aluminum',
            'Database Status': 'Obsolete',
            'Family': 'D38999',
            'Shell Type': '20 - Receptacle B',
            'Shell Size': '14',
            'Insert Arrangement': 'C - 3',
            'Socket Type': 'Type A',
            'Keying': 'C'
        },
        {
            'Part Number': 'VG95234F10A001PN',
            'Part Code': 'VG95234-F10A001PN',
            'Minified Part Code': 'VG95234F10A001PN',
            'Material': 'Composite',
            'Database Status': 'Active',
            'Family': 'VG',
            'Shell Type': '26 - Plug',
            'Shell Size': '8',
            'Insert Arrangement': 'A - 1',
            'Socket Type': 'Type C',
            'Keying': 'D'
        },
        {
            'Part Number': 'VG95234F12B002SN',
            'Part Code': 'VG95234-F12B002SN',
            'Minified Part Code': 'VG95234F12B002SN',
            'Material': 'Stainless Steel',
            'Database Status': 'Active',
            'Family': 'VG',
            'Shell Type': '24 - Receptacle',
            'Shell Size': '9',
            'Insert Arrangement': 'B - 2',
            'Socket Type': 'Type D',
            'Keying': 'E'
        },
        {
            'Part Number': 'MS3470L16-10P',
            'Part Code': 'MS3470L16-10P',
            'Minified Part Code': 'MS3470L1610P',
            'Material': 'Aluminum',
            'Database Status': 'Active',
            'Family': 'MS',
            'Shell Type': '26 - Plug',
            'Shell Size': '16',
            'Insert Arrangement': 'A - 10',
            'Socket Type': 'Type A',
            'Keying': 'Normal'
        },
        {
            'Part Number': 'MS3476L16-10S',
            'Part Code': 'MS3476L16-10S',
            'Minified Part Code': 'MS3476L1610S',
            'Material': 'Aluminum',
            'Database Status': 'Active',
            'Family': 'MS',
            'Shell Type': '24 - Receptacle',
            'Shell Size': '16',
            'Insert Arrangement': 'A - 10',
            'Socket Type': 'Type A',
            'Keying': 'Normal'
        },
        {
            'Part Number': 'EN3645-003-12',
            'Part Code': 'EN3645-003-12',
            'Minified Part Code': 'EN364500312',
            'Material': 'Composite',
            'Database Status': 'Active',
            'Family': 'EN',
            'Shell Type': '26 - Plug',
            'Shell Size': '12',
            'Insert Arrangement': 'B - 3',
            'Socket Type': 'Type B',
            'Keying': 'F'
        },
    ]


@pytest.fixture
def connector_df(sample_connector_data) -> pd.DataFrame:
    """Create a DataFrame from sample connector data"""
    return pd.DataFrame(sample_connector_data)
