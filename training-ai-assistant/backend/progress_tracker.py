"""
Progress Tracker Module
SQLite-based tracking of employee learning progress
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

class ProgressTracker:
    """Tracks employee learning progress"""
    
    def __init__(self, db_path: str = "backend/progress.db"):
        """
        Initialize progress tracker with SQLite database
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Create database tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Employees table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                email TEXT,
                department TEXT,
                role TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Modules table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS modules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                module_name TEXT UNIQUE NOT NULL,
                description TEXT,
                order_index INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Module progress table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS module_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id TEXT NOT NULL,
                module_id INTEGER NOT NULL,
                status TEXT DEFAULT 'not_started',
                progress_percentage INTEGER DEFAULT 0,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                FOREIGN KEY(module_id) REFERENCES modules(id)
            )
        ''')
        
        # Quiz attempts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quiz_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id TEXT NOT NULL,
                quiz_topic TEXT NOT NULL,
                score REAL NOT NULL,
                total_questions INTEGER NOT NULL,
                correct_answers INTEGER NOT NULL,
                percentage REAL NOT NULL,
                attempt_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                answers TEXT
            )
        ''')
        
        # Questions asked table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS questions_asked (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id TEXT NOT NULL,
                question TEXT NOT NULL,
                category TEXT,
                asked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def register_employee(self, employee_id: str, name: str, email: str = None, 
                         department: str = None, role: str = None) -> bool:
        """Register a new employee"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO employees (employee_id, name, email, department, role)
                VALUES (?, ?, ?, ?, ?)
            ''', (employee_id, name, email, department, role))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def get_employee(self, employee_id: str) -> Optional[Dict]:
        """Get employee info"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM employees WHERE employee_id = ?', (employee_id,))
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    def add_module(self, module_name: str, description: str = None, order_index: int = None):
        """Add a training module"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO modules (module_name, description, order_index)
                VALUES (?, ?, ?)
            ''', (module_name, description, order_index))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def start_module(self, employee_id: str, module_name: str) -> bool:
        """Mark module as started"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get module id
            cursor.execute('SELECT id FROM modules WHERE module_name = ?', (module_name,))
            result = cursor.fetchone()
            if not result:
                conn.close()
                return False
            
            module_id = result[0]
            
            # Update or insert progress
            cursor.execute('''
                INSERT OR REPLACE INTO module_progress 
                (employee_id, module_id, status, started_at)
                VALUES (?, ?, 'in_progress', CURRENT_TIMESTAMP)
            ''', (employee_id, module_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error starting module: {e}")
            return False
    
    def complete_module(self, employee_id: str, module_name: str, progress_percentage: int = 100) -> bool:
        """Mark module as completed"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT id FROM modules WHERE module_name = ?', (module_name,))
            result = cursor.fetchone()
            if not result:
                conn.close()
                return False
            
            module_id = result[0]
            
            cursor.execute('''
                UPDATE module_progress 
                SET status = 'completed', progress_percentage = ?, completed_at = CURRENT_TIMESTAMP
                WHERE employee_id = ? AND module_id = ?
            ''', (progress_percentage, employee_id, module_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error completing module: {e}")
            return False
    
    def log_quiz_attempt(self, employee_id: str, topic: str, score: float, 
                        total_questions: int, correct_answers: int, answers: str = None) -> bool:
        """Log a quiz attempt"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            percentage = (correct_answers / total_questions * 100) if total_questions > 0 else 0
            
            cursor.execute('''
                INSERT INTO quiz_attempts 
                (employee_id, quiz_topic, score, total_questions, correct_answers, percentage, answers)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (employee_id, topic, score, total_questions, correct_answers, percentage, answers))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error logging quiz attempt: {e}")
            return False
    
    def log_question(self, employee_id: str, question: str, category: str = None) -> bool:
        """Log a question asked by employee"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO questions_asked (employee_id, question, category)
                VALUES (?, ?, ?)
            ''', (employee_id, question, category))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error logging question: {e}")
            return False
    
    def get_employee_progress(self, employee_id: str) -> dict:
        """Get comprehensive progress for an employee"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get module progress
            cursor.execute('''
                SELECT m.module_name, mp.status, mp.progress_percentage, mp.started_at, mp.completed_at
                FROM module_progress mp
                JOIN modules m ON mp.module_id = m.id
                WHERE mp.employee_id = ?
                ORDER BY m.order_index
            ''', (employee_id,))
            
            modules = [dict(row) for row in cursor.fetchall()]
            
            # Get quiz results
            cursor.execute('''
                SELECT quiz_topic, percentage, attempt_at, correct_answers, total_questions
                FROM quiz_attempts
                WHERE employee_id = ?
                ORDER BY attempt_at DESC
                LIMIT 10
            ''', (employee_id,))
            
            quizzes = [dict(row) for row in cursor.fetchall()]
            
            conn.close()
            
            return {
                'modules': modules,
                'quiz_history': quizzes,
                'total_modules': len(modules),
                'completed_modules': sum(1 for m in modules if m['status'] == 'completed'),
                'average_quiz_score': sum(q['percentage'] for q in quizzes) / len(quizzes) if quizzes else 0
            }
            
        except Exception as e:
            print(f"Error getting progress: {e}")
            return {}
    
    def get_all_progress(self) -> List[Dict]:
        """Get progress for all employees"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT e.employee_id, e.name, e.email, e.department, e.role,
                       COUNT(DISTINCT CASE WHEN mp.status = 'completed' THEN mp.module_id END) as completed_modules,
                       COUNT(DISTINCT qa.id) as questions_asked,
                       AVG(qa.percentage) as avg_quiz_score
                FROM employees e
                LEFT JOIN module_progress mp ON e.employee_id = mp.employee_id
                LEFT JOIN quiz_attempts qa ON e.employee_id = qa.employee_id
                GROUP BY e.employee_id
            ''')
            
            rows = cursor.fetchall()
            conn.close()
            
            return [dict(row) for row in rows]
            
        except Exception as e:
            print(f"Error getting all progress: {e}")
            return []


# Global instance
progress_tracker = ProgressTracker()
