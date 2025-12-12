from ..model.schema import ProductPage
from ..state import AgentState
from typing_extensions import Dict,Any
import json
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProductPageAgent:
    """Agent to build product page"""
    
    def __init__(self, llm, max_retries: int = 3):
        self.structured_llm = llm.with_structured_output(ProductPage)
        self.name = "ProductPageAgent"
        self.max_retries = max_retries
    
    def build(self, state: AgentState) -> AgentState:
        """Build product page using structured output"""
        
        product = state["product_model"]

        if not product:
            return {
                "errors": [f"[{self.name}] Missing product_model"],
                "logs": [f"[{self.name}] Skipped — no product data"]
            }
        
        # Collect all granular blocks safely
        blocks = {
            "benefits": state.get("benefits_block", {}),
            "usage": state.get("usage_block", {}),
            "ingredients": state.get("ingredients_block", {}),
            "safety": state.get("safety_block", {}),
            "overview": state.get("overview_block", {})
        }
        
        prompt = f"""Create a complete product page using the product data and content blocks.

            Product:
            {json.dumps(product, indent=2)}

            Content Blocks:
            {json.dumps(blocks, indent=2)}

            Instructions:
            1. Create Product Model with product name, compelling tagline, and formatted price
            2. Build overview from product data
            3. Use benefits from benefits_block
            4. Use ingredients from ingredients_block
            5. Use usage from usage_block
            6. Use safety from safety_block
            7. Set generated_at to current ISO timestamp

            Compose a professional, complete product page.
        """
        for attempt in range(1, self.max_retries + 1):
            try:

                logger.info(f"[{self.name}] Building product page — attempt {attempt}")
                # Returns ProductPage instance
                product_page: ProductPage = self.structured_llm.invoke(prompt)
                
                # Set timestamp
                product_page.metadata.generated_at = datetime.utcnow().isoformat()
                
                product_page = product_page.model_dump()
                
                return {
                    "product_page":product_page,
                    "logs":[f"[{self.name}] Built product page"]
                }
            
            except Exception as e:
                logger.error(f"[{self.name}] Attempt {attempt} failed: {e}")
                
                if attempt == self.max_retries:
                    fallback_page = self._create_fallback_product_page(product, blocks)
                    return {
                        "product_page": fallback_page,
                        "logs": [f"[{self.name}] Used deterministic fallback product page"],
                        "errors": [f"Product page generation failed after {self.max_retries} attempts"]
                    }

        return {"logs": [f"[{self.name}] Unexpected exit"]}

    def _create_fallback_product_page(self, product: dict, blocks: dict) -> Dict[str, Any]:
        """100% deterministic fallback — always returns valid page"""
        price_amount = product["price"]["amount"] if isinstance(product["price"], dict) else product["price"]
        
        return {
            "template": "product_page_v1",
            "hero": {
                "product_name": product.get("name", "Premium Skincare Product"),
                "tagline": f"Advanced {product.get('concentration', '')} Formula",
                "price": {
                    "amount": price_amount,
                    "currency": "INR",
                    "display": f"₹{int(price_amount):,}"
                }
            },
            "overview": {
                "description": f"High-performance skincare solution designed for {', '.join(product.get('skin_types', ['all skin types']))}.",
                "skin_types": product.get("skin_types", []),
                "category": "skincare"
            },
            "benefits": blocks.get("benefits", {}).get("content", []),
            "ingredients": blocks.get("ingredients", {}),
            "usage": blocks.get("usage", {}),
            "safety": blocks.get("safety", {}),
            "metadata": {
                "product_id": product.get("id", "prod_001"),
                "generated_at": datetime.utcnow().isoformat()
            }
        }