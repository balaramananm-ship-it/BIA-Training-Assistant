/* ==================== Configuration ==================== */

const API_BASE_URL = 'http://localhost:8000';
let currentEmployeeId = 'anonymous';
let currentQuiz = null;

/* ==================== DOM Selectors ==================== */

const navLinks = document.querySelectorAll('.nav-link');
const tabContents = document.querySelectorAll('.tab-content');
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const uploadProgress = document.getElementById('uploadProgress');
const uploadResult = document.getElementById('uploadResult');
const progressFill = document.getElementById('progressFill');
const uploadStatus = document.getElementById('uploadStatus');
const questionInput = document.getElementById('questionInput');
const sendButton = document.getElementById('sendButton');
const chatMessages = document.getElementById('chatMessages');
const generateQuizBtn = document.getElementById('generateQuizBtn');
const quizTopic = document.getElementById('quizTopic');
const quizCount = document.getElementById('quizCount');
const quizLoading = document.getElementById('quizLoading');
const quizContent = document.getElementById('quizContent');
const quizQuestions = document.getElementById('quizQuestions');
const submitQuizBtn = document.getElementById('submitQuizBtn');
const quizResults = document.getElementById('quizResults');
const resultsContent = document.getElementById('resultsContent');
const newQuizBtn = document.getElementById('newQuizBtn');
const employeeId = document.getElementById('employeeId');
const loadProgressBtn = document.getElementById('loadProgressBtn');
const progressContent = document.getElementById('progressContent');
const toastContainer = document.getElementById('toastContainer');

/* ==================== Initialization ==================== */

document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    checkSystemHealth();
    updateVectorstoreStats();
});

/* ==================== Event Listeners ==================== */

function setupEventListeners() {
    // Navigation
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            switchTab(link.dataset.tab);
        });
    });

    // Upload
    uploadArea.addEventListener('click', () => fileInput.click());
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });
    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        handleFileSelect(e.dataTransfer.files);
    });
    fileInput.addEventListener('change', (e) => {
        handleFileSelect(e.target.files);
    });

    // Chat
    sendButton.addEventListener('click', askQuestion);
    questionInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') askQuestion();
    });

    // Quiz
    generateQuizBtn.addEventListener('click', generateQuiz);
    submitQuizBtn.addEventListener('click', submitQuiz);
    newQuizBtn.addEventListener('click', () => {
        quizContent.classList.add('hidden');
        quizResults.classList.add('hidden');
        quizSetup.classList.remove('hidden');
    });

    // Progress
    loadProgressBtn.addEventListener('click', loadProgress);
}

/* ==================== Tab Switching ==================== */

function switchTab(tabName) {
    // Update nav links
    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.dataset.tab === tabName) {
            link.classList.add('active');
        }
    });

    // Update tab content
    tabContents.forEach(content => {
        content.classList.remove('active');
        if (content.id === tabName) {
            content.classList.add('active');
        }
    });
}

/* ==================== File Upload ==================== */

async function handleFileSelect(files) {
    if (files.length === 0) return;

    for (let file of files) {
        await uploadFile(file);
    }
}

async function uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);

    uploadProgress.classList.remove('hidden');
    uploadResult.classList.add('hidden');
    uploadStatus.textContent = `Uploading ${file.name}...`;

    try {
        const xhr = new XMLHttpRequest();
        
        xhr.upload.addEventListener('progress', (e) => {
            if (e.lengthComputable) {
                const percentComplete = (e.loaded / e.total) * 100;
                progressFill.style.width = percentComplete + '%';
            }
        });

        xhr.addEventListener('load', () => {
            const response = JSON.parse(xhr.responseText);
            if (xhr.status === 200) {
                showAlert(`✓ ${response.message}`, 'success');
                updateVectorstoreStats();
                fileInput.value = '';
                uploadProgress.classList.add('hidden');
            } else {
                showAlert(`✗ Upload failed: ${response.detail}`, 'error');
            }
        });

        xhr.addEventListener('error', () => {
            showAlert('✗ Upload failed', 'error');
        });

        xhr.open('POST', `${API_BASE_URL}/upload-doc`);
        xhr.send(formData);

    } catch (error) {
        showAlert(`✗ Error uploading file: ${error.message}`, 'error');
    }
}

/* ==================== Questions & Answers ==================== */

