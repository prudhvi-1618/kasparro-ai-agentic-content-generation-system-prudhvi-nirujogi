from ..model.schema import UsageBlock
from ..state import AgentState
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UsageBlockAgent:
    """Dedicated agent for usage block"""
    
    def __init__(self, llm, max_retries: int = 3):
        self.structured_llm = llm.with_structured_output(UsageBlock)
        self.name = "UsageBlockAgent"
        self.max_retries = max_retries
    
    def generate(self, state: AgentState) -> AgentState:
        """Generate usage block with error handling"""
        
        if not state.get("product_model"):
            errors = [f"[{self.name}] No product model available"]
            return {
                "errors":errors
            }
        
        product = state["product_model"]
        
        prompt = f"""Create a usage instructions block for this product.

            Usage Instructions: {product.get('usage_instructions', '')}

            Provide:
            1. The main instructions
            2. Step-by-step breakdown (4-5 steps)
            3. Usage frequency (morning/evening/daily)

            Output format: UsageBlock with instructions, steps array, and frequency.
        """
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"[{self.name}] Attempt {attempt + 1}/{self.max_retries}")
                
                usage_block: UsageBlock = self.structured_llm.invoke(prompt)
                
                usage_block = usage_block.model_dump()
                logs = [f"[{self.name}] Generated usage block"]
                logger.info(f"[{self.name}] Success")
                
                return {
                    "usage_block":usage_block,
                    "logs":logs
                }
                
            except Exception as e:
                error_msg = [f"[{self.name}] Error on attempt {attempt + 1}: {str(e)}"]
                logger.error(error_msg)
                
                if attempt == self.max_retries - 1:
                    usage_block = {
                        "block_type": "usage",
                        "instructions": product.get('usage_instructions', 'See packaging'),
                        "steps": [
                            "Cleanse your face",
                            "Apply product",
                            "Massage gently",
                            "Follow with moisturizer"
                        ],
                        "frequency": "Daily"
                    }
                    logs = [f"[{self.name}] Used fallback usage block"]

                    return {
                        "usage_block":usage_block,
                        "logs":logs,
                        "errors":error_msg
                    }
        
        return {"logs": [f"[{self.name}] Unexpected exit"]}
