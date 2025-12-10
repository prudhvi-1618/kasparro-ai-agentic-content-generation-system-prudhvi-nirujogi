from langgraph.graph import StateGraph,END
from langchain_groq.chat_models import ChatGroq

from .state import AgentState

from typing_extensions import Dict,Any
from dotenv import load_dotenv
from .Agents.data_parser import DataParserAgent
from .Agents.question_generator import QuestionGeneratorAgent
from .Agents.faq_page import FAQPageAgent
from .Agents.content_block import ContentBlockAgent
from .Agents.product_page import ProductPageAgent
from .Agents.productb_generator import ProductBGeneratorAgent
from .Agents.comparison_page import ComparisonPageAgent

import os
import json

load_dotenv()

class ContentGeneration:
    """Main orchestrator using LangGraph"""
    
    def __init__(self):
        # Initialize LLM
        self.llm = ChatGroq(model="llama-3.3-70b-versatile")

        # Initialize all agents
        self.data_parser = DataParserAgent(self.llm)
        self.question_generator = QuestionGeneratorAgent(self.llm)
        self.content_block_agent = ContentBlockAgent(self.llm)
        self.product_b_generator = ProductBGeneratorAgent(self.llm)
        self.faq_builder = FAQPageAgent(self.llm)
        self.product_page_builder = ProductPageAgent(self.llm)
        self.comparison_builder = ComparisonPageAgent(self.llm)

        # Build the graph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        
        workflow = StateGraph(AgentState)

        def checkpoint(_state):
            return {} 

        # Add nodes
        workflow.add_node("parse_data", self.data_parser.parse)

        workflow.add_node("parse_data_checkpoint", checkpoint)

        workflow.add_node("generate_questions", self.question_generator.generate)
        workflow.add_node("generate_content_blocks", self.content_block_agent.generate_blocks)
        workflow.add_node("generate_product_b", self.product_b_generator.generate)
        workflow.add_node("build_faq", self.faq_builder.build)
        workflow.add_node("build_product_page", self.product_page_builder.build)
        workflow.add_node("build_comparison", self.comparison_builder.build)

        # Define edges
        workflow.set_entry_point("parse_data")
        
        workflow.add_edge("parse_data", "parse_data_checkpoint")

        # # Parallel branches after parsing
        workflow.add_edge("parse_data_checkpoint", "generate_questions")
        workflow.add_edge("parse_data_checkpoint", "generate_content_blocks")
        workflow.add_edge("parse_data", "generate_product_b")

        # # Page builders
        workflow.add_edge("generate_questions", "build_faq")
        workflow.add_edge("generate_content_blocks", "build_product_page")
        workflow.add_edge("generate_product_b", "build_comparison")
        
        # # All end
        workflow.add_edge("build_faq", END)
        workflow.add_edge("build_product_page", END)
        workflow.add_edge("build_comparison", END)

        return workflow.compile()
    
    def execute(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the entire pipeline"""
            
        initial_state = {
            "raw_product_data": product_data,
            "product_model": {},
            "product_b_model": {},
            "questions": {},
            "content_blocks": {},
            "faq_page": {},
            "product_page": {},
            "comparison_page": {},
            "logs": [],
            "errors": []
        }
        
        # Run the graph
        final_state = self.graph.invoke(initial_state)
        
        return final_state

def main():
    """Main execution function"""
    
    PRODUCT_DATA = {
        "name": "GlowBoost Vitamin C Serum",
        "concentration": "10% Vitamin C",
        "skin_type": "Oily, Combination",
        "key_ingredients": "Vitamin C, Hyaluronic Acid",
        "benefits": "Brightening, Fades dark spots",
        "how_to_use": "Apply 2–3 drops in the morning before sunscreen",
        "side_effects": "Mild tingling for sensitive skin",
        "price": "₹699"
    }

    print("\n\nMulti-Agent Content Generation System (Structured Output)")
    print("=" * 60)
    
    orchestrator = ContentGeneration()
    
    print("\n Executing pipeline with structured outputs...\n")
    results = orchestrator.execute(PRODUCT_DATA)
    
    # Save outputs
    # output_dir = "outputs"
    current_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(current_dir, "output")
    os.makedirs(output_dir, exist_ok=True)
    
    outputs = {
        "faq.json": results["faq_page"],
        "product_page.json": results["product_page"],
        "comparison_page.json": results["comparison_page"]
    }
    
    print("\n Saving outputs:")
    print("-" * 60)
    for filename, content in outputs.items():
        filepath = os.path.join(output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(content, f, indent=2, ensure_ascii=False)
        print(f"  ✓ Saved: {filepath}")

if __name__ == "__main__":
    main()