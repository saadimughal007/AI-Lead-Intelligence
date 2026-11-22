# 🚀 AI Lead Intelligence & Sales Automation Platform

\<p align="center">
&#x20; \<strong>Turn business leads into intelligent sales opportunities with AI.\</strong>
\</p>

\<p align="center">
&#x20; \<img src="[https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white](https://img.shields.io/badge/Python-3776AB?style=for-the-badge\&logo=python\&logoColor=white)" alt="Python"/>
&#x20; \<img src="[https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge\&logo=fastapi\&logoColor=white)" alt="FastAPI"/>
&#x20; \<img src="[https://img.shields.io/badge/Google%20Gemini-8E75B2?style=for-the-badge&logo=googlegemini&logoColor=white](https://img.shields.io/badge/Google%20Gemini-8E75B2?style=for-the-badge\&logo=googlegemini\&logoColor=white)" alt="Gemini"/>
&#x20; \<img src="[https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge\&logo=postgresql\&logoColor=white)" alt="PostgreSQL"/>
&#x20; \<img src="[https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge\&logo=streamlit\&logoColor=white)" alt="Streamlit"/>
\</p>

\<p align="center">
&#x20; \<em>An AI-powered sales intelligence system for lead analysis, qualification, personalized outreach, and sales workflow management.\</em>
\</p>

---

## 📌 Overview

AI Lead Intelligence is an AI-powered sales automation platform designed to help businesses manage leads, evaluate their potential, and generate personalized sales outreach.

The platform combines a FastAPI backend, PostgreSQL database, Google Gemini AI, and an interactive Streamlit dashboard to create a centralized lead intelligence workflow.

Instead of manually evaluating every prospect and writing outreach messages from scratch, users can leverage AI-assisted analysis and structured automation.

## ✨ Key Features

| Feature                   | Description                                          |
| ------------------------- | ---------------------------------------------------- |
| 🎯 Lead Management        | Create, store, and manage business leads             |
| 🧠 AI Lead Scoring        | Evaluate leads using AI-driven scoring               |
| 🔍 Lead Enrichment        | Extract additional information from company websites |
| ✍️ AI Outreach Generation | Generate personalized sales communication            |
| 👤 Human-in-the-Loop      | Review, approve, or reject generated outreach        |
| 📊 Analytics Dashboard    | Monitor lead intelligence and sales metrics          |
| 📈 3D Analytics           | Explore lead score and confidence relationships      |
| 🔐 Authentication         | User authentication and security functionality       |

## 🏗️ System Architecture

```mermaid
flowchart TD
    A["Streamlit Dashboard"] --> B["FastAPI Backend"]
    B --> C["Authentication"]
    B --> D["Lead Management"]
    B --> E["AI Intelligence Services"]
    E --> F["Google Gemini AI"]
    E --> G["Lead Scoring"]
    E --> H["Website Enrichment"]
    B --> I["Outreach Generator"]
    I --> J["Human Approval"]
    B --> K[("PostgreSQL Database")]
    D --> K
    I --> K
```

## 🛠️ Technology Stack

**Backend**

- Python
- FastAPI
- SQLAlchemy
- Pydantic
- Alembic

**Artificial Intelligence**

- Google Gemini API
- AI-powered lead analysis
- AI-assisted lead scoring
- Personalized outreach generation

**Frontend & Analytics**

- Streamlit
- Pandas
- Plotly
- Interactive analytics and 3D visualizations

**Database & Infrastructure**

- PostgreSQL
- Psycopg
- Environment-based configuration
- REST API architecture

## 📂 Project Structure

```text
AI-Lead-Intelligence/
│
├── backend/
│   ├── app/
│   │   ├── core/
│   │   ├── models/
│   │   ├── routes/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── database.py
│   │   └── main.py
│   │
│   ├── migrations/
│   ├── alembic.ini
│   ├── requirements.txt
│   └── pyproject.toml
│
├── dashboard/
│   ├── app.py
│   └── requirements.txt
│
├── database/
│   └── schema.sql
│
├── .gitignore
└── README.md
```

## ⚙️ Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/saadimughal007/AI-Lead-Intelligence.git
cd AI-Lead-Intelligence
```

### 2. Backend Setup

```bash
cd backend

python -m venv .venv
```

Activate the environment:

**Windows PowerShell**

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file inside the `backend` directory:

```env
DATABASE_URL=postgresql+psycopg://username:password@host:5432/database_name

GEMINI_API_KEY=your_gemini_api_key

JWT_SECRET_KEY=your_secure_random_secret
```

Never commit real credentials or API keys to GitHub.

### 4. Start FastAPI

From the backend directory:

```bash
uvicorn app.main:app --reload
```

Backend:

`http://127.0.0.1:8000`

Interactive API documentation:

`http://127.0.0.1:8000/docs`

### 5. Dashboard Setup

Open a new terminal:

```powershell
cd dashboard

python -m venv .venv
.venv\Scripts\Activate.ps1

pip install -r requirements.txt

streamlit run app.py
```

The dashboard uses the backend API URL configured through `API_BASE_URL`, which defaults to:

```env
API_BASE_URL=http://127.0.0.1:8000
```

## 🔌 API Modules

| Module      | Responsibility                             |
| ----------- | ------------------------------------------ |
| `/auth`     | Authentication                             |
| `/leads`    | Lead management, scoring and enrichment    |
| `/outreach` | Outreach generation and approval workflows |
| `/health`   | Application health check                   |
| `/db-check` | Database connectivity check                |

Interactive API documentation is available through FastAPI Swagger UI at `/docs`.

## 🧠 AI Workflow

1. **Lead Acquisition:** Add business leads to the platform.
2. **Lead Enrichment:** Retrieve additional information from company websites.
3. **AI Evaluation:** Analyze and score leads.
4. **Outreach Generation:** Generate personalized sales messages.
5. **Human Review:** Approve or reject AI-generated content.
6. **Analytics:** Monitor lead intelligence through the dashboard.

## 🚧 Development Roadmap

- [x] FastAPI backend foundation
- [x] Lead management modules
- [x] AI scoring and enrichment services
- [x] AI outreach generation
- [x] Human approval workflow
- [x] Streamlit dashboard implementation
- [x] Interactive analytics and 3D visualization
- [ ] Cloud deployment and production verification
- [ ] Automated lead discovery
- [ ] CRM integrations
- [ ] Email and WhatsApp outreach delivery
- [ ] Advanced autonomous sales agents

## 🔮 Future Vision

The long-term vision is to evolve this platform into an intelligent sales automation ecosystem with autonomous AI agents capable of researching prospects, identifying high-value opportunities, coordinating outreach workflows, and assisting sales teams throughout the customer acquisition process.

## 👨‍💻 Author

**Saad Mughal**

AI Automation | Generative AI | Agentic AI

- GitHub: [@saadimughal007](https://github.com/saadimughal007)
- LinkedIn: [Saad Mughal](https://www.linkedin.com/in/saadi-mughal-06007a349)

---

\<p align="center">
&#x20; \<strong>Built with Python, AI, and a vision for intelligent sales automation.\</strong>
\</p>
