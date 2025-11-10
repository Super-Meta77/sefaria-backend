# ✅ Extract ALL Sugyot from ALL Tractates - Complete Guide

## 🎯 What This Does

The system now **automatically discovers and extracts sugyot from ALL tractates** in your database, without needing to specify tractate names manually.

---

## 🚀 Quick Start

### Option 1: CLI Tool (Recommended)

```bash
cd backend

# Extract from ALL tractates (automatic discovery)
python extract_sugyot_ai.py --all --limit 50

# With more texts per tractate
python extract_sugyot_ai.py --all --limit 100

# Export results to JSON
python extract_sugyot_ai.py --all --limit 50 --export results.json
```

### Option 2: API Endpoint

```bash
# Start backend
uvicorn main:app --reload

# Trigger extraction (background job)
curl -X POST "http://localhost:8000/api/sugya/extract-all?limit_per_tractate=50"

# Synchronous (waits for completion)
curl -X POST "http://localhost:8000/api/sugya/extract-all-sync?limit_per_tractate=20"
```

### Option 3: Python Code

```python
from ai.sugya_extractor import get_sugya_extractor

extractor = get_sugya_extractor()

# Extract from ALL tractates
stats = extractor.extract_all_sugyot(
    limit_per_tractate=50
)

print(f"Processed {stats['tractates_processed']} tractates")
print(f"Saved {stats['total_saved']} sugyot")
```

---

## 🔍 How It Works

### Step 1: Automatic Discovery
```cypher
MATCH (t:Text)
WHERE t.id =~ '.*\d+[ab]:.*'
WITH split(t.id, ' ') as parts
WHERE size(parts) > 1
WITH parts[0] as tractate
RETURN DISTINCT tractate
ORDER BY tractate
```

Discovers all tractates that have Talmudic texts.

### Step 2: Extraction Loop
For each discovered tractate:
1. Fetch texts (up to limit)
2. Group by page reference
3. Analyze with AI (or simulated)
4. Extract dialectic structure
5. Save to database

### Step 3: Aggregation
Combines results from all tractates into comprehensive statistics.

---

## 📊 Example Output

```
🌍 DISCOVERING ALL TRACTATES IN DATABASE
================================================================================

Found 15 tractates with Talmudic texts:
  - Berakhot
  - Beitzah
  - Chagigah
  - Eiruvin
  - Gittin
  - Jerusalem
  - Menachot
  - Mishnah
  - Nazir
  - Nedarim
  - Pesachim
  - Shabbat
  - Taanit
  - Yevamot
  - Yoma

================================================================================
🚀 STARTING EXTRACTION FROM ALL TRACTATES
================================================================================

================================================================================
📖 TRACTATE 1/15: Berakhot
================================================================================

🔍 Extracting sugyot from Berakhot ...
   Found 50 texts to analyze
   Grouped into 12 pages
   
   Analyzing Berakhot 2a...
   ✅ Extracted: Discussion on Berakhot 2a
   
   ... (more extractions)

💾 Saving to database...
   ✅ Saved: Berakhot 2a - Discussion on Berakhot 2a
   ... (more saves)

✅ Berakhot: Extracted 12, Saved 12

================================================================================
📖 TRACTATE 2/15: Beitzah
================================================================================

... (continues for all tractates)

================================================================================
📊 EXTRACTION SUMMARY
================================================================================
Tractates Found: 15
Tractates Processed: 15
Total Extracted: 156
Successfully Saved: 156
Failed: 0
================================================================================
```

---

## 🎛️ Parameters

### `--all` (CLI) or `extract_all_sugyot()` (Python)

| Parameter | Default | Description |
|-----------|---------|-------------|
| `limit_per_tractate` | 50 | Maximum texts to analyze per tractate |

### Why Use Limits?

- **Cost control**: GPT-4 API costs money
- **Time management**: Full extraction can take hours
- **Testing**: Start small to verify everything works
- **Incremental**: Process in batches

---

## 📈 Performance Estimates

### With `limit_per_tractate=50`:
- **Tractates**: ~15-20 discovered
- **Total texts**: 750-1,000 analyzed
- **Sugyot extracted**: 150-200
- **Time**: 5-10 minutes (with GPT-4)
- **Cost**: ~$1-2 (with GPT-4)

### With `limit_per_tractate=100`:
- **Tractates**: ~15-20 discovered
- **Total texts**: 1,500-2,000 analyzed
- **Sugyot extracted**: 300-400
- **Time**: 10-20 minutes (with GPT-4)
- **Cost**: ~$2-4 (with GPT-4)

### Full Extraction (no limit):
- **Total texts**: 3,000+ analyzed
- **Sugyot extracted**: 500-700
- **Time**: 30-60 minutes (with GPT-4)
- **Cost**: ~$5-10 (with GPT-4)

---

## 🗄️ Database Results

### Tractates Discovered (Example)

