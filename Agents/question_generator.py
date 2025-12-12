from ..state import AgentState
from ..model.schema import QuestionsOutput

import json

class QuestionGeneratorAgent:
    """Agent with structured question output"""
    
    def __init__(self, llm):
        self.structured_llm = llm.with_structured_output(QuestionsOutput)
        self.name = "QuestionGeneratorAgent"
    
    def generate(self, state: AgentState) -> AgentState:
        """Generate questions using structured output"""
        
        product = state["product_model"]
        
        prompt = f"""
            Generate AT LEAST 15 user questions about this product across certain categories.
            Example:
            - Category1 (3+ questions)
            - Category2 (3+ questions)
            - Category3 (3+ questions)
            - Category4 (3+ questions)
            - Category5 (2+ questions)
            - Category6 (2+ questions)

            Product:
            {json.dumps(product, indent=2)}

            Generate realistic questions a customer would ask. Base ALL questions on the actual product data.
        """
        
        # Returns QuestionsOutput instance
        questions_output: QuestionsOutput = self.structured_llm.invoke(prompt)
        
        questions = questions_output.model_dump()
        
        return {
            "questions":questions,
            "logs":[f"[{self.name}] Generated {questions_output.total_count} questions"]
        }
