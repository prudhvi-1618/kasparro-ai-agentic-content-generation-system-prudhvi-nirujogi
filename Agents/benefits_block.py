from ..model.schema import BenefitsBlock
from ..state import AgentState
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BenefitsBlockAgent:
    """Dedicated agent for benefits block"""
    
    def __init__(self, llm, max_retries: int = 3):
        self.structured_llm = llm.with_structured_output(BenefitsBlock)
        self.name = "BenefitsBlockAgent"
        self.max_retries = max_retries
    
    def generate(self, state: AgentState) -> AgentState:
        """Generate benefits block with error handling"""
        
        if not state.get("product_model"):
            errors = [f"[{self.name}] No product model available"]
            return {
                "errors":errors
            }
        
        product = state["product_model"]
        
        prompt = f"""Create a benefits content block for this product.

            Product Benefits: {product.get('benefits', [])}
            Product Name: {product.get('name', '')}

            For each benefit, provide:
            1. The benefit name
            2. A detailed description explaining how the product achieves this benefit

            Output format: BenefitsBlock with list of BenefitDetail objects.
        """
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"[{self.name}] Attempt {attempt + 1}/{self.max_retries}")
                
                benefits_block: BenefitsBlock = self.structured_llm.invoke(prompt)
                
                benefits_block = benefits_block.model_dump()
                logs = [f"[{self.name}] Generated benefits block"]
                logger.info(f"[{self.name}] Success")
                
                return {
                    "benefits_block":benefits_block,
                    "logs":logs
                }
                
            except Exception as e:
                error_msg = [f"[{self.name}] Error on attempt {attempt + 1}: {str(e)}"]
                logger.error(error_msg)
                
                if attempt == self.max_retries - 1:
                    # Create fallback
                    benefits_block = {
                        "block_type": "benefits",
                        "content": [
                            {"benefit": b, "description": f"This product helps with {b.lower()}."}
                            for b in product.get('benefits', ['General skincare'])
                        ]
                    }
                    logs = [f"[{self.name}] Used fallback benefits block"]

                    return {
                        "benefits_block": benefits_block,
                        "logs": logs,
                        "errors": error_msg
                    }
        
        return {"logs": [f"[{self.name}] Unexpected exit"]}