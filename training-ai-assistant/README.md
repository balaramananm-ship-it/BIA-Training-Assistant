# 🤖 AI Training Assistant for New Employees

A production-ready MVP for an AI-powered employee onboarding and training platform that runs entirely on local infrastructure using Ollama and llama3.2.

## Features

✨ **Core Capabilities**
- 📄 **Document Ingestion**: Upload and parse training materials (PDF, DOCX, TXT, Markdown)
- 💬 **Intelligent Q&A**: Ask questions about training content with RAG-powered answers
- 📝 **Dynamic Quiz Generation**: Create MCQ quizzes from training materials
- 🎯 **Answer Evaluation**: Automated scoring and personalized feedback
- 📊 **Progress Tracking**: Monitor employee learning progress with SQLite
- 🚀 **Role-Based Learning**: Contextual help based on department/role
- 🔐 **100% Local**: No cloud APIs, all inference runs on Ollama

## Architecture

```
training-ai-assistant/
├── backend/
│   ├── ollama_client.py          # Ollama API wrapper
│   ├── ingestion_service.py      # Document parsing & chunking
│   ├── embedding_service.py      # Local embeddings (SentenceTransformers)
│   ├── vector_store.py           # FAISS vector database
│   ├── rag_pipeline.py           # RAG (Retrieval Augmented Generation)
│   ├── quiz_generator.py         # Dynamic quiz generation
│   ├── evaluator.py              # Answer evaluation & scoring
│   ├── progress_tracker.py       # SQLite progress tracking
│   └── api.py                    # FastAPI backend
├── frontend/
│   ├── index.html                # Main UI
│   ├── styles.css                # Styling
│   └── script.js                 # Frontend logic
├── vectorstore/                  # FAISS indices & metadata
├── uploads/                      # Uploaded documents
├── requirements.txt              # Python dependencies
├── run.sh                        # Quick start script
└── README.md                     # This file
```

## Tech Stack

### Backend
- **Framework**: FastAPI (Python)
- **LLM**: Ollama + llama3.2
- **Vector DB**: FAISS
- **Embeddings**: SentenceTransformers (all-MiniLM-L6-v2)
- **Database**: SQLite
- **Document Processing**: PyMuPDF, python-docx, Markdown

### Frontend
- **HTML5** + **CSS3** + **Vanilla JavaScript**
- **API Client**: Fetch API
- **No external dependencies** (lightweight)

## Prerequisites

1. **Python 3.8+**
   ```bash
   python3 --version
   ```

