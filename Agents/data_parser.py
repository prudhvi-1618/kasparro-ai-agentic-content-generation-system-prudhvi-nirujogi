from ..state import AgentState
from ..model.schema import Product
import json
import logging
from pydantic import ValidationError
from typing_extensions import Dict,Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataParserAgent:
    """Agent with structured output using Pydantic"""
    
    def __init__(self, llm, max_retries: int = 3):
        # Create structured LLM that outputs ProductModel
        self.structured_llm = llm.with_structured_output(Product)
        self.name = "DataParserAgent"
        self.max_retries = max_retries
    
    def parse(self, state: AgentState) -> AgentState:
        """Parse raw product data using structured output"""
        
        # Create prompt
        prompt = f"""
            Parse this product data into a structured format:

            Product Data:
            {json.dumps(state['raw_product_data'], indent=2)}

            Instructions:
            1. Normalize all fields
            2. Parse comma-separated values into lists
            3. Extract price value with it's currency symbol
        """
        for attempt in range(self.max_retries):
            try:
                logger.info(f"[{self.name}] Attempt {attempt + 1}/{self.max_retries}")
                # Invoke structured LLM - returns ProductModel instance
                product_model: Product = self.structured_llm.invoke(prompt)

                # Convert to dict for state
                product_model = product_model.model_dump()
                logger.info(f"[{self.name}] Success")

                return {
                    "product_model":product_model,
                    "logs":[f"[{self.name}] Parsed product data successfully"]
                }
            
            except ValidationError as e:
                error_msg = [f"[{self.name}] Validation error on attempt {attempt + 1}: {str(e)}"]
                logger.error(error_msg)
                
                if attempt == self.max_retries - 1:
                    # Final attempt failed - use fallback
                    state["product_model"] = self._create_fallback_model(state['raw_product_data'])
                    logs = [f"[{self.name}] Used fallback model after {self.max_retries} attempts"]

                    return {
                        "product_model":product_model,
                        "errors":error_msg,
                        "logs":logs
                    }
                    
            except Exception as e:
                error_msg = [f"[{self.name}] Unexpected error on attempt {attempt + 1}: {str(e)}"]
                logger.error(error_msg)
                
                if attempt == self.max_retries - 1:
                    product_model = self._create_fallback_model(state['raw_product_data'])
                    logs = [f"[{self.name}] Used fallback model after error"]

                    return {
                        "product_model":product_model,
                        "logs":logs,
                        "errors":error_msg
                    }
        
        return {"logs": [f"[{self.name}] Unexpected exit"]}
    
    def _create_fallback_model(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a basic fallback model from raw data"""
        return {
            "id": "prod_001",
            "name": raw_data.get("name", "Unknown Product"),
            "category": "skincare",
            "concentration": raw_data.get("concentration", "Unknown"),
            "skin_types": raw_data.get("skin_type", "All").split(", "),
            "ingredients": raw_data.get("key_ingredients", "").split(", "),
            "benefits": raw_data.get("benefits", "").split(", "),
            "usage_instructions": raw_data.get("how_to_use", "See packaging"),
            "warnings": raw_data.get("side_effects", "Consult dermatologist"),
            "price": int(''.join(filter(str.isdigit, str(raw_data.get("price", "0"))))),
            "currency": "INR"
        }