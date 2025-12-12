from ..model.schema import Product
from ..state import AgentState

import json

class ProductBGeneratorAgent:
    """Agent to generate fictional competitor"""
    
    def __init__(self, llm):
        self.structured_llm = llm.with_structured_output(Product)
        self.name = "ProductBGeneratorAgent"
    
    def generate(self, state: AgentState) -> AgentState:
        """Generate Product B using structured output"""
        
        product_a = state["product_model"]
        
        prompt = f"""
            Create a FICTIONAL competing product (Product B) based on Product A:

            Product A:
            {json.dumps(product_a, indent=2)}

            Requirements for Product B:
            - Different name (make it sound like a competing brand)
            - Similar to its category 
            - Different price point (can be higher or lower)
            - Similar but not identical formulation
            - Overlapping but different benefits
            - Different skin types (some overlap OK)
            - Generate unique product ID (e.g., prod_002)

            Make it realistic but clearly different from Product A.
        """
        
        # Returns ProductModel instance
        product_b: Product = self.structured_llm.invoke(prompt)
        
        product_b_model = product_b.model_dump()
        
        return {
            "product_b_model":product_b_model,
            "logs":[f"[{self.name}] Generated fictional Product B: {product_b.name}"]
        }