# 🏠 AccessAble — Accessible Smart-Home Agent

> An AI-powered, accessible smart-home backend for people with limited mobility.  
> Control simulated devices using natural-language commands — no real hardware required.

---

## ⚠️ Simulation Notice

**All device operations in this project are SIMULATED.**  
No physical hardware is connected or controlled.  
Device state changes update a SQLite database record only.

---

## 📁 Project Structure

```
AccessAble/
├── app/
│   ├── __init__.py
│   ├── main.py              ← FastAPI app, startup seeder, CORS
│   ├── database.py          ← SQLAlchemy engine + session factory
│   ├── models.py            ← ORM table definitions (7 tables)
│   ├── schemas.py           ← Pydantic request/response models
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py        ← Settings loaded from .env
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── devices.py       ← GET /devices, GET /devices/{id}, PATCH state
│   │   ├── commands.py      ← POST /commands (NL processing)
│   │   ├── routines.py      ← GET/POST /routines, POST /execute, cancel
│   │   ├── actions.py       ← POST /confirm, POST /cancel, GET /actions/{id}
│   │   ├── preferences.py   ← GET/PUT /preferences
│   │   └── history.py       ← GET /history
│   └── services/
│       ├── __init__.py
│       ├── planner.py       ← Rule-based NLP intent + entity extractor
│       ├── device_service.py← Device CRUD + simulated state changes
│       ├── routine_service.py← Execution lifecycle, partial success handling
│       └── safety_service.py← Confirmation gate, duplicate/expiry guards
├── tests/
│   ├── __init__.py
│   ├── conftest.py          ← In-memory SQLite fixtures, TestClient setup
│   ├── test_devices.py
│   ├── test_commands.py
│   ├── test_routines.py
│   ├── test_actions.py
│   └── test_accessibility.py
├── .env                     ← Local settings (copy from .env.example)
├── .env.example
├── requirements.txt
└── README.md
```

---

## 🚀 Windows Installation Guide

### Step 1 — Open PowerShell in the project folder

```powershell
cd "C:\Users\srini\OneDrive\Desktop\Accessible Smart-Home Agent"
```

### Step 2 — Create a virtual environment

```powershell
python -m venv venv
```

### Step 3 — Activate the virtual environment

```powershell
.\venv\Scripts\Activate.ps1
```

> If you see an error about script execution, run:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

### Step 4 — Install dependencies

```powershell
pip install -r requirements.txt
```

### Step 5 — Copy environment file

```powershell
Copy-Item .env.example .env
```

(The `.env` file is already created for you, so this step is optional.)

### Step 6 — Start the server

```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

You should see:

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
AccessAble backend started. Visit http://127.0.0.1:8000/docs
```

The database (`accessable.db`) is created automatically on first run.

---

## 🧪 Running Tests

```powershell
# From the project root with venv active:
pytest tests/ -v
```

### Verified Test Run

The complete project test suite was run locally with Python 3.12:

```text
68 passed
```

The tests use an in-memory SQLite database and do not modify the local
`accessable.db` file.

---

## 🌐 API Reference

All endpoints are explorable at **http://127.0.0.1:8000/docs** (Swagger UI).

### Root

| Method | Path      | Description              |
|--------|-----------|--------------------------|
| GET    | `/`       | Welcome + links          |
| GET    | `/health` | Backend health check     |

### Devices

| Method | Path                     | Description                    |
|--------|--------------------------|--------------------------------|
| GET    | `/devices`               | List all 5 simulated devices   |
| GET    | `/devices/{id}`          | Get a single device by ID      |
| PATCH  | `/devices/{id}/state`    | Directly update device state   |

### Commands (Natural Language)

| Method | Path        | Description                              |
|--------|-------------|------------------------------------------|
| POST   | `/commands` | Process a natural-language command       |

**Request body:**
```json
{
  "text": "Turn on the bedroom light",
  "user_id": 1
}
```

Sensitive actions are never auto-confirmed. For example, a door-lock command
returns an action in `awaiting_confirmation`; send a separate request to
`POST /actions/{action_id}/confirm` before it runs.

**Response:**
```json
{
  "intent": "TURN_ON",
  "explanation": "I'll turn on your bedroom light.",
  "planned_actions": [
    {
      "order": 0,
      "device_name": "bedroom_light",
      "action": "turn_on",
      "description": "Turn on bedroom light",
      "requires_confirmation": false
    }
  ],
  "execution_id": 1,
  "requires_confirmation": false,
  "confirmation_note": null,
  "success": true,
  "warning": null
}
```

### Routines

| Method | Path                              | Description                       |
|--------|-----------------------------------|-----------------------------------|
| GET    | `/routines`                       | List all routines                 |
| POST   | `/routines`                       | Create a custom routine           |
| GET    | `/routines/{id}`                  | Get routine details               |
| POST   | `/routines/{id}/execute`          | Trigger a routine                 |
| GET    | `/routines/executions/{id}`       | Get execution details             |
| POST   | `/routines/executions/{id}/cancel`| Cancel in-progress execution      |

### Actions (Confirmation Gate)

| Method | Path                      | Description                          |
|--------|---------------------------|--------------------------------------|
| GET    | `/actions/{id}`           | Get action details                   |
| POST   | `/actions/{id}/confirm`   | Confirm & execute a pending action   |
| POST   | `/actions/{id}/cancel`    | Cancel a pending action              |

