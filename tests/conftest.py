import pytest
from pathlib import Path

@pytest.fixture
def sample_product_data():
    return {
        "name": "GlowBoost Vitamin C Serum",
        "concentration": "20% Vitamin C",
        "skin_types": ["Normal", "Combination"],
        "key_ingredients": ["Vitamin C", "Hyaluronic Acid", "Ferulic Acid"],
        "benefits": ["Brightening", "Anti-aging", "Hydration"],
        "how_to_use": "Apply 3-4 drops in the morning",
        "side_effects": "Mild tingling possible",
        "price": {"amount": 899, "currency": "INR", "display": "₹899"}
    }