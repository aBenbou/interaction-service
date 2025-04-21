# scripts/register_service.py
import os
import requests
import argparse
import sys
import jwt
import getpass

def validate_jwt_token(token):
    """
    Validate if a string is a properly formatted JWT token.
    
    Args:
        token: String to validate
        
    Returns:
        (bool, str): Tuple with validation result and message
    """
    if not token:
        return False, "Token is empty"
    
    try:
        # Check if token has proper JWT format (3 segments)
        parts = token.split('.')
        if len(parts) != 3:
            return False, f"Invalid JWT format: expected 3 segments, got {len(parts)}"
        
        # Verify it can be decoded (header and payload)
        # This doesn't verify signature, just structure
        header = jwt.get_unverified_header(token)
        payload = jwt.decode(token, options={"verify_signature": False})
        
        return True, "Token has valid JWT format"
    except Exception as e:
        return False, f"JWT validation error: {str(e)}"

def get_admin_token(auth_url, username=None, password=None):
    """
    Get an admin JWT token by authenticating with the Auth Service.
    
    Args:
        auth_url: URL of the Auth Service
        username: Optional admin username (if not provided, will prompt)
        password: Optional password (if not provided, will prompt)
        
    Returns:
        str: JWT token if successful, None otherwise
    """
    if not username:
        username = input("Enter admin username: ")
    
    if not password:
        password = getpass.getpass("Enter admin password: ")
    
    try:
        response = requests.post(
            f"{auth_url}/api/auth/login",
            json={
                "username": username,
                "password": password
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print("Admin authentication successful")
            return data.get('access_token')
        else:
            print(f"Failed to authenticate: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error authenticating: {str(e)}")
        return None

def create_service_token(auth_url, admin_token, service_name):
    """
    Create a service token for the interaction service.
    
    Args:
        auth_url: URL of the Auth Service
        admin_token: Admin JWT token
        service_name: Name of the service to register
        
    Returns:
        str: Service API token if successful, None otherwise
    """
    # First create the service if it doesn't exist
    try:
        service_response = requests.post(
            f"{auth_url}/api/roles/services",
            headers={
                "Authorization": f"Bearer {admin_token}",
                "Content-Type": "application/json"
            },
            json={
                "name": service_name,
                "description": f"{service_name.replace('_', ' ').title()} Microservice"
            }
        )
        
        if service_response.status_code == 201 or (service_response.status_code == 400 and "already exists" in service_response.text):
            # Service created or already exists
            # Try to get service ID
            if service_response.status_code == 201:
                service_id = service_response.json().get('service_id')
                print(f"Service registered successfully with ID: {service_id}")
            else:
                # Need to fetch the service ID
                services_response = requests.get(
                    f"{auth_url}/api/roles/services",
                    headers={"Authorization": f"Bearer {admin_token}"}
                )
                
                if services_response.status_code != 200:
                    print(f"Failed to get services: {services_response.status_code} - {services_response.text}")
                    return None
                
                services = services_response.json().get('services', [])
                service = next((s for s in services if s['name'] == service_name), None)
                
                if not service:
                    print(f"Service {service_name} not found in the list")
                    return None
                
                service_id = service['id']
                print(f"Using existing service with ID: {service_id}")
            
            # Now create a token for this service
            token_response = requests.post(
                f"{auth_url}/api/tokens/",
                headers={
                    "Authorization": f"Bearer {admin_token}",
                    "Content-Type": "application/json"
                },
                json={
                    "service_id": service_id,
                    "name": f"{service_name}_api_token",
                    "expires_in_days": 365  # Token valid for a year
                }
            )
            
            if token_response.status_code == 201:
                token_data = token_response.json()
                print(f"Service token created successfully")
                return token_data.get('token')
            else:
                print(f"Failed to create token: {token_response.status_code} - {token_response.text}")
                return None
        else:
            print(f"Failed to register service: {service_response.status_code} - {service_response.text}")
            return None
    except Exception as e:
        print(f"Error creating service token: {str(e)}")
        return None

def register_service(auth_url, api_key, service_name, service_description):
    """
    Register this service with the Auth Service.
    
    Args:
        auth_url: URL of the Auth Service
        api_key: API key for service-to-service communication
        service_name: Name of this service
        service_description: Description of this service
    """
    # First validate the API key format
    is_valid, message = validate_jwt_token(api_key)
    if not is_valid:
        print(f"API key validation failed: {message}")
        print("Please provide a valid JWT token as your API key")
        return False
    
    try:
        # Debug information
        print(f"Attempting to register with Auth Service at: {auth_url}")
        print(f"API Key provided: {api_key[:10]}...{api_key[-10:] if len(api_key) > 20 else ''}")
        
        # Validate the token first
        validation_response = requests.get(
            f"{auth_url}/api/tokens/validate",
            headers={"Authorization": f"Bearer {api_key}"}
        )
        
        if validation_response.status_code != 200:
            print(f"API key validation failed: {validation_response.status_code} - {validation_response.text}")
            print("Try regenerating an admin token and creating a service token")
            return False
        
        print("API key validated successfully")
        
        # First, get the service data from the token validation
        service_data = validation_response.json().get('service', {})
        service_id = service_data.get('id')
        
        if not service_id:
            print("Could not determine service ID from token")
            return False
        
        print(f"Using service ID: {service_id}")
        
        # Create default roles for the service
        create_default_roles(auth_url, api_key, service_id)
        
        return True
            
    except Exception as e:
        print(f"Error registering service: {str(e)}")
        return False

def create_default_roles(auth_url, api_key, service_id):
    """
    Create default roles for the interaction service.
    
    Args:
        auth_url: URL of the Auth Service
        api_key: API key for service-to-service communication
        service_id: ID of the registered service
    """
    roles = [
        {
            "name": "interaction_admin",
            "description": "Administrator for the Interaction Service",
            "permissions": ["interaction:read", "interaction:write", "feedback:read", 
                           "feedback:write", "validation:read", "validation:write", 
                           "dataset:read", "dataset:write"]
        },
        {
            "name": "validator",
            "description": "Can validate feedback submissions",
            "permissions": ["interaction:read", "feedback:read", "validation:read", "validation:write"]
        },
        {
            "name": "user",
            "description": "Regular user of the Interaction Service",
            "permissions": ["interaction:read", "interaction:write", "feedback:read", "feedback:write"]
        }
    ]
    
    for role in roles:
        try:
            response = requests.post(
                f"{auth_url}/api/roles/service/{service_id}",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "name": role["name"],
                    "description": role["description"],
                    "permissions": role["permissions"]
                }
            )
            
            if response.status_code == 201:
                print(f"Role created: {role['name']}")
            elif response.status_code == 400 and "already exists" in response.text:
                print(f"Role {role['name']} already exists")
            else:
                print(f"Failed to create role {role['name']}: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"Error creating role {role['name']}: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Register Interaction Service with Auth Service")
    parser.add_argument("--auth-url", default=os.environ.get("AUTH_SERVICE_URL", "http://localhost:5000"), 
                      help="Auth Service URL")
    parser.add_argument("--api-key", default=os.environ.get("SERVICE_API_KEY"), 
                      help="Service API key")
    parser.add_argument("--service-name", default="interaction_service", 
                      help="Service name")
    parser.add_argument("--description", default="AI Model Interaction and Feedback Service", 
                      help="Service description")
    parser.add_argument("--admin-user", help="Admin username for authentication")
    parser.add_argument("--admin-pass", help="Admin password for authentication")
    parser.add_argument("--generate-token", action="store_true", help="Generate a new service token")
    
    args = parser.parse_args()
    
    # If the generate-token flag is set, create a new service token
    if args.generate_token:
        admin_token = get_admin_token(args.auth_url, args.admin_user, args.admin_pass)
        if admin_token:
            service_token = create_service_token(args.auth_url, admin_token, args.service_name)
            if service_token:
                print("\nService token generated successfully. Use this token as your SERVICE_API_KEY:")
                print(f"\n{service_token}\n")
                print("Or run the script again with:")
                print(f"python scripts/register_service.py --api-key=\"{service_token}\"")
                sys.exit(0)
        sys.exit(1)
    
    if not args.api_key:
        print("Error: SERVICE_API_KEY must be provided")
        print("You can:")
        print("1. Set it as an environment variable: export SERVICE_API_KEY=your_jwt_token")
        print("2. Pass it directly to the script: --api-key=your_jwt_token")
        print("3. Generate a new token with: --generate-token")
        sys.exit(1)
        
    register_service(args.auth_url, args.api_key, args.service_name, args.description)