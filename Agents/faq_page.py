from ..state import AgentState
from ..model.schema import FAQPage

import json
from datetime import datetime

class FAQPageAgent:
    """Agent to build FAQ page"""
    
    def __init__(self, llm):
        self.structured_llm = llm.with_structured_output(FAQPage)
        self.name = "FAQPageAgent"
    
    def build(self, state: AgentState) -> AgentState:
        """Build FAQ page using structured output"""
        
        product = state["product_model"]
        questions = state["questions"]
        
        prompt = f"""Create a comprehensive FAQ page with MINIMUM 5 Q&A pairs.

            Product:
            {json.dumps(product, indent=2)}

            Available Questions:
            {json.dumps(questions, indent=2)}

            Instructions:
            1. Group questions by category
            2. Write clear, helpful answers based ONLY on product data
            3. Create at least 5 Q&A pairs (you can add more if relevant)
            4. Set generated_at to current ISO timestamp
            5. Count total questions in metadata

            Do not invent facts not in the product data.

            Use proper JSON formatting:
            - Use " for strings (not \")
            - Don't escape single quotes (use ' not \')
        """
        
        # Returns FAQPage instance
        faq: FAQPage = self.structured_llm.invoke(prompt)
        
        # Set timestamp
        faq.metadata.generated_at = datetime.utcnow().isoformat()
        
        faq_page= faq.model_dump()
        # logs = state["logs"].append(f"[{self.name}] Built FAQ page with {faq.metadata.question_count} questions")
        
        return {
            "faq_page":faq_page,
            "logs":[f"[{self.name}] Built FAQ page with {faq.metadata.question_count} questions"]
        }