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
        questions_data = state["questions"]
        
        total_questions = questions_data["total_count"]
        questions_list = questions_data["questions"]

        system_prompt = f"""You are the FAQ Page Builder Agent.

            Your ONLY job is to create a structured FAQ page using **ALL {total_questions} questions** provided below.

            RULES — FOLLOW EXACTLY:
            - Use **every single question** from the list. Do not skip, summarize, filter, or discard any.
            - You MUST output exactly {total_questions} Q&A pairs — no more, no less.
            - Group questions by their original 'category' field.
            - Write clear, accurate, friendly answers based ONLY on the provided product data.
            - Do not add new questions.
            - Do not remove or rephrase existing questions.
            - Set metadata.question_count = {total_questions}
            - Set metadata.generated_at = current ISO timestamp (you can leave placeholder, it will be overwritten)

            This is a strict data preservation step. Losing questions = pipeline failure.
        """

        human_prompt = f"""Product Data:
            {json.dumps(product, indent=2)}

            All {total_questions} Questions (use every one):
            {json.dumps(questions_list, indent=2)}

            Now build the FAQ page with exactly {total_questions} Q&A pairs.
        """

        messages = [
            ("system", system_prompt),
            ("human", human_prompt)
        ]

        # Returns FAQPage instance
        faq: FAQPage = self.structured_llm.invoke(messages)
        
        # Set timestamp
        faq.metadata.generated_at = datetime.utcnow().isoformat()
        
        faq_page= faq.model_dump()
        
        return {
            "faq_page":faq_page,
            "logs":[f"[{self.name}] Built FAQ page with {faq.metadata.question_count} questions"]
        }