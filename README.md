📘 Disaster Relief Multi-Agent Coordinator

A Multi-Agent Disaster Response System built for the Kaggle × Google Agentic AI Intensive Program (Agents for Good Track).

The Disaster Relief Multi-Agent Coordinator is an intelligent agentic system that detects real-time environmental hazards, evaluates risk, and generates coordinated emergency response plans using Google ADK, custom tools, weather alert engines, and Google Maps API–based geospatial intelligence.
It features an interactive disaster map, live alert ingestion, automated volunteer assignment, shelter routing, and structured plan generation powered by multi-agent reasoning.

This project demonstrates how AI agents can assist public safety organizations, NGOs, and emergency authorities in making faster and more informed decisions during floods, earthquakes, cyclones, and other emergencies.

🚀 Features

Multi-agent system (CoordinatorAgent, RiskAgent, PlannerAgent) built using Google ADK

Real-time hazard alert ingestion with a background producer

Interactive geospatial map with markers, zoom, and popups

Risk evaluation using LLM-powered reasoning

Dynamic evacuation plan generation

Volunteer assignment tool

Routing & travel time estimation using Google Maps API

Nearby shelter recommendation

Log viewer for observing agent behavior

Long-term memory storage using MemoryBank

Modern React frontend with Vite + Tailwind

🎯 ADK Concepts Demonstrated (Meets Submission Requirements)

This project satisfies more than the required three ADK features, including:

Multi-Agent System: RiskAgent, PlannerAgent, CoordinatorAgent

LLM-Powered Agents: Agents running on Gemini 2.0 Flash

Sequential & Parallel Tool Usage

Custom Tools: weather alert tool, volunteer tool, shelter finder, routing tool

Sessions & Memory: MemoryBank for storing alerts and plans

Context Engineering: structured JSON prompts and context compaction

Observability: Logging, tracing, and live log viewer

Agent Evaluation & A2A-style orchestration

🗂 Project Structure
disaster_coordinator_adk/
│
├── backend/
│   ├── main.py
│   ├── agents/
│   ├── tools/
│   ├── memory/
│   └── .venv/
│
└── frontend/
    ├── src/
    ├── public/
    ├── package.json
    └── vite.config.js

🔧 Requirements
Backend

Python 3.10+

FastAPI

Google ADK SDK

python-dotenv

uvicorn

requests

geopy (optional)

A valid Google Maps API key in .env

Frontend

Node.js 18+

npm or yarn

Vite

React 18+

TailwindCSS

react-leaflet + leaflet

📦 Installation
1️⃣ Clone the Repository
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>

🖥️ Backend Setup
2️⃣ Create & Activate Virtual Environment
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1     # Windows

3️⃣ Install Requirements
pip install -r requirements.txt

4️⃣ Create .env File
ADK_MODEL=gemini-2.0-flash
GOOGLE_MAPS_API_KEY=your_api_key_here

5️⃣ Run Backend
uvicorn main:app --host 127.0.0.1 --port 8000 --reload


Your backend will now run at:

➡️ http://127.0.0.1:8000

🌐 Frontend Setup

Open a new terminal:

cd frontend
npm install
npm run dev


Your frontend will run at:

➡️ http://127.0.0.1:5173

📡 API Endpoints
GET /api/poll_alerts

Returns all current hazard alerts.

POST /api/plan/{alert_id}

Generates a structured disaster response plan.

GET /api/logs

Returns system logs for observability.

GET /api/incidents

Returns stored incident history.

GET /api/health

Backend health check.

🧪 Running Full System

Start backend:

cd backend
.\.venv\Scripts\Activate.ps1
uvicorn main:app --host 127.0.0.1 --port 8000 --reload


Start frontend:

cd frontend
npm run dev


Open your browser at:
http://127.0.0.1:5173

🤝 Contributing

Contributions, improvements, and pull requests are welcome!

If you would like to suggest features, fix bugs, optimize agent workflows, or enhance the UI, feel free to open an issue or submit a PR.
Please ensure your changes align with the existing project structure and coding style.

📜 License

This project is open-source under the MIT License.
You are free to use, modify, and distribute it with proper attribution.
