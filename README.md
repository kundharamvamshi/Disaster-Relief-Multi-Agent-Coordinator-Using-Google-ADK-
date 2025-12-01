# 🌐 Disaster Relief Multi-Agent Coordinator  
*A multi-agent disaster response system built for the Kaggle × Google Agentic AI Intensive (Agents for Good Track).*

The **Disaster Relief Multi-Agent Coordinator** is an AI-driven system that detects real-time hazard alerts, evaluates risk using multi-agent reasoning, and automatically generates emergency response plans. Using **Google ADK**, **custom tools**, **Google Maps APIs**, and an **interactive map**, the system demonstrates how agentic AI enables smarter disaster management for floods, earthquakes, cyclones, and other emergencies.

---

## 📌 Features
- Multi-agent architecture powered by Google ADK  
- LLM-based risk evaluation and planning  
- Real-time alert ingestion with background producer  
- Interactive map UI (Leaflet)  
- Shelter recommendation & routing (Google Maps API)  
- Volunteer assignment tool  
- MemoryBank for long-term storage  
- Observability: logs, tracing, live log viewer  
- Full-stack integration: FastAPI + React + Vite + TailwindCSS  

---

## 🧠 ADK Concepts Demonstrated
This project includes **more than 3** ADK-required features:
- Multi-Agent System: CoordinatorAgent, RiskAgent, PlannerAgent  
- LLM-powered tool orchestration using FunctionTools  
- Custom Tools (weather, volunteers, geocode, routing, shelters)  
- MemoryBank providing long-term state  
- Context engineering with structured JSON  
- Observability via logs endpoint  

---


---

## 🛠 Requirements

### Backend
- Python 3.10+
- FastAPI
- Uvicorn
- Google ADK SDK
- python-dotenv
- requests
- Google Maps API Key

### Frontend
- Node.js 18+
- npm
- React 18+
- Vite
- TailwindCSS
- react-leaflet & leaflet

---

## Run Backend
>>uvicorn main:app --host 127.0.0.1 --port 8000 --reload
Backend:
👉 http://127.0.0.1:8000

### Run Frontend
Open new terminal:
>>cd frontend
>>npm install
>>npm run dev

Frontend:
👉 http://127.0.0.1:5173




🤝 Contributing

Contributions, issues, and pull requests are welcome!
If you enhance agents, tools, UI, or architecture, please include documentation for maintainability.

📜 License

This project is licensed under the MIT License.
You are free to use, modify, and distribute with attribution.


