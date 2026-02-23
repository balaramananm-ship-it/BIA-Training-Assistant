# 🚀 Quick Start Guide - AI Training Assistant

## 5-Minute Setup

### Step 1: Verify Prerequisites (2 min)
```bash
# Check Python
python3 --version  # Should be 3.8+

# Check if Ollama is installed
ollama --version
```

### Step 2: Install Ollama & llama3.2 (if needed)
```bash
# Download and install Ollama from https://ollama.ai
# Then start the service:
ollama serve

# In another terminal, pull the model:
ollama pull llama3.2

# Verify it's working:
curl http://localhost:11434/api/tags
```

### Step 3: Setup Backend (2 min)
```bash
# Navigate to project
cd /Users/saketh/BIA\ Capstone/training-ai-assistant

# Make run script executable
chmod +x run.sh

# Start backend
./run.sh
```

The script will:
- ✓ Create virtual environment
- ✓ Install dependencies
- ✓ Check Ollama connection
- ✓ Start FastAPI server

### Step 4: Open Frontend (1 min)
```bash
# In browser, open:
file:///Users/saketh/BIA\ Capstone/training-ai-assistant/frontend/index.html

# OR serve with Python:
cd frontend
python3 -m http.server 8080
# Visit: http://localhost:8080
```

### Step 5: Test the System
1. Go to "Upload Documents" tab
2. Upload a sample PDF/DOCX file
3. Go to "Ask Questions" tab
4. Ask a question about the document
5. Go to "Quiz" tab and create a quiz

## Detailed Setup

### Manual Backend Setup
```bash
# Navigate to project
cd /Users/saketh/BIA\ Capstone/training-ai-assistant

# Create virtual environment
python3 -m venv backend/venv

# Activate it
source backend/venv/bin/activate  # macOS/Linux
# On Windows: backend\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start backend
cd backend
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

### Verify Ollama Setup
```bash
# Check Ollama service
curl -X GET http://localhost:11434/api/tags

# Expected response should show available models
# If error, start Ollama: ollama serve

# Ensure llama3.2 is available
ollama list  # Should show llama3.2

# If not listed, pull it:
ollama pull llama3.2
```

### Check API is Running
```bash
# Test health endpoint
curl http://localhost:8000/health

# View API docs
# Browser: http://localhost:8000/docs
```

## Folder Structure After Setup

```
training-ai-assistant/
├── backend/
│   ├── venv/                    # Virtual environment (created)
│   ├── ollama_client.py
│   ├── ingestion_service.py
│   ├── embedding_service.py
│   ├── vector_store.py
│   ├── rag_pipeline.py
│   ├── quiz_generator.py
│   ├── evaluator.py
│   ├── progress_tracker.py
│   ├── api.py
│   └── progress.db              # Created on first use
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── script.js
├── vectorstore/
│   ├── .gitkeep
│   └── index.faiss              # Created on first upload
├── uploads/
│   └── .gitkeep
└── ...
```

## Common Tasks

### Upload Your First Document

**Via Browser UI:**
1. Click "Upload Documents" tab
2. Drag & drop a PDF/DOCX/TXT file
3. Or click to select file
4. Watch progress bar
5. Confirm success message

**Via API:**
```bash
curl -X POST "http://localhost:8000/upload-doc" \
  -F "file=@/path/to/document.pdf"
```

### Ask a Question

**Via UI:**
1. Click "Ask Questions" tab
2. Type your question
3. Press Enter or click Send
4. Get AI answer with confidence score

**Via API:**
```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is company culture?", "employee_id": "emp001"}'
```

### Generate and Take a Quiz

**Via UI:**
1. Click "Quiz" tab
2. Enter topic (optional)
3. Select number of questions
4. Click "Generate Quiz"
5. Answer questions
6. Submit and get results

**Via API:**
```bash
# Generate quiz
curl -X POST "http://localhost:8000/generate-quiz" \
  -H "Content-Type: application/json" \
  -d '{"topic": "company culture", "num_questions": 5}'

