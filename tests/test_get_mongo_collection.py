import pytest
from unittest.mock import patch, MagicMock
from pymongo import errors
from common.mongodb_connection import get_mongo_collection 

@pytest.fixture
def mock_mongo_client():
    """Fixture to mock MongoClient."""
    with patch("common.mongodb_connection.MongoClient") as mock_client:
        yield mock_client

def test_successful_connection_and_collection(mock_mongo_client):
    """Test a successful database and collection retrieval."""
    mock_client_instance = mock_mongo_client.return_value
    mock_client_instance.list_database_names.return_value = ["test_db"]
    mock_db = mock_client_instance.__getitem__.return_value
    mock_db.list_collection_names.return_value = ["test_collection"]

    collection = get_mongo_collection("test_db", "test_collection", "mongodb://localhost:27017")
    assert collection is not None

def test_connection_failure(mock_mongo_client):
    """Test MongoDB connection failure."""
    mock_mongo_client.side_effect = errors.ServerSelectionTimeoutError
    with pytest.raises(ConnectionError, match="Failed to connect to MongoDB"):
        get_mongo_collection("test_db", "test_collection", "mongodb://invalid-uri")

def test_general_connection_error(mock_mongo_client):
    """Test general PyMongo connection error."""
    mock_mongo_client.side_effect = errors.PyMongoError("Some connection issue")
    with pytest.raises(RuntimeError, match="MongoDB connection error: Some connection issue"):
        get_mongo_collection("test_db", "test_collection", "mongodb://localhost:27017")

def test_database_does_not_exist(mock_mongo_client):
    """Test when the specified database does not exist."""
    mock_client_instance = mock_mongo_client.return_value
    mock_client_instance.list_database_names.return_value = ["other_db"]  # Simulate missing db

    with pytest.raises(ValueError, match="Database 'test_db' does not exist."):
        get_mongo_collection("test_db", "test_collection", "mongodb://localhost:27017")

def test_collection_does_not_exist(mock_mongo_client):
    """Test when the specified collection does not exist in the database."""
    mock_client_instance = mock_mongo_client.return_value
    mock_client_instance.list_database_names.return_value = ["test_db"]
    mock_db = mock_client_instance.__getitem__.return_value
    mock_db.list_collection_names.return_value = ["other_collection"]  # Simulate missing collection

    with pytest.raises(ValueError, match="Collection 'test_collection' does not exist in database 'test_db'."):
        get_mongo_collection("test_db", "test_collection", "mongodb://localhost:27017")

def test_mongo_operation_error(mock_mongo_client):
    """Test MongoDB operational errors like permissions or query failures."""
    mock_client_instance = mock_mongo_client.return_value
    mock_client_instance.list_database_names.side_effect = errors.OperationFailure("Operation error")

    with pytest.raises(RuntimeError, match="MongoDB operation error: Operation error"):
        get_mongo_collection("test_db", "test_collection", "mongodb://localhost:27017")
