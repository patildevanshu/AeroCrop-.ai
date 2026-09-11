# AeroCrop.ai — Deployment Guide

This guide details how to deploy **AeroCrop.ai** cleanly and reliably across different environments.

---

## 1. Single-Command Docker Deployment (Recommended)

AeroCrop includes a multi-stage `Dockerfile` that builds the React frontend, packages Python dependencies, and serves both via high-performance Uvicorn.

### With Docker Compose (FastAPI + Optional Email Microservice)
```bash
# Build and run both containers in background
docker compose up -d --build
```
- Web Application & API: `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/api/health`

### With Standalone Docker
```bash
# Build the image
docker build -t aerocrop:latest .

# Run the container
docker run -d -p 8000:8000 \
  -v aerocrop_data:/app/data \
  -v aerocrop_uploads:/app/uploads \
  --name aerocrop aerocrop:latest
```

---

## 2. Deploying on Oracle Cloud Free Tier A1 (ARM64) via Coolify

AeroCrop.ai is natively optimized for Oracle Cloud Free Tier Ampere A1 instances (**ARM64 / aarch64**, 2 OCPU / 4 vCPUs, 12 GB RAM).

### Architecture Compatibility
- **PyTorch**: Native Linux `aarch64` PyTorch wheels with multi-threaded CPU tensor execution.
- **Database**: MongoDB 7.0 with native ARMv8.2-A LSE instruction set support.
- **Node.js**: Multi-stage `node:20-alpine` frontend build with zero compilation overhead.
- **RAM Footprint**: ~1.5 GB total runtime memory across all 4 services (well within the 12 GB allocation).

### Prerequisites on Oracle Cloud
1. In Oracle Cloud Console, navigate to **Compute > Instances > [Your Instance]**.
2. Under **Virtual Cloud Network > Security Lists**, add Ingress Rules:
   - Port `80` (HTTP)
   - Port `443` (HTTPS)
   - Port `8000` (Coolify dashboard / Direct API access)
3. Open firewall in the VPS instance (Ubuntu/Debian):
   ```bash
   sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 80 -j ACCEPT
   sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 443 -j ACCEPT
   sudo netfilter-persistent save
   ```

### Coolify Setup (1-Click Docker Compose)
1. In your Coolify dashboard, create a **New Project** and select **Docker Compose**.
2. Select your connected GitHub repository: `patildevanshu/AeroCrop-.ai` (branch `main`).
3. Coolify will automatically detect the root [`docker-compose.yml`](file:///d:/Codes/final_year_project/docker-compose.yml).
4. Configure **Environment Variables** in the Coolify UI:
   ```env
   # Security
   JWT_SECRET_KEY=generate-a-strong-random-secret-key
   CORS_ORIGINS=https://your-domain.com,http://localhost:8000

   # Agronomic Validator (Optional vision cross-verification)
   VALIDATOR_API_KEY=your_vision_api_key_here
   VALIDATOR_MODEL=gemini-3.1-flash-lite-preview

   # Farmer Email Dispatch
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=465
   SMTP_SECURE=true
   EMAIL_USER=your_email@gmail.com
   EMAIL_PASS=your_gmail_app_password
   ```
5. Set your domain name in Coolify for the `aerocrop` service (e.g. `https://aerocrop.yourdomain.com`).
6. Click **Deploy**. Coolify will pull the repo, build all containers on ARM64, attach Let's Encrypt SSL, and start the platform.

---

## 3. Alternative: Direct Native Host on ARM64 VPS (No Docker)

If you prefer to run the services directly on the host without containers:

```bash
# 1. System packages
sudo apt update && sudo apt install -y python3-pip python3-venv nodejs npm git

# 2. Clone repository
git clone https://github.com/patildevanshu/AeroCrop-.ai.git
cd AeroCrop-.ai

# 3. Build React Frontend
cd frontend && npm install && npm run build && cd ..

# 4. Setup Python Virtual Environment
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 5. Run MongoDB (via native apt package)
sudo apt install -y mongodb-org
sudo systemctl enable --now mongod

# 6. Run Email Service
cd backend/email_service && npm install && node server.js &
cd ../..

# 7. Run Validator Service
cd validator_service && pip install -r requirements.txt && python3 server.py &
cd ..

# 8. Start AeroCrop Backend (serves Frontend + API together)
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

---

## 4. Local Development

### Option A: Unified FastAPI Server
```bash
# 1. Build frontend once
cd frontend && npm install && npm run build && cd ..

# 2. Start FastAPI (serves React frontend + APIs together)
uvicorn backend.main:app --reload --port 8000
```

### Option B: Decoupled Hot-Reload Dev
- Terminal 1 (Backend API):
  ```bash
  uvicorn backend.main:app --reload --port 8000
  ```
- Terminal 2 (React Vite HMR):
  ```bash
  cd frontend && npm run dev
  ```
  *(Vite proxies `/api` and `/uploads` requests automatically to `http://127.0.0.1:8000`)*
- Terminal 3 (Optional Email Service):
  ```bash
  cd backend/email_service && npm start
  ```

---

## 5. Directory Layout Reference

```
├── backend/            # FastAPI, controllers, services, database, microservices
├── frontend/           # React + TypeScript Vite dashboard + legacy views
├── model/              # PyTorch MultiModal network architecture & inference
├── data/               # Persistent database storage
├── uploads/            # Persistent media uploads
├── tests/              # Pytest test suite
├── Dockerfile          # Production multi-stage Docker build
└── docker-compose.yml  # Multi-container orchestration
```
