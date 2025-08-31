import pytest
from fastapi.testclient import TestClient
import uuid
from unittest.mock import patch, MagicMock

from main import app
from services.database import get_session


# Create test client
client = TestClient(app)


# Mock database session
@pytest.fixture
def mock_db_session():
    """Create a mock database session for testing"""
    mock = MagicMock()
    return mock


# Override database dependency
@pytest.fixture(autouse=True)
def override_get_session(mock_db_session):
    """Override the database session dependency"""
    app.dependency_overrides[get_session] = lambda: mock_db_session
    yield
    app.dependency_overrides = {}


class TestSummarizeEndpoint:
    @patch('routers.summarize.build_summarization_chain')
    def test_summarize_success(self, mock_build_chain, mock_db_session):
        """Test successful summarization"""
        # Set up mock
        mock_chain = MagicMock()
        mock_chain.return_value = {
            "summary": "Test summary",
            "highlights": ["Point 1", "Point 2"],
            "decisions": ["Decision 1"],
            "action_items": ["Task 1", "Task 2"]
        }
        mock_build_chain.return_value = mock_chain
        
        # Make request
        response = client.post(
            "/summarize",
            json={"text": "Test content for summarization"}
        )
        
        # Check response
        assert response.status_code == 200
        data = response.json()
        assert data["summary"] == "Test summary"
        assert len(data["highlights"]) == 2
        assert len(data["decisions"]) == 1
        assert len(data["action_items"]) == 2
    
    def test_summarize_empty_text(self):
        """Test summarization with empty text"""
        response = client.post(
            "/summarize",
            json={"text": ""}
        )
        assert response.status_code == 400


class TestTasksEndpoint:
    @patch('routers.tasks.build_task_chain')
    def test_extract_tasks_success(self, mock_build_chain, mock_db_session):
        """Test successful task extraction"""
        # Set up mock
        mock_chain = MagicMock()
        mock_chain.return_value = {
            "tasks": [
                {
                    "description": "Task 1",
                    "due_date": None,
                    "owner": "John",
                    "completed": False
                },
                {
                    "description": "Task 2",
                    "completed": False
                }
            ]
        }
        mock_build_chain.return_value = mock_chain
        
        # Make request
        response = client.post(
            "/tasks/extract",
            json={"text": "Test content with tasks"}
        )
        
        # Check response
        assert response.status_code == 200
        data = response.json()
        assert len(data["tasks"]) == 2
    
    @patch('routers.tasks.build_task_chain')
    def test_extract_tasks_with_note_id(self, mock_build_chain, mock_db_session):
        """Test task extraction with note ID"""
        # Set up mock
        mock_chain = MagicMock()
        mock_chain.return_value = {
            "tasks": [
                {
                    "description": "Task 1",
                    "completed": False
                }
            ]
        }
        mock_build_chain.return_value = mock_chain
        
        # Configure save_tasks mock
        mock_db_session.commit = MagicMock()
        
        # Generate test UUID
        test_uuid = str(uuid.uuid4())
        
        # Make request
        response = client.post(
            "/tasks/extract",
            json={"text": "Test content", "source_note_id": test_uuid}
        )
        
        # Check response
        assert response.status_code == 200
        
        # Verify save_tasks was called
        mock_db_session.commit.assert_called_once()


class TestSearchEndpoint:
    @patch('routers.search.make_retriever')
    @patch('routers.search.build_qa_chain')
    def test_search_success(self, mock_build_qa, mock_make_retriever, mock_db_session):
        """Test successful search"""
        # Set up mocks
        mock_retriever = MagicMock()
        mock_make_retriever.return_value = mock_retriever
        
        mock_qa_chain = MagicMock()
        mock_qa_chain.return_value = "Answer with citation [note_id:123e4567-e89b-12d3-a456-426614174000]"
        mock_build_qa.return_value = mock_qa_chain
        
        # Make request
        response = client.post(
            "/search/query",
            json={"query": "Test query"}
        )
        
        # Check response
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert "citations" in data
        assert len(data["citations"]) == 1


class TestNotesEndpoint:
    def test_list_notes(self, mock_db_session):
        """Test listing notes"""
        # Configure mock for list_notes
        mock_db_session.execute.return_value.scalars.return_value.all.return_value = [
            MagicMock(
                id=uuid.uuid4(),
                title="Test Note",
                body="Test content",
                created_at="2023-01-01T00:00:00Z",
                updated_at="2023-01-01T00:00:00Z"
            )
        ]
        
        # Make request
        response = client.get("/notes")
        
        # Check response
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Test Note"
