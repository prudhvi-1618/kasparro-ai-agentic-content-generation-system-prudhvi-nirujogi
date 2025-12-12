import json
from pathlib import Path
import pytest

OUTPUT_FILES = ["faq.json", "product_page.json", "comparison_page.json"]

@pytest.mark.parametrize("filename", OUTPUT_FILES)
def test_output_files_are_valid_json(filename, tmp_path):
    # Simulate output dir
    output_dir = Path("output")
    if not output_dir.exists():
        pytest.skip("Run main.py first to generate outputs")
    
    file_path = output_dir / filename
    assert file_path.exists(), f"{filename} not generated"
    
    with open(file_path) as f:
        data = json.load(f)
    
    assert isinstance(data, dict)
    assert "metadata" in data or "template" in data
    assert "generated_at" in str(data)