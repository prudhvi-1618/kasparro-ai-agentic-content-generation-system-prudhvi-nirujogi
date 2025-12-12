from ..model.schema import OverviewBlock
from ..state import AgentState

import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OverviewBlockAgent:
    """Dedicated agent for overview block"""
    
    def __init__(self, llm, max_retries: int = 3):
        self.structured_llm = llm.with_structured_output(OverviewBlock)
        self.name = "OverviewBlockAgent"
        self.max_retries = max_retries
    
    def generate(self, state: AgentState) -> AgentState:
        """Generate overview block with error handling"""
        
        if not state.get("product_model"):
            errors = [f"[{self.name}] No product model available"]
            return {
                "errors":errors
            }
        
        product = state["product_model"]
        
        prompt = f"""Create an overview block for this product.

            Product: {json.dumps(product, indent=2)}

            Provide:
            1. A catchy tagline (15-20 words)
            2. A compelling description (50-100 words)

            Output format: OverviewBlock.
        """
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"[{self.name}] Attempt {attempt + 1}/{self.max_retries}")
                
                overview_block: OverviewBlock = self.structured_llm.invoke(prompt)
                
                overview_block = overview_block.model_dump()
                logs = [f"[{self.name}] Generated overview block"]
                logger.info(f"[{self.name}] Success")
                
                return {
                    "overview_block":overview_block,
                    "logs":logs
                }
                
            except Exception as e:
                error_msg = [f"[{self.name}] Error on attempt {attempt + 1}: {str(e)}"]
                logger.error(error_msg)

                if attempt == self.max_retries - 1:
                    overview_block = {
                        "block_type": "overview",
                        "tagline": f"{product.get('concentration', '')} for {', '.join(product.get('benefits', ['skincare']))}",
                        "description": f"Experience {product.get('name', 'this product')} formulated for {', '.join(product.get('skin_types', ['all skin types']))}."
                    }
                    logs = [f"[{self.name}] Used fallback ingredients block"]

                    return {
                        "overview_block":overview_block,
                        "logs":logs,
                        "errors":error_msg
                    }
        
        return {"logs": [f"[{self.name}] Unexpected exit"]}