"""
Initialize the database for the Business Chatbot application.
Run this script once after deploying to Render to set up the database.
"""
from app import app, db
from flask_migrate import upgrade

print("Initializing database...")
with app.app_context():
    # Create all tables
    db.create_all()
    print("Database tables created.")

    # Run migrations if any
    try:
        upgrade()
        print("Migrations applied successfully.")
    except Exception as e:
        print(f"Note: No migrations to apply or error occurred: {e}")

print("Database initialization complete!") 