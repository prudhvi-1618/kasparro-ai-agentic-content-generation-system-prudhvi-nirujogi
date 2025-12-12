import pytest
from main import ContentGenerationOrchestrator
from unittest.mock import MagicMock

def test_full_pipeline_runs_without_crashing(sample_product_data, monkeypatch):
    # Mock LLM to avoid real API calls
    mock_llm = MagicMock()
    mock_llm.with_structured_output.return_value.invoke.return_value = MagicMock(model_dump=lambda: {"mock": "data"})
    
    monkeypatch.setattr("builtins.print", lambda *args: None)  
    orchestrator = ContentGenerationOrchestrator(api_key="fake")
    monkeypatch.setattr(orchestrator, "llm", mock_llm)
    
    results = orchestrator.execute(sample_product_data)
    
    assert "product_page" in results
    assert "faq_page" in results
    assert "comparison_page" in results
    assert len(results.get("errors", [])) == 0
    assert len(results.get("logs", [])) > 5