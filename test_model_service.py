# Save as test_model_service.py in the interaction-service container
import requests
import sys
import json

MODEL_SERVICE_URL = "http://model-manager:8000"

def test_endpoints():
    print("Testing /endpoints endpoint...")
    try:
        response = requests.get(f"{MODEL_SERVICE_URL}/endpoints")
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            print(json.dumps(response.json(), indent=2))
            return True
        return False
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def test_endpoint_details(endpoint_name):
    print(f"Testing /endpoint/{endpoint_name} endpoint...")
    try:
        response = requests.get(f"{MODEL_SERVICE_URL}/endpoint/{endpoint_name}")
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            print(json.dumps(response.json(), indent=2))
            return True
        return False
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    print(f"Testing Model Service at {MODEL_SERVICE_URL}")
    
    # Test endpoints
    if not test_endpoints():
        print("Failed to get endpoints")
        sys.exit(1)
    
    # Test endpoint details
    # Get the first endpoint name from the endpoints response
    try:
        response = requests.get(f"{MODEL_SERVICE_URL}/endpoints")
        if response.status_code == 200 and "endpoints" in response.json():
            endpoint_name = response.json()["endpoints"][0]["endpointName"]
            if not test_endpoint_details(endpoint_name):
                print("Failed to get endpoint details")
                sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)
    
    print("All tests passed!")
    sys.exit(0)