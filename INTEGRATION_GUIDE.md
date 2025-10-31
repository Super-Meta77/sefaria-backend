# Backend-Frontend Integration Guide

This document explains how to integrate the FastAPI backend with your Next.js frontend for the advanced Sefaria platform.

## Table of Contents
1. [Quick Start](#quick-start)
2. [API Endpoints Reference](#api-endpoints-reference)
3. [Frontend Integration Examples](#frontend-integration-examples)
4. [Data Flow](#data-flow)
5. [Error Handling](#error-handling)

---

## Quick Start

### 1. Start the Backend

```bash
cd backend
source venv/bin/activate  # Windows: .\venv\Scripts\activate
uvicorn backend.main:app --reload --port 8000
```

Backend will be available at: `http://localhost:8000`
- Swagger docs: `http://localhost:8000/docs`
- API root: `http://localhost:8000/api/`

### 2. Configure Frontend

Update your frontend API configuration (create `lib/api-client.ts` if not exists):

```typescript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function apiGet<T>(endpoint: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${endpoint}`);
  if (!response.ok) {
    throw new Error(`API Error: ${response.statusText}`);
  }
  return response.json();
}

export async function apiPost<T>(endpoint: string, data: any): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    throw new Error(`API Error: ${response.statusText}`);
  }
  return response.json();
}
```

---

## API Endpoints Reference

### 1. Dynamic Intertextual Graph Engine

#### Get Connections for a Node
```typescript
// GET /api/connections/{node_id}?genre=halakhic&author=Rashi&limit=50

interface Connection {
  source: string;
  target: string;
  type: string;
  strength: number;
  metadata: Record<string, any>;
}

const connections = await apiGet<Connection[]>(
  '/api/connections/Genesis_1_1?genre=halakhic'
);
```

#### Get Full Graph Data
```typescript
// GET /api/connections/graph/{node_id}?depth=2

interface GraphData {
  nodes: Array<{
    id: string;
    title: string;
    type: string;
    metadata: { genre?: string; author?: string; era?: string };
  }>;
  links: Array<{
    source: string;
    target: string;
    type: string;
    strength: number;
  }>;
}

const graphData = await apiGet<GraphData>(
  '/api/connections/graph/Genesis_1_1?depth=2'
);
```

### 2. Textual Topology Engine

#### Get Manuscript Versions
```typescript
// GET /api/manuscripts/{ref}

interface Manuscript {
  id: string;
  name: string;
  source: string;
  date?: string;
  location?: string;
  segments: Array<{
    id: string;
    text: string;
    translation?: string;
    footnotes: Array<{ id: string; text: string }>;
    changes: Array<{ type: string; position: number; text: string; note?: string }>;
  }>;
}

const manuscripts = await apiGet<Manuscript[]>('/api/manuscripts/Genesis_1');
```

#### Compare Manuscripts
```typescript
// GET /api/manuscripts/compare/{ref}?primary=vilna&alternate=aleppo

const comparison = await apiGet('/api/manuscripts/compare/Genesis_1?primary=vilna&alternate=aleppo');
```

### 3. Dialectic Mapping & Sugya Structure

#### Get Sugya Structure
```typescript
// GET /api/sugya/{ref}

interface SugyaNode {
  id: string;
  type: 'question' | 'answer' | 'kasha' | 'terutz' | 'teiku' | 'dispute' | 'resolution';
  label: string;
  sugyaLocation: string;
  children: SugyaNode[];
}

interface SugyaStructure {
  ref: string;
  title: string;
  root: SugyaNode;
  summary: string;
}

const sugya = await apiGet<SugyaStructure>('/api/sugya/Berakhot_2a');
```

### 4. Psak Lineage Tracer

#### Get Psak Chain
```typescript
// GET /api/psak/{ruling_ref}

interface PsakNode {
  id: string;
  source: string;
  text: string;
  era: string;
  year: number;
  type: 'source' | 'interpretation' | 'analysis' | 'codification' | 'final_ruling';
  author?: string;
  ref?: string;
}

interface PsakLineage {
  ruling_ref: string;
  title: string;
  chain: PsakNode[];
}

const lineage = await apiGet<PsakLineage>('/api/psak/OC_1:1');
```

### 5. AI-Assisted Commentarial Layering

#### Get AI Commentary
```typescript
// POST /api/ai/commentary/

interface AICommentaryRequest {
  text_ref: string;
  tradition: 'Rashi' | 'Ramban' | 'Maharal';
  mode: 'pshat' | 'halakhah' | 'mystical';
}

interface AICommentary {
  text_ref: string;
  tradition: string;
  mode: string;
  generated: string;
}

const commentary = await apiPost<AICommentary>('/api/ai/commentary/', {
  text_ref: 'Genesis.1.1',
  tradition: 'Rashi',
  mode: 'pshat'
});
```

### 6. Author Map

#### Get Author Network
```typescript
// GET /api/author-map/?tradition=Ashkenaz&school=mystical

interface Author {
  id: string;
  name: string;
  hebrew_name?: string;
  birth_year?: number;
  death_year?: number;
  location?: string;
  tradition: string;
  school: string;
  works: string[];
}

interface AuthorMapData {
  authors: Author[];
  relations: Array<{
    source: string;
    target: string;
    type: string;
    strength: number;
  }>;
  time_range: { min: number; max: number };
}

const authorMap = await apiGet<AuthorMapData>('/api/author-map/?tradition=Ashkenaz');
```

### 7. Concepts Index

#### Search Concepts
```typescript
// GET /api/concepts/search/?query=chesed&tradition=Hasidic

interface ConceptSearchResult {
  concept: {
    id: string;
    name: string;
    hebrew_name: string;
    description: string;
    category: string;
    references: Array<{
      ref: string;
      text: string;
      author?: string;
      tradition: string;
      excerpt: string;
    }>;
  };
  relevance: number;
}

const results = await apiGet<ConceptSearchResult[]>(
  '/api/concepts/search/?query=chesed&tradition=Hasidic'
);
```

### 8. Lexical Hypergraph

#### Get Semantic Drift
```typescript
// GET /api/lexical/{term}

interface SemanticDriftData {
  term: string;
  hebrew_term: string;
  nodes: Array<{
    id: string;
    term: string;
    hebrew_term: string;
    era: string;
    meaning: string;
    corpus: string;
    sources: string[];
    frequency: number;
  }>;
  links: Array<{
    source: string;
    target: string;
    similarity: number;
    drift_type: string;
  }>;
  drift_summary: string;
}

const drift = await apiGet<SemanticDriftData>('/api/lexical/chesed');
```

### 9. Annotations

#### Get Annotations for Text
```typescript
// GET /api/annotations/{text_ref}

interface Annotation {
  text_ref: string;
  user: string;
  layer?: string;
  content: string;
  selection?: string;
  type?: string;
}

const annotations = await apiGet<Annotation[]>('/api/annotations/Genesis.1.1');
```

#### Add Annotation
```typescript
// POST /api/annotations/

const newAnnotation = await apiPost<Annotation>('/api/annotations/', {
  text_ref: 'Genesis.1.1',
  user: 'username',
  content: 'This is my annotation',
  type: 'comment'
});
```

### 10. Calendar Integration

#### Get Today's Learning
```typescript
// GET /api/calendar/today/

interface CalendarItem {
  type: 'daf_yomi' | 'parsha' | 'haftara' | 'rambam' | 'fast' | 'holiday';
  title: string;
  ref: string;
  description?: string;
  url?: string;
}

interface DaySchedule {
  date: string;
  jewish_date: string;
  items: CalendarItem[];
}

const today = await apiGet<DaySchedule>('/api/calendar/today/');
```

---

## Frontend Integration Examples

### Example 1: ConnectionsModal Integration

Update your `components/modals/ConnectionsModal.tsx`:

```typescript
import { useEffect, useState } from 'react';
import { apiGet } from '@/lib/api-client';

export function ConnectionsModal({ nodeId }: { nodeId: string }) {
  const [graphData, setGraphData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchConnections() {
      try {
        const data = await apiGet(`/api/connections/graph/${nodeId}?depth=2`);
        setGraphData(data);
      } catch (error) {
        console.error('Failed to fetch connections:', error);
      } finally {
        setLoading(false);
      }
    }
    
    if (nodeId) {
      fetchConnections();
    }
  }, [nodeId]);

  if (loading) return <div>Loading...</div>;
  
  return <D3Graph data={graphData} />;
}
```

### Example 2: Calendar Integration

Update your `components/CalendarDrawer.tsx`:

```typescript
import { useEffect, useState } from 'react';
import { apiGet } from '@/lib/api-client';