2. **Ollama** (Download from [ollama.ai](https://ollama.ai))
   ```bash
   # Start Ollama service (runs on localhost:11434)
   ollama serve
   
   # In another terminal, pull llama3.2
   ollama pull llama3.2
   ```

3. **Git** (optional, for version control)

## Installation & Setup

### 1. Clone/Download the project
```bash
cd /Users/saketh/BIA\ Capstone/training-ai-assistant
```

### 2. Create virtual environment
```bash
python3 -m venv backend/venv
source backend/venv/bin/activate  # On Windows: backend\venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Start Ollama (if not already running)
```bash
# In a separate terminal
ollama serve

# In another terminal, ensure llama3.2 is available
ollama pull llama3.2
```

### 5. Start the backend
```bash
# Option A: Using the run script
chmod +x run.sh
./run.sh

# Option B: Manual startup
cd backend
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

### 6. Access the frontend
Open your browser and navigate to:
```
file:///Users/saketh/BIA\ Capstone/training-ai-assistant/frontend/index.html
```

Or serve it with Python:
```bash
cd frontend
python3 -m http.server 8080
# Visit http://localhost:8080
```

## API Endpoints

### Health & Status
- `GET /health` - System health check
- `GET /vectorstore-stats` - Vector store statistics

### Document Management
- `POST /upload-doc` - Upload training document

### Question Answering
- `POST /ask` - Answer question (standard response)
- `POST /ask-stream` - Answer question (streaming response)

### Quiz Management
- `POST /generate-quiz` - Generate quiz from training materials
- `POST /submit-quiz` - Submit and evaluate quiz answers

### Employee Management
- `POST /register-employee` - Register new employee
- `GET /progress/{employee_id}` - Get employee progress
- `GET /all-progress` - Get all employees' progress

### Module Management
- `POST /add-module` - Add training module
- `POST /start-module` - Mark module as started
- `POST /complete-module` - Mark module as completed

### Vector Store
- `DELETE /vectorstore-clear` - Clear all vectors (⚠️ dangerous!)

## Usage Guide

### 1. Upload Training Materials
1. Click "Upload Documents" in navigation
2. Drag and drop or select PDF/DOCX/TXT/Markdown files
3. System automatically chunks and indexes documents
4. Check vectorstore status to confirm upload

### 2. Ask Questions
1. Click "Ask Questions" tab
2. Type your question in the chat box
3. AI responds based on uploaded materials
4. Confidence scores and sources are provided

### 3. Take Quizzes
1. Click "Quiz" tab
2. Enter topic (optional) and number of questions
3. Answer multiple choice questions
4. Submit for evaluation
5. View detailed feedback and score

### 4. Track Progress
1. Click "Progress" tab
2. Enter your employee ID
3. View completed modules, quiz history, average score
4. Monitor learning journey

## Configuration

### Environment Variables
```bash
# .env file (optional)
OLLAMA_API_URL=http://localhost:11434/api/generate
MODEL_NAME=llama3.2
CHUNK_SIZE=512
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

### Database
- SQLite file: `backend/progress.db`
- Automatically created on first run
- Contains: employees, modules, quiz attempts, questions, progress

### Vector Store
- FAISS index: `vectorstore/index.faiss`
- Metadata: `vectorstore/index.faiss_metadata.pkl`
- Automatically created on first document upload

## Performance Tips

1. **First Run**: First API call may be slow as llama3.2 loads into memory
2. **Batch Processing**: Process documents in reasonable sizes (< 100MB total recommended)
3. **Local Inference**: Runs on your CPU/GPU, speed depends on hardware
4. **Embedding Cache**: Embeddings are cached, subsequent searches are fast

## Troubleshooting

### Ollama Connection Error
```
Error: Failed to connect to Ollama at http://localhost:11434
```
**Solution**: 
- Start Ollama: `ollama serve`
- Check it's running: `curl http://localhost:11434/api/tags`

### Model Not Found
```
Error: llama3.2 model not found
```
**Solution**:
- Pull the model: `ollama pull llama3.2`
- List available: `ollama list`

### Port Already in Use
```
Error: Address already in use
```
**Solution**:
- Kill process using port 8000: `lsof -ti:8000 | xargs kill -9`
- Or change port in run.sh

### CORS Errors in Frontend
**Solution**: CORS is enabled for all origins (`*`). Check browser console for details.

### Slow Quiz Generation
**Solution**: Quiz generation requires LLM inference. First attempt may take 30-60 seconds.

## File Structure Details

### Backend Modules

**ollama_client.py**
- Wrapper around Ollama HTTP API
- Handles streaming and non-streaming responses
- Health check functionality

**ingestion_service.py**
- Parses multiple document formats
- Chunks text with overlap for better context
- Handles PDFs, DOCX, TXT, Markdown

**embedding_service.py**
- Uses SentenceTransformers for local embeddings
- all-MiniLM-L6-v2 model (lightweight, fast)
- Similarity calculation

**vector_store.py**
- FAISS-based semantic search
- Persistent storage with metadata
- Add/search chunks, statistics

**rag_pipeline.py**
- Combines retrieval with LLM generation
- Enforces grounded answers from context
- Confidence scoring

**quiz_generator.py**
- Generates MCQs from training content
- JSON parsing with fallback
- Customizable question count

**evaluator.py**
- Evaluates MCQ and free-form answers
- Semantic matching for open-ended questions
- Personalized feedback generation

**progress_tracker.py**
- SQLite database management
- Employee registration
- Module and quiz tracking
- Comprehensive progress reporting

**api.py**
- FastAPI application
- RESTful endpoints
- Error handling and validation
- CORS support

### Frontend Structure

**index.html**
- Semantic HTML5 structure
- Tab-based navigation
- Chat interface
- Quiz forms
- Progress dashboard

**styles.css**
- Modern, responsive design
- CSS variables for theming
- Mobile-optimized
- Smooth animations

**script.js**
- Tab switching
- File upload with drag-drop
- Chat interface logic
- Quiz generation and submission
- Progress loading
- API integration

## Security Notes

⚠️ **Production Considerations**:
- Add authentication/authorization
- Implement rate limiting
- Validate all file uploads
- Use HTTPS in production
- Run on isolated network for sensitive data
- Implement access controls for employee data

## Extending the System

### Add New Document Types
Edit `ingestion_service.py`:
```python
def parse_new_format(self, file_path: str) -> str:
    # Add parsing logic
    return text
```

### Customize LLM Prompts
Edit prompts in:
- `rag_pipeline.py` - QA prompts
- `quiz_generator.py` - Quiz generation
- `evaluator.py` - Answer evaluation

### Add Role-Based Modules
Extend `progress_tracker.py`:
```python
def add_role_module(self, role: str, module_name: str):
    # Add role-specific modules
```

### Change Embedding Model
Edit `embedding_service.py`:
```python
def __init__(self, model_name: str = "your-model"):
```

Available models: [Hugging Face Sentence Transformers](https://www.sbert.net/docs/pretrained_models.html)

## Performance Metrics

Typical performance on standard hardware:

| Operation | Time |
|-----------|------|
| PDF Upload (10MB) | 2-5 seconds |
| Question Answer | 10-30 seconds* |
| Quiz Generation (5 Q) | 30-60 seconds* |
| Quiz Evaluation | 5-10 seconds* |
| Vectorstore Search | <100ms |

*Depends on model load time and hardware

## License

This project is open source and available for educational and commercial use.

## Support

For issues or questions:
1. Check troubleshooting section
2. Review API documentation at `/docs`
3. Check backend logs for errors
4. Ensure Ollama is running and model is loaded

---

**Built with ❤️ for effective employee training**

Version: 1.0.0  
Last Updated: February 2026
