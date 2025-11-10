# Engine 1: Dynamic Intertextual Graph Engine 🔗

## Overview

The **Dynamic Intertextual Graph Engine** is the core feature that enables exploration of connections and relationships between texts in the Sefaria corpus. It provides real-time graph traversal and visualization powered by Neo4j.

### Key Features
- ✅ Multi-hop graph traversal (1-3 degrees of separation)
- ✅ Relationship type filtering
- ✅ Real-time queries against 727K+ nodes and 1.2M+ relationships
- ✅ Interactive graph visualization
- ✅ Export capabilities
- ✅ Dynamic filtering and exploration

---

## Architecture

```
Frontend (Next.js)                  Backend (FastAPI)                   Database (Neo4j)
┌──────────────────┐               ┌────────────────────┐              ┌──────────────────┐
│                  │               │                    │              │                  │
│  Graph Explorer  │──────────────▶│  /api/connections  │─────────────▶│  727K+ Nodes     │
│  Page            │               │  - GET /{node_id}  │              │  1.2M+ Relations │
│                  │               │  - GET /graph/..   │              │                  │
│  Interactive     │◀──────────────│  - GET /stats      │◀─────────────│  Cypher Queries  │
│  Graph Component │               │                    │              │                  │
└──────────────────┘               └────────────────────┘              └──────────────────┘
```

---

## API Endpoints

### 1. Get Direct Connections

**Endpoint:** `GET /api/connections/{node_id}`

Get direct connections for a specific node.

**Parameters:**
- `node_id` (path): Node ID to query
- `relationship_type` (query, optional): Filter by relationship type
- `limit` (query, optional): Maximum results (default: 100)

**Example Request:**
```bash
curl "http://localhost:8000/api/connections/Genesis%201:1?limit=50"
```

**Example Response:**
```json
[
  {
    "source": "Genesis 1:1",
    "target": "Rashi on Genesis 1:1",
    "type": "COMMENTARY_ON",
    "strength": 0.8,
    "metadata": {
      "target_name": "Rashi on Genesis 1:1",
      "target_labels": ["Commentary"]
    }
  }
]
```

---

### 2. Get Graph Data for Visualization

**Endpoint:** `GET /api/connections/graph/{node_id}`

Get full graph data including multi-hop traversal.

**Parameters:**
- `node_id` (path): Starting node ID
- `depth` (query, optional): Traversal depth 1-3 (default: 2)
- `relationship_type` (query, optional): Filter by relationship type
- `limit` (query, optional): Maximum results (default: 200)

**Example Request:**
```bash
curl "http://localhost:8000/api/connections/graph/Genesis%201:1?depth=2&relationship_type=CITES"
```

**Example Response:**
```json
{
  "nodes": [
    {
      "id": "Genesis 1:1",
      "title": "Genesis 1:1",
      "type": "Text",
      "snippet": "In the beginning God created...",
      "metadata": {
        "labels": ["Text", "Torah"],
        "era": "Tannaitic"
      }
    }
  ],
  "links": [
    {
      "source": "Genesis 1:1",
      "target": "Rashi on Genesis 1:1",
      "type": "COMMENTARY_ON",
      "strength": 0.7
    }
  ],
  "stats": {
    "total_nodes": 15,
    "total_links": 28,
    "depth": 2,
    "relationship_types": ["COMMENTARY_ON", "CITES", "EXPLICIT"]
  }
}
```

---

### 3. Get Available Relationship Types

**Endpoint:** `GET /api/connections/relationship-types`

Get all relationship types available in the database.

**Example Request:**
```bash
curl "http://localhost:8000/api/connections/relationship-types"
```

**Example Response:**
```json
{
  "relationship_types": [
    "BELONGS_TO",
    "CITES",
    "COMMENTARY_ON",
    "EXPLICIT",
    "MEMBER_OF"
  ],
  "total": 5
}
```

---

### 4. Get Graph Statistics

**Endpoint:** `GET /api/connections/stats`

Get overall statistics about the graph database.

**Example Request:**
```bash
curl "http://localhost:8000/api/connections/stats"
```

**Example Response:**
```json
{
  "nodes": {
    "total": 727309,
    "labels": ["Text", "Author", "Commentary", "Collection"],
    "label_count": 4
  },
  "relationships": {
    "total": 1258688,
    "types": ["CITES", "COMMENTARY_ON", "BELONGS_TO", "MEMBER_OF"],
    "type_count": 4
  }
}
```

---

## Frontend Integration

### Using the Graph Explorer Page

Navigate to `/explore/graph` to access the interactive graph explorer.

**Features:**
- Search for any node by ID or reference
- Adjust traversal depth (1-3 hops)
- Filter by relationship type
- Interactive D3.js visualization
- Export graph data as JSON

### Using the API Client

```typescript
import { backendAPI } from '@/lib/backend-api'

// Get graph data
const graphData = await backendAPI.getGraphData(
  'Genesis 1:1',  // node ID
  2,              // depth
  'CITES'         // relationship type (optional)
)

console.log(graphData.nodes)  // Array of nodes
console.log(graphData.links)  // Array of connections
console.log(graphData.stats)  // Graph statistics
```

