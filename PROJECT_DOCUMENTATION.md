# LogiMAS - Complete Project Documentation

## 📋 Table of Contents
1. [Project Overview](#project-overview)
2. [Changes Made](#changes-made)
3. [File Structure](#file-structure)
4. [Setup Instructions](#setup-instructions)
5. [User Accounts](#user-accounts)
6. [Running the Application](#running-the-application)
7. [Testing Guide](#testing-guide)
8. [Troubleshooting](#troubleshooting)

---

## 📊 Project Overview

**LogiMAS** is a Multi-Agent Logistics Management System with:
- Role-based access control (RBAC)
- Real-time shipment tracking with maps
- AI-powered chat assistant
- Performance analytics dashboard
- Knowledge base browser
- Incident reporting system

### Technology Stack
- **Frontend**: Next.js 14, React, TypeScript, TailwindCSS
- **Backend**: FastAPI, Python
- **Database**: Supabase (PostgreSQL)
- **AI/ML**: LangChain, LangGraph, OpenAI
- **Maps**: Leaflet, OpenStreetMap
- **Charts**: Recharts

---

## 🔧 Changes Made

### 1. Authentication System Fixed
**Files Modified:**
- `apps/web/components/auth/AuthForm.tsx`
- `apps/web/contexts/AuthContext.tsx`

**Changes:**
- ✅ Removed backend authentication endpoint dependency
- ✅ Integrated direct Supabase authentication
- ✅ Added role and permission fetching from database
- ✅ Implemented real-time auth state listening
- ✅ Fixed logout to properly sign out from Supabase

**Why:** The frontend was trying to authenticate via backend `/auth/token` endpoint which didn't exist. Now it authenticates directly with Supabase.

---

### 2. Sidebar Role-Based Display Fixed
**Files Modified:**
- `apps/web/components/dashboard/Sidebar.tsx`
- `apps/web/contexts/AuthContext.tsx`

**Changes:**
- ✅ Added proper permission checking from database
- ✅ Implemented async logout with redirect
- ✅ Improved user info display (shows role and email)
- ✅ Menu items now filter based on actual user permissions

**Why:** Sidebar wasn't showing menu items because permissions weren't being fetched from the database.

---

### 3. Analysis Page Endpoint Fixed
**Files Modified:**
- `packages/agents/logimas_agents/main.py`

**Changes:**
- ✅ Updated `/admin/kpis` endpoint to calculate metrics directly from shipments
- ✅ Added fallback logic if materialized view doesn't exist
- ✅ Implemented daily on-time performance calculation
- ✅ Added proper error handling and logging

**Why:** The endpoint was looking for a `daily_on_time_rate` materialized view that didn't exist.

**New Files Created:**
- `supabase/CREATE_KPI_VIEW.sql` - Optional materialized view for better performance

---

### 4. Database Setup
**Files Created:**
- `supabase/CLEAN_SETUP.sql` - Complete database setup with proper UUID defaults
- `supabase/CREATE_KPI_VIEW.sql` - KPI materialized view (optional)

**Changes:**
- ✅ All tables now have `DEFAULT gen_random_uuid()` for ID columns
- ✅ Proper foreign key relationships
- ✅ RBAC tables with roles and permissions
- ✅ Indexes for performance

**Why:** Original tables were missing UUID defaults, causing insertion errors.

---

### 5. Data Seeding Scripts
**Files Created:**
- `packages/data_pipeline/scripts/seed_large_dataset.py` - Main seeding script
- `packages/data_pipeline/scripts/seed_knowledge_base.py` - Knowledge base documents
- `packages/data_pipeline/scripts/seed_audit_logs.py` - Agent audit logs
- `packages/data_pipeline/scripts/seed_additional_data.py` - Runs both additional scripts

**Changes:**
- ✅ Split order and shipment generation to handle database-generated IDs
- ✅ Added knowledge base document seeding with embeddings
- ✅ Added sample agent audit logs
- ✅ Proper error handling and progress bars

**Why:** Needed to populate database with realistic test data.

---

### 6. Environment Configuration
**Files Created:**
- `apps/web/.env.local` - Frontend environment variables

**Required Variables:**
```env
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
```

**Why:** Frontend needs Supabase credentials to authenticate users.

---

## 📁 File Structure

### ✅ Active Files (Currently Used)

```
LogiMAS/
├── apps/
│   └── web/                                    # Frontend (Next.js)
│       ├── app/
│       │   ├── dashboard/
│       │   │   ├── analysis/page.tsx          # ✅ Performance analytics
│       │   │   ├── chat/page.tsx              # ✅ AI chat interface
│       │   │   ├── knowledge/page.tsx         # ✅ Data browser
│       │   │   ├── tracking/page.tsx          # ✅ Shipment tracking
│       │   │   ├── place-order/page.tsx       # ✅ Order placement
│       │   │   ├── report-incident/page.tsx   # ✅ Incident reporting
│       │   │   └── layout.tsx                 # ✅ Dashboard layout
│       │   ├── login/page.tsx                 # ✅ Login page
│       │   └── signup/page.tsx                # ✅ Signup page
│       ├── components/
│       │   ├── auth/
│       │   │   └── AuthForm.tsx               # ✅ MODIFIED - Supabase auth
│       │   ├── dashboard/
│       │   │   └── Sidebar.tsx                # ✅ MODIFIED - Role-based menu
│       │   ├── charts/
│       │   │   └── DailyPerformanceChart.tsx  # ✅ Recharts component
│       │   ├── maps/
│       │   │   └── LiveTrackingMap.tsx        # ✅ Leaflet map
│       │   └── ui/
│       │       └── RealtimeTelemetry.tsx      # ✅ Vehicle telemetry
│       ├── contexts/
│       │   └── AuthContext.tsx                # ✅ MODIFIED - Auth state management
│       ├── lib/
│       │   └── supabaseClient.ts              # ✅ Supabase client
│       ├── .env.local                         # ✅ CREATED - Environment variables
│       └── package.json                       # ✅ Dependencies
│
├── packages/
│   ├── agents/
│   │   └── logimas_agents/
│   │       ├── main.py                        # ✅ MODIFIED - FastAPI backend
│   │       ├── chains/
│   │       │   └── graph.py                   # ✅ LangGraph agent
│   │       └── tools/
│   │           ├── database.py                # ✅ Database tools
│   │           └── vector_store.py            # ✅ RAG tools
│   │
│   └── data_pipeline/
│       └── scripts/
│           ├── seed_large_dataset.py          # ✅ MODIFIED - Main seeding
│           ├── seed_knowledge_base.py         # ✅ CREATED - KB documents
│           ├── seed_audit_logs.py             # ✅ CREATED - Audit logs
│           └── seed_additional_data.py        # ✅ CREATED - Run all
│
└── supabase/
    ├── CLEAN_SETUP.sql                        # ✅ CREATED - Complete DB setup
    ├── CREATE_KPI_VIEW.sql                    # ✅ CREATED - KPI view
    ├── COMPLETE_SETUP.sql                     # ✅ Original setup
    └── migrations/
        ├── 0002_rbac_schema.sql               # ✅ RBAC tables
        ├── 0003_update_permissions.sql        # ✅ Permissions
        └── 0004_complete_database_setup.sql   # ✅ Complete schema
```

### ❌ Unused/Deprecated Files

```
LogiMAS/
├── packages/
│   └── agents/
│       └── logimas_agents/
│           └── auth.py.disabled               # ❌ NOT USED - Backend auth (disabled)
│
└── apps/
    └── web/
        └── middleware.ts.disabled             # ❌ NOT USED - Auth middleware (disabled)
```

**Why Disabled:**
- `auth.py.disabled` - Backend authentication not needed (using Supabase directly)
- `middleware.ts.disabled` - Route protection handled by AuthContext

---

## 🚀 Setup Instructions

### Prerequisites
- Node.js 18+ and npm
- Python 3.9+
- Supabase account
- OpenAI API key (for AI chat)

### Step 1: Clone and Install Dependencies

```bash
# Install frontend dependencies
cd apps/web
npm install

# Install backend dependencies
cd ../../packages/agents
pip install -r requirements.txt

# Install data pipeline dependencies
cd ../data_pipeline
pip install -r requirements.txt
```

### Step 2: Setup Supabase

1. **Create Supabase Project**
   - Go to https://supabase.com
   - Create a new project
   - Note your project URL and keys

2. **Run Database Setup**
   - Open Supabase SQL Editor
   - Copy entire content from `supabase/CLEAN_SETUP.sql`
   - Run it
   - Verify: Should see "Setup Complete!" message

3. **Optional: Create KPI View (for better performance)**
   - Copy content from `supabase/CREATE_KPI_VIEW.sql`
   - Run in SQL Editor

### Step 3: Configure Environment Variables

**Root `.env` file:**
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
SUPABASE_ANON_KEY=your_anon_key
OPENAI_API_KEY=your_openai_api_key
```

**Frontend `.env.local` file:**
```env
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
```

### Step 4: Seed Database

```bash
# Seed main data (customers, orders, shipments, warehouses, vehicles)
cd packages/data_pipeline/scripts
python seed_large_dataset.py

# Seed additional data (knowledge base, audit logs)
python seed_additional_data.py
```

**Expected Results:**
- ✅ 100 customers
- ✅ 5,000 orders
- ✅ ~4,500 shipments
- ✅ 10 warehouses
- ✅ 50 vehicles
- ✅ 20 knowledge base documents
- ✅ 50 agent audit logs

### Step 5: Create User Accounts

**In Supabase Dashboard:**
1. Go to **Authentication** → **Users**
2. Click **"Add User"**
3. Create these users:

| Email | Password |
|-------|----------|
| admin.logimas@gmail.com | Admin@2024 |
| customer.logimas@gmail.com | Customer@2024 |
| delivery.logimas@gmail.com | Delivery@2024 |

4. **Disable Email Confirmation** (Settings → Auth → Email Confirmations → OFF)

**Assign Roles (Run in SQL Editor):**
```sql
-- Admin role
INSERT INTO user_roles (user_id, role_id)
SELECT u.id, r.role_id
FROM auth.users u, roles r
WHERE u.email = 'admin.logimas@gmail.com' 
  AND r.role_name = 'admin'
ON CONFLICT DO NOTHING;

-- Customer role
INSERT INTO user_roles (user_id, role_id)
SELECT u.id, r.role_id
FROM auth.users u, roles r
WHERE u.email = 'customer.logimas@gmail.com' 
  AND r.role_name = 'customer'
ON CONFLICT DO NOTHING;

-- Delivery person role
INSERT INTO user_roles (user_id, role_id)
SELECT u.id, r.role_id
FROM auth.users u, roles r
WHERE u.email = 'delivery.logimas@gmail.com' 
  AND r.role_name = 'delivery_person'
ON CONFLICT DO NOTHING;
```

---

## 👥 User Accounts

### Admin User
**Credentials:**
```
Email: admin.logimas@gmail.com
Password: Admin@2024
```

**Permissions:**
- ✅ View Tracking
- ✅ Access Knowledge Base
- ✅ Perform Analysis
- ✅ Access Chat
- ✅ Full Admin Access

**Sidebar Menu:**
- Chat
- Tracking
- Knowledge Base
- Analysis

---

### Customer User
**Credentials:**
```
Email: customer.logimas@gmail.com
Password: Customer@2024
```

**Permissions:**
- ✅ Place Order
- ✅ View Tracking
- ✅ Access Chat

**Sidebar Menu:**
- Chat
- Tracking
- Place Order

---

### Delivery Person User
**Credentials:**
```
Email: delivery.logimas@gmail.com
Password: Delivery@2024
```

**Permissions:**
- ✅ View Tracking
- ✅ Report Incident
- ✅ Access Chat

**Sidebar Menu:**
- Chat
- Tracking
- Report Incident

---

## 🏃 Running the Application

### Start Backend Server

```bash
cd packages/agents
uvicorn logimas_agents.main:app --reload --port 8000
```

**Backend will run at:** `http://localhost:8000`

**Verify backend:**
```bash
curl http://localhost:8000/
# Should return: {"status":"ok","message":"LogiMAS Agent Server is running."}
```

---

### Start Frontend Server

**Open a NEW terminal:**
```bash
cd apps/web
npm run dev
```

**Frontend will run at:** `http://localhost:3000`

---

### Access the Application

1. **Open browser:** `http://localhost:3000`
2. **Click "Sign In"**
3. **Login with any test user**
4. **Explore the dashboard!**

---

## 🧪 Testing Guide

### Test 1: Login & Role-Based Access

**As Admin:**
1. Login with `admin.logimas@gmail.com`
2. ✅ Should see: Chat, Tracking, Knowledge Base, Analysis
3. ❌ Should NOT see: Place Order, Report Incident

**As Customer:**
1. Login with `customer.logimas@gmail.com`
2. ✅ Should see: Chat, Tracking, Place Order
3. ❌ Should NOT see: Analysis, Knowledge Base, Report Incident

**As Delivery Person:**
1. Login with `delivery.logimas@gmail.com`
2. ✅ Should see: Chat, Tracking, Report Incident
3. ❌ Should NOT see: Analysis, Knowledge Base, Place Order

---

### Test 2: Tracking Page

1. **Get a shipment ID from database:**
```sql
SELECT shipment_id, status FROM shipments LIMIT 5;
```

2. **Go to Tracking page**
3. **Enter shipment ID**
4. **Click "Track Shipment"**

**Expected Result:**
- ✅ Shipment details displayed
- ✅ Map shows vehicle location (if telemetry exists)
- ✅ Current ETA and status shown

---

### Test 3: Analysis Page (Admin Only)

1. **Login as admin**
2. **Go to Analysis page**

**Expected Result:**
- ✅ Total shipments count
- ✅ Daily performance chart
- ✅ Performance data table

---

### Test 4: Knowledge Base (Admin Only)

1. **Login as admin**
2. **Go to Knowledge Base**
3. **Select different tables from dropdown**

**Expected Result:**
- ✅ Tables: customers, orders, shipments, vehicles, warehouses, documents, agent_audit_logs
- ✅ Data displayed with pagination
- ✅ Can switch between 10/25/50 rows per page

---

### Test 5: Chat (All Users)

1. **Login with any user**
2. **Go to Chat page**
3. **Ask questions like:**
   - "What is the standard delivery time?"
   - "How do I track my package?"
   - "Show me recent shipments"

**Expected Result:**
- ✅ AI agent responds with relevant information
- ✅ Uses knowledge base documents
- ✅ Can query database

---

### Test 6: Logout

1. **Click Logout button in sidebar**

**Expected Result:**
- ✅ Signed out from Supabase
- ✅ Redirected to login page
- ✅ Cannot access dashboard without logging in again

---

## 🔍 API Endpoints Reference

### Backend Endpoints

| Endpoint | Method | Purpose | Permission Required |
|----------|--------|---------|-------------------|
| `/` | GET | Health check | None |
| `/agent/invoke` | POST | Chat with AI agent | `access_chat` |
| `/shipments/{id}` | GET | Get shipment details | `view_tracking` |
| `/admin/kpis` | GET | Get KPI data | `perform_analysis` |
| `/browser/{table}` | GET | Browse table data | `access_knowledge_base` |
| `/knowledge/documents` | GET | List documents | `access_knowledge_base` |
| `/knowledge/schemas` | GET | Get table schemas | `access_knowledge_base` |
| `/incidents` | POST | Report incident | `report_incident` |
| `/orders` | POST | Place new order | `place_order` |

**Test an endpoint:**
```bash
# Health check
curl http://localhost:8000/

# Get shipment (replace with actual shipment_id)
curl http://localhost:8000/shipments/your-shipment-id
```

---

## 🐛 Troubleshooting

### Issue: "Not Found" error on login

**Solution:**
1. Check if backend is running: `http://localhost:8000`
2. Verify `.env.local` exists in `apps/web/`
3. Restart frontend: `npm run dev`

---

### Issue: Sidebar not showing menu items

**Solution:**
1. Verify user has role assigned in database:
```sql
SELECT u.email, r.role_name
FROM auth.users u
JOIN user_roles ur ON u.id = ur.user_id
JOIN roles r ON ur.role_id = r.role_id;
```
2. If no role, run the role assignment SQL from Step 5
3. Logout and login again

---

### Issue: Analysis page shows error

**Solution:**
1. Backend should calculate KPIs automatically
2. If still failing, check backend logs
3. Verify shipments have `shipped_at` dates:
```sql
SELECT COUNT(*) FROM shipments WHERE shipped_at IS NOT NULL;
```

---

### Issue: Knowledge Base tables are empty

**Solution:**
```bash
cd packages/data_pipeline/scripts
python seed_additional_data.py
```

---

### Issue: "Module not found" errors

**Solution:**
```bash
# Frontend
cd apps/web
npm install

# Backend
cd packages/agents
pip install -r requirements.txt
```

---

### Issue: Database connection errors

**Solution:**
1. Check `.env` file has correct Supabase credentials
2. Verify Supabase project is active
3. Check if service role key is correct (not anon key)

---

## 📊 Database Schema Summary

### Core Tables
- `customers` - Customer information
- `orders` - Order records
- `shipments` - Shipment tracking
- `vehicles` - Vehicle fleet
- `warehouses` - Warehouse locations
- `vehicle_telemetry` - Real-time vehicle data

### RBAC Tables
- `roles` - User roles (admin, customer, delivery_person)
- `permissions` - Available permissions
- `role_permissions` - Role-permission mapping
- `user_roles` - User-role assignments

### AI/Knowledge Tables
- `documents` - Knowledge base for RAG
- `agent_audit_logs` - AI agent decision logs

---

## 📝 Summary of Changes

### Files Modified: 3
1. `apps/web/components/auth/AuthForm.tsx` - Supabase authentication
2. `apps/web/contexts/AuthContext.tsx` - Role/permission management
3. `packages/agents/logimas_agents/main.py` - KPI endpoint fix

### Files Created: 8
1. `apps/web/.env.local` - Frontend environment
2. `supabase/CLEAN_SETUP.sql` - Database setup
3. `supabase/CREATE_KPI_VIEW.sql` - KPI view
4. `packages/data_pipeline/scripts/seed_knowledge_base.py` - KB seeding
5. `packages/data_pipeline/scripts/seed_audit_logs.py` - Log seeding
6. `packages/data_pipeline/scripts/seed_additional_data.py` - Combined seeding
7. `packages/data_pipeline/scripts/README_ADDITIONAL_SEEDING.md` - Seeding docs
8. `WEBSITE_STATUS.md` - Status documentation

### Files Disabled: 2
1. `packages/agents/logimas_agents/auth.py.disabled` - Not needed
2. `apps/web/middleware.ts.disabled` - Not needed

---

## 🎯 Quick Start Checklist

- [ ] Install Node.js and Python dependencies
- [ ] Create Supabase project
- [ ] Run `CLEAN_SETUP.sql` in Supabase
- [ ] Configure `.env` and `.env.local` files
- [ ] Run `seed_large_dataset.py`
- [ ] Run `seed_additional_data.py`
- [ ] Create 3 test users in Supabase
- [ ] Assign roles via SQL
- [ ] Start backend: `uvicorn logimas_agents.main:app --reload`
- [ ] Start frontend: `npm run dev`
- [ ] Login at `http://localhost:3000`
- [ ] Test all features!

---

## 📞 Support

If you encounter issues:
1. Check the Troubleshooting section
2. Verify all environment variables are set
3. Check backend and frontend logs
4. Ensure Supabase project is active

---

**🎉 Your LogiMAS application is now fully functional!**

Last Updated: October 12, 2025