# Submit answers
curl -X POST "http://localhost:8000/submit-quiz" \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": "emp001",
    "topic": "company culture",
    "answers": [
      {
        "question_id": 1,
        "answer": "Option A",
        "correct_answer": "Option A"
      }
    ]
  }'
```

### Track Progress

**Via UI:**
1. Click "Progress" tab
2. Enter employee ID
3. View modules completed, quiz history, average score

**Via API:**
```bash
# Get employee progress
curl "http://localhost:8000/progress/emp001"

# Get all employees' progress
curl "http://localhost:8000/all-progress"
```

## Troubleshooting

### Issue: "Cannot connect to Ollama"

**Check 1:** Is Ollama running?
```bash
ps aux | grep ollama
# or
lsof -i :11434
```

**Check 2:** Start Ollama
```bash
ollama serve
```

**Check 3:** Test connection
```bash
curl http://localhost:11434/api/tags
```

### Issue: "ModuleNotFoundError"

**Solution:** Install dependencies
```bash
pip install -r requirements.txt
# Or for specific issues:
pip install --upgrade torch sentence-transformers faiss-cpu
```

### Issue: Port 8000 Already in Use

**Find and kill process:**
```bash
lsof -ti:8000 | xargs kill -9
```

**Or use different port:**
```bash
cd backend
uvicorn api:app --port 8001
```

### Issue: Slow Response Times

**First-time slowness:** Normal! llama3.2 loads into memory
- First question: 30-60 seconds
- Subsequent questions: 10-30 seconds

**To improve:**
- Increase system RAM
- Use GPU (if available)
- Pre-load model: `ollama run llama3.2`

### Issue: Frontend Blank Screen

**Check 1:** Browser console for errors (F12)

**Check 2:** Verify API is running
```bash
curl http://localhost:8000/health
```

**Check 3:** Clear browser cache
- Press Ctrl+Shift+Delete (or Cmd+Shift+Delete on Mac)
- Clear all data
- Refresh page

## API Quick Reference

### Core Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/health` | Check system status |
| POST | `/upload-doc` | Upload training document |
| POST | `/ask` | Get answer to question |
| POST | `/generate-quiz` | Create quiz |
| POST | `/submit-quiz` | Submit quiz answers |
| POST | `/register-employee` | Register employee |
| GET | `/progress/{id}` | Get employee progress |
| POST | `/add-module` | Add training module |
| POST | `/start-module` | Start module |
| POST | `/complete-module` | Complete module |
| GET | `/vectorstore-stats` | Vector store info |

### Response Format

**Success Response (200):**
```json
{
  "status": "success",
  "message": "...",
  "data": { }
}
```

**Error Response (400/500):**
```json
{
  "detail": "Error message explaining what went wrong"
}
```

## Performance Notes

- **First API call:** 30-60 seconds (model loading)
- **Subsequent calls:** 10-30 seconds
- **Vector search:** <100ms
- **File upload:** 2-5 seconds per document
- **Quiz generation:** 30-60 seconds
- **Answer evaluation:** 5-10 seconds

## Next Steps

1. ✅ Upload your company training materials
2. ✅ Register employees in the system
3. ✅ Create training modules
4. ✅ Generate quizzes for assessment
5. ✅ Track employee learning progress
6. ✅ Gather feedback and iterate

## Environment Files

Edit `.env` to customize:
```env
# Ollama
OLLAMA_API_URL=http://localhost:11434/api/generate
MODEL_NAME=llama3.2

# Processing
CHUNK_SIZE=512
EMBEDDING_MODEL=all-MiniLM-L6-v2

# API
API_PORT=8000
```

## Support

### Documentation
- API Docs: http://localhost:8000/docs (Swagger UI)
- README: See project README.md
- Code Comments: Inline documentation in each module

### Debug Mode
```bash
# Enable verbose logging
export PYTHONUNBUFFERED=1
cd backend
uvicorn api:app --reload --log-level debug
```

### Check Logs
```bash
# Backend logs are printed to console during `./run.sh`
# Look for errors after ❌ or ⚠️

# Check specific service
grep -i "error" backend/api.py  # Search for known issues
```

---

**Ready to go!** 🎉

Start with `./run.sh` and visit the frontend. Happy training!
