# WebScraper AI 🤖

A powerful AI-powered web scraping and monitoring system that transforms any website into an intelligent agent. Chat with website content, monitor changes automatically, and receive email notifications.

## 📺 Demo Video




https://github.com/user-attachments/assets/4d511b78-6c11-4ed4-84f3-9dae6562ebff






---

## 🌟 Features

* **AI-Powered Agents** - Create custom agents with specific roles and expertise
* **Intelligent Chat Interface** - Ask questions about scraped content using natural language
* **Smart Monitoring** - Track website changes with configurable intervals
* **Email Notifications** - Receive AI-generated summaries of content changes
* **User Authentication** - Secure login with session management
* **Vector Search** - Semantic search powered by ChromaDB
* **Background Scheduling** - Automated scraping and monitoring with APScheduler

---

## 🚀 Tech Stack

### Frontend

* React 18
* Vite
* React Router
* Tailwind CSS
* Axios
* Lucide React Icons

### Backend

* FastAPI
* Python 3.10+
* SQLite (User & Agent data)
* ChromaDB (Vector storage)
* Groq API (LLM - Llama 3.3 70B)
* Playwright (Web scraping)
* APScheduler (Background jobs)
* BeautifulSoup4 (HTML parsing)
* Sentence Transformers (Embeddings)

---

## 📋 Prerequisites

* Python 3.10 or higher
* Node.js 18 or higher
* npm or yarn
* Groq API key (free tier available)
* Gmail account (for SMTP notifications)

---

## 🛠️ Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/webscraper-ai.git
cd webscraper-ai

```

### 2. Backend Setup

Navigate to the backend directory and set up the Python environment:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

```

**Configure Environment Variables:**

Rename `backend/.env.example` to `backend/.env` and configure:

```env
# Groq API Configuration
GROQ_API_KEY=your_groq_api_key_here

# SMTP Email Configuration (Gmail example)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_gmail_app_password

```

**Start the Backend Server:**

```bash
python -m fastapi dev backend/main.py

```

The backend will be running on **http://localhost:8000**.

### 3. Frontend Setup

Navigate to the frontend directory:

```bash
cd frontend

```

**Install Dependencies:**

```bash
npm install

```

**Start the Development Server:**

```bash
npm run dev

```

The frontend will be running on **http://localhost:5173**.

---

## 🎯 Usage

### Creating Your First Agent

1. **Sign Up/Login** to your account at http://localhost:5173.
2. Click **"Create Agent"** button on the dashboard.
3. Configure your agent name and role (e.g., "Tech News Analyzer").

### Adding Knowledge Base

1. Open your created agent and click **"Add URL"** or **"Scrape"**.
2. Enter the website URL to scrape.
3. Configure scraping options like **Multi-page** or **CSS Selectors**.
4. Click **"Scrape"** to build the knowledge base.

### Chatting with Your Agent

1. Open the agent and click **"Chat"**.
2. Ask questions about the scraped content using natural language.
3. Agent responds using RAG (Retrieval-Augmented Generation).

### Setting Up Reminders

1. Navigate to **"Reminders"** page and click **"Create Reminder"**.
2. Configure the URL, email notification, and check interval.
3. Receive email notifications when content changes with AI-generated summaries.

---

## 📁 Project Structure

```
webscraper-ai/
├── backend/
│   ├── api/routes/          # API endpoints
│   ├── core/                # LLM, Scheduler, VectorDB
│   ├── models/              # Database models
│   └── main.py              # FastAPI application
├── frontend/
│   ├── src/                 # Components, Pages, Services
│   └── package.json
├── data/                    # SQLite & ChromaDB storage
├── requirements.txt
└── README.md

```

---

## 🔧 Configuration

### Available Groq Models

Edit `backend/core/llm_service.py` to change the model:

```python
MODEL_NAME = "llama-3.3-70b-versatile"  # Recommended

```

### Gmail SMTP Setup

1. Enable 2-Factor Authentication on your Google account.
2. Generate an **App Password** at [https://myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords).
3. Use this 16-character password in your `.env` file.

---

## 🔌 API Endpoints

### Authentication

* `POST /api/auth/signup` - Register new user
* `POST /api/auth/login` - Login user
* `GET /api/auth/me` - Get current user info

### Agents & Chat

* `POST /api/agents/create` - Create new agent
* `GET /api/agents/list` - List user's agents
* `POST /api/process` - Chat with agent

---

## 🐛 Troubleshooting

* **Backend won't start:** Check if port 8000 is already in use.
* **Playwright error:** Run `playwright install chromium` to install browsers.
* **Email not sending:** Verify your Gmail App Password and ensure 2FA is enabled.

---

## 📞 Support

For support, please open an issue in the repository or contact faranarfi1@gmail.com.

**Made with ❤️ by Faran Arfi*