async function askQuestion() {
    const question = questionInput.value.trim();
    if (!question) return;

    // Add user message to chat
    addChatMessage(question, 'user');
    questionInput.value = '';
    sendButton.disabled = true;

    try {
        const response = await fetch(`${API_BASE_URL}/ask`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                question: question,
                employee_id: currentEmployeeId
            })
        });

        const data = await response.json();

        if (data.error) {
            addChatMessage(`Error: ${data.answer}`, 'assistant');
        } else {
            let answerText = data.answer;
            if (data.sources && data.sources.length > 0) {
                answerText += `\n\n📚 Sources: ${data.sources.length} reference(s) found`;
            }
            answerText += `\n\n🎯 Confidence: ${(data.confidence * 100).toFixed(1)}%`;
            addChatMessage(answerText, 'assistant');
        }
    } catch (error) {
        addChatMessage(`Error: ${error.message}`, 'assistant');
    } finally {
        sendButton.disabled = false;
        questionInput.focus();
    }
}

function addChatMessage(message, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    
    let avatar = sender === 'user' ? '👤' : '🤖';
    messageDiv.innerHTML = `
        <div class="message-avatar">${avatar}</div>
        <div class="message-content">${escapeHtml(message)}</div>
    `;
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

/* ==================== Quiz Management ==================== */

async function generateQuiz() {
    const topic = quizTopic.value.trim() || null;
    const numQuestions = parseInt(quizCount.value);

    document.getElementById('quizSetup').classList.add('hidden');
    quizLoading.classList.remove('hidden');

    try {
        const response = await fetch(`${API_BASE_URL}/generate-quiz`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                topic: topic,
                num_questions: numQuestions
            })
        });

        const data = await response.json();

        if (data.error) {
            showAlert(`Error: ${data.message}`, 'error');
            quizLoading.classList.add('hidden');
            document.getElementById('quizSetup').classList.remove('hidden');
            return;
        }

        currentQuiz = data;
        displayQuiz(data);
    } catch (error) {
        showAlert(`Error generating quiz: ${error.message}`, 'error');
        quizLoading.classList.add('hidden');
        document.getElementById('quizSetup').classList.remove('hidden');
    }
}

function displayQuiz(quiz) {
    quizQuestions.innerHTML = '';

    quiz.questions.forEach((question, index) => {
        const questionDiv = document.createElement('div');
        questionDiv.className = 'quiz-question';
        questionDiv.innerHTML = `
            <div class="question-number">Question ${index + 1} of ${quiz.questions.length}</div>
            <div class="question-text">${escapeHtml(question.question)}</div>
            <div class="options">
                ${question.options.map((option, optIndex) => `
                    <label class="option-label">
                        <input type="radio" name="question_${question.id}" value="${optIndex}">
                        <span>${escapeHtml(option)}</span>
                    </label>
                `).join('')}
            </div>
        `;
        quizQuestions.appendChild(questionDiv);
    });

    quizLoading.classList.add('hidden');
    quizContent.classList.remove('hidden');
}

async function submitQuiz() {
    const answers = [];

    currentQuiz.questions.forEach((question) => {
        const selectedInput = document.querySelector(`input[name="question_${question.id}"]:checked`);
        if (selectedInput) {
            const answerIndex = parseInt(selectedInput.value);
            answers.push({
                question_id: question.id,
                answer: question.options[answerIndex],
                correct_answer: question.options[question.correct_answer],
                options: question.options
            });
        }
    });

    if (answers.length !== currentQuiz.questions.length) {
        showAlert('Please answer all questions before submitting', 'warning');
        return;
    }

    submitQuizBtn.disabled = true;
    submitQuizBtn.textContent = 'Submitting...';

    try {
        const response = await fetch(`${API_BASE_URL}/submit-quiz`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                employee_id: currentEmployeeId,
                topic: currentQuiz.topic || 'General',
                answers: answers
            })
        });

        const results = await response.json();
        displayQuizResults(results);
    } catch (error) {
        showAlert(`Error submitting quiz: ${error.message}`, 'error');
    } finally {
        submitQuizBtn.disabled = false;
        submitQuizBtn.textContent = 'Submit Quiz';
    }
}

function displayQuizResults(results) {
    quizContent.classList.add('hidden');

    const resultsHTML = `
        <div class="result-score">${results.correct_answers}/${results.total_questions}</div>
        <div class="result-percentage">${results.percentage}%</div>
        <p style="text-align: center; margin: 1rem 0;">${results.overall_feedback}</p>
        
        <h4>Detailed Results:</h4>
        ${results.detailed_results.map((result, index) => `
            <div class="result-item ${result.is_correct ? 'correct' : 'incorrect'}">
                <strong>Question ${index + 1}:</strong> ${result.is_correct ? '✓ Correct' : '✗ Incorrect'}
                <p><strong>Your answer:</strong> ${escapeHtml(result.user_answer)}</p>
                ${!result.is_correct ? `<p><strong>Correct answer:</strong> ${escapeHtml(result.correct_answer)}</p>` : ''}
                <p><em>${escapeHtml(result.feedback)}</em></p>
            </div>
        `).join('')}
    `;

    resultsContent.innerHTML = resultsHTML;
    quizResults.classList.remove('hidden');
    showAlert(`Quiz completed! You scored ${results.percentage}%`, 'success');
}

