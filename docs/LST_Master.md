# 🧱 Low-Level Source of Truth — MASTER SPEC

---

## 📛 Project Codename
**The Regiment — Discipline Dealer Protocol**

## 🎯 Purpose of this Document
This file defines the **execution-grade contracts**, global behaviors, naming rules, and architectural structure of *The Regiment* — a discipline-first, AI-powered transformation and compliance system.

It serves as the root authority for:
- Module design
- Schema consistency
- Trigger logic
- Cursor build alignment
- DSPy flag integration

All modules reference this master.  
All engines must conform to its rules.

---

## 🧠 Core System Doctrine

- **Discipline > Convenience** — The system enforces structure. No flexibility is a feature.
- **Automation is tactical** — You (the Commander) remain in control at all times.
- **AI is a recon officer, not a coach** — DSPy flags, summarizes, and detects. It never adjusts without permission.
- **No guessing allowed** — Every log, message, and schema must follow spec.
- **Cursor is a tool, not a planner** — Cursor executes based on what is written here. Nothing else.

---

## 🗂️ Modular Engine Index (Each with its own LST file)

| Engine Module                | Spec File Name                   |
|------------------------------|----------------------------------|
| 🧾 Onboarding Engine         | `lst_onboarding_engine.md`       |
| 🍽️ Meal Delivery Engine     | `lst_meal_delivery_engine.md`    |
| 🏋️ Training Dispatcher      | `lst_training_dispatcher.md`     |
| 🏃 Cardio Regiment Engine    | `lst_cardio_regiment_engine.md`  |
| ⚖️ Check-In Analyzer         | `lst_checkin_analyzer.md`        |
| 🧠 DSPy Flag Engine          | `lst_dspy_flag_engine.md`        |
| 🚨 Infraction Monitor        | `lst_infraction_monitor.md`      |
| 🖥️ Battle Station UI         | `lst_battle_station_ui.md`       |
| 🔐 Schema Definitions        | `lst_schema_definitions.md`      |
| ⚙️ Automation Scheduler      | `lst_automation_scheduler.md`    |

All engines operate as isolated services, reading from a shared `client_profile`, writing their own logs, and triggering DSPy flag assessments where relevant.

---

## 📁 File Structure & Convention

- All engine LSTs live in `/lst/`
- Naming convention: `lst_<engine_name>.md`
- All specs must define:
  - Inputs & expected data structure
  - Output (messages, API responses, DB writes)
  - Failure logic (what if data missing, paused, etc)
  - Trigger conditions (time, flags, conditions)

---

## 📡 Cursor Execution Rules

- Cursor builds must reference this file and associated LSTs
- Cursor must never infer behavior from examples
- Cursor must never modify DSPy or schema logic without an explicit spec
- Output must conform to existing schema definitions
- All changes must be traceable to this source of truth

---

## ⛓️ LST Master Sections (Scaffold)

Below this header, each of the following sections should be filled out:

### 1. 🧱 Global Field Definitions
Define the standard fields used across all engines:
- `user_id`, `timestamp`, `meal_id`, `template_id`, `exercise`, `timezone_offset`, etc.

### 2. 🧱 Naming Conventions
- Snake_case vs camelCase
- All logs stored as JSON with ISO 8601 timestamps
- Field names must match schema contracts

### 3. 🧱 Global Trigger Rules
- Meal drop = 06:00 client time
- Check-in = 05:30 client time
- Training drop = 07:00 client time
- Flag scan = Sunday 20:00

### 4. 🧱 Log Format Overview
- Unified shape for meal logs, training logs, check-in logs
- All logs include: `user_id`, `timestamp`, `source_engine`, `status`, `data`

### 5. 🧱 Master DB Structure Summary
- `client_profile`
- `meal_logs`
- `training_logs`
- `checkin_logs`
- `job_cards`
- `flags`
- `pause_log`

### 6. 🧱 External Dependencies
- NeonDB
- FastAPI
- Discord API
- DSPy core engine

### 7. 🧱 Error & Failure Handling Philosophy
- Missed logs are tracked, not excused
- System should never silently skip a drop
- All failures must result in:
  - Log to DB
  - Optional job card
  - Coach-visible alert

### 8. 🧱 Developer & Cursor Notes
- Where to look first when extending logic
- How to safely add new engines/templates
- Where to inject DSPy hooks

