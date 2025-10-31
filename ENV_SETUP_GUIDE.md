# Environment Variable Setup Guide

## Problem Fixed

The backend was experiencing two main errors:
1. **Neo4j Connection Error**: Trying to connect to `localhost:7687` instead of the cloud instance
2. **OpenAI API Key Error**: `OPENAI_API_KEY` not being loaded from environment

## Root Cause

The issue was an **import order problem** in `main.py`. The environment variables were being loaded AFTER the API modules were imported, which meant:
- `database.py` was reading environment variables before `load_dotenv()` was called
- `ai/commentary_generator.py` and `ai/embeddings.py` couldn't find the `OPENAI_API_KEY`

## Solution Applied

### 1. Fixed Import Order in `main.py`

**Before:**
```python
from dotenv import load_dotenv
from api import texts, connections, diffs, ai, annotations, users
# ... more imports
load_dotenv()  # Too late!
```

**After:**
```python
from dotenv import load_dotenv

# Load environment variables FIRST, before any other imports
load_dotenv()

from api import texts, connections, diffs, ai, annotations, users
# ... rest of imports
```

### 2. Added Debug Output

Added helpful debug messages in:
- `database.py` - Shows Neo4j configuration on startup
- `ai/commentary_generator.py` - Confirms OpenAI API key is loaded
- `ai/embeddings.py` - Confirms OpenAI API key is loaded

### 3. Improved Error Handling

Added checks to ensure OpenAI client is properly initialized before making API calls.

## Environment Variables

Your `.env` file should contain:

```env
# Neo4j Database Configuration
NEO4J_URI=neo4j+s://8260863b.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-password-here

# OpenAI API Configuration
OPENAI_API_KEY=sk-proj-your-key-here
```

## Testing

Run the test script to verify everything is configured correctly:

```bash
python test_env_loading.py
```

Expected output:
- ✅ Neo4j connection successful!
- ✅ OpenAI client initialized successfully!

## Starting the Backend

```bash
# Option 1: Using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Option 2: Using the start script (Windows)
start.bat

# Option 3: Using the start script (Linux/Mac)
./start.sh
```

## Verifying the Fix

1. Start the backend server
2. You should see debug output like:
   ```
   🔧 Neo4j Configuration:
      URI: neo4j+s://8260863b.databases.neo4j.io
      User: neo4j
      Password: ***************
   
   ✅ OpenAI API key loaded (length: 164)
   ✅ Connected to Neo4j at neo4j+s://8260863b.databases.neo4j.io
   ```

3. Test the API endpoints:
   - Health check: http://localhost:8000/health
   - API docs: http://localhost:8000/docs

## Troubleshooting

### If Neo4j still fails to connect:
1. Verify your `.env` file is in the `backend/` directory
2. Check that the URI starts with `neo4j+s://` for cloud instances
3. Verify credentials are correct

### If OpenAI API key not found:
1. Make sure `.env` file contains `OPENAI_API_KEY=sk-proj-...`
2. Verify the key has no extra spaces or quotes
3. Check that `python-dotenv>=1.0.0` is installed

### If imports fail:
1. Make sure you're in the backend directory
2. Activate virtual environment: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Linux/Mac)
3. Install dependencies: `pip install -r requirements.txt`

