from langgraph.graph import StateGraph,END
from langchain_groq.chat_models import ChatGroq

from .state import AgentState
from .config import config

from typing_extensions import Dict,Any
from .Agents.data_parser import DataParserAgent
from .Agents.question_generator import QuestionGeneratorAgent
from .Agents.faq_page import FAQPageAgent
from .Agents.content_block import ContentBlockAgent
from .Agents.product_page import ProductPageAgent
from .Agents.productb_generator import ProductBGeneratorAgent
from .Agents.comparison_page import ComparisonPageAgent
from .Agents.benefits_block import BenefitsBlockAgent
from .Agents.ingredients_block import IngredientsBlockAgent
from .Agents.overview_block import OverviewBlockAgent
from .Agents.safety_block import SafetyBlockAgent
from .Agents.usage_block import UsageBlockAgent

import os
import json
import errno
from pathlib import Path

class ContentGeneration:
    """Main orchestrator using LangGraph"""
    
    def __init__(self):
        # Initialize LLM
        self.llm = ChatGroq(
            model=config.LLM_MODEL,     
            api_key=config.GROQ_API_KEY,
            # Force-disable any possibility of usage of tools like search 
            # tools=[],                   
            # tool_choice={"type": "auto", "disable_parallel_tool_use": True},
        )

        # Initialize all agents
        self.data_parser = DataParserAgent(self.llm)
        self.question_generator = QuestionGeneratorAgent(self.llm)
        self.content_block_agent = ContentBlockAgent(self.llm)
        self.product_b_generator = ProductBGeneratorAgent(self.llm)

        self.benefits_agent = BenefitsBlockAgent(self.llm)
        self.usage_agent = UsageBlockAgent(self.llm)
        self.ingredients_agent = IngredientsBlockAgent(self.llm)
        self.safety_agent = SafetyBlockAgent(self.llm)
        self.overview_agent = OverviewBlockAgent(self.llm)

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

        workflow.add_node("generate_benefits", self.benefits_agent.generate)
        workflow.add_node("generate_usage", self.usage_agent.generate)
        workflow.add_node("generate_ingredients", self.ingredients_agent.generate)
        workflow.add_node("generate_safety", self.safety_agent.generate)
        workflow.add_node("generate_overview", self.overview_agent.generate)
        
        workflow.add_node("build_faq", self.faq_builder.build)
        workflow.add_node("build_product_page", self.product_page_builder.build)
        workflow.add_node("build_comparison", self.comparison_builder.build)

        # Define edges
        workflow.set_entry_point("parse_data")
        
        workflow.add_edge("parse_data", "parse_data_checkpoint")

        # All generation agents depend on parser
        workflow.add_edge("parse_data_checkpoint", "generate_questions")
        workflow.add_edge("parse_data_checkpoint", "generate_benefits")
        workflow.add_edge("parse_data_checkpoint", "generate_usage")
        workflow.add_edge("parse_data_checkpoint", "generate_ingredients")
        workflow.add_edge("parse_data_checkpoint", "generate_safety")
        workflow.add_edge("parse_data_checkpoint", "generate_overview")
        workflow.add_edge("parse_data_checkpoint", "generate_product_b")
        
        # Page builders depend on their respective inputs
        workflow.add_edge("generate_questions", "build_faq")
        workflow.add_edge("generate_benefits", "build_product_page")
        workflow.add_edge("generate_usage", "build_product_page")
        workflow.add_edge("generate_ingredients", "build_product_page")
        workflow.add_edge("generate_safety", "build_product_page")
        workflow.add_edge("generate_overview", "build_product_page")
        workflow.add_edge("generate_product_b", "build_comparison")
        
        # All end
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
    current_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = Path(current_dir) / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    outputs = {
        "faq.json": results["faq_page"],
        "product_page.json": results["product_page"],
        "comparison_page.json": results["comparison_page"]
    }
    
    print("\n Saving outputs:")
    print("-" * 60)
    for filename, content in outputs.items():
        filepath = output_dir / filename
        save_json_safely(content, filepath)

def save_json_safely(data: dict, filepath: str) -> None:
    """
    Safely save JSON with proper error handling and user-friendly messages.
    """
    try:
        # Ensure parent directory exists
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)

        # Write with atomic safety (temp file + rename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Atomic replace (avoids partial writes)
        os.replace(filepath, filepath)
        
        print(f"  ✓: Saved: {filepath}")

    except PermissionError as e:
        print(f"  Failed: Permission denied: Cannot write to {filepath}")
        print(f"         Run as admin or check folder permissions.")
        raise
    except OSError as e:
        if e.errno == errno.ENOSPC:
            print(f"  Failed: Disk full — cannot save {filepath}")
        elif e.errno == errno.EACCES:
            print(f"  Failed: Access denied: {filepath}")
        else:
            print(f"  Failed: Failed to save {filepath}: {e}")
        raise
    except Exception as e:
        print(f"  Failed: Unexpected error saving {filepath}: {e}")
        raise

if __name__ == "__main__":
    main()