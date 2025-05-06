
def test_interaction_endpoint(client):
    response = client.get('/api/interactions')
    assert response.status_code == 200
    assert isinstance(response.json, list)

def test_interaction_creation(client):
    response = client.post('/api/interactions', json={'data': 'test'})
    assert response.status_code == 201
    assert 'id' in response.json

def test_interaction_not_found(client):
    response = client.get('/api/interactions/999')
    assert response.status_code == 404

def test_interaction_update(client):
    response = client.post('/api/interactions', json={'data': 'test'})
    interaction_id = response.json['id']
    response = client.put(f'/api/interactions/{interaction_id}', json={'data': 'updated'})
    assert response.status_code == 200
    assert response.json['data'] == 'updated'

def test_interaction_deletion(client):
    response = client.post('/api/interactions', json={'data': 'test'})
    interaction_id = response.json['id']
    response = client.delete(f'/api/interactions/{interaction_id}')
    assert response.status_code == 204

def test_interaction_validation(client):
    response = client.post('/api/interactions', json={})
    assert response.status_code == 400
    assert 'error' in response.json