from typing import TypedDict
from typing_extensions import Dict,Any,Annotated,List
from operator import add

class AgentState(TypedDict):
    """Central state managed by LangGraph"""
    # Input
    raw_product_data: Dict[str, Any]
    
    # Parsed models
    product_model: Dict[str, Any]
    product_b_model: Dict[str, Any]
    
    # Generated content
    questions: Dict[str, Any]
    content_blocks: Annotated[dict, lambda x, y: {**x, **y}]
    
    # Granular content blocks
    benefits_block: Dict[str, Any]
    usage_block: Dict[str, Any]
    ingredients_block: Dict[str, Any]
    safety_block: Dict[str, Any]
    overview_block: Dict[str, Any]

    # Final outputs
    faq_page: Dict[str, Any]
    product_page: Dict[str, Any]
    comparison_page: Dict[str, Any]
    
    # Metadata
    logs: Annotated[List[str], add]
    errors: Annotated[List[str], add]