---

## ✅ Final Note
This file is not optional.  
It defines The Regiment as code.  
Cursor builds from it. Humans enforce it.

If it’s not written here, it doesn’t exist.

---

Let me know when you're ready to begin Section 1 (Global Fields) and we’ll structure it cleanly with types and examples.

1. 🧱 Global Field Definitions
This section defines all standardized fields used across every engine, log, and DSPy operation. Any module referencing these fields must use the exact format and constraints defined below. Cursor is expected to validate its outputs against these definitions.

Field Name	Type	Example	Required	Description
user_id	string	98237482919374	✅ Yes	Discord user ID, unique per client
timestamp	string	2025-05-21T06:00:00Z	✅ Yes	ISO 8601 format for log timestamps
timezone_offset	string	UTC+2	✅ Yes	Client's local time offset, used for scheduling
date	string	2025-05-21	✅ Yes	Simple date format for daily logs
meal_id	string	planC_meal3	✅ Yes	Unique ID for each meal in a plan
training_template_id	string	steel_block_A	✅ Yes	Training block assigned to the client
meal_template_id	string	template_A	✅ Yes	Meal plan template assigned to the client
status	string	completed, missed, underperformed	✅ Yes	Execution result of the task/log
paused	boolean	true / false	✅ Yes	If true, engine skips client in all runners
start_date	string	2025-05-27	✅ Yes	Date when engines begin delivering to client
block_id	string	steel_block_3a	✅ Yes	ID of the training plan block
day_index	int	18	✅ Yes	Relative day within the block or cycle
exercise_id	string	ex_dl_001	✅ Yes	Unique exercise ID from the library
exercise_name	string	Deadlift	✅ Yes	Human-readable name of exercise
weight_kg	float	140.0	✅ Yes	Logged weight lifted
reps	int	6	✅ Yes	Logged reps completed
macros	object	{protein: 210, carbs: 250, fats: 60}	✅ Yes	Macronutrient targets, used by compiler
cardio_minutes	int	30	✅ Yes	Daily assigned cardio, in minutes
actual_minutes	int	27	✅ No	Client-reported cardio duration
goal	string	cut / bulk / recomp	✅ Yes	Used to determine plan design and flag analysis
notes	string	“Low energy today.”	✅ No	Optional field for client check-in notes

2. 🧱 Naming Conventions
This section defines the mandatory format, casing, and structure rules across your system. These prevent chaos, drift, and Cursor confusion as the system scales.

md
Copy
Edit
### 2. 🧱 Naming Conventions

All field names, file names, and schema references must follow a strict naming standard.

| Element                  | Convention              | Example                              | Notes                                                           |
|--------------------------|--------------------------|---------------------------------------|------------------------------------------------------------------|
| Field Names              | `snake_case`             | `user_id`, `meal_template_id`         | Applies to all DB fields, JSON logs, schema definitions         |
| Enum Values              | `lowercase` or `snake`   | `cut`, `bulk`, `recomp`               | Logged exactly as shown                                         |
| Boolean Fields           | `true` / `false`         | `paused: true`                        | Never use strings like `"yes"` or `"no"`                        |
| Timestamps               | ISO 8601 UTC             | `2025-05-21T06:00:00Z`                | Always include `Z` or explicit offset like `+02:00`             |
| Date-only Fields         | `YYYY-MM-DD`             | `2025-05-21`                          | No slashes or localized formats                                 |
| Training Blocks / Meals  | `snake_case identifiers` | `steel_block_b`, `template_c`         | Used for template ID fields                                     |
| DB Table Names           | `snake_case plural`      | `client_profiles`, `meal_logs`        | All lowercase, pluralized                                       |
| Log Files / JSON Objects | `snake_case`             | `training_log`, `checkin_report`      | Always flat key/value — no camelCase in keys                    |
| Discord Commands         | `slash_command`          | `/onboard`, `/pause_client`           | All lower, underscore-delimited                                 |
| API Routes (FastAPI)     | `kebab-case`             | `/log-meal`, `/submit-checkin`        | Matches REST practice, but still clear for frontend/backend use |
| Exercise IDs             | `ex_<shortname>_<id>`    | `ex_dl_001`                           | Prefix all IDs with type                                        |
| Template IDs             | `template_<name>`        | `template_b`                          | Never use raw strings like “bulk1”                              |

