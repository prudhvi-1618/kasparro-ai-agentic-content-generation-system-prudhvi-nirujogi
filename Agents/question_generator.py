from ..state import AgentState
from ..model.schema import QuestionsOutput
from typing_extensions import Dict,Any
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QuestionGeneratorAgent:
    """Agent with structured question output"""
    
    def __init__(self, llm, max_retries: int = 3):
        self.structured_llm = llm.with_structured_output(QuestionsOutput)
        self.name = "QuestionGeneratorAgent"
        self.max_retries = max_retries
    
    def generate(self, state: AgentState) -> AgentState:
        """Generate questions using structured output"""
        
        product = state["product_model"]

        if not product:
            return {
                "errors": [f"[{self.name}] Missing product_model"],
                "logs": [f"[{self.name}] Skipped — no product data"]
            }
        
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

        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(f"[{self.name}] Generating questions — attempt {attempt}")
        
                # Returns QuestionsOutput instance
                questions_output: QuestionsOutput = self.structured_llm.invoke(prompt)
                
                questions = questions_output.model_dump()
                
                return {
                    "questions":questions,
                    "logs":[f"[{self.name}] Generated {questions_output.total_count} questions"]
                }
            
            except Exception as e:
                logger.error(f"[{self.name}] Attempt {attempt} failed: {e}")
                
                if attempt == self.max_retries:
                    fallback = self._create_fallback_questions(product)
                    return {
                        "questions": fallback,
                        "logs": [f"[{self.name}] Used fallback — 15 questions generated"],
                        "errors": [f"Question generation failed after {self.max_retries} attempts"]
                    }

        return {"logs": [f"[{self.name}] Unexpected exit"]}

    def _create_fallback_questions(self, product: dict) -> Dict[str, Any]:
        """Deterministic fallback — always returns 15 solid questions"""
        name = product.get("name", "this product")
        return {
            "questions": [
                {"category": "Informational", "question": f"What is {name}?"},
                {"category": "Informational", "question": "What skin concerns does it target?"},
                {"category": "Informational", "question": "What is the main active ingredient?"},

                {"category": "Ingredients", "question": "What are the full ingredients?"},
                {"category": "Ingredients", "question": "Is it fragrance-free?"},
                {"category": "Ingredients", "question": "Does it contain alcohol or parabens?"},

                {"category": "Usage", "question": "How do I apply it?"},
                {"category": "Usage", "question": "When should I use it — morning or night?"},
                {"category": "Usage", "question": "How many drops/pumps should I use?"},

                {"category": "Safety", "question": "Is it safe for sensitive skin?"},
                {"category": "Safety", "question": "Can I use it during pregnancy?"},
                {"category": "Safety", "question": "Should I patch test first?"},

                {"category": "Benefits", "question": "How long until I see results?"},
                {"category": "Benefits", "question": "Will it help with dark spots?"},

                {"category": "Purchase", "question": "How much does it cost?"},
                {"category": "Purchase", "question": "Is there a subscription option?"}
            ],
            "total_count": 16
        }
