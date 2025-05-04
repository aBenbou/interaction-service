def test_dimensions_api(client):
    response = client.get('/api/dimensions')
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_dimension_creation(client):
    response = client.post('/api/dimensions', json={'name': 'New Dimension'})
    assert response.status_code == 201
    assert response.json()['name'] == 'New Dimension'

def test_dimension_not_found(client):
    response = client.get('/api/dimensions/999')
    assert response.status_code == 404

def test_dimension_update(client):
    response = client.put('/api/dimensions/1', json={'name': 'Updated Dimension'})
    assert response.status_code == 200
    assert response.json()['name'] == 'Updated Dimension'

def test_dimension_deletion(client):
    response = client.delete('/api/dimensions/1')
    assert response.status_code == 204
    response = client.get('/api/dimensions/1')
    assert response.status_code == 404