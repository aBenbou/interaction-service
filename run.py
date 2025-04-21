# run.py
import os
import click
from app import create_app, db
from app.models.dimension import EvaluationDimension

app = create_app()

@app.cli.command("setup-initial-data")
def setup_initial_data():
    """Set up initial data in the database."""
    from app.utils.model_constants import DEFAULT_EVALUATION_DIMENSIONS
    
    print("Setting up initial data...")
    
    # Create global dimensions applicable to all models
    global_dimensions = [
        {
            "name": "Accuracy",
            "description": "The factual accuracy of the response"
        },
        {
            "name": "Helpfulness", 
            "description": "How helpful and useful the response is"
        },
        {
            "name": "Relevance",
            "description": "How relevant the response is to the query"
        },
        {
            "name": "Clarity",
            "description": "How clear and understandable the response is"
        },
        {
            "name": "Completeness",
            "description": "How comprehensive and complete the response is"
        }
    ]
    
    # System user ID for automatic creation
    system_user_id = "00000000-0000-0000-0000-000000000000"
    
    # Add global dimensions
    for dim in global_dimensions:
        # Check if dimension already exists
        existing = EvaluationDimension.query.filter_by(
            model_id="all", 
            name=dim["name"]
        ).first()
        
        if not existing:
            dimension = EvaluationDimension(
                model_id="all",
                name=dim["name"],
                description=dim["description"],
                created_by=system_user_id,
                is_active=True
            )
            db.session.add(dimension)
            print(f"Added global dimension: {dim['name']}")
    
    try:
        db.session.commit()
        print("Initial data setup complete!")
    except Exception as e:
        db.session.rollback()
        print(f"Error setting up initial data: {str(e)}")

@app.cli.command("create-admin")
@click.argument("user_id")
def create_admin(user_id):
    """
    Add a user to the admin list for testing.
    
    Args:
        user_id: UUID of the user to mark as admin
    """
    # This is a simplified approach for testing/development
    admin_users = os.environ.get('ADMIN_USERS', '')
    
    if user_id in admin_users:
        print(f"User {user_id} is already an admin")
    else:
        new_admins = f"{admin_users},{user_id}" if admin_users else user_id
        print(f"Updated ADMIN_USERS environment variable")
        print(f"Add this to your .env file or environment:")
        print(f"ADMIN_USERS={new_admins}")

@app.cli.command("create-validator")
@click.argument("user_id")
def create_validator(user_id):
    """
    Add a user to the validator list for testing.
    
    Args:
        user_id: UUID of the user to mark as validator
    """
    # This is a simplified approach for testing/development
    validator_users = os.environ.get('VALIDATOR_USERS', '')
    
    if user_id in validator_users:
        print(f"User {user_id} is already a validator")
    else:
        new_validators = f"{validator_users},{user_id}" if validator_users else user_id
        print(f"Updated VALIDATOR_USERS environment variable")
        print(f"Add this to your .env file or environment:")
        print(f"VALIDATOR_USERS={new_validators}")

if __name__ == "__main__":
    app.run()