---

#### ⛔️ Violations That Trigger Build Rejection

- Using camelCase in any schema
- Using inconsistent timestamp formats
- Logging a boolean field as `"true"` or `"false"` (must be raw boolean)
- Switching between singular/plural DB table names
- Including fields not defined in LST / schema_definitions.md

---

### ✅ Cursor Build Compatibility

These conventions ensure:
- Cursor can generate consistent schema-bound logic
- FastAPI and DSPy modules will not drift
- All logs are machine-readable, parseable, and queryable

---

3. 🧱 Global Trigger Rules
This section defines all global schedule rules and time-of-day triggers that control when each engine activates. All modules must follow these triggers unless explicitly overridden. Timezones are always calculated from each client’s timezone_offset (stored at onboarding).

Trigger Name	Local Time (client)	Frequency	Module / Action
checkin_drop	05:30	Daily	Sends morning check-in prompt
meal_drop	06:00	Daily	Sends daily meal protocol + cardio block
training_drop	07:00	Training days only	Sends workout mission if today is a scheduled session
checkin_flag	12:00	Daily	Flags any unsubmitted check-ins
dspy_flag_scan	22:00 UTC (Sunday)	Weekly	Triggers full DSPy review + Job Card creation
honors_board_update	22:30 UTC (Sunday)	Weekly	(Future) Posts honors board in Discord
pause_check	Always enforced	Per tick	If paused = true → engine skip logic applies

🔄 Timezone Handling (Standardized)
All time-sensitive engines use the following logic:

client_now = current_utc + timezone_offset
if client_now == scheduled_time:
    run_engine()
Each engine runner is checked hourly via APScheduler.

🛑 Trigger Inhibitors (Override Rules)
These trigger suppression flags are globally enforced:

Field	If True	Engines Affected
paused = true	No drops sent	Meal, Training, Cardio, Check-in
start_date > today	No drops sent	All engines
training_day = false	No workout drop	Training Dispatcher only

These guards must be enforced in all engine runners, independently. No central switch.

4. 🧱 Log Format Overview
This section defines the canonical logging format used across the system. Every log (meal, training, check-in, cardio, flag) must follow this shape for consistency, automation, and DSPy compatibility.

Logs are always:

Stored in NeonDB as flat JSON rows

Validated by Pydantic / jsonschema

Timestamped with ISO 8601 UTC

Source-labeled by engine

🔖 Unified Log Structure (V1)
Every log record must include the following base fields:

Field	Type	Required	Description
user_id	string	✅ Yes	Discord ID or UUID for the client
date	string	✅ Yes	YYYY-MM-DD, always client-local day
timestamp	string	✅ Yes	ISO 8601 full timestamp (UTC, with offset)
source_engine	string	✅ Yes	Origin of the log: "meal", "training", etc.
status	string	✅ Yes	completed, missed, underperformed, etc.
data	object	✅ Yes	Engine-specific payload

🔧 Log Examples
Meal Log

json
Copy
Edit
{
  "user_id": "1234",
  "date": "2025-05-21",
  "timestamp": "2025-05-21T06:01:22Z",
  "source_engine": "meal",
  "status": "completed",
  "data": {
    "meal_id": "planC_meal3"
  }
}
Training Log (Top Set)

json
Copy
Edit
{
  "user_id": "1234",
  "date": "2025-05-21",
  "timestamp": "2025-05-21T07:44:01Z",
  "source_engine": "training",
  "status": "completed",
  "data": {
    "exercise_id": "ex_dl_001",
    "exercise_name": "Deadlift",
    "weight_kg": 140,
    "reps": 6,
    "block_id": "steel_block_b",
    "day_index": 13
  }
}
Check-In Log

json
Copy
Edit
{
  "user_id": "1234",
  "date": "2025-05-21",
  "timestamp": "2025-05-21T05:34:00Z",
  "source_engine": "checkin",
  "status": "completed",
  "data": {
    "weight": 93.8,
    "mood": "😐",
    "soreness": "🟡",
    "stress": "⚡",
    "sleep": "🔥",
    "notes": "Feeling okay but a bit tight in the back."
  }
}
Cardio Log

