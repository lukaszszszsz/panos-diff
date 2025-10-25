"""
Unit tests for XML diff service.
"""
import pytest
from pathlib import Path
from xml.etree import ElementTree as ET
from panos_diff.differ import differ

@pytest.fixture(scope="module")
def test_data():
    """Fixture providing test data for XML diff tests."""
    test_data_dir = Path(__file__).parent / 'data'
    src_config_path = test_data_dir / 'src_config.xml'
    dst_config_path = test_data_dir / 'dst_config.xml'
    
    # Load test configurations
    with open(src_config_path, 'r', encoding='utf-8') as f:
        src_xml = f.read()
    with open(dst_config_path, 'r', encoding='utf-8') as f:
        dst_xml = f.read()

    return {
        'src_xml': src_xml,
        'dst_xml': dst_xml,
        'src_path': src_config_path,
        'dst_path': dst_config_path
    }



def test_generate_diff_with_string_input(test_data):
    """Test diff generation with string XML input."""
    differ.diff(test_data['src_xml'], test_data['dst_xml'])
    diff = differ.changes
    assert isinstance(diff, list)    # Verify diff entries have required fields
    
    for entry in diff:
        assert isinstance(entry, dict)
        assert 'type' in entry
        assert 'path' in entry

# TODO: write complex tests