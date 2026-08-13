import os
import json
import pytest
from src.evaluation.run_benchmark import compute_metrics, find_block

def test_compute_metrics():
    # Test perfect match
    p, r, f = compute_metrics(10, 0, 0)
    assert p == 1.0
    assert r == 1.0
    assert f == 1.0

    # Test partial match
    p, r, f = compute_metrics(8, 2, 2)
    assert p == pytest.approx(0.8)
    assert r == pytest.approx(0.8)
    assert f == pytest.approx(0.8)

    # Test division by zero
    p, r, f = compute_metrics(0, 0, 0)
    assert p == 0.0
    assert r == 0.0
    assert f == 0.0

def test_find_block_invalid_path():
    assert find_block(None, "invalid_container / paragraph=abc") is None