json
Copy
Edit
{
  "user_id": "1234",
  "date": "2025-05-21",
  "timestamp": "2025-05-21T18:34:11Z",
  "source_engine": "cardio",
  "status": "underperformed",
  "data": {
    "assigned_minutes": 30,
    "actual_minutes": 24
  }
}
🧠 DSPy Expectations
DSPy expects logs in this unified shape. Any missing, malformed, or non-standard entries will be ignored or flagged as corrupted.

Every log must:

Use required base fields

Use schema-enforced data block (data key)

Match type definitions in schema_definitions.md

5. 🧱 Master DB Structure Summary
This section defines all database tables used across The Regiment, including their purpose, read/write relationships, and the engines that touch them.

The structure assumes NeonDB (PostgreSQL) with JSON-compatible fields where needed.

Each table must have:

A unique id (or composite key)

user_id as a foreign key to client_profiles

A timestamp and date for traceability

A contract defined in lst_schema_definitions.md

📦 Table: client_profiles
Field	Type	Description
user_id	string	Discord ID or UUID
timezone_offset	string	UTC+2, used for local time triggers
start_date	date	When the engines begin serving this client
paused	boolean	If true, suppress all drops
goal	string	cut, bulk, recomp
training_template_id	string	Current training template
meal_template_id	string	Current meal plan template
cardio_minutes	int	Assigned daily cardio target
macros	object	{protein: 210, carbs: 250, fats: 60}
block_id	string	Training block assigned
cycle_start_date	date	Start of current 7-day meal cycle

📦 Table: meal_logs
Field	Type	Description
user_id	string	Client ID
timestamp	string	Time of ✅ / ❌ button press
date	string	Client-local date
meal_id	string	templateB_meal2
status	string	completed, missed
source_engine	string	Always "meal"

📦 Table: training_logs
Field	Type	Description
user_id	string	Client ID
timestamp	string	Time of set log
date	string	Date of session
exercise_id	string	e.g. ex_bp_003
exercise_name	string	e.g. Incline DB Press
weight_kg	float	Logged top set weight
reps	int	Logged reps
block_id	string	Current training block
day_index	int	Relative day within the block
status	string	completed, missed
source_engine	string	Always "training"

📦 Table: checkin_logs
Field	Type	Description
user_id	string	Client ID
timestamp	string	Time of check-in
date	string	Date of check-in (client-local)
weight	float	Scale weight
mood	string	Emoji / coded value
soreness	string	Emoji or flag
stress	string	Emoji or flag
sleep	string	Sleep tier: 💤 / 🔥 / 😴
notes	string	Optional free-text field
source_engine	string	Always "checkin"

📦 Table: cardio_logs
Field	Type	Description
user_id	string	Client ID
timestamp	string	Time cardio log was entered
date	string	Local date of cardio
assigned_minutes	int	Daily target
actual_minutes	int	What was reported by client
status	string	completed, underperformed, missed
source_engine	string	Always "cardio"

📦 Table: job_cards
Field	Type	Description
user_id	string	Client ID
timestamp	string	Time of flag
date	string	Week ending on
summary	string	Text summary of DSPy findings
flags	object	List of triggered flags
action_suggested	string	Manual next step recommendation
resolved	boolean	Whether coach has taken action

📦 Table: pause_log (optional, v2+)
Field	Type	Description
user_id	string	Client ID
timestamp	string	When paused/unpaused
paused	boolean	True = paused, False = resumed
duration_days	int	Optional, how long pause lasted
reason	string	Optional text entered by coach

🧱 6. Known External Dependencies
This section clearly defines all non-internal systems, packages, libraries, and services the entire Regiment stack depends on. These are not optional and must be aligned across all engines and runners.

✅ Primary Runtime Dependencies
Dependency	Version / Spec	Role
Python	3.11+	Core runtime for all services
FastAPI	0.100+	Backend API routing and engine logic
discord.py	2.x	Bot interface, command handling, UI events (✅, ❌, inputs)
NeonDB (Postgres)	Serverless (v15+)	Primary data store for all client logs, flags, templates
Pydantic	v1.10+	Data schema definition and validation
jsonschema	Draft-07+	Cross-validation and downstream DSPy compatibility
APScheduler	3.x	Timezone-aware job scheduling per client
DSPy	0.4+	Flag engine — weekly job card generation, compliance scan

