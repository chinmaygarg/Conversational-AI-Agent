# Bilingual Speech Recognition & Response Generation System

A comprehensive system for real-time Hindi/English speech recognition, response generation, and text-to-speech capabilities with RAG integration.

## Features

- Real-time bilingual (Hindi/English) speech recognition
- Code-switching support
- Local RAG pipeline for document retrieval
- Dynamic response generation with LLM integration
- Function calling capabilities
- Neural TTS with voice cloning
- Call management and data storage
- Low-latency architecture
- Comprehensive monitoring and analytics

## System Requirements

- Python 3.8+
- CUDA-capable GPU (recommended)
- PostgreSQL with pgvector extension
- 64GB RAM (minimum)
- 8-core CPU (minimum)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd bilingual-speech-system
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
DATABASE_URL=postgresql://user:password@localhost:5432/bilingual_speech_db
ASR_MODEL=whisper-large-v2  # Speech recognition model
TTS_MODEL=resemble-ai       # Text-to-speech model
LLM_MODEL=mistral-7b       # Language model for responses
EMBEDDING_MODEL=BAAI/bge-small-en-v1.5  # Model for document embeddings
OPENAI_API_KEY=your-openai-api-key        # For LLM integration
RESEMBLE_AI_API_KEY=your-resemble-ai-key  # For text-to-speech
TWILIO_ACCOUNT_SID=your-twilio-sid        # For call management
TWILIO_AUTH_TOKEN=your-twilio-token       # For call management
VECTOR_DB_TYPE=faiss
VECTOR_DB_PATH=./data/vector_store
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
UPLOAD_DIR=./data/uploads
MAX_UPLOAD_SIZE=10485760  # 10MB in bytes
```

5. Initialize the database:
```bash
python scripts/init_db.py
```

## Project Structure

```
bilingual-speech-system/
├── app/
│   ├── api/            # FastAPI routes
│   ├── core/           # Core functionality
│   ├── models/         # Data models
│   ├── services/       # Business logic
│   └── utils/          # Utility functions
├── config/             # Configuration files
├── data/               # Data storage
├── models/             # ML models
├── scripts/            # Utility scripts
├── tests/              # Test files
└── docs/               # Documentation
```

## Usage

1. Start the API server:
```bash
uvicorn app.main:app --reload
```

2. Access the API documentation:
```
http://localhost:8000/docs
```

## API Endpoints

- `POST /api/v1/speech-to-text`: Convert speech to text
- `POST /api/v1/text-to-speech`: Convert text to speech
- `POST /api/v1/chat`: Chat with the AI agent
- `POST /api/v1/ingest-document`: Ingest documents into RAG system
- `GET /api/v1/health`: Health check endpoint

## Development

1. Run tests:
```bash
pytest
```

2. Format code:
```bash
black .
```

3. Check types:
```bash
mypy .
```

## License

MIT License

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request 