Based on your database, the system discovered:
- Berakhot
- Beitzah
- Chagigah
- Eiruvin
- Gittin
- Jerusalem Talmud texts
- Menachot
- Mishnah texts
- Nazir
- Nedarim
- Pesachim
- Shabbat
- Taanit
- Yevamot
- Yoma

**Total: ~15 tractates** with Talmudic texts

### Sugyot Created

For each tractate, creates:
```cypher
(:Sugya {
  ref: "Berakhot 2a",
  title: "Discussion on Berakhot 2a",
  summary: "...",
  theme: "...",
  main_question: "...",
  extraction_method: "ai_powered"
})
  -[:HAS_DIALECTIC_NODE]->
(:DialecticNode {
  type: "question",
  label: "...",
  speaker: "..."
})
  -[:CONTAINS_TEXT]->
(:Text {id: "Berakhot 2a:1"})
```

---

## 🔍 Query Results

### View All Discovered Tractates
```cypher
MATCH (s:Sugya)
WITH split(s.ref, ' ')[0] as tractate, count(*) as count
RETURN tractate, count
ORDER BY count DESC
```

### View All AI-Extracted Sugyot
```cypher
MATCH (s:Sugya)
WHERE s.extraction_method = 'ai_powered'
RETURN s.ref, s.title, s.theme
ORDER BY s.ref
LIMIT 50
```

### Count by Tractate
```cypher
MATCH (s:Sugya)
WHERE s.extraction_method = 'ai_powered'
WITH split(s.ref, ' ')[0] as tractate
RETURN tractate, count(*) as sugyot_count
ORDER BY sugyot_count DESC
```

---

## 💡 Best Practices

### 1. **Start Small**
```bash
# Test with small limit first
python extract_sugyot_ai.py --all --limit 10
```

### 2. **Monitor Progress**
Watch the console output to see:
- Which tractates are being processed
- How many sugyot are extracted
- Any errors that occur

### 3. **Incremental Extraction**
Run multiple times with increasing limits:
```bash
# First run
python extract_sugyot_ai.py --all --limit 20

# Second run (will update existing + add new)
python extract_sugyot_ai.py --all --limit 50

# Third run
python extract_sugyot_ai.py --all --limit 100
```

### 4. **Export Results**
```bash
python extract_sugyot_ai.py --all --limit 50 --export extraction_log.json
```

### 5. **Use API for Background Jobs**
```bash
# Let it run in background
curl -X POST "http://localhost:8000/api/sugya/extract-all?limit_per_tractate=100"

# Check logs later
tail -f logs/extraction.log
```

---

## 🚧 Troubleshooting

### "No tractates found"
- Check database connection
- Verify Text nodes exist
- Run: `MATCH (t:Text) RETURN count(t)`

### "Extraction too slow"
- Reduce `limit_per_tractate`
- Use simulated mode (no API key)
- Process one tractate at a time

### "Too expensive"
- Use `gpt-3.5-turbo` instead of GPT-4
- Reduce limit
- Use simulated mode for development

### "Errors on some tractates"
- Check console output for specific errors
- Some tractates may have unusual text format
- System continues processing other tractates

---

## 📊 Statistics Dashboard

After extraction, query stats:

```cypher
// Total sugyot by extraction method
MATCH (s:Sugya)
RETURN s.extraction_method, count(*) as count

// Tractates with most sugyot
MATCH (s:Sugya)
WITH split(s.ref, ' ')[0] as tractate
RETURN tractate, count(*) as count
ORDER BY count DESC
LIMIT 10

// Dialectic node types distribution
MATCH (:Sugya)-[:HAS_DIALECTIC_NODE]->(d:DialecticNode)
RETURN d.type, count(*) as count
ORDER BY count DESC
```

---

## 🎉 Summary

### What You Get

✅ **Automatic Discovery** - Finds all tractates in database  
✅ **Bulk Extraction** - Processes all tractates in one command  
✅ **AI Analysis** - Uses GPT-4 for intelligent extraction  
✅ **Database Persistence** - Saves all results to Neo4j  
✅ **Detailed Statistics** - Comprehensive extraction reports  
✅ **Error Handling** - Continues even if some fail  
✅ **Flexible Limits** - Control cost and time  
✅ **Multiple Interfaces** - CLI, API, Python  

### Commands Summary

```bash
# Discover what's available
python -c "from ai.sugya_extractor import get_sugya_extractor; print(get_sugya_extractor().discover_all_tractates())"

# Extract from all
python extract_sugyot_ai.py --all --limit 50

# Extract from all with export
python extract_sugyot_ai.py --all --limit 100 --export results.json

# Via API
curl -X POST "http://localhost:8000/api/sugya/extract-all-sync?limit_per_tractate=20"
```

---

**The system now automatically discovers and extracts from ALL tractates!** 🚀

No manual tractate specification needed - just run `--all` and let it discover everything!