🧱 Optional but Supported Tools
Tool	When Used	Status
n8n	No-code automation/scheduling	Optional
OpenTelemetry	Logging, tracing, Prometheus hooks	Later
PostHog / Sentry	UX & error tracking	Later

✅ Frontend + Dev Flow
Tool/Layer	Role
Discord	Primary UX layer (bot-based command UI)
Local UI (React)	Battle Station dashboard for coach control
Cursor	Dev automation + build generator (runs from .source_of_truth.md)
GitHub / GitLab	CI/CD, version control
Docker (optional)	Local environment replication (for advanced testing/deploys)

💀 Non-Optional for Cursor Builds
Component	Reason for Strict Lock
Field naming (snake_case)	Ensures contract match across logs, FastAPI, and UI
ISO Timestamps	Needed for DSPy parsing and time calc
Unified schemas	Cursor will fail builds if drift is detected

✅ Final Note for Cursor Use:

Every dependency listed here must be locked in pyproject.toml or similar environment manifest.

No additions allowed unless explicitly spec'd in the master.
No “we’ll add it later” — Cursor requires the environment to be deterministic from Day 1.

7. 🧱 Error & Failure Handling Philosophy
This section defines how failures, missed logs, broken schedules, or missing data must be handled across all engines.

There is no silent fail logic in The Regiment.
Missed = Tracked.
Inconsistent = Flagged.
Failure = Logged.

✅ Core Handling Rules (All Engines)
Condition	System Response
✅ / ❌ button not clicked (meal or training)	Auto-log as status: "missed" by 22:00 local
Check-in not submitted by 12:00 local	Auto-log as missed + DSPy flag + Job Card created
Cardio underperformed	Auto-log with actual_minutes and status: "underperformed"
Start date in the future	Engine skip — no delivery, no logging
paused = true	Engine skip — but log that client is in paused state
Discord delivery fails (API issue)	Retry 3x, then raise log entry + send alert to Battle Station
DB write fails	Retry 3x, then save payload to local cache queue for re-ingest
Template missing (bad plan ID)	Fallback to default template (e.g. meal template A) + Job Card
Invalid schema (bad input)	Reject log, store in quarantine buffer, and raise Job Card

📡 Flagging Logic Summary
Every engine is required to escalate failures to DSPy or coach where relevant.

Trigger	Action
Missed 2+ meals in 48 hours	Flag → Job Card with “soft compliance” tag
Missed 2 training logs in 7 days	Flag → Job Card, even if meal compliance is 100%
Missed check-in + weight up	High priority flag → escalate to direct review
Cardio skipped 3x in a week	Escalate → “Grit failure” Job Card
Auto-switch triggered (defaulted to Template A)	Flag for “no response” compliance

🔐 Developer Contracts
Cursor and all engine modules must:

NEVER skip logic silently

Always write a log (status: missed) if an action was not completed

Never delete logs — only update with new timestamps or overrides

Always raise an alert if a Discord or DB action fails 3 times

Add failure logs to the source_engine table they belong to

🧠 DSPy Compliance Tracker
DSPy is expected to:

Scan all status != "completed" entries

Flag anything that matches known escalation rules

Track patterns over 7- and 14-day windows

Trigger Job Cards for coach review — but never act on its own

8. 🧱 Developer & Cursor Notes
This section captures all engineering guardrails, development discipline, and AI-coding assistant expectations to keep the MonsterCoach system stable, modular, and scalable — especially when Cursor is driving the build.

