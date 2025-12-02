# Parking Management System

## 📁 Project Structure

```
parking/
├── python/              # FastAPI Backend
│   ├── main.py
│   ├── app.py
│   ├── requirements.txt
│   ├── controllers/
│   ├── models/
│   └── utils/
│
├── frontend/            # React Frontend
│   ├── src/
│   ├── public/
│   └── package.json
│
└── package.json         # Root configuration
```

## 🚀 Installation

### Install All Dependencies
```bash
npm run install:all
```

Or install separately:

### Install Python Backend
```bash
npm run install:python
# or manually:
cd python
pip install -r requirements.txt
```

### Install Frontend
```bash
npm run install:frontend
# or manually:
cd frontend
npm install
```

## 💻 Development

### Run Python Backend (Port 3001)
```bash
npm run dev
# or manually:
cd python
python main.py
```

### Run Frontend (Port 5173)
```bash
npm run dev:frontend
# or manually:
cd frontend
npm run dev
```

## 🏗️ Build & Deploy

### Build Frontend
```bash
npm run build:ui
```

### Deploy to Render
```bash
npm run deploy:render
```

This will:
1. Build the frontend
2. Add changes to git
3. Commit with message "Deploy to Render"
4. Push to repository

## 🌐 Deployment

### Render.com (Recommended)

The project includes `render.yaml` for automatic deployment:

1. **Backend Service:**
   - Type: Web Service
   - Runtime: Python 3.11
   - Build: `pip install -r python/requirements.txt`
   - Start: `cd python && uvicorn main:app --host 0.0.0.0 --port $PORT`

2. **Frontend Service:**
   - Type: Static Site
   - Build: `cd frontend && npm install && npm run build`
   - Publish: `frontend/dist`

### Manual Deployment

#### Backend
```bash
cd python
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 3001
```

#### Frontend
```bash
cd frontend
npm install
npm run build
# Serve the dist folder with any static server
```

## 🔧 Environment Variables

### Python Backend (.env in python/)
```env
MONGODB_URI=mongodb+srv://...
PORT=3001
NODE_ENV=production
```

### Frontend (.env in frontend/)
```env
VITE_API_URL=http://localhost:3001/api
```

## 📝 Available Scripts

| Command | Description |
|---------|-------------|
| `npm run start` | Run Python backend in production |
| `npm run dev` | Run Python backend in development |
| `npm run dev:frontend` | Run React frontend |
| `npm run install:python` | Install Python dependencies |
| `npm run install:frontend` | Install Frontend dependencies |
| `npm run install:all` | Install all dependencies |
| `npm run build:ui` | Build frontend for production |
| `npm run deploy:render` | Build & deploy to Render |

## 🛠️ Tech Stack

### Backend
- FastAPI 0.115.0
- Motor 3.6.0 (Async MongoDB)
- Pydantic 2.10.0
- Uvicorn (ASGI Server)

### Frontend
- React 19.1.1
- Vite 5.0
- TailwindCSS 4.1
- Axios 1.12.2

### Database
- MongoDB Atlas

## 📚 Documentation

- Backend API Docs: `http://localhost:3001/docs` (Swagger)
- Backend API Docs: `http://localhost:3001/redoc` (ReDoc)
- Frontend: `http://localhost:5173`

## ⚡ Quick Start

```bash
# 1. Clone repository
git clone <repository-url>
cd parking

# 2. Install dependencies
npm run install:all

# 3. Configure environment
cp python/.env.example python/.env
# Edit python/.env with your MongoDB URI

# 4. Run backend
npm run dev

# 5. Run frontend (in another terminal)
npm run dev:frontend
```

## 🚢 Production Deployment Checklist

- [ ] Set `MONGODB_URI` in Render environment variables
- [ ] Set `PORT` to `$PORT` in Render (auto-assigned)
- [ ] Set `NODE_ENV` to `production`
- [ ] Update `VITE_API_URL` in frontend to production backend URL
- [ ] Build frontend: `npm run build:ui`
- [ ] Deploy: `npm run deploy:render`

## 📄 License

MIT
