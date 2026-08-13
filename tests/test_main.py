import os
import pytest
from src.main import validate_arguments

def test_missing_input_path():
    with pytest.raises(ValueError, match="Input file path must be specified"):
        validate_arguments("", "output.docx")

def test_missing_output_path():
    with pytest.raises(ValueError, match="Output file path must be specified"):
        validate_arguments("input.docx", "")

def test_non_docx_extension():
    with pytest.raises(ValueError, match="must have a .docx extension"):
        validate_arguments("input.txt", "output.docx")

def test_input_file_does_not_exist():
    with pytest.raises(FileNotFoundError, match="does not exist"):
        validate_arguments("non_existent_file_xyz.docx", "output.docx")

def test_valid_input_file(tmp_path):
    # Create a dummy docx file in the temp path
    dummy_input = tmp_path / "test_input.docx"
    dummy_input.write_text("dummy docx content")
    
    # This should run without raising any exceptions
    validate_arguments(str(dummy_input), "output.docx")
