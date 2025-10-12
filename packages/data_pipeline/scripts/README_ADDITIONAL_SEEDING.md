# Additional Data Seeding Scripts

These scripts populate the `documents` and `agent_audit_logs` tables with sample data.

## Why These Tables Were Empty

### 1. Documents Table
- **Purpose**: Stores knowledge base documents for RAG (Retrieval Augmented Generation)
- **Used by**: AI chat agent to answer questions about policies, procedures, and FAQs
- **Why empty**: Needs to be manually populated with company knowledge

### 2. Agent Audit Logs Table
- **Purpose**: Logs AI agent decisions and actions for auditing
- **Used by**: Tracking agent behavior, debugging, and compliance
- **Why empty**: Only populated when agents make decisions (e.g., during chat interactions)

---

## How to Populate These Tables

### Option 1: Run All at Once (Recommended)

```bash
cd packages/data_pipeline/scripts
python seed_additional_data.py
```

This will:
- ✅ Seed 20 knowledge base documents (policies, procedures, FAQs)
- ✅ Seed 50 agent audit logs (sample agent decisions)

### Option 2: Run Individually

**Seed Knowledge Base Only:**
```bash
python seed_knowledge_base.py
```

**Seed Audit Logs Only:**
```bash
python seed_audit_logs.py
```

---

## What Gets Seeded

### Knowledge Base Documents (20 documents)
- **Policies**: Delivery times, package requirements, insurance, returns
- **Procedures**: Incident reporting, vehicle maintenance, temperature control
- **FAQs**: Tracking, claims, operating hours, weekend delivery

Each document includes:
- Text content
- Vector embeddings (for semantic search)
- Source type and ID
- Region information

### Agent Audit Logs (50 logs)
Sample decisions from various agents:
- **Routing Agent**: Route optimization, rerouting
- **Delay Prediction Agent**: Traffic predictions, ETA updates
- **Customer Service Agent**: Query responses, recommendations
- **Incident Response Agent**: Emergency handling
- **Capacity Planning Agent**: Resource allocation

Each log includes:
- Agent name
- Decision details
- Confidence score
- Input context
- Timestamp

---

## Requirements

Make sure you have these packages installed:

```bash
pip install sentence-transformers
```

(Other requirements should already be installed from the main seeding)

---

## After Seeding

### Verify Documents
```sql
SELECT COUNT(*) FROM documents;
SELECT source_type, COUNT(*) FROM documents GROUP BY source_type;
```

### Verify Audit Logs
```sql
SELECT COUNT(*) FROM agent_audit_logs;
SELECT agent_name, COUNT(*) FROM agent_audit_logs GROUP BY agent_name;
```

### Test in Knowledge Base Page
1. Login as admin
2. Go to Knowledge Base
3. Select "documents" table
4. You should see 20 documents

### Test in Chat
The AI agent can now answer questions like:
- "What is the standard delivery time?"
- "How do I track my package?"
- "What should I do if my package is damaged?"

---

## Notes

- Documents include embeddings for semantic search
- Audit logs span the last 30 days
- Both tables can be cleared and re-seeded anytime
- Real audit logs will be created automatically when using the chat feature

---

## Troubleshooting

**Error: "sentence-transformers not found"**
```bash
pip install sentence-transformers
```

**Error: "Missing Supabase credentials"**
- Make sure `.env` file exists in the root directory
- Check that `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` are set

**Slow embedding generation**
- First run downloads the model (~80MB)
- Subsequent runs are much faster
- Consider using GPU if available

---

## Clean Up

To clear these tables:

```sql
-- Clear documents
DELETE FROM documents;

-- Clear audit logs
DELETE FROM agent_audit_logs;
```

Then re-run the seeding scripts.
