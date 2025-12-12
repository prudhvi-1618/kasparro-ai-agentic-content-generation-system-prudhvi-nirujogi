from typing_extensions import List
from ..model.schema import PriceComparison,IngredientsComparison,BenefitsComparison

class DeterministicCalculations:
    """Pure Python functions for deterministic calculations"""
    
    @staticmethod
    def calculate_price_comparison(price_a: float, price_b: float, name_a: str, name_b: str) -> PriceComparison:
        """Calculate price comparison deterministically"""
        difference = abs(price_a - price_b)
        winner = name_a if price_a < price_b else name_b
        
        cheaper_price = min(price_a, price_b)
        more_expensive = max(price_a, price_b)
        
        analysis = f"{winner} is ₹{difference} less expensive than the other product (₹{cheaper_price} vs ₹{more_expensive})."
        
        return PriceComparison(
            winner=winner,
            difference=difference,
            analysis=analysis
        )
    
    @staticmethod
    def calculate_ingredients_comparison(ingredients_a: List[str], ingredients_b: List[str]) -> IngredientsComparison:
        """Calculate ingredients comparison deterministically"""
        set_a = set(ingredients_a)
        set_b = set(ingredients_b)
        
        common = sorted(list(set_a & set_b))
        unique_to_a = sorted(list(set_a - set_b))
        unique_to_b = sorted(list(set_b - set_a))
        
        return IngredientsComparison(
            common=common,
            unique_to_a=unique_to_a,
            unique_to_b=unique_to_b
        )
    
    @staticmethod
    def calculate_benefits_comparison(benefits_a: List[str], benefits_b: List[str]) -> BenefitsComparison:
        """Calculate benefits comparison deterministically"""
        set_a = set(benefits_a)
        set_b = set(benefits_b)
        
        common = sorted(list(set_a & set_b))
        unique_to_a = sorted(list(set_a - set_b))
        unique_to_b = sorted(list(set_b - set_a))
        
        return BenefitsComparison(
            common=common,
            unique_to_a=unique_to_a,
            unique_to_b=unique_to_b
        )