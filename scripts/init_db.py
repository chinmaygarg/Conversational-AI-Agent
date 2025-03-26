import os
from app.core.database import init_db
from app.core.config import settings

def create_directories():
    """Create necessary directories for the application."""
    directories = [
        settings.VECTOR_DB_PATH,
        settings.UPLOAD_DIR,
        settings.PROMETHEUS_MULTIPROC_DIR,
        "data/models",
        "data/logs"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Created directory: {directory}")

def main():
    """Initialize the application."""
    print("Creating directories...")
    create_directories()
    
    print("Initializing database...")
    init_db()
    
    print("Initialization complete!")

if __name__ == "__main__":
    main() 