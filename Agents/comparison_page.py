from ..model.schema import ComparisonPage,SkinTypeComparison,ComparisonProduct,ComparisonAnalysis,Recommendation,ComparisonMetadata
from ..state import AgentState
from ..logic.deterministic import DeterministicCalculations

import json
from datetime import datetime

class ComparisonPageAgent:
    """Agent to build comparison page"""
    
    def __init__(self, llm,max_retries:int = 3):
        self.structured_llm = llm.with_structured_output(ComparisonPage)
        self.name = "ComparisonPageAgent"
        self.max_retries = max_retries
    
    def build(self, state: AgentState) -> AgentState:
        """Build comparison page using structured output"""
        
        product_a = state["product_model"]
        product_b = state["product_b_model"]

        price_a = product_a["price"]["amount"] if isinstance(product_a["price"], dict) else product_a["price"]
        price_b = product_b["price"]["amount"] if isinstance(product_b["price"], dict) else product_b["price"]

        # 1. Price Comparison (Deterministic)
        price_comparison = DeterministicCalculations.calculate_price_comparison(
            price_a,
            price_b,
            product_a.get('name', 'Product A'),
            product_b.get('name', 'Product B')
        )
        
        # 2. Ingredients Comparison (Deterministic)
        ingredients_comparison = DeterministicCalculations.calculate_ingredients_comparison(
            product_a.get('ingredients', []),
            product_b.get('ingredients', [])
        )
        
        # 3. Benefits Comparison (Deterministic)
        benefits_comparison = DeterministicCalculations.calculate_benefits_comparison(
            product_a.get('benefits', []),
            product_b.get('benefits', [])
        )
        
        # 4. Skin Type Comparison (Deterministic)
        skin_types_comparison = SkinTypeComparison(
            product_a=product_a.get('skin_types', []),
            product_b=product_b.get('skin_types', [])
        )
        
        # LLM CALL FOR RECOMMENDATION TEXT 
        recommendation_prompt = f"""Given this comparison data, provide a brief recommendation summary.

            Price Winner: {price_comparison.winner}
            Common Ingredients: {ingredients_comparison.common}
            Common Benefits: {benefits_comparison.common}

            Write a 2-3 sentence analysis helping users choose. Be objective and balanced.
        """
        
        for attempt in range(self.max_retries):
            try:
                recommendation_text = self.llm.invoke(recommendation_prompt).content
                break
            except Exception as e:
                if attempt == self.max_retries - 1:
                    recommendation_text = "Both products offer effective formulations. Choose based on your skin type and budget."
        
        # Build final comparison page
        comparison_page = ComparisonPage(
            title="Product Comparison",
            products=[
                ComparisonProduct(
                    name=product_a.get('name', ''),
                    price=product_a["price"]["amount"] if isinstance(product_a["price"], dict) else product_a["price"],
                    concentration=product_a.get('concentration', ''),
                    ingredients=product_a.get('ingredients', []),
                    benefits=product_a.get('benefits', []),
                    skin_types=product_a.get('skin_types', [])
                ),
                ComparisonProduct(
                    name=product_b.get('name', ''),
                    price=product_b["price"]["amount"] if isinstance(product_b["price"], dict) else product_b["price"],
                    concentration=product_b.get('concentration', ''),
                    ingredients=product_b.get('ingredients', []),
                    benefits=product_b.get('benefits', []),
                    skin_types=product_b.get('skin_types', [])
                )
            ],
            comparison=ComparisonAnalysis(
                price=price_comparison,
                ingredients=ingredients_comparison,
                benefits=benefits_comparison,
                skin_types=skin_types_comparison
            ),
            recommendation=Recommendation(
                budget_conscious=price_comparison.winner,
                analysis=recommendation_text
            ),
            metadata=ComparisonMetadata(
                generated_at=datetime.utcnow().isoformat()
            )
        )
        
        comparison_page = comparison_page.model_dump()
        
        return {
            "comparison_page":comparison_page,
            "logs":[f"[{self.name}] Built comparison page"]
        }