from ..model.schema import SafetyBlock
from ..state import AgentState
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SafetyBlockAgent:
    """Dedicated agent for safety block"""
    
    def __init__(self, llm, max_retries: int = 3):
        self.structured_llm = llm.with_structured_output(SafetyBlock)
        self.name = "SafetyBlockAgent"
        self.max_retries = max_retries
    
    def generate(self, state: AgentState) -> AgentState:
        """Generate safety block with error handling"""
        
        if not state.get("product_model"):
            errors = [f"[{self.name}] No product model available"]
            return {
                "errors":errors
            }
        
        product = state["product_model"]
        
        prompt = f"""Create a safety information block for this product.

            Warnings: {product.get('warnings', '')}
            Suitable For: {product.get('skin_types', [])}

            Provide:
            1. Warnings from product data
            2. Suitable skin types
            3. Standard precautions (3-4 items)

            Output format: SafetyBlock.
        """
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"[{self.name}] Attempt {attempt + 1}/{self.max_retries}")
                
                safety_block: SafetyBlock = self.structured_llm.invoke(prompt)
                
                safety_block = safety_block.model_dump()
                logs = [f"[{self.name}] Generated safety block"]
                logger.info(f"[{self.name}] Success")
                
                return {
                    "safety_block":safety_block,
                    "logs":logs
                }
                
            except Exception as e:
                error_msg = [f"[{self.name}] Error on attempt {attempt + 1}: {str(e)}"]
                logger.error(error_msg)
                
                if attempt == self.max_retries - 1:
                    safety_block = {
                        "block_type": "safety",
                        "warnings": product.get('warnings', 'Consult dermatologist if irritation occurs'),
                        "suitable_for": product.get('skin_types', ['All skin types']),
                        "precautions": [
                            "Patch test before first use",
                            "Avoid contact with eyes",
                            "Store in cool, dry place",
                            "Discontinue if irritation occurs"
                        ]
                    }
                    logs = [f"[{self.name}] Used fallback safety block"]

                    return {
                        "safety_block":safety_block,
                        "logs":logs,
                        "errors":error_msg
                    }
        
        return {"logs": [f"[{self.name}] Unexpected exit"]}