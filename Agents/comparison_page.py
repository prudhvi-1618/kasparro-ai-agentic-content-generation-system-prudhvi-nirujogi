from ..model.schema import ComparisonPage
from ..state import AgentState

import json
from datetime import datetime

class ComparisonPageAgent:
    """Agent to build comparison page"""
    
    def __init__(self, llm):
        self.structured_llm = llm.with_structured_output(ComparisonPage)
        self.name = "ComparisonPageAgent"
    
    def build(self, state: AgentState) -> AgentState:
        """Build comparison page using structured output"""
        
        product_a = state["product_model"]
        product_b = state["product_b_model"]
        
        prompt = f"""Create a comprehensive comparison page for these two products.

        Product A:
        {json.dumps(product_a, indent=2)}

        Product B:
        {json.dumps(product_b, indent=2)}

        Instructions:
        1. List both products with all key details
        2. Compare prices - identify winner and calculate difference
        3. Compare ingredients - find common, unique to A, unique to B
        4. Compare benefits - find common, unique to A, unique to B
        5. Compare skin type suitability
        6. Provide recommendation for budget conscious buyers
        7. Write overall analysis
        8. Set generated_at to current ISO timestamp

        Be objective and analytical in comparisons.
        """
        
        # Returns ComparisonPage instance
        comparison: ComparisonPage = self.structured_llm.invoke(prompt)
        # Set timestamp
        comparison.metadata.generated_at = datetime.utcnow().isoformat()
        
        comparison_page = comparison.model_dump()
        # state["logs"].append(f"[{self.name}] Built comparison page")
        
        return {
            "comparison_page":comparison_page,
            "logs":[f"[{self.name}] Built comparison page"]
        }