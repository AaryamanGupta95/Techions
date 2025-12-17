# Connected Intelligence Hub - Techions

**EY Techathon 6.0 Project**

An AI-powered automotive aftermarket management system that transforms reactive maintenance into proactive intelligence.

## 🚀 Live Demo

Visit the live application: [https://aaryamangupta95.github.io/Techions/](https://aaryamangupta95.github.io/Techions/)

## 📋 Overview

Connected Intelligence Hub is a comprehensive, agentic AI-powered platform that connects vehicle owners, service centers, and manufacturers in one intelligent ecosystem.

### Key Features

- **Proactive Maintenance Alerts**: AI monitors vehicle health 24/7 and alerts customers before breakdowns
- **Smart Service Scheduling**: Automatically assigns technicians based on specialization
- **Pre-Diagnosed Service Cases**: Technicians see predicted issues before vehicles arrive
- **Manufacturing Insights**: RCA/CAPA insights for quality improvement
- **Real-time Notifications**: Service completion alerts and maintenance reminders
- **Customer Reviews**: Rating system for service centers

## 🏗️ Architecture

### Tech Stack

**Frontend:**
- React 18
- Vite
- Tailwind CSS
- React Router
- Axios

**Backend:**
- FastAPI
- MongoDB
- Python 3.9+

**AI Agents:**
- Master-Worker Agent Pattern
- 8 Specialized AI Agents:
  1. Master Agent
  2. Telemetry Agent
  3. Failure Prediction Agent
  4. Customer Engagement Agent
  5. Smart Scheduling Agent
  6. Feedback Agent
  7. Manufacturing Insights Agent
  8. UEBA Security Agent

## 🚀 Getting Started

### Prerequisites

- Node.js 18+
- Python 3.9+
- MongoDB

### Installation

1. Clone the repository:
```bash
git clone https://github.com/AaryamanGupta95/Techions.git
cd Techions
```

2. **Backend Setup:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Frontend Setup:**
```bash
cd frontend
npm install
```

4. **Initialize Demo Data:**
```bash
cd backend
python scripts/init_demo_data.py
```

### Running Locally

**Backend:**
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm run dev
```

Visit `http://localhost:3000` to access the application.

## 👥 Demo Credentials

- **Customer**: `customer` / `password123`
- **Service Center**: `service_center` / `password123`
- **Manufacturing**: `manufacturing` / `password123`
- **Admin**: `admin` / `password123`

## 📊 Features by Role

### Customer
- Vehicle health monitoring
- Proactive maintenance alerts
- One-click service booking
- Service status tracking
- Service history
- Customer reviews

### Service Center
- Daily workload dashboard
- Pre-diagnosed service cases
- Smart appointment queue
- Technician management
- Service status updates
- Customer reviews dashboard

### Manufacturing
- Failure pattern analysis
- RCA/CAPA insights
- Production batch correlation
- Warranty risk indicators
- PDF report generation

### Admin
- System dashboard
- Agent monitoring
- Security event tracking
- Anomaly detection

## 🔒 Security

- Role-based access control (RBAC)
- UEBA (User and Entity Behavior Analytics)
- JWT authentication
- CORS protection

## 📝 License

This project was developed for EY Techathon 6.0.

## 👨‍💻 Author

Aaryaman Gupta

---

**Note**: The live GitHub Pages deployment shows the frontend interface. For full functionality, run the backend server locally.
