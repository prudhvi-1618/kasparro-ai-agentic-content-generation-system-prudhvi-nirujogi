from ..model.schema import IngredientsBlock
from ..state import AgentState
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IngredientsBlockAgent:
    """Dedicated agent for ingredients block"""
    
    def __init__(self, llm, max_retries: int = 3):
        self.structured_llm = llm.with_structured_output(IngredientsBlock)
        self.name = "IngredientsBlockAgent"
        self.max_retries = max_retries
    
    def generate(self, state: AgentState) -> AgentState:
        """Generate ingredients block with error handling"""
        
        if not state.get("product_model"):
            errors = [f"[{self.name}] No product model available"]
            return {
                "errors":errors
            }
        
        product = state["product_model"]
        
        prompt = f"""Create an ingredients block for this product.

            Primary Ingredient: {product.get('concentration', '')}
            All Ingredients: {product.get('ingredients', [])}

            Provide:
            1. Primary active ingredient
            2. Supporting ingredients (list)
            3. Details for each ingredient (name and purpose)

            Output format: IngredientsBlock.
        """
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"[{self.name}] Attempt {attempt + 1}/{self.max_retries}")
                
                ingredients_block: IngredientsBlock = self.structured_llm.invoke(prompt)
                
                ingredients_block = ingredients_block.model_dump()
                logs = [f"[{self.name}] Generated ingredients block"]
                logger.info(f"[{self.name}] Success")
                
                return {
                    "ingredients_block":ingredients_block,
                    "logs":logs
                }
                
            except Exception as e:
                error_msg = [f"[{self.name}] Error on attempt {attempt + 1}: {str(e)}"]
                logger.error(error_msg)
                
                if attempt == self.max_retries - 1:
                    ingredients = product.get('ingredients', [])
                    ingredients_block = {
                        "block_type": "ingredients",
                        "primary": product.get('concentration', 'Active ingredient'),
                        "supporting": ingredients[1:] if len(ingredients) > 1 else [],
                        "details": [
                            {"name": ing, "purpose": "Skin care benefit"}
                            for ing in ingredients
                        ]
                    }
                    logs = [f"[{self.name}] Used fallback ingredients block"]

                    return {
                        "ingredients_block":ingredients_block,
                        "logs":logs,
                        "errors":error_msg
                    }
        
        return {"logs": [f"[{self.name}] Unexpected exit"]}