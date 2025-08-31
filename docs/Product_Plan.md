awesome—your workflow is clear and solid. here’s a **no-nonsense, do-this-next** implementation plan that reuses your existing modules, adds a FastAPI layer, and brings in a Next.js dashboard—while keeping Streamlit as a working demo. one venv only. 💪

# 🔧 Phase 0 — Preflight (½ day)

* Keep your current venv. Add deps only if missing:

  * `fastapi uvicorn python-multipart pydantic[email] python-jose[cryptography] passlib[bcrypt] orjson httpx pytest-asyncio`
* Create `.env` (read with `pydantic-settings` or `dotenv`):

  * `DATA_DIR=data`, `ATTENDANCE_CSV=data/attendance.csv`, `FACES_DIR=data/faces`, `EMBEDDINGS_JSON=data/faces.json`, `JWT_SECRET=...`, `JWT_EXP_MIN=1440`
* Set up logging:

  * Python `logging` config → logs in `logs/eyed_%Y%m%d.log`

---

# 🧠 Phase 1 — FastAPI around existing services (2–3 days)

## 1.1 Project skeleton

```
EyeD/
├── src/
│   ├── modules/                # (existing)
│   ├── services/               # (existing)
│   └── dashboard/              # Streamlit (existing)
├── backend/
│   ├── main.py
│   ├── deps.py
│   ├── auth/
│   │   ├── router.py
│   │   └── security.py
│   ├── routes/
│   │   ├── registration.py
│   │   ├── attendance.py
│   │   └── analytics.py
│   ├── dto/                    # Pydantic models
│   │   ├── user.py
│   │   ├── attendance.py
│   │   └── analytics.py
│   ├── adapters/               # Thin wrappers over services/*
│   │   ├── registration_adapter.py
│   │   ├── recognition_adapter.py
│   │   ├── liveness_adapter.py
│   │   └── analytics_adapter.py
│   └── tests/
└── .env
```

## 1.2 DTOs (Pydantic)

* `UserCreate`: `name:str`, optional `id:str`
* `UserRecord`: `name,id,registered_at,image_path,embedding_dim`
* `MarkAttendanceRequest`: `image_file | frame_bytes | video_file`, optional `session_id`
* `MarkAttendanceResponse`: `name,id,date,time,status,confidence,liveness_verified,session_id`
* `AnalyticsResponse`: buckets for daily/weekly %, late arrivals, streaks, leaderboard

## 1.3 Auth (simple, optional)

* `/auth/register`, `/auth/login` → issue JWT
* `@router.get` protected with `Depends(verify_token)`
* Keep public GET analytics if needed for demo

## 1.4 Routes (map 1:1 to your workflow)

### `POST /register-user`

* form-data: `name`, `image` (file) OR `webcam_frame` (bytes)
* Steps:

  1. quality + face detect
  2. embeddings via DeepFace (MobileNet)
  3. persist: image → `data/faces/{id or slug}.jpg`, embeddings → `faces.json`
  4. upsert user record (no overwrite image unless explicit `force=True`)
* Returns `UserRecord`

### `POST /mark-attendance`

* form-data: `image | frame | video`
* Pipeline:

  * detect → crop → embed → compare (top-1) → confidence
  * liveness (blink/EAR) with MediaPipe → pass/fail
  * decision matrix (your table)
  * duplicate-day check (first hit wins)
  * append to `attendance.csv` and journal event to log
* Returns `MarkAttendanceResponse`

### `GET /get-attendance`

* Query: `user,date_from,date_to,status`
* Returns JSON rows of CSV

### `GET /get-analytics`

* Wrap your `analytics_service`:

  * overall % (daily/weekly/monthly), late distribution, per-user trends
  * streaks leaderboard, badges snapshot

### `GET /healthz`

* returns model load status, CSV readability, versions

## 1.5 Adapters

* Thin wrappers to call your `services/*` with strict I/O (Pydantic in, dict out)
* Normalize CSV columns (`Date`, `Time`, `Status`, `Name`, `ID`, `Confidence`, `Liveness_Verified`, `Session_ID`)

## 1.6 Testing (API)

* `pytest + httpx.AsyncClient`
* happy paths + edge cases:

  * no face / multiple faces
  * low-res photo
  * duplicate same-day entry
  * liveness fail
  * corrupted CSV
* Add a tiny fixture dataset under `backend/tests/fixtures/`

---

# 🖥️ Phase 2 — Next.js + Mantine dashboard (3–4 days, in parallel)

## 2.1 Bootstrap

```
npx create-next-app@latest eyed-dashboard --ts
cd eyed-dashboard
npm i @mantine/core @mantine/hooks @mantine/charts framer-motion axios react-webcam dayjs
```

* Theme: Notus-inspired (Inter + Poppins)
* `NEXT_PUBLIC_API_BASE_URL` points to FastAPI

## 2.2 Pages

* `/` (Dashboard): stats cards + AreaChart (from `/get-analytics`)
* `/daily`: webcam capture → `POST /mark-attendance` → toast feedback
* `/logs`: table with filters, CSV export (client-side)
* `/analytics`: Bar/Donut/Line from `/get-analytics`
* `/gamification`: cards + badges, streaks, timeline

## 2.3 Components

* `StatsGrid`, `LivePresentCard`, `AttendanceTable`, `BadgeCard`, `TimelineScatter`
* Global `axios` client with auth interceptor (if JWT)
* Error boundary + retry (exponential backoff) for flaky calls

