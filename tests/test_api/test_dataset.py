def test_dataset_api(client):
    response = client.get('/api/dataset')
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_dataset_api_error(client):
    response = client.get('/api/dataset/invalid')
    assert response.status_code == 404

def test_dimensions_api(client):
    response = client.get('/api/dimensions')
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_feedback_api(client):
    response = client.post('/api/feedback', json={"data": "test"})
    assert response.status_code == 201
    assert response.json().get('message') == 'Feedback received'

def test_interactions_api(client):
    response = client.get('/api/interactions')
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_validation_api(client):
    response = client.post('/api/validation', json={"input": "test"})
    assert response.status_code == 200
    assert response.json().get('valid') is True