### Using the Interactive Graph Component

```tsx
import InteractiveGraph from '@/components/InteractiveGraph'

function MyComponent() {
  const [graphData, setGraphData] = useState({ nodes: [], links: [] })
  
  const handleNodeClick = (node) => {
    console.log('Clicked node:', node)
    // Load connections for clicked node
  }
  
  return (
    <InteractiveGraph
      data={graphData}
      onNodeClick={handleNodeClick}
      onClose={() => {}}
    />
  )
}
```

---

## Common Relationship Types

| Type | Description | Example |
|------|-------------|---------|
| `CITES` | One text cites another | Talmud → Mishnah |
| `COMMENTARY_ON` | Commentary relationship | Rashi → Torah |
| `EXPLICIT` | Explicit reference | Text A → Text B |
| `BELONGS_TO` | Collection membership | Chapter → Book |
| `MEMBER_OF` | Category membership | Text → Category |

---

## Query Examples

### Find All Commentary on a Text

```python
# Backend Cypher query
query = """
MATCH (text)-[r:COMMENTARY_ON]-(commentary)
WHERE text.`<id>` = $node_id
RETURN commentary
"""
```

### Multi-Hop Citation Chain

```python
# Find texts citing texts that cite the source
query = """
MATCH path = (source)-[:CITES*1..3]->(target)
WHERE source.`<id>` = $node_id
RETURN path
"""
```

### Get All Texts by Era

```python
query = """
MATCH (n:Text)
WHERE n.era = 'Amoraic'
RETURN n
LIMIT 100
"""
```

---

## Performance Considerations

### Optimization Tips

1. **Limit Depth**: Use depth=1 or 2 for faster queries
2. **Filter by Type**: Specify relationship_type to reduce results
3. **Set Reasonable Limits**: Use limit parameter to avoid large result sets
4. **Use Indexes**: Ensure Neo4j indexes are created on commonly queried properties

### Neo4j Indexes

Recommended indexes for optimal performance:

```cypher
-- Index on node IDs
CREATE INDEX text_id_index IF NOT EXISTS
FOR (t:Text) ON (t.`<id>`);

-- Index on node names
CREATE INDEX text_name_index IF NOT EXISTS
FOR (t:Text) ON (t.name);

-- Index on era for filtering
CREATE INDEX text_era_index IF NOT EXISTS
FOR (t:Text) ON (t.era);
```

---

## Troubleshooting

### Common Issues

#### 1. "No graph data found for node"

**Cause:** Node ID doesn't exist or has no connections

**Solution:**
- Verify node ID format (e.g., "Genesis 1:1" not "Genesis.1.1")
- Check if node exists in Neo4j database
- Try example nodes: "Berakhot 2a", "Genesis 1:1"

#### 2. Slow Query Performance

**Cause:** Too many hops or large result set

**Solution:**
- Reduce depth parameter (use 1 or 2 instead of 3)
- Add relationship_type filter
- Reduce limit parameter
- Ensure Neo4j indexes are created

#### 3. Frontend Connection Error

**Cause:** Backend not running or CORS issue

**Solution:**
- Verify backend is running: `http://localhost:8000/health`
- Check CORS settings in `backend/main.py`
- Verify `NEXT_PUBLIC_API_URL` environment variable

---

## Development

### Running the Backend

```bash
cd backend
python -m uvicorn main:app --reload
```

Access API docs: http://localhost:8000/docs

### Running the Frontend

```bash
npm run dev
```

Access Graph Explorer: http://localhost:3000/explore/graph

### Testing the API

```bash
# Test connection endpoint
curl http://localhost:8000/api/connections/Genesis%201:1

# Test graph endpoint
curl "http://localhost:8000/api/connections/graph/Genesis%201:1?depth=2"

# Test stats
curl http://localhost:8000/api/connections/stats
```

---

## Future Enhancements

### Planned Features
- [ ] Saved graph views
- [ ] Graph annotations
- [ ] Collaborative filtering
- [ ] Advanced path finding algorithms
- [ ] Graph analytics (centrality, clustering)
- [ ] Real-time graph updates
- [ ] Graph comparison views
- [ ] Export to various formats (GraphML, GEXF)

### API Extensions
- [ ] POST endpoints for graph mutations
- [ ] Batch query support
- [ ] GraphQL interface
- [ ] WebSocket support for real-time updates

---

## Related Documentation

- [Neo4j Integration Guide](./NEO4J_INTEGRATION.md)
- [Backend API Documentation](./README.md)
- [Frontend Integration Guide](../FRONTEND_INTEGRATION.md)
- [AI Features Documentation](./AI_FEATURES_READY.md)

---

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review API documentation at `/docs`
3. Examine Neo4j database directly
4. Check backend logs for errors

---

**Engine Status:** ✅ **Fully Operational**

Last Updated: November 2025

