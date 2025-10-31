# Quick Start Guide - Backend with Environment Variables

## ✅ Problem Fixed!

Your backend now correctly loads environment variables from the `.env` file using `python-dotenv`.

## 🚀 Starting the Backend

### Windows (PowerShell):
```powershell
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Linux/Mac:
```bash
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Using the provided scripts:
```bash
# Windows
cd backend
start.bat

# Linux/Mac
cd backend
./start.sh
```

## ✔️ Verify Setup First

Before starting the server, verify your configuration:

```bash
cd backend
python test_env_loading.py
```

**Expected output:**
- ✅ Neo4j connection successful!
- ✅ OpenAI client initialized successfully!

## 🔍 What to Look For

When the server starts correctly, you should see:

```
🔧 Neo4j Configuration:
   URI: neo4j+s://8260863b.databases.neo4j.io
   User: neo4j
   Password: *******************************************

✅ OpenAI API key loaded (length: 164)
✅ Connected to Neo4j at neo4j+s://8260863b.databases.neo4j.io

INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx] using StatReload
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

## 🌐 Access the API

Once running:

- **API Documentation:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health
- **Root Info:** http://localhost:8000/

## 🧪 Test the Endpoints

### 1. Health Check
```bash
curl http://localhost:8000/health
# Should return: {"status":"healthy","service":"sefaria-backend"}
```

### 2. API Root
```bash
curl http://localhost:8000/
# Should return API information and available endpoints
```

### 3. Test AI Commentary (requires OPENAI_API_KEY)
Visit: http://localhost:8000/docs and try:
- `/api/ai-enhanced/commentary/{text_ref}`

### 4. Test Neo4j Connections
Visit: http://localhost:8000/docs and try:
- `/api/connections/{node_id}`

## ⚙️ Environment Variables

Your `.env` file location: `backend/.env`

Required variables:
```env
NEO4J_URI=neo4j+s://8260863b.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-password-here
OPENAI_API_KEY=sk-proj-your-key-here
```

## 🐛 Troubleshooting

### If you see "localhost:7687" error:
- ❌ Environment variables not loaded
- ✅ Solution: Make sure `.env` file exists in `backend/` directory

### If you see "OPENAI_API_KEY required" error:
- ❌ OpenAI key not loaded
- ✅ Solution: Verify `OPENAI_API_KEY=sk-proj-...` in `.env` file

### If imports fail:
```bash
# Activate virtual environment first
cd backend
.\venv\Scripts\activate  # Windows
source venv/bin/activate # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

## 📚 Documentation Files

- `ENV_SETUP_GUIDE.md` - Detailed setup guide
- `ENVIRONMENT_FIX_SUMMARY.md` - Complete fix documentation
- `QUICK_START.md` - This file
- `test_env_loading.py` - Configuration test script

## 🎯 Next Steps

1. ✅ Run `python test_env_loading.py` to verify configuration
2. ✅ Start the backend: `python -m uvicorn main:app --reload`
3. ✅ Visit http://localhost:8000/docs to explore the API
4. ✅ Test the endpoints you need

## 💡 Tips

- Use `--reload` flag during development for auto-reload on code changes
- Check the console output for debug messages about loaded config
- Use the `/docs` endpoint to test all API endpoints interactively
- The API supports CORS for frontend integration (ports 3000, 3001)
