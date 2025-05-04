from app.models.response import Response  # Corrected import

def test_response_model():
    response = Response(
        prompt_id="123e4567-e89b-12d3-a456-426614174000",
        content="Test content",
        model_endpoint="test-endpoint"
    )
    assert response.content == "Test content"
    assert response.model_endpoint == "test-endpoint"