/* ==================== Progress Tracking ==================== */

async function loadProgress() {
    const empId = employeeId.value.trim();
    if (!empId) {
        showAlert('Please enter an employee ID', 'warning');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/progress/${empId}`);
        const data = await response.json();

        if (response.status === 404) {
            showAlert('Employee not found', 'error');
            return;
        }

        currentEmployeeId = empId;
        displayProgress(data);
    } catch (error) {
        showAlert(`Error loading progress: ${error.message}`, 'error');
    }
}

function displayProgress(progress) {
    let modulesHTML = '';
    if (progress.modules && progress.modules.length > 0) {
        modulesHTML = progress.modules.map(module => `
            <div class="module-item">
                <span>${escapeHtml(module.module_name)}</span>
                <span class="module-status ${module.status}">${module.status.replace('_', ' ')}</span>
            </div>
        `).join('');
    } else {
        modulesHTML = '<p>No modules started yet</p>';
    }

    let quizHistoryHTML = '';
    if (progress.quiz_history && progress.quiz_history.length > 0) {
        quizHistoryHTML = progress.quiz_history.map(quiz => `
            <div class="module-item">
                <div>
                    <strong>${escapeHtml(quiz.quiz_topic)}</strong><br>
                    <small>${new Date(quiz.attempt_at).toLocaleDateString()} - ${quiz.correct_answers}/${quiz.total_questions} correct</small>
                </div>
                <span style="font-weight: bold; color: var(--primary-color);">${quiz.percentage.toFixed(1)}%</span>
            </div>
        `).join('');
    } else {
        quizHistoryHTML = '<p>No quiz attempts yet</p>';
    }

    document.getElementById('completedModules').textContent = progress.completed_modules || 0;
    document.getElementById('avgQuizScore').textContent = 
        progress.average_quiz_score ? `${progress.average_quiz_score.toFixed(1)}%` : '--';
    document.getElementById('modulesList').innerHTML = modulesHTML;
    document.getElementById('quizHistory').innerHTML = quizHistoryHTML;
    progressContent.classList.remove('hidden');
}

/* ==================== System Health & Stats ==================== */

async function checkSystemHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        const data = await response.json();

        const healthStatus = document.getElementById('health-status');
        healthStatus.innerHTML = `
            <strong>🔧 System Status:</strong> ${data.status}<br>
            <strong>🤖 Ollama:</strong> ${data.ollama === 'running' ? '✓ Running' : '✗ Not Running'}
        `;

        if (data.ollama !== 'running') {
            healthStatus.innerHTML += '<br><span style="color: #ef4444;">⚠️ Ollama is not running. Please start it first!</span>';
        }
    } catch (error) {
        document.getElementById('health-status').textContent = '✗ Cannot connect to backend';
    }
}

async function updateVectorstoreStats() {
    try {
        const response = await fetch(`${API_BASE_URL}/vectorstore-stats`);
        const stats = await response.json();

        const statsDiv = document.getElementById('vectorstoreDetails') || createStatsDiv();
        statsDiv.innerHTML = `
            <p><strong>📊 Total Chunks:</strong> ${stats.total_chunks}</p>
            <p><strong>📄 Documents:</strong> ${stats.total_documents}</p>
            <p><strong>📈 Index Size:</strong> ${stats.index_size}</p>
            <p><strong>🔢 Embedding Dimension:</strong> ${stats.embedding_dimension}</p>
        `;

        // Update dashboard stats
        document.getElementById('doc-count').textContent = stats.total_documents || 0;
    } catch (error) {
        console.error('Error fetching vectorstore stats:', error);
    }
}

function createStatsDiv() {
    const div = document.createElement('div');
    div.id = 'vectorstoreDetails';
    const uploadCard = document.querySelector('#upload .card:nth-child(2)');
    if (uploadCard) {
        uploadCard.appendChild(div);
    }
    return div;
}

/* ==================== Utilities ==================== */

function showAlert(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    toastContainer.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Add slide out animation
const style = document.createElement('style');
style.textContent = `
    @keyframes slideOut {
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