export function CalendarDrawer() {
  const [schedule, setSchedule] = useState(null);

  useEffect(() => {
    async function fetchTodaySchedule() {
      const data = await apiGet('/api/calendar/today/');
      setSchedule(data);
    }
    fetchTodaySchedule();
  }, []);

  return (
    <div>
      <h3>{schedule?.jewish_date}</h3>
      {schedule?.items.map(item => (
        <div key={item.ref}>
          <h4>{item.title}</h4>
          <a href={item.url}>{item.ref}</a>
        </div>
      ))}
    </div>
  );
}
```

### Example 3: AI Commentary Integration

```typescript
async function fetchAICommentary(textRef: string, tradition: string, mode: string) {
  const commentary = await apiPost('/api/ai/commentary/', {
    text_ref: textRef,
    tradition,
    mode
  });
  
  return commentary.generated;
}

// Usage in component
const [commentary, setCommentary] = useState('');

const handleGetCommentary = async () => {
  const result = await fetchAICommentary('Genesis.1.1', 'Rashi', 'pshat');
  setCommentary(result);
};
```

---

## Data Flow

```
Frontend (Next.js)
    ↓
API Client (fetch/axios)
    ↓
Backend API (FastAPI) - http://localhost:8000/api/*
    ↓
├─ Neo4j (Graph connections)
├─ Text Database (Manuscripts, texts)
├─ AI/NLP Services (Commentary generation)
└─ Calendar Services (Hebrew calendar calculations)
```

---

## Error Handling

### Standard Error Response
```typescript
interface APIError {
  detail: string;
}

try {
  const data = await apiGet('/api/some-endpoint');
} catch (error) {
  if (error instanceof Error) {
    console.error('API Error:', error.message);
    // Show user-friendly error message
  }
}
```

### HTTP Status Codes
- `200` - Success
- `404` - Resource not found
- `400` - Bad request (invalid parameters)
- `401` - Unauthorized
- `500` - Internal server error

---

## Environment Variables

Create `.env.local` in your frontend root:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

For production:

```bash
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
```

---

## Testing the Integration

1. Start backend: `uvicorn backend.main:app --reload`
2. Start frontend: `npm run dev`
3. Open browser console and test:

```javascript
// Test in browser console
fetch('http://localhost:8000/api/calendar/today/')
  .then(r => r.json())
  .then(console.log);
```

---

## Next Steps

1. Replace dummy data with real database connections
2. Implement JWT authentication for protected routes
3. Add caching (Redis) for frequently accessed data
4. Implement rate limiting
5. Add comprehensive error logging
6. Deploy backend and frontend to production

---

## Support

For issues or questions, check:
- Backend docs: `http://localhost:8000/docs`
- API health: `http://localhost:8000/health`

