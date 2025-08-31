import pytest
from unittest.mock import patch, MagicMock

from services.llm import build_summarization_chain, build_task_chain, build_qa_chain


class TestSummarizationChain:
    @pytest.fixture
    def mock_llm(self):
        """Mock LLM that returns predefined responses"""
        mock = MagicMock()
        # Set up the mock to return formatted summary
        mock.return_value = """
        ## Summary
        - Key point 1 about the meeting
        - Key point 2 about the decision
        - Key point 3 about follow-up actions
        
        ## Decisions
        - Decision 1
        - Decision 2
        
        ## Action Items
        - Action item 1
        - Action item 2
        - Action item 3
        """
        return mock
    
    @patch('services.llm.get_llm')
    def test_summarize(self, mock_get_llm, mock_llm):
        """Test that summarization chain returns expected structure"""
        mock_get_llm.return_value = mock_llm
        
        # Create the chain
        summarize_chain = build_summarization_chain()
        
        # Run the chain
        result = summarize_chain("Test content for summarization")
        
        # Check structure
        assert "summary" in result
        assert "highlights" in result
        assert "decisions" in result
        assert "action_items" in result
        
        # Check content
        assert len(result["highlights"]) > 0
        assert len(result["decisions"]) > 0
        assert len(result["action_items"]) > 0


class TestTaskChain:
    @pytest.fixture
    def mock_llm(self):
        """Mock LLM that returns predefined task JSON"""
        mock = MagicMock()
        mock.return_value = {
            "tasks": [
                {
                    "description": "Complete project proposal",
                    "due_date": "2023-12-31T23:59:59Z",
                    "owner": "John Doe",
                    "completed": False
                },
                {
                    "description": "Schedule meeting with stakeholders",
                    "owner": "Jane Smith",
                    "completed": False
                }
            ]
        }
        return mock
    
    @patch('services.llm.get_llm')
    def test_tasks(self, mock_get_llm, mock_llm):
        """Test that task chain returns valid task schema"""
        mock_get_llm.return_value = mock_llm
        
        # Create the chain
        task_chain = build_task_chain()
        
        # Run the chain
        result = task_chain("Test content with tasks")
        
        # Check structure
        assert "tasks" in result
        assert len(result["tasks"]) > 0
        
        # Check task schema
        for task in result["tasks"]:
            assert "description" in task
            assert isinstance(task["description"], str)
            assert "completed" in task
            assert isinstance(task["completed"], bool)


class TestQAChain:
    @pytest.fixture
    def mock_retriever(self):
        """Mock retriever that returns predefined documents"""
        mock = MagicMock()
        mock.get_relevant_documents.return_value = [
            MagicMock(
                page_content="Document 1 content",
                metadata={"note_id": "123e4567-e89b-12d3-a456-426614174000"}
            ),
            MagicMock(
                page_content="Document 2 content",
                metadata={"note_id": "223e4567-e89b-12d3-a456-426614174001"}
            )
        ]
        return mock
    
    @pytest.fixture
    def mock_llm(self):
        """Mock LLM that returns predefined QA response with citations"""
        mock = MagicMock()
        mock.return_value = """
        Based on the information provided, the answer is that we should proceed with option A 
        [note_id:123e4567-e89b-12d3-a456-426614174000] and consider the implications for 
        future projects [note_id:223e4567-e89b-12d3-a456-426614174001].
        """
        return mock
    
    @patch('services.llm.get_llm')
    def test_qa(self, mock_get_llm, mock_retriever, mock_llm):
        """Test that QA chain returns answer with citations"""
        mock_get_llm.return_value = mock_llm
        
        # Create the chain
        qa_chain = build_qa_chain(mock_retriever)
        
        # Run the chain
        result = qa_chain("What should we do about the project?")
        
        # Check answer contains citations in expected format
        assert "note_id:123e4567-e89b-12d3-a456-426614174000" in result
        assert "note_id:223e4567-e89b-12d3-a456-426614174001" in result
