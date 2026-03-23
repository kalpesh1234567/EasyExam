# EasyExam – Subjective Answer Evaluation System (ASAE)

A full Django web application for automated evaluation of subjective answers using NLP and Machine Learning.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip

### Setup & Run (Linux/Mac)
```bash
cd asae_project
chmod +x setup_and_run.sh
./setup_and_run.sh
```

### Setup & Run (Windows)
```
Double-click: setup_and_run.bat
```

### Manual Setup
```bash
pip install Django
python manage.py makemigrations classroom
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Then open: **http://127.0.0.1:8000**

---

## 📁 Project Structure

```
asae_project/
├── asae/                    # Django project settings
│   ├── settings.py
│   └── urls.py
├── classroom/               # Main application
│   ├── models.py            # Database models
│   ├── views.py             # All views
│   ├── forms.py             # Django forms
│   ├── nlp_engine.py        # 🧠 NLP evaluation engine (NO external deps)
│   └── migrations/
├── templates/               # HTML templates
│   ├── base.html
│   └── classroom/
│       ├── home.html
│       ├── login.html
│       ├── signup.html
│       ├── teacher_dashboard.html
│       ├── student_dashboard.html
│       ├── create_classroom.html
│       ├── view_classroom.html
│       ├── create_test.html
│       ├── add_question.html
│       ├── attend_test.html
│       ├── test_result.html
│       ├── students_work.html
│       └── review_answer.html
├── manage.py
├── requirements.txt
└── README.md
```

---

## 🧠 NLP Engine (No External Dependencies!)

The `nlp_engine.py` uses **pure Python** — no NLTK, no sklearn, no transformers needed!

### Techniques Used:
| Component | Method |
|-----------|--------|
| Tokenization | Regex-based word splitting |
| Stopword Removal | Custom 80+ word list |
| Stemming | Rule-based suffix removal |
| Text Vectorization | TF-IDF (from scratch) |
| Similarity | Cosine Similarity |
| Keyword Analysis | Frequency-based extraction |
| Final Score | Weighted: 50% cosine + 35% keywords + 15% length |

### Scoring Formula:
```
final_score = (cosine_similarity × 0.50) 
            + (keyword_coverage × 0.35) 
            + (length_score × 0.15)
```

---

## 👤 User Roles

### Teacher
- Create classrooms with unique 6-digit codes
- Create timed tests with multiple questions
- Add reference answers for each question
- View all student submissions
- Override ML scores with manual scores
- Full detailed review of each answer

### Student
- Join classrooms using the classroom code
- Take tests within the time window
- Answers auto-saved to browser (no data loss)
- Instant results with AI feedback after submission
- See matched/missed keywords

---

## 🔌 REST API

### Evaluate a single answer
```
POST /api/evaluate/
Content-Type: application/json

{
  "student_answer": "A database is an organized collection of data...",
  "reference_answer": "A database is a structured set of data...",
  "max_score": 10
}
```

**Response:**
```json
{
  "score": 7.5,
  "percentage": 75.0,
  "similarity": 0.821,
  "keyword_coverage": 0.667,
  "feedback": "✅ Excellent semantic alignment...",
  "matched_keywords": ["database", "organized", "collection"],
  "missed_keywords": ["relational", "schema"]
}
```

---

## 🎨 Tech Stack
- **Backend**: Django 4.2, SQLite
- **NLP**: Pure Python (no external NLP libs needed)
- **Frontend**: Vanilla HTML/CSS/JS (no frameworks)
- **Font**: Sora + JetBrains Mono (Google Fonts)

---

## 👥 Team
- Sejal Jagtap (B400400430)
- Vaishnavi Joshi (B400400432)
- Sanika Nikam (B400400446)
- Nandini Randive (B400400453)

**Guide**: Prof. M.A. Gade  
**Department**: Information Technology, JSCOE, Pune