## 2.4 UX rules

* optimistic toasts on submit; replace with server response
* handle Streamlit-Cloud demo mode (no webcam): show “Upload image/video” fallback

---

# 📺 Phase 3 — Keep Streamlit demo (0.5 day)

* Keep your current Streamlit app as **Demo Mode**:

  * add env var `DEMO_MODE=true` → hide webcam, enable upload & prerecorded demo
  * link to live Next.js from navbar
* Benefit: immediate working demo link for recruiters

---

# 🗃️ Phase 4 — Data & Integrity (1 day)

## 4.1 Duplicate prevention

* index key: `(ID, Date)` in memory per request; enforce before writing
* if repeat: return same-day “already marked” status with first timestamp

## 4.2 Backups

* On write, append CSV then copy to `data/exports/attendance_YYYYMMDD.csv`
* Nightly rotation (simple cron or `schedule` inside app)

## 4.3 Validation

* confidence in \[0,100], liveness `{Yes|No}`
* strict datetime: ISO at write, human-friendly at read

---

# 🧪 Phase 5 — Quality, Perf, and Observability (1–2 days)

## 5.1 Unit tests you must have

* registration (quality gates, bad files)
* recognition (top-1 match threshold boundary)
* liveness (EAR thresholds; blinking vs static)
* CSV I/O (missing columns; BOM; delimiter issues)

## 5.2 API tests

* end-to-end: register → mark-attendance → list → analytics

## 5.3 Performance budgets

* recognition compare: < 1ms per candidate (cache embeddings in RAM)
* analytics endpoints: < 250ms on 10k rows (pandas + cached summaries)
* cold start model load: log time; prewarm on `/healthz`

## 5.4 Monitoring

* structured logs (JSON) for each decision
* counters: `attendance_marked_total`, `liveness_fail_total`, `duplicates_blocked_total`

---

# 🚀 Phase 6 — Deployment (1–2 days)

## 6.1 Backend (Render/Railway)

* Startup: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
* Persistent volume for `/data` (or fall back to object storage)
* CORS: allow Vercel domain
* Health checks → `/healthz`

## 6.2 Frontend (Vercel)

* `NEXT_PUBLIC_API_BASE_URL` set to backend URL
* Image/video upload size limits (e.g., 10–20MB)

## 6.3 Streamlit Cloud (Demo)

* `DEMO_MODE=true`
* Provide sample files + `demos/demo.mp4`

---

# 🏆 Gamification & Analytics (implementation notes)

## Badges (computed server-side; returned in `/get-analytics`)

* Attendance % tiers; Streaks (current/best); Timing (Early Bird/Late Comer); Quality Master
* Return:

  ```
  {
    badges: [{id, label, emoji, reason}],
    streaks: {current: N, best: M},
    leaderboard: [{id, name, pct, streak}],
    timeline: [{id, name, date, arrival_time}]
  }
  ```

## Timeline

* store `Time` consistently; compute arrival buckets server-side
* return scatter-ready `{date, minutes_since_9am}`

---

# 🧰 Concrete task breakdown (10 working days)

**Day 1**

* Backend scaffold, env, logging, CORS, `/healthz`
* Wire adapters to existing `services/*`

**Day 2**

* `POST /register-user` (upload + webcam bytes)
* Quality checks, face detect, embedding, save

**Day 3**

* `POST /mark-attendance` with decision matrix + duplicate guard
* CSV write + backup; structured event log

**Day 4**

* `GET /get-attendance`, `GET /get-analytics`
* Normalize CSV columns, analytics wrapper

**Day 5**

* API tests (happy paths + edge cases)
* Perf: embedding cache, analytics memoization

**Day 6**

* Next.js boot, theme, layout, API client, auth stub
* Dashboard (`/`) cards + area chart

**Day 7**

* `/daily` webcam + upload fallback; success/fail toasts
* Reuse decision messages:

  * ✅ “Alice 9:15 AM, Confidence 97%, Liveness OK”
  * ❌ “Not recognized / Liveness failed”

**Day 8**

* `/logs` table + filters + CSV export
* `/analytics` charts (weekly %, late arrivals, streaks)

**Day 9**

* `/gamification` badges, streaks, timeline view
* Error boundaries, retries, empty states

**Day 10**

* Deploy FastAPI → Render/Railway, Next.js → Vercel
* Streamlit Demo mode on Streamlit Cloud
* Final QA: register → mark → logs → analytics → badges

---

# 🔐 Security & Privacy quick hits

* Don’t expose raw embeddings over API.
* Sign URLs if you must serve face images, otherwise serve thumbnails or redact.
* Rate-limit `/mark-attendance`.
* Store only what’s needed (name/id/time/confidence/liveness), avoid PII bloat.

---

# ✅ Acceptance criteria checklist

* [ ] Register user via API; appears in faces.json & image saved
* [ ] Mark attendance end-to-end with decision matrix enforced
* [ ] Duplicate same-day prevented
* [ ] Logs retrievable, filterable; CSV export works
* [ ] Analytics + streaks + badges correct for sample data
* [ ] Next.js pages functional on mobile and desktop
* [ ] Streamlit Demo functional without webcam
* [ ] Deployed URLs + health checks passing
* [ ] Tests green; perf budgets met

---

