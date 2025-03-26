import faiss
import numpy as np
from typing import List, Dict, Optional
import logging
from sentence_transformers import SentenceTransformer
from app.core.config import settings
from app.models.database import Document, Language
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

class RAGService:
    def __init__(self, db: Session):
        self.db = db
        self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
        self.index = self._load_or_create_index()
        
    def _load_or_create_index(self) -> faiss.Index:
        """Load existing FAISS index or create new one."""
        try:
            return faiss.read_index(settings.VECTOR_DB_PATH)
        except:
            # Create new index
            dimension = self.embedding_model.get_sentence_embedding_dimension()
            index = faiss.IndexFlatL2(dimension)
            faiss.write_index(index, settings.VECTOR_DB_PATH)
            return index
    
    async def ingest_document(
        self,
        title: str,
        content: str,
        doc_type: str,
        language: Language,
        metadata: Optional[Dict] = None
    ) -> Document:
        """Ingest a new document into the RAG system."""
        try:
            # Generate embedding
            embedding = self.embedding_model.encode(content)
            
            # Store in database
            document = Document(
                title=title,
                content=content,
                doc_type=doc_type,
                language=language,
                embedding=embedding.tolist(),
                metadata=metadata or {}
            )
            
            self.db.add(document)
            self.db.commit()
            self.db.refresh(document)
            
            # Update FAISS index
            self.index.add(np.array([embedding]))
            faiss.write_index(self.index, settings.VECTOR_DB_PATH)
            
            return document
            
        except Exception as e:
            logger.error(f"Error ingesting document: {str(e)}")
            self.db.rollback()
            raise
    
    async def retrieve_relevant_documents(
        self,
        query: str,
        language: Optional[Language] = None,
        top_k: int = 3
    ) -> List[Document]:
        """Retrieve relevant documents for a query."""
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query)
            
            # Search in FAISS index
            distances, indices = self.index.search(
                np.array([query_embedding]), top_k
            )
            
            # Get documents from database
            documents = self.db.query(Document).filter(
                Document.id.in_(indices[0])
            ).all()
            
            # Filter by language if specified
            if language:
                documents = [doc for doc in documents if doc.language == language]
            
            return documents
            
        except Exception as e:
            logger.error(f"Error retrieving documents: {str(e)}")
            raise
    
    async def generate_response(
        self,
        query: str,
        conversation_history: List[Dict],
        language: Optional[Language] = None
    ) -> str:
        """Generate response using RAG and LLM."""
        try:
            # Retrieve relevant documents
            documents = await self.retrieve_relevant_documents(query, language)
            
            # Prepare context from documents
            context = "\n".join([doc.content for doc in documents])
            
            # Prepare conversation history
            history = "\n".join([
                f"{msg['role']}: {msg['content']}"
                for msg in conversation_history[-5:]  # Last 5 messages
            ])
            
            # Generate response using LLM
            # Note: This is a placeholder. You'll need to implement the actual LLM call
            response = await self._call_llm(
                query=query,
                context=context,
                history=history,
                language=language
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            raise
    
    async def _call_llm(
        self,
        query: str,
        context: str,
        history: str,
        language: Optional[Language] = None
    ) -> str:
        """Call LLM to generate response."""
        # TODO: Implement actual LLM call
        # This is a placeholder that should be replaced with actual LLM integration
        prompt = f"""
        Context: {context}
        
        Conversation History:
        {history}
        
        Query: {query}
        
        Language: {language.value if language else 'mixed'}
        
        Generate a response:
        """
        
        # Placeholder response
        return "This is a placeholder response. Implement actual LLM integration." 