"""
FastAPI Backend for AI Training Assistant
RESTful API for training, quizzes, and progress tracking
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import os
import uuid
from pathlib import Path

from ollama_client import ollama_client
from ingestion_service import ingestor
from vector_store import vector_store
from rag_pipeline import rag_pipeline
from quiz_generator import quiz_generator
from evaluator import evaluator
from progress_tracker import progress_tracker

# Initialize FastAPI app
app = FastAPI(
    title="AI Training Assistant API",
    description="Local AI-powered employee onboarding and training platform",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directories
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# ==================== Pydantic Models ====================

class QuestionRequest(BaseModel):
    question: str
    employee_id: Optional[str] = "anonymous"

class QuizAnswerRequest(BaseModel):
    question_id: int
    answer: str
    correct_answer: str
    options: Optional[List[str]] = None

class QuizRequest(BaseModel):
    topic: Optional[str] = None
    num_questions: int = 5

class QuizSubmissionRequest(BaseModel):
    employee_id: str
    topic: str
    answers: List[QuizAnswerRequest]

class EmployeeRegisterRequest(BaseModel):
    employee_id: str
    name: str
    email: Optional[str] = None
    department: Optional[str] = None
    role: Optional[str] = None

class ModuleRequest(BaseModel):
    module_name: str
    description: Optional[str] = None

class ModuleProgressRequest(BaseModel):
    employee_id: str
    module_name: str

# ==================== Health Check ====================

@app.get("/health")
async def health_check():
    """Check system health and Ollama connectivity"""
    ollama_status = ollama_client.health_check()
    return {
        "status": "healthy",
        "ollama": "running" if ollama_status else "not running",
        "vectorstore": vector_store.get_stats()
    }

# ==================== Document Upload ====================

@app.post("/upload-doc")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload and ingest a training document
    Supports: PDF, DOCX, TXT, Markdown
    """
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file selected")
        
        # Validate file type
        file_ext = Path(file.filename).suffix.lower()
        allowed_extensions = ['.pdf', '.docx', '.txt', '.md', '.markdown']
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Save file
        file_path = UPLOAD_DIR / f"{uuid.uuid4()}_{file.filename}"
        content = await file.read()
        
        with open(file_path, 'wb') as f:
            f.write(content)
        
        # Ingest document
        chunks = ingestor.ingest_document(str(file_path))
        
        # Add to vector store
        vector_store.add_chunks(chunks, document_name=file.filename)
        
        return {
            "status": "success",
            "message": f"Document '{file.filename}' uploaded successfully",
            "chunks_created": len(chunks),
            "file_size": len(content),
            "vectorstore_stats": vector_store.get_stats()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading document: {str(e)}")

# ==================== Question Answering ====================

@app.post("/ask")
async def ask_question(request: QuestionRequest):
    """
    Answer a question based on training materials using RAG
    """
    try:
        if not request.question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty")
        
        # Log the question
        progress_tracker.log_question(
            employee_id=request.employee_id,
            question=request.question
        )
        
        # Get answer from RAG pipeline
        result = rag_pipeline.answer_question(request.question)
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")

@app.post("/ask-stream")
async def ask_question_stream(request: QuestionRequest):
    """
    Answer a question with streaming response
    """
    try:
        if not request.question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty")
        
        # Log the question
        progress_tracker.log_question(
            employee_id=request.employee_id,
            question=request.question
        )
        
        def generate():
            for token in rag_pipeline.answer_question_stream(request.question):
                yield token
        
        return StreamingResponse(generate(), media_type="text/event-stream")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")

# ==================== Quiz Management ====================

@app.post("/generate-quiz")
async def generate_quiz(request: QuizRequest):
    """
    Generate a quiz from training materials
    """
    try:
        quiz = quiz_generator.generate_quiz(
            topic=request.topic,
            num_questions=request.num_questions
        )
        
        if quiz.get('error'):
            raise HTTPException(status_code=400, detail=quiz.get('message'))
        
        return quiz
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating quiz: {str(e)}")

@app.post("/submit-quiz")
async def submit_quiz(request: QuizSubmissionRequest):
    """
    Submit quiz answers and get evaluation
    """
    try:
        if not request.answers:
            raise HTTPException(status_code=400, detail="No answers provided")
        
        # Convert request format for evaluator
        quiz_responses = [
            {
                'question': answer.question_id,
                'answer': answer.answer,
                'correct': answer.correct_answer,
                'options': answer.options
            }
            for answer in request.answers
        ]
        
        # Evaluate quiz
        evaluation = evaluator.evaluate_quiz(quiz_responses)
        
        # Log quiz attempt
        progress_tracker.log_quiz_attempt(
            employee_id=request.employee_id,
            topic=request.topic,
            score=evaluation['correct_answers'],
            total_questions=evaluation['total_questions'],
            correct_answers=evaluation['correct_answers']
        )
        
        return evaluation
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error submitting quiz: {str(e)}")

# ==================== Employee Management ====================

@app.post("/register-employee")
async def register_employee(request: EmployeeRegisterRequest):
    """
    Register a new employee
    """
    try:
        success = progress_tracker.register_employee(
            employee_id=request.employee_id,
            name=request.name,
            email=request.email,
            department=request.department,
            role=request.role
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Employee already registered")
        
        return {
            "status": "success",
            "message": f"Employee '{request.name}' registered successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error registering employee: {str(e)}")

# ==================== Module Management ====================

@app.post("/add-module")
async def add_module(request: ModuleRequest):
    """
    Add a training module
    """
    try:
        success = progress_tracker.add_module(
            module_name=request.module_name,
            description=request.description
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Module already exists")
        
        return {
            "status": "success",
            "message": f"Module '{request.module_name}' added successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding module: {str(e)}")

@app.post("/start-module")
async def start_module(request: ModuleProgressRequest):
    """
    Mark module as started
    """
    try:
        success = progress_tracker.start_module(
            employee_id=request.employee_id,
            module_name=request.module_name
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Module not found")
        
        return {
            "status": "success",
            "message": f"Started module '{request.module_name}'"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting module: {str(e)}")

@app.post("/complete-module")
async def complete_module(request: ModuleProgressRequest):
    """
    Mark module as completed
    """
    try:
        success = progress_tracker.complete_module(
            employee_id=request.employee_id,
            module_name=request.module_name
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Module not found")
        
        return {
            "status": "success",
            "message": f"Completed module '{request.module_name}'"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error completing module: {str(e)}")

# ==================== Progress Tracking ====================

@app.get("/progress/{employee_id}")
async def get_employee_progress(employee_id: str):
    """
    Get learning progress for an employee
    """
    try:
        progress = progress_tracker.get_employee_progress(employee_id)
        
        if not progress:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        return progress
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching progress: {str(e)}")

@app.get("/all-progress")
async def get_all_progress():
    """
    Get progress for all employees
    """
    try:
        progress = progress_tracker.get_all_progress()
        return {"employees": progress}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching progress: {str(e)}")

# ==================== Vector Store Management ====================

@app.get("/vectorstore-stats")
async def get_vectorstore_stats():
    """
    Get vector store statistics
    """
    return vector_store.get_stats()

@app.delete("/vectorstore-clear")
async def clear_vectorstore():
    """
    Clear all documents from vector store (dangerous!)
    """
    try:
        vector_store.clear()
        return {
            "status": "success",
            "message": "Vector store cleared"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing vector store: {str(e)}")

# ==================== Error Handlers ====================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

# ==================== Root ====================

@app.get("/")
async def root():
    """Welcome endpoint"""
    return {
        "name": "AI Training Assistant API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
