# How to Start the Backend Server

## ⚠️ IMPORTANT: You must be in the `backend/` directory!

### ❌ WRONG - From project root:
```powershell
# This will NOT work:
PS D:\Project\Sefaria\sefaria-frontend> python -m uvicorn main:app --reload
ERROR: Error loading ASGI app. Could not import module "main".
```

### ✅ CORRECT - From backend directory:

```powershell
# Navigate to backend directory first
cd backend

# Then start the server
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Step-by-Step Instructions

### 1. Open PowerShell/Terminal

### 2. Navigate to backend directory:
```powershell
cd D:\Project\Sefaria\sefaria-frontend\backend
```

### 3. (Optional) Verify you're in the right place:
```powershell
# You should see main.py in the current directory
dir main.py
```

### 4. (Optional) Test environment variables:
```powershell
python test_env_loading.py
```

Expected output:
```
✅ Neo4j connection successful!
✅ OpenAI client initialized successfully!
```

### 5. Start the server:
```powershell
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 6. Verify it's running:

You should see:
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

### 7. Test the API:

Open your browser to:
- **API Documentation:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

## Quick Command Reference

```powershell
# From anywhere, navigate to backend:
cd D:\Project\Sefaria\sefaria-frontend\backend

# Test configuration:
python test_env_loading.py

# Start server (development mode with auto-reload):
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Start server (production mode):
python -m uvicorn main:app --host 0.0.0.0 --port 8000

# Stop server:
# Press Ctrl+C in the terminal
```

## Using the Batch File (Windows)

Alternatively, you can use the provided batch file:

```powershell
cd D:\Project\Sefaria\sefaria-frontend\backend
.\start.bat
```

## Troubleshooting

### "Could not import module 'main'"
- ❌ You're in the wrong directory
- ✅ Solution: `cd backend` first

### "Module not found" errors
- ❌ Dependencies not installed or venv not activated
- ✅ Solution: 
  ```powershell
  cd backend
  .\venv\Scripts\activate
  pip install -r requirements.txt
  ```

### "OPENAI_API_KEY not found"
- ❌ `.env` file missing or incorrect
- ✅ Solution: Verify `backend\.env` exists with your API key

### Port already in use
- ❌ Another process using port 8000
- ✅ Solution: Use a different port:
  ```powershell
  python -m uvicorn main:app --reload --port 8001
  ```

## All Environment Variables Configured

All backend files now properly use environment variables from `.env`:

✅ `main.py` - Loads `.env` before all imports
✅ `database.py` - Uses NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
✅ `ai/commentary_generator.py` - Uses OPENAI_API_KEY
✅ `ai/embeddings.py` - Uses OPENAI_API_KEY
✅ `scripts/embed_texts.py` - Uses OPENAI_API_KEY
✅ `scripts/test_ai_features.py` - Uses OPENAI_API_KEY

