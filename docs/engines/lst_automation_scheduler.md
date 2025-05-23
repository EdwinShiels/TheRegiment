⚙️ lst_automation_scheduler.md
Low-Level Source of Truth — Automation Scheduler Engine

🎯 Purpose
The Automation Scheduler is the timekeeper of The Regiment. It runs the master clock across all timezones and engines.
It ensures daily delivery and compliance actions are triggered per client at the right time using timezone offsets and interval checks.

This is not a logic engine.
It is a dispatcher and trigger system.

🔁 Execution Model
Trigger Type	Frequency	Description
Client-based	Every hour	Evaluates all active clients for trigger windows
Global-based	Fixed UTC	Executes global scans (e.g. DSPy job cards)
Error Retry Queue	Every 5 min	Retries failed Discord/API events

✅ Inputs
Field	Type	Source	Description
user_id	string	client_profiles	Used to target engine activation
timezone_offset	string	client_profiles	Used to calculate local trigger windows
start_date	date	client_profiles	Suppresses actions until date is reached
paused	boolean	client_profiles	Suppresses all activity if true
engine_state	dict	Internal (optional)	Tracks if action was already triggered today

🧠 State Tracked
Variable	Type	Description
last_triggered	timestamp	When engine was last run for this user
daily_queue	list	Pending jobs to dispatch for the hour
global_queue	list	Once-a-day scans (e.g. DSPy flag engine)

⏰ Task Table
Time (local / UTC)	Action Description	Engine Triggered
05:30 local	Drop check-in prompt	checkin_analyzer
06:00 local	Drop meals, cardio	meal_delivery, cardio_regiment
07:00 local	Drop training (if scheduled)	training_dispatcher
12:00 local	Auto-log missed check-in	checkin_analyzer
22:00 local	Auto-log missed meals, workouts, cardio	respective engines
22:00 UTC (Sunday)	Global scan & flag pass	dspy_flag_engine
Every hour	Trigger engine queues by offset	All local-time engines

🔧 Actions
Function	Description
schedule_tasks()	Prepares per-user queue from timezone logic
run_task(task)	Triggers correct engine input
retry_failed()	Reattempts failed events from last run
run_global_scan()	DSPy + honors board on fixed UTC

❌ Failure Handling
Failure Type	System Response
Engine run failure	Log error, add to retry queue
Discord delivery fails	Retry up to 3x, escalate to alert buffer
Invalid time format	Skip user and flag Job Card
Paused or future client	Skip silently, no logging

🔗 Dependencies
System	Use
APScheduler	Base task queue / hourly heartbeat
FastAPI	Interface for event triggers (optional)
Discord Bot	For engine drops that require delivery
NeonDB	Pull user schedule and status
All Engines	Triggered by scheduler dispatcher

✅ Invariants
Rule	Enforced Logic
Each engine must run only once per day per user	Timestamp tracked internally
Global scans must not run per-client	Triggered once only at UTC
Engine calls must validate client active state	paused/start_date check enforced

🧠 AI Build Prompt
txt
Copy
Edit
You are Cursor.

Build the Automation Scheduler using the following contract:

Use APScheduler to run an hourly trigger.

Each hour:
- For every client, use their `timezone_offset` and check what time it is locally.
- If the current local time matches a registered task (like 06:00), dispatch the related engine (e.g. `meal_delivery_engine`) for that user.
- Enforce `paused = false` and `start_date <= today` before any engine runs.
- Do not allow duplicate runs — track per-user trigger history.

Also:
- Every Sunday at 22:00 UTC → run `dspy_flag_engine` for all clients
- Implement a retry mechanism for failed engine executions (e.g. Discord API)

All task schedules are defined in `lst_master.md`.
Do not drift from that definition. This engine is the nerve center.
