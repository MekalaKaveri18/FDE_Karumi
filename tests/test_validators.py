"""Tests for validators module"""

import pytest
from src.validators import ConfigurationValidator


@pytest.mark.asyncio
async def test_configuration_validator_initialization():
    """Test validator initialization"""
    validator = ConfigurationValidator(headless=True, timeout=30000)
    
    assert validator.headless is True
    assert validator.timeout == 30000
    assert len(validator.results) == 0


@pytest.mark.asyncio
async def test_results_tracking():
    """Test results tracking"""
    validator = ConfigurationValidator()
    
    # Validate empty results
    assert len(validator.results) == 0
    assert len(validator.edge_cases) == 0


def test_validator_properties():
    """Test validator properties"""
    validator = ConfigurationValidator(headless=False)
    
    assert validator.headless is False
    assert validator.results == []
    assert validator.recommendations == []
