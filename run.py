import uvicorn
import os
from app.core.config import settings

if __name__ == "__main__":
    # Create necessary directories
    os.makedirs(settings.VECTOR_DB_PATH, exist_ok=True)
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.PROMETHEUS_MULTIPROC_DIR, exist_ok=True)
    
    # Run the application
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        workers=1  # Use 1 worker for development
    ) 