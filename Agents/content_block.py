from ..model.schema import ContentBlocks
from ..state import AgentState
import json

class ContentBlockAgent:
    """Agent with structured content blocks"""
    
    def __init__(self, llm):
        self.structured_llm = llm.with_structured_output(ContentBlocks)
        self.name = "ContentBlockAgent"
    
    def generate_blocks(self, state: AgentState) -> AgentState:
        """Generate content blocks using structured output"""
        
        product = state["product_model"]
        
        prompt = f"""Create 5 reusable content blocks for this product:

            Product:
            {json.dumps(product, indent=2)}

            Generate:
            1. Benefits block - expand each benefit with detailed descriptions
            2. Usage block - create step-by-step instructions from the usage text
            3. Ingredients block - categorize and describe each ingredient
            4. Safety block - compile warnings and add standard precautions
            5. Overview block - create a compelling tagline and description

            Use ONLY the product data provided.
        """
        
        # Returns ContentBlocks instance
        blocks: ContentBlocks = self.structured_llm.invoke(prompt)
        
        content_blocks = blocks.model_dump()
        
        return {
            "content_blocks": content_blocks,
            "logs":[f"[{self.name}] Generated 5 content blocks"]
        }