"""
Test PartsList data source knows what columns to look for
"""
from productivity_app.data_pipeline.sources.data_sources import DataSources


def test_partslist_has_schema():
    """PartsList data source has a schema"""
    assert DataSources.PartsList.schema is not None


def test_partslist_knows_required_columns():
    """PartsList knows to look for Part Name and Part Number"""
    required = DataSources.PartsList.schema.required_columns
    
    assert "Part Name" in required
    assert "Part Number" in required


def test_partslist_knows_optional_columns():
    """PartsList knows optional columns"""
    optional = DataSources.PartsList.schema.optional_columns
    
    assert "Quantity" in optional
    assert "Unit Cost" in optional
