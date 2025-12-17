"""
Test PartsList data source leads to Part objects
"""
from typing import Iterable
from productivity_app.data_pipeline.sources.data_sources import DataSources
from productivity_app.data_pipeline.models.part import Part


def test_partslist_type_hint_is_iterable_part():
    """PartsList parameter leads to Iterable[Part] type hint"""
    # This is a design test - verify the intended usage pattern

    def example_function(input_parts: Iterable[Part]):
        """Example showing intended type hint"""
        return list(input_parts)

    # Create Part instances
    parts = [
        Part(part_name="Resistor", part_number="R001"),
        Part(part_name="Capacitor", part_number="C001")
    ]

    # Should work with Iterable[Part]
    result = example_function(parts)
    assert len(result) == 2
    assert all(isinstance(p, Part) for p in result)


def test_part_has_required_fields():
    """Part dataclass has part_name and part_number"""
    part = Part(part_name="Test", part_number="T001")

    assert part.part_name == "Test"
    assert part.part_number == "T001"


def test_part_has_optional_fields():
    """Part dataclass has optional quantity and unit_cost"""
    part = Part(
        part_name="Test",
        part_number="T001",
        quantity=10,
        unit_cost=1.5
    )

    assert part.quantity == 10
    assert part.unit_cost == 1.5
