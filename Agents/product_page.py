from ..model.schema import ProductPage
from ..state import AgentState
import json
from datetime import datetime

class ProductPageAgent:
    """Agent to build product page"""
    
    def __init__(self, llm):
        self.structured_llm = llm.with_structured_output(ProductPage)
        self.name = "ProductPageAgent"
    
    def build(self, state: AgentState) -> AgentState:
        """Build product page using structured output"""
        
        product = state["product_model"]
        blocks = state["content_blocks"]
        
        prompt = f"""Create a complete product page using the product data and content blocks.

            Product:
            {json.dumps(product, indent=2)}

            Content Blocks:
            {json.dumps(blocks, indent=2)}

            Instructions:
            1. Create hero section with product name, compelling tagline, and formatted price
            2. Build overview from product data
            3. Use benefits from benefits_block
            4. Use ingredients from ingredients_block
            5. Use usage from usage_block
            6. Use safety from safety_block
            7. Set generated_at to current ISO timestamp

            Compose a professional, complete product page.
        """
        
        # Returns ProductPage instance
        product_page: ProductPage = self.structured_llm.invoke(prompt)
        
        # Set timestamp
        product_page.metadata.generated_at = datetime.utcnow().isoformat()
        
        product_page = product_page.model_dump()
        # logs = state["logs"].append(f"[{self.name}] Built product page")
        
        return {
            "product_page":product_page,
            "logs":[f"[{self.name}] Built product page"]
        }