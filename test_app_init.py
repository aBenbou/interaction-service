# Save as test_app_init.py in the interaction-service container
import sys

print("Testing app imports...")

try:
    print("Importing app module...")
    from app import create_app
    print("Creating app instance...")
    app = create_app()
    print("App created successfully!")
    
    print("Testing ModelClient...")
    from app.utils.model_client import ModelClient
    model_client = ModelClient()
    print("ModelClient initialized successfully!")
    
    print("Testing model validation...")
    print(f"Validating model: result={model_client.validate_model('google-bert-bert-base-uncased')}")
    
    sys.exit(0)
except Exception as e:
    print(f"Error: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)