# Complete Setup, Testing & Deployment Guide

## 🎯 Pre-Deployment Checklist

### System Requirements
- [ ] macOS 10.14+ OR Linux OR Windows with WSL2
- [ ] Python 3.8 or higher
- [ ] 16GB RAM (minimum 8GB, recommended 16GB+)
- [ ] 50GB free disk space (for models and data)
- [ ] Stable internet (for downloading models)

### Software Requirements
- [ ] Ollama installed from ollama.ai
- [ ] Git (optional, for version control)
- [ ] curl (for API testing)
- [ ] Web browser (Chrome/Firefox/Safari)

---

## 📦 Complete Installation Guide

### Step 1: Install Ollama

**macOS:**
```bash
# Download from https://ollama.ai
# Run the installer
# Ollama will start automatically
```

**Linux (Ubuntu/Debian):**
```bash
curl https://ollama.ai/install.sh | sh
ollama serve  # Start service
```

**Verify Installation:**
```bash
ollama --version
curl http://localhost:11434/api/tags
```

### Step 2: Pull llama3.2 Model

```bash
# In a new terminal
ollama pull llama3.2

# Verify it's available
ollama list
# Should show: llama3.2 ... GiB
```

**Note:** First pull takes 15-30 minutes depending on internet speed.

### Step 3: Clone/Setup Project

```bash
cd /Users/saketh/BIA\ Capstone
ls training-ai-assistant/
```

Should show:
```
backend/
frontend/
vectorstore/
uploads/
requirements.txt
run.sh
README.md
QUICKSTART.md
...
```

### Step 4: Install Python Dependencies

```bash
cd training-ai-assistant

# Create virtual environment
python3 -m venv backend/venv

# Activate it
source backend/venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Verify installation
python3 -c "import torch, faiss, sentence_transformers; print('✓ All packages installed')"
```

**Expected output:** `✓ All packages installed`

### Step 5: Test Backend Server

```bash
# Start backend
cd backend
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### Step 6: Test Frontend

**In another terminal:**
```bash
# Navigate to frontend
cd /Users/saketh/BIA\ Capstone/training-ai-assistant/frontend

# Serve with Python
python3 -m http.server 8080
```

**Or open directly in browser:**
```
file:///Users/saketh/BIA\ Capstone/training-ai-assistant/frontend/index.html
```

---

## 🧪 Testing Procedures

### Phase 1: Backend API Tests

**1. Health Check**
```bash
curl http://localhost:8000/health
# Expected: {"status": "healthy", "ollama": "running", ...}
```

**2. Vector Store Stats**
```bash
curl http://localhost:8000/vectorstore-stats
# Expected: {"total_chunks": 0, "total_documents": 0, ...}
```

**3. API Documentation**
```
# Browser: http://localhost:8000/docs
# You should see Swagger UI with all endpoints
```

### Phase 2: Document Upload Test

**Test 1: Upload Sample Markdown**
```bash
curl -X POST "http://localhost:8000/upload-doc" \
  -F "file=@/Users/saketh/BIA\ Capstone/training-ai-assistant/sample_materials/employee_handbook.md"
```

**Expected response:**
```json
{
  "status": "success",
  "message": "Document 'employee_handbook.md' uploaded successfully",
  "chunks_created": 42,
  "vectorstore_stats": {...}
}
```

**Test 2: Verify Vector Store**
```bash
curl http://localhost:8000/vectorstore-stats
# Should show: "total_chunks": 42, "total_documents": 1
```

### Phase 3: Question Answering Test

**Test 1: Simple Question**
```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the company mission?",
    "employee_id": "test001"
  }'
```

**Expected response:**
```json
{
  "answer": "The company mission is to create innovative...",
  "sources": ["chunk1...", "chunk2..."],
  "confidence": 0.92,
  "question": "What is the company mission?"
}
```

**Test 2: Question Not in Materials**
```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the weather today?",
    "employee_id": "test001"
  }'
```

**Expected response:**
```json
{
  "answer": "I don't have that information in the training materials.",
  ...
}
```

### Phase 4: Quiz Generation Test

**Test 1: Generate Quiz**
```bash
curl -X POST "http://localhost:8000/generate-quiz" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "company culture",
    "num_questions": 3
  }'
```

**Expected response:**
```json
{
  "questions": [
    {
      "id": 1,
      "question": "What is our core value?",
      "options": ["Innovation", "Tradition", "Speed", "Cost"],
      "correct_answer": 0,
      "explanation": "Innovation is listed as our core value..."
    },
    ...
  ],
  "total_questions": 3,
  "topic": "company culture"
}
```

### Phase 5: Quiz Submission Test

**Test 1: Submit Answers**
```bash
curl -X POST "http://localhost:8000/submit-quiz" \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": "emp001",
    "topic": "company culture",
    "answers": [
      {
        "question_id": 1,
        "answer": "Innovation",
        "correct_answer": "Innovation",
        "options": ["Innovation", "Tradition", "Speed", "Cost"]
      }
    ]
  }'
```

**Expected response:**
```json
{
  "total_questions": 1,
  "correct_answers": 1,
  "percentage": 100.0,
  "overall_feedback": "Excellent work!",
  "detailed_results": [...]
}
```

### Phase 6: Employee Management Test

**Test 1: Register Employee**
```bash
curl -X POST "http://localhost:8000/register-employee" \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": "emp001",
    "name": "John Doe",
    "email": "john@company.com",
    "department": "Engineering",
    "role": "Software Engineer"
  }'
```

**Expected response:**
```json
{
  "status": "success",
  "message": "Employee 'John Doe' registered successfully"
}
```

### Phase 7: Frontend Tests

**Test 1: UI Loads**
- [ ] Page loads without errors
- [ ] All tabs visible in navigation
- [ ] Dashboard displays correctly

**Test 2: Upload Works**
- [ ] Click "Upload Documents" tab
- [ ] Drag and drop sample file
- [ ] See success message
- [ ] Vectorstore stats update

**Test 3: Chat Works**
- [ ] Click "Ask Questions" tab
- [ ] Type a question
- [ ] Get response with sources
- [ ] Multiple questions work

**Test 4: Quiz Works**
- [ ] Click "Quiz" tab
- [ ] Generate quiz on uploaded topic
- [ ] Answer questions
- [ ] Submit and view results
- [ ] Results show feedback

**Test 5: Progress Works**
- [ ] Click "Progress" tab
- [ ] Enter employee ID (emp001)
- [ ] Click Load Progress
- [ ] See quiz history

---

## 🚀 Production Deployment

### Option 1: Local Machine (Development)

```bash
cd /Users/saketh/BIA\ Capstone/training-ai-assistant
chmod +x run.sh
./run.sh
```

This starts:
- Ollama at `localhost:11434`
- Backend at `localhost:8000`
- Frontend at `file://` protocol

### Option 2: Server Deployment (Linux)

#### A. Setup on Server

```bash
# SSH into server
ssh user@your-server.com

# Install Python, Ollama
sudo apt update && sudo apt install python3.10 python3-pip

# Install Ollama
curl https://ollama.ai/install.sh | sh

# Clone project
git clone <your-repo-url> training-ai-assistant
cd training-ai-assistant

# Setup backend
python3 -m venv backend/venv
source backend/venv/bin/activate
pip install -r requirements.txt
```

#### B. Create systemd Service

**Create `/etc/systemd/system/ollama.service`:**
```ini
[Unit]
Description=Ollama Service
After=network.target

[Service]
User=ollama
ExecStart=/usr/bin/ollama serve
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Create `/etc/systemd/system/training-ai.service`:**
```ini
[Unit]
Description=Training AI Assistant
After=network.target ollama.service

[Service]
User=www-data
WorkingDirectory=/home/user/training-ai-assistant/backend
ExecStart=/home/user/training-ai-assistant/backend/venv/bin/uvicorn api:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

**Enable and start services:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable ollama
sudo systemctl enable training-ai
sudo systemctl start ollama
sudo systemctl start training-ai
```

**Check status:**
```bash
sudo systemctl status ollama
sudo systemctl status training-ai
```

#### C. Setup Nginx Reverse Proxy

**Create `/etc/nginx/sites-available/training-ai`:**
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /frontend/ {
        alias /home/user/training-ai-assistant/frontend/;
        try_files $uri $uri/ =404;
    }
}
```

**Enable site:**
```bash
sudo ln -s /etc/nginx/sites-available/training-ai /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Option 3: Docker Deployment (Advanced)

**Create `Dockerfile`:**
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy project
COPY . /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose ports
EXPOSE 8000

# Start backend
WORKDIR /app/backend
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Build and run:**
```bash
docker build -t training-ai:latest .
docker run -p 8000:8000 -e OLLAMA_API_URL=http://ollama:11434/api/generate training-ai:latest
```

---

## 📊 Monitoring & Maintenance

### Check System Health

```bash
# Backend health
curl http://localhost:8000/health

# Vector store stats
curl http://localhost:8000/vectorstore-stats

# Database integrity
sqlite3 backend/progress.db ".tables"
```

### View Logs

```bash
# Backend logs (if running in foreground)
# Check terminal output

# System logs (if using systemd)
sudo journalctl -u training-ai -f

# Ollama logs (if using systemd)
sudo journalctl -u ollama -f
```

### Database Backup

```bash
# Backup SQLite database
cp backend/progress.db backups/progress.db.$(date +%Y%m%d)

# Backup vector store
cp -r vectorstore/ backups/vectorstore.$(date +%Y%m%d)/
```

### Performance Optimization

```bash
# Clear old uploads
find uploads/ -mtime +30 -delete

# Clear old database records (if needed)
sqlite3 backend/progress.db "DELETE FROM quiz_attempts WHERE attempt_at < datetime('now', '-6 months');"

# Rebuild vector store index if needed
rm vectorstore/index.faiss*
# Re-upload documents through API
```

---

## 🔒 Security Hardening

### 1. Add Authentication

Edit `backend/api.py`:
```python
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from fastapi import Depends

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthCredentials = Depends(security)):
    token = credentials.credentials
    if not verify_jwt_token(token):
        raise HTTPException(status_code=401, detail="Invalid token")
    return token

@app.post("/ask")
async def ask_question(request: QuestionRequest, token: str = Depends(verify_token)):
    # ... rest of endpoint
```

### 2. Add Rate Limiting

```bash
pip install slowapi
```

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/ask")
@limiter.limit("10/minute")
async def ask_question(request: QuestionRequest):
    # ... endpoint
```

### 3. Enable HTTPS

```bash
# Get SSL certificate (Let's Encrypt)
sudo apt install certbot python3-certbot-nginx
sudo certbot certonly --nginx -d your-domain.com

# Update Nginx config with SSL
sudo nano /etc/nginx/sites-available/training-ai
# Add ssl_certificate and ssl_certificate_key directives
```

### 4. Set Environment Variables

```bash
# Create .env file with secrets
echo "ADMIN_API_KEY=your-secret-key" > .env
echo "OLLAMA_API_URL=http://localhost:11434/api/generate" >> .env

# Load in Python
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("ADMIN_API_KEY")
```

---

## ✅ Final Verification

Before considering deployment complete, verify:

- [ ] Ollama service running and responsive
- [ ] Backend API running without errors
- [ ] Frontend loads and displays properly
- [ ] Can upload documents successfully
- [ ] Can ask questions and get answers
- [ ] Can generate and submit quizzes
- [ ] Can register employees and track progress
- [ ] Database created and storing data
- [ ] Vector store created and searchable
- [ ] All endpoints accessible via API
- [ ] CORS working properly
- [ ] Error handling working correctly
- [ ] Logging configured
- [ ] Security basics implemented
- [ ] Backup procedures created

---

## 📞 Troubleshooting Matrix

| Issue | Cause | Solution |
|-------|-------|----------|
| Can't connect to Ollama | Service not running | `ollama serve` |
| Model not found | Not downloaded | `ollama pull llama3.2` |
| Port 8000 in use | Another process | `lsof -ti:8000 \| xargs kill -9` |
| Slow responses | Model loading | Wait, then check RAM |
| No documents indexed | Upload failed silently | Check logs, re-upload |
| CORS errors | Frontend wrong URL | Update API_BASE_URL |
| Database locked | Concurrent access | Stop process, check integrity |
| OOM (Out of Memory) | Model too large for RAM | Use smaller model or more RAM |
| GPU not used | CUDA/MPS not configured | Check PyTorch installation |

---

## 🎓 Next Steps After Deployment

1. **Populate Content**
   - Upload company training materials
   - Create structured modules
   - Categorize content by department

2. **Onboard Users**
   - Register employees
   - Create learning paths
   - Send welcome emails

3. **Monitor Usage**
   - Track engagement metrics
   - Collect feedback
   - Identify improvement areas

4. **Iterate**
   - Update training materials
   - Refine quizzes
   - Add new features

5. **Scale**
   - Plan for larger employee base
   - Optimize database queries
   - Consider distributed deployment

---

**🎉 Congratulations!**

Your AI Training Assistant is ready for deployment. Begin with the Quick Start Guide and follow this checklist for a smooth setup experience.

For support, refer to:
- README.md - Complete documentation
- QUICKSTART.md - Fast 5-minute setup
- ARCHITECTURE.md - Technical details
- API Docs - http://localhost:8000/docs

**Version:** 1.0.0  
**Last Updated:** February 2026