**Confirm request body:**
```json
{ "user_id": 1 }
```

**Confirm response:**
```json
{
  "action_id": 5,
  "status": "completed",
  "message": "Action 'lock' on 'Front Door Lock' completed successfully (SIMULATED).",
  "device_updated": true,
  "new_device_state": { "locked": true, "status": "locked" }
}
```

### History & Preferences

| Method | Path           | Description                           |
|--------|----------------|---------------------------------------|
| GET    | `/history`     | Activity audit log (filterable)       |
| GET    | `/preferences` | Get accessibility preferences         |
| PUT    | `/preferences` | Update accessibility preferences      |

---

## 🗣️ Supported Commands

| You say...                     | Intent detected        |
|--------------------------------|------------------------|
| Turn on the bedroom light      | TURN_ON                |
| Switch off the fan             | TURN_OFF               |
| Lock the door                  | LOCK (with confirm)    |
| Unlock the door                | UNLOCK (with confirm)  |
| I'm going to bed / Bedtime     | BEDTIME_ROUTINE        |
| Good morning / Wake up         | WAKEUP_ROUTINE         |
| I'm leaving / Goodbye          | LEAVING_ROUTINE        |
| Make it comfortable / Relax    | COMFORT_ROUTINE        |
| Turn off all the lights        | TURN_OFF (multi-device)|
| Open / close the window        | OPEN_WINDOW / CLOSE_WINDOW |

---

## 🏠 Simulated Devices

| ID | Name               | Type   | Location     | Initial State              |
|----|--------------------|--------|--------------|----------------------------|
| 1  | bedroom_light      | light  | bedroom      | power: off, brightness: 80 |
| 2  | living_room_light  | light  | living_room  | power: off, brightness: 100|
| 3  | fan                | fan    | bedroom      | power: off, speed: medium  |
| 4  | door_lock          | lock   | entrance     | locked: true               |
| 5  | smart_window       | window | bedroom      | position: closed           |

---

## 🔒 Safety System

The safety system enforces these rules:

1. **Confirmation required** — locking/unlocking doors and any action on the `door_lock` device requires user confirmation via `POST /actions/{id}/confirm`.
2. **Duplicate confirmation blocked** — confirming an already-confirmed action returns `409 Conflict`.
3. **Expiry** — confirmation tokens expire after 5 minutes (configurable in `.env`).
4. **Cancel gate** — cancelled actions cannot be confirmed or re-executed.
5. **No pre-execution** — actions in `awaiting_confirmation` status are never executed automatically.
6. **No direct lock bypass** — the device state endpoint cannot modify a door lock; use a command and confirmation.
7. **Partial success** — if some actions in a routine succeed and others fail, the execution is marked `partial_success` (not falsely reported as complete).

---

## ♿ Accessibility Features

Configure via `PUT /preferences`:

| Setting           | Default  | Description                            |
|-------------------|----------|----------------------------------------|
| `simple_language` | true     | Use plain, clear language              |
| `short_responses` | false    | Use shorter, more concise responses    |
| `voice_friendly`  | false    | Structure responses for TTS reading    |
| `preferred_room`  | bedroom  | Default room for ambiguous commands    |
| `theme`           | light    | light / dark / high_contrast           |
| `font_size`       | medium   | small / medium / large / xlarge        |
| `frequent_routines`| []      | List of often-used routine names       |

---

## 🔧 Architecture

```
HTTP Request
     │
     ▼
FastAPI Router   ← validates with Pydantic schemas
     │
     ▼
Service Layer    ← business logic (planner / device / routine / safety)
     │
     ▼
SQLAlchemy ORM   ← database operations
     │
     ▼
SQLite Database  ← accessable.db (local file)
```

**Key design principles:**
- **Separation of concerns** — routes only call services, services handle all logic.
- **No AI required** — rule-based planner works fully offline.
- **AI-ready** — replace `plan_command()` in `planner.py` to plug in an LLM.
- **Simulation-first** — no real hardware; safe for development/demo.
- **Accessibility-first** — structured responses designed for voice & screen readers.

---

## 🔄 Typical Workflow

1. User says: *"I'm going to bed"*
2. `POST /commands` → planner detects `BEDTIME_ROUTINE`
3. Five actions are created; four execute immediately (lights off, fan on, window close)
4. One action (lock door) is left in `awaiting_confirmation`
5. Response includes `execution_id` and lists the action ID to confirm
6. User calls `POST /actions/{id}/confirm`
7. Door lock action executes (simulated), `device_updated: true`
8. All events are logged in `/history`

---

## 📦 Dependencies

| Package           | Version | Purpose                    |
|-------------------|---------|----------------------------|
| fastapi           | 0.111   | Web framework              |
| uvicorn           | 0.29    | ASGI server                |
| sqlalchemy        | 2.0     | ORM + database abstraction |
| pydantic          | 2.7     | Data validation            |
| pydantic-settings | 2.2     | Settings from .env         |
| python-dotenv     | 1.0     | .env file loading          |
| httpx             | 0.27    | Async HTTP (test client)   |
| pytest            | 8.2     | Testing framework          |
| aiosqlite         | 0.20    | Async SQLite support       |
