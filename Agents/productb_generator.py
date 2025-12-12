from ..model.schema import Product
from ..state import AgentState
from typing_extensions import Dict,Any
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProductBGeneratorAgent:
    """Agent to generate fictional competitor"""
    
    def __init__(self, llm, max_retries: int = 3):
        self.structured_llm = llm.with_structured_output(Product)
        self.name = "ProductBGeneratorAgent"
        self.max_retries = max_retries
    
    def generate(self, state: AgentState) -> AgentState:
        """Generate Product B using structured output"""
        
        product_a = state["product_model"]

        if not product_a:
            return {
                "errors": [f"[{self.name}] Missing product_model"],
                "logs": [f"[{self.name}] Skipped — no input product"]
            }
        
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
        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(f"[{self.name}] Generating Product B — attempt {attempt}")
                # Returns ProductModel instance
                product_b: Product = self.structured_llm.invoke(prompt)
                
                product_b_model = product_b.model_dump()
                
                return {
                    "product_b_model":product_b_model,
                    "logs":[f"[{self.name}] Generated fictional Product B: {product_b.name}"]
                }
            except Exception as e:
                logger.error(f"[{self.name}] Attempt {attempt} failed: {e}")
                
                if attempt == self.max_retries:
                    fallback = self._create_fallback_product_b(product_a)
                    return {
                        "product_b_model": fallback,
                        "logs": [f"[{self.name}] Used fallback Product B: {fallback['name']}"],
                        "errors": [f"Product B generation failed after {self.max_retries} attempts"]
                    }

        return {"logs": [f"[{self.name}] Unexpected exit"]}

    def _create_fallback_product_b(self, product_a: Dict[str, Any]) -> Dict[str, Any]:
        """Deterministic fallback — always works"""
        base_price = product_a["price"]["amount"] if isinstance(product_a["price"], dict) else product_a["price"]
        
        return {
            "id": "prod_002",
            "name": "RadiantGlow Vitamin C Serum",
            "category": "skincare",
            "concentration": "15% Vitamin C + Ferulic",
            "skin_types": ["Normal", "Combination", "Dry"],
            "ingredients": ["L-Ascorbic Acid", "Ferulic Acid", "Hyaluronic Acid", "Vitamin E"],
            "benefits": ["Brightens skin", "Reduces dark spots", "Boosts collagen", "Hydrates deeply"],
            "usage_instructions": "Apply 3-4 drops in the morning after cleansing",
            "warnings": "Patch test recommended. Avoid eye area.",
            "price": {"amount": int(base_price * 1.35), "currency": "INR", "display": ""},
        }