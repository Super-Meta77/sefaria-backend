# Neo4j Integration Guide

## Your Current Database Schema

Based on the screenshots provided, your Neo4j database contains:

### Nodes (727,309 total)
- **Author** - Torah scholars and commentators (e.g., Moses, Biblical authors)
- **Category** - Organizational categories (e.g., "Seder Nezikin")
- **Concept** - Abstract theological/philosophical concepts
- **Event** - Historical events
- **Text** - Text passages with Hebrew content
- **Tradition** - Jewish traditions (e.g., "Torah")
- **Version** - Different versions/editions of texts
- **Work** - Torah books and works (e.g., "Isaiah", "Tanakh")

### Relationships (1,258,688 total)
- **BELONGS_TO** - Hierarchical belonging
- **CITES** - Citation relationships
- **COMMENTARY_ON** - Commentary references
- **EXPLICIT** - Explicit textual connections
- **HAS_VERSION** - Version relationships
- **MEMBER_OF** - Membership in groups/categories
- **SUBCATEGORY_OF** - Category hierarchy
- **WRITTEN_BY** - Authorship

### Example Node Properties

**Author Node (Moses):**
```
<id>: 4:77e8e1c5-85ab-4696-be05-74d00c2a1d2f:727281
created_at: 2025-10-29T00:17:55.204Z
era: "Biblical Period"
name: "Moses"
updated_at: 2025-10-29T00:17:55.204Z
```

**Text Node (Malbim on Jeremiah):**
```
<id>: 4:77e8e1c5-85ab-4696-be05-74d00c2a1d2f:15
content_en: []
content_he: "<b>...Hebrew text...</b>"
id: "Malbim Beur Hamilot on Jeremiah 17:5:1"
```

**Tradition Node (Torah):**
```
<id>: 4:77e8e1c5-85ab-4696-be05-74d00c2a1d2f:727282
created_at: 2025-10-29T00:17:55.324Z
name: "Torah"
updated_at: 2025-10-29T00:17:55.324Z
```

**Work Node (Isaiah):**
```
<id>: 4:77e8e1c5-85ab-4696-be05-74d00c2a1d2f:726487
category: "Tanakh"
created_at: 2025-10-28T06:52:11.736Z
he_name: "ישעיה"
name: "Isaiah"
updated_at: 2025-10-28T06:52:11.736Z
```

---

## Configuration

### 1. Set Your Neo4j Credentials

Create a `.env` file in the `backend/` directory:

```bash
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_actual_password
```

### 2. Or Set Environment Variables

**Windows PowerShell:**
```powershell
$env:NEO4J_URI="bolt://localhost:7687"
$env:NEO4J_USER="neo4j"
$env:NEO4J_PASSWORD="your_password"
```

**Linux/Mac:**
```bash
export NEO4J_URI="bolt://localhost:7687"
export NEO4J_USER="neo4j"
export NEO4J_PASSWORD="your_password"
```

---

## Updated API Endpoints

### Get Connections

```bash
# Get all connections for a node (by <id> or internal ID)
curl "http://localhost:8000/api/connections/4:77e8e1c5-85ab-4696-be05-74d00c2a1d2f:727281"

# Filter by relationship type
curl "http://localhost:8000/api/connections/4:77e8e1c5-85ab-4696-be05-74d00c2a1d2f:727281?relationship_type=WRITTEN_BY"

# Available relationship types:
# - CITES
# - COMMENTARY_ON
# - EXPLICIT
# - BELONGS_TO
# - MEMBER_OF
# - SUBCATEGORY_OF
# - WRITTEN_BY
# - HAS_VERSION
```

### Get Graph Visualization Data

```bash
# Get graph data for D3.js visualization
curl "http://localhost:8000/api/connections/graph/4:77e8e1c5-85ab-4696-be05-74d00c2a1d2f:727282?depth=2"
```

Response includes:
```json
{
  "nodes": [
    {
      "id": "4:77e8e1c5-85ab-4696-be05-74d00c2a1d2f:727282",
      "title": "Torah",
      "type": "Tradition",
      "metadata": {
        "labels": ["Tradition"],
        "era": null
      }
    }
  ],
  "links": [
    {
      "source": "...",
      "target": "...",
      "type": "MEMBER_OF",
      "strength": 0.7
    }
  ]
}
```

---

## Example Cypher Queries

The backend now uses queries compatible with your schema:

### Find All Texts Related to Torah Tradition
```cypher
MATCH (t:Tradition {name: "Torah"})-[r:MEMBER_OF]-(w:Work)
RETURN t, r, w
LIMIT 50
```

### Find Commentary Chains
```cypher
MATCH (text:Text)-[:COMMENTARY_ON*1..3]->(original:Text)
WHERE text.id CONTAINS "Malbim"
RETURN text, original
LIMIT 20
```

### Find Author's Works
```cypher
MATCH (a:Author {name: "Moses"})-[:WRITTEN_BY]-(w:Work)
RETURN a, w
```

### Get Hierarchical Categories
```cypher
MATCH (child:Category)-[:SUBCATEGORY_OF*1..3]->(parent:Category)
WHERE parent.name = "Mishnah"
RETURN child, parent
```

---

## Testing the Integration

### 1. Test Connection
```bash
# Start the backend
cd backend
uvicorn main:app --reload
```

### 2. Check Health
```bash
curl http://localhost:8000/health
```

### 3. Test with Real Data

Using the Moses author node from your screenshot:
```bash
curl "http://localhost:8000/api/connections/4:77e8e1c5-85ab-4696-be05-74d00c2a1d2f:727281"
```

Using the Torah tradition node:
```bash
curl "http://localhost:8000/api/connections/4:77e8e1c5-85ab-4696-be05-74d00c2a1d2f:727282"
```

Using the Isaiah work node:
```bash
curl "http://localhost:8000/api/connections/4:77e8e1c5-85ab-4696-be05-74d00c2a1d2f:726487"
```

---

## Frontend Integration

Update your frontend to use the actual node IDs from your database:

```typescript
// components/ConnectionsModal.tsx
import { apiGet } from '@/lib/api-client';

async function fetchConnections(nodeId: string) {
  const data = await apiGet(`/api/connections/${encodeURIComponent(nodeId)}`);
  return data;
}

// Example usage with your actual IDs
const torahConnections = await fetchConnections(
  '4:77e8e1c5-85ab-4696-be05-74d00c2a1d2f:727282'
);
```

---

## Advanced Queries

### Get All Relationship Types
```cypher
MATCH ()-[r]->()
RETURN DISTINCT type(r) as relationship_type, count(*) as count
ORDER BY count DESC
```

### Get All Node Labels
```cypher
MATCH (n)
RETURN DISTINCT labels(n) as node_type, count(*) as count
ORDER BY count DESC
```

### Find Most Connected Nodes
```cypher
MATCH (n)
WITH n, size((n)-[]-()) as degree
WHERE degree > 10
RETURN n.name as name, labels(n) as type, degree
ORDER BY degree DESC
LIMIT 20
```

---

## Troubleshooting

### Connection Issues

If you see `ModuleNotFoundError: No module named 'neo4j'`:
```bash
pip install neo4j>=5.0.0
```

If you see connection errors:
1. Check Neo4j is running
2. Verify credentials in `.env` or environment variables
3. Check the URI (bolt:// vs neo4j://)
4. Ensure firewall allows port 7687

### Testing Connection Manually

```python
from neo4j import GraphDatabase

driver = GraphDatabase.driver(
    "bolt://localhost:7687",
    auth=("neo4j", "your_password")
)

with driver.session() as session:
    result = session.run("MATCH (n) RETURN count(n) as count")
    print(result.single()["count"])  # Should print 727309
```

---

## Next Steps

1. ✅ **Connection configured** - Update credentials in `.env`
2. ✅ **API endpoints updated** - Now query your actual schema
3. 🔄 **Test with real data** - Use actual node IDs from your database
4. 🔄 **Integrate with frontend** - Update ConnectionsModal, graph visualizations
5. 🔄 **Optimize queries** - Add indexes for performance

---

## Performance Optimization

### Create Indexes

```cypher
// Index on <id> property (your unique identifier)
CREATE INDEX node_id_index IF NOT EXISTS FOR (n) ON (n.`<id>`);

// Index on name property
CREATE INDEX node_name_index IF NOT EXISTS FOR (n) ON (n.name);

// Index on Work category
CREATE INDEX work_category_index IF NOT EXISTS FOR (w:Work) ON (w.category);
```

### Query Optimization Tips

1. Always use `LIMIT` to prevent large result sets
2. Use specific relationship types when possible
3. Index frequently queried properties
4. Use `EXPLAIN` and `PROFILE` to analyze query performance

---

Your backend is now fully configured to work with your existing Neo4j database! 🎉