🔧 Cursor Prompting Protocol
Rule	Description
🔒 Always Load HST + LST	Cursor should always be loaded with both HST_New.md and LST_Master.md before any build begins. These are the system's high-level and low-level source of truth, and override any vague user input.
🧪 Test-First Thinking	Every module, especially those involving Discord or DSPy, must have example test cases provided before function or class code is written. Cursor should ask for inputs/outputs if missing.
🧱 Match Schema Contracts	Cursor must cross-reference schema_definitions.md or the correct contract from the LST before writing any logic involving data structures. All FastAPI routes must match input/output shape exactly.
⚠️ No Assumptions	If a field is ambiguous or missing, Cursor must prompt for clarification before proceeding. Never guess at structure, naming, or logic.
🧠 No Auto-Flexibility	Cursor must remember that this is a rigidity-first protocol: clients do not get options. All behavior is based on HST logic and coach-side overrides.
🛠️ Modular Engines Only	Cursor should never build monolithic logic. Every engine has its own runner, endpoint, schema, and state logic. Cursor must enforce that separation by default.
📦 One Source of Truth	Cursor must never create ad hoc schemas or implicit structures. All data must match known tables, contracts, or engine formats.
🔁 Prefer Stateless Logic	Where possible, Cursor should write functions and endpoints to be stateless and re-runnable (e.g., engine dispatch per client, based on passed client_id).
🧩 Use Explicit IDs	All entities (clients, plans, workouts, meals) must use id fields — never rely on string names or positional arrays. Cursor must enforce this for all storage and logic.
🚫 No Magic Defaults	Cursor should not introduce fallback values, defaults, or inferred behavior unless explicitly defined in HST or LST.
👮 Discipline-Driven System	Cursor must always favor rigidity, flags, and hard-coded rituals over soft UX. This is not a coaching assistant — it’s a command stack.

🧠 Cursor Setup Prompt (Reference Snippet)
This is the baseline you can paste into Cursor to start any structured build:

txt
Copy
Edit
Load these two files:
- HST_New.md (high-level design doctrine)
- LST_Master.md (low-level implementation contracts)

You are building a military-grade AI coaching system called MonsterCoach.

Do not make assumptions.
Do not allow user choices unless specified.
All logic follows rigid templates, fixed schedules, and structured compliance checks.

All outputs should follow modular engine architecture, Pydantic schema validation, and strict discipline-first delivery.

Always ask for clarification if a value or schema is undefined.

Do not use your imagination — follow the doctrine.

9. 🧱 schema_definitions.md Summary
This section outlines the purpose and structure of the schema definitions file. This file enforces strict input/output formats across all engines, ensures consistency in DB writes, and provides validation contracts for Cursor, FastAPI, and DSPy.

It will contain one schema (as a Pydantic model or JSON Schema block) per engine input and per log output.

✅ Purpose of schema_definitions.md
Goal	Description
Enforce contract precision	All data must match a declared shape before it enters any engine
Eliminate implicit logic	If a schema isn’t defined, the data cannot be used
Centralize structure	Keeps all field names, types, and constraints in one source
Make Cursor bulletproof	Cursor can reference this directly to generate code that "just works"

🧩 Required Schemas
Here’s what must be defined inside schema_definitions.md:

Schema Name	Used By Engine	Purpose
ClientProfileSchema	All	Main user info state
MealLogSchema	meal_delivery_engine	✅ / ❌ button presses
TrainingLogSchema	training_dispatcher	Top set input per exercise
CheckinSchema	checkin_analyzer	Daily weight, mood, soreness
CardioLogSchema	cardio_regiment_engine	Daily cardio duration
JobCardSchema	dspy_flag_engine	Weekly DSPy review summary
PauseLogSchema	all engines	Tracked when user is paused/unpaused
PlanChoiceSchema	onboarding_engine	Optional — client chooses plan (A, B, etc.)
FlagSummarySchema	DSPy internal	Internal schema for DSPy parsing

📦 Schema File Format
Schemas should be written in one of two formats:

Pydantic Models (recommended if using FastAPI)

python
Copy
Edit
class MealLogSchema(BaseModel):
    user_id: str
    date: str  # YYYY-MM-DD
    timestamp: datetime
    meal_id: str
    status: Literal["completed", "missed"]
JSON Schema (for downstream validation or DSPy)

json
Copy
Edit
{
  "type": "object",
  "properties": {
    "user_id": { "type": "string" },
    "date": { "type": "string", "format": "date" },
    "timestamp": { "type": "string", "format": "date-time" },
    "meal_id": { "type": "string" },
    "status": { "type": "string", "enum": ["completed", "missed"] }
  },
  "required": ["user_id", "date", "timestamp", "meal_id", "status"]
}
🧠 Cursor Enforcement Rule
Cursor builds must:

Always import and use the official schema from schema_definitions.md

Never invent their own field names or structures

Reference this file before generating Pydantic models or endpoint parameters

📁 File Location Convention
File Name	Location
schema_definitions.md	/lst/ root
Optional JSON Schemas	/schemas/json/ (for validation or external tools)