"""
Test central registry singleton
"""
import pytest
from productivity_app.data_pipeline.registry import registry, CentralRegistry
from productivity_app.data_pipeline.parameters.input_parameters import DataSource
from productivity_app.data_pipeline.types_enum import DataTypes


def test_registry_is_singleton():
    """Central registry should be a singleton"""
    reg1 = CentralRegistry()
    reg2 = CentralRegistry()
    assert reg1 is reg2
    assert registry is reg1


def test_register_collector():
    """Test registering a collector"""
    
    def test_collector(filepath: str):
        return "data"
    
    registry.register_collector(
        name="TestCollector",
        func=test_collector,
        inputs=[DataSource.FilePath],
        outputs=[DataTypes.DataFrame]
    )
    
    # Should be retrievable
    collector_info = registry.get_collector("TestCollector")
    assert collector_info is not None
    assert collector_info['func'] == test_collector
    
    # Should appear in collectors for DataFrame type
    collectors = registry.get_collectors_for_type(DataTypes.DataFrame)
    assert "TestCollector" in collectors
    
    # Cleanup
    registry.clear()


def test_register_report():
    """Test registering a report"""
    
    def test_report(filepath: str):
        return "report"
    
    registry.register_report(
        title="Test Report",
        func=test_report,
        description="A test report",
        inputs=[DataSource.FilePath]
    )
    
    # Should be retrievable
    report_info = registry.get_report("Test Report")
    assert report_info is not None
    assert report_info['func'] == test_report
    
    # Cleanup
    registry.clear()


def test_collectors_and_reports_separate():
    """Collectors and reports should be separate namespaces"""
    
    def collector_func():
        pass
    
    def report_func():
        pass
    
    registry.register_collector(
        name="MyFunc",
        func=collector_func,
        inputs=[],
        outputs=[DataTypes.DataFrame]
    )
    
    registry.register_report(
        title="MyFunc",
        func=report_func,
        description="Same name",
        inputs=[]
    )
    
    # Both should exist independently
    collector = registry.get_collector("MyFunc")
    report = registry.get_report("MyFunc")
    
    assert collector is not None
    assert report is not None
    assert collector['func'] == collector_func
    assert report['func'] == report_func
    
    # Cleanup
    registry.clear()


def test_clear_registry():
    """Test clearing the registry"""
    
    registry.register_collector(
        name="TestCol",
        func=lambda: None,
        inputs=[],
        outputs=[DataTypes.DataFrame]
    )
    
    registry.register_report(
        title="TestRep",
        func=lambda: None,
        description="Test",
        inputs=[]
    )
    
    # Should have entries
    assert len(registry.get_all_collectors()) > 0
    assert len(registry.get_all_reports()) > 0
    
    # Clear should empty both
    registry.clear()
    
    assert len(registry.get_all_collectors()) == 0
    assert len(registry.get_all_reports()) == 0
