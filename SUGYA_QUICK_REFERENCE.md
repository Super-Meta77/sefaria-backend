# Sugya System - Quick Reference

## 🚀 Quick Start

### 1. Initialize Sugyot in Database
```bash
cd backend
python init_sugyot.py
```

### 2. Start Backend
```bash
uvicorn main:app --reload
```

### 3. Test API
```bash
python test_sugya_api.py
```

Or visit: http://localhost:8000/docs

---

## 📚 API Endpoints

### List All Sugyot
```bash
GET /api/sugya/list/available

Response:
{
  "sugyot": [
    {
      "ref": "Berakhot 2a",
      "title": "Time for Evening Shema",
      "normalized": "Berakhot_2a"
    },
    ...
  ],
  "total": 6
}
```

### Get Sugya Structure
```bash
GET /api/sugya/{ref}

Example: GET /api/sugya/Berakhot%202a

Response:
{
  "ref": "Berakhot 2a",
  "title": "Time for Evening Shema",
  "summary": "Discussion about the proper time...",
  "root": {
    "id": "Berakhot 2a-root",
    "type": "question",
    "label": "When do we recite evening Shema?",
    "sugyaLocation": "Berakhot 2a",
    "children": [...]
  }
}
```

---

## 💻 Code Examples

### Python (Backend)
```python
from api.sugya_manager import get_sugya_manager

manager = get_sugya_manager()

# List sugyot
sugyot = manager.list_all_sugyot()

# Get structure
structure = manager.get_sugya_structure("Berakhot 2a")

# Create new sugya
manager.create_sugya_node(
    "Berakhot 5a",
    "Suffering and Reward",
    "Summary..."
)
```

### TypeScript (Frontend)
```typescript
import { backendAPI } from "@/lib/backend-api"

// List sugyot
const { sugyot } = await backendAPI.getAvailableSugyot()

// Get structure
const structure = await backendAPI.getSugyaStructure("Berakhot 2a")
```

---

## 🗄️ Database Schema

### Sugya Node
```cypher
(:Sugya {
  ref: "Berakhot 2a",
  title: "Time for Evening Shema",
  summary: "Discussion about...",
  created_at: datetime(),
  updated_at: datetime()
})
```

### Relationships
```cypher
(s:Sugya)-[:CONTAINS_TEXT]->(t:Text)
```

---

## 🎨 Node Types

| Type | Hebrew | Color | Description |
|------|--------|-------|-------------|
| question | שאלה | Blue | Initial inquiry |
| answer | תשובה | Green | Response/teaching |
| kasha | קושיא | Yellow | Challenge/difficulty |
| terutz | תירוץ | Purple | Resolution |
| dispute | מחלוקת | Orange | Disagreement |
| teiku | תיקו | Gray | Unresolved |

---

## 🔧 Maintenance

### Add More Sugyot
Edit `init_sugyot.py` and add to `INITIAL_SUGYOT`:
```python
{
    "ref": "Berakhot 5a",
    "title": "Your Title",
    "summary": "Your summary"
}
```

Then run:
```bash
python init_sugyot.py
```

### Query Sugyot Directly
```cypher
// In Neo4j Browser
MATCH (s:Sugya)
RETURN s.ref, s.title
ORDER BY s.ref
```

---

## 📊 Statistics

- **Database**: 727,309 nodes, 1,258,688 relationships
- **Berakhot Texts**: 3,050+
- **Initialized Sugyot**: 6
- **Potential Sugyot**: 32+ (identified from Berakhot)

---

## 🐛 Troubleshooting

### "Sugya not found"
- Make sure you've run `init_sugyot.py`
- Check Neo4j connection in `.env`
- Verify sugya exists: `curl http://localhost:8000/api/sugya/list/available`

### Empty autocomplete
- Backend may not be running
- Check console for API errors
- Verify CORS is enabled

### Database connection error
- Check `backend/.env` has correct Neo4j credentials
- Verify Neo4j database is online
- Test with: `python -c "from database import get_driver; get_driver()"`

---

## 📖 References

- Full documentation: `SUGYA_SYSTEM_COMPLETE.md`
- Manager code: `api/sugya_manager.py`
- API routes: `api/sugya.py`
- Frontend: `components/sidebar/tabs/SugyaMapTab.tsx`

