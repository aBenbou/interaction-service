from flask import Flask, jsonify, request
import pytest

app = Flask(__name__)

@app.route('/feedback', methods=['POST'])
def feedback():
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'error': 'Invalid input'}), 400
    return jsonify({'status': 'success', 'message': data['message']}), 200

def test_feedback():
    client = app.test_client()
    response = client.post('/feedback', json={'message': 'Great service!'})
    assert response.status_code == 200
    assert response.json == {'status': 'success', 'message': 'Great service!'}

    response = client.post('/feedback', json={})
    assert response.status_code == 400
    assert response.json == {'error': 'Invalid input'}