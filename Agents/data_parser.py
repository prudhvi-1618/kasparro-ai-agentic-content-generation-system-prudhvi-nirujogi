from langchain_core.messages import SystemMessage,HumanMessage
from ..state import AgentState
from ..model.schema import Product
import json

# AGENT 1: DATA PARSER AGENT
class DataParserAgent:
    """Agent with structured output using Pydantic"""
    
    def __init__(self, llm):
        # Create structured LLM that outputs ProductModel
        self.structured_llm = llm.with_structured_output(Product)
        self.name = "DataParserAgent"
    
    def parse(self, state: AgentState) -> AgentState:
        """Parse raw product data using structured output"""
        
        # Create prompt
        prompt = f"""
            Parse this product data into a structured format:

            Product Data:
            {json.dumps(state['raw_product_data'], indent=2)}

            Instructions:
            2. Normalize all fields
            3. Parse comma-separated values into lists
            4. Extract price value with it's currency symbol
        """
        
        # Invoke structured LLM - returns ProductModel instance
        product_model: Product = self.structured_llm.invoke(prompt)

        # Convert to dict for state
        product_model = product_model.model_dump()
        # logs=state["logs"].append(f"[{self.name}] Parsed product data successfully")
        
        return {
            "product_model":product_model,
            "logs":[f"[{self.name}] Parsed product data successfully"]
        }