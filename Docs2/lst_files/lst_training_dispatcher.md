🏋️ lst_training_dispatcher.md
Low-Level Source of Truth — Training Dispatcher Engine

🎯 Purpose
Delivers one full workout per assigned training day from the client’s template block, including sets/reps and rest periods per exercise. Requires client to log top set (final set) for every exercise. Logs are tracked and synced to DSPy for progression analysis and compliance enforcement. This is not optional — it’s execution or violation.

1. ✅ Inputs
Field	Type	Source	Description
user_id	string	client_profiles	Discord ID of client
training_template_id	string	client_profiles	Assigned block ID for workout generation
timezone_offset	string	client_profiles	Used for 07:00 delivery trigger
start_date	date	client_profiles	Suppresses delivery if not reached
paused	bool	client_profiles	Suppresses engine if true
block_id	string	client_profiles	Current program block (e.g. steel_block_A)
day_index	int	Internal derived	Relative day in the block
schedule_days	array	training_template	Days of the week this client trains (e.g. MWF)

2. 🧠 Internal State / Persistence
Field	Table	Description
training_logs	training_logs	Stores one log per exercise, per session
day_index	Internal / DB	Tracks client’s relative day in plan
exercise_history	derived lookup	Used to show last top set on delivery

3. 🔧 Actions
Action	Trigger	Description
drop_training()	07:00 client-local	Posts full workout for today
log_top_set()	User modal entry (weight/reps)	Stores per-exercise set log
check_for_missed_logs()	22:00 client time	Flags any exercises with missing top set log

4. 🔁 State Transitions
drop_training():

Looks up training block + current day_index

Posts each exercise with reps, sets, rest

Includes last logged top set for reference (if available)

log_top_set():

One log per exercise → written to training_logs

Auto-updates exercise history for future recall

missed:

If top set not logged by 22:00 → insert status: missed with blank reps/weight

5. 📤 Output Events
Event	Format	Destination	Description
Daily workout message	Discord	Client DM/channel	Markdown list + top set inputs
Log entries (each)	DB row	training_logs	One per exercise
Missed log fallback	DB row	training_logs	Status = missed, if none entered

6. ❌ Error Handling
Condition	Handling
No training today (not scheduled)	Engine skip, no log
Client paused or start date not reached	Suppress engine
Missing block_id or invalid template	Job Card + fallback to default
Discord post fails	Retry 3x → escalate alert
Top set input invalid (bad weight/reps)	Reject log and show error prompt

7. ✅ Validation & Invariants
Rule	Enforcement
Top set must be logged once per exercise	Enforced by 22:00 deadline per day
Weight must be float or int ≥ 0	Enforced in modal + schema
Reps must be int ≥ 1	Enforced in modal + schema
day_index advances only on training day	Used to control progression
Rest timer per exercise is required	Shown with each drop, coach-defined

8. ⏰ Timing & Execution
Action	Schedule
drop_training()	07:00 client time (if scheduled day)
log_top_set()	Anytime after post
check_for_missed_logs()	22:00 client time

All engine triggers checked hourly via APScheduler

Training only drops if today matches assigned day

9. 🔗 Dependencies
System	Use
Discord bot	Workout post + top set modal
NeonDB	Training logs + lookup cache
APScheduler	Triggers delivery + check-ins
DSPy	Weekly compliance scan
Battle Station	Coach can reassign block, view logs

10. 🧠 AI Build Prompt
txt
Copy
Edit
You are Cursor.

Build the Training Dispatcher Engine using the following contract:

At 07:00 client-local time (if today is a scheduled training day), post a Discord message with the day’s workout — showing sets, reps, rest time, and top set from last session (if available).

For each exercise, require client to enter top set (weight, reps) via modal. This must be logged before 22:00 or it is marked missed.

Each logged set creates a row in `training_logs` with: user_id, timestamp, date, exercise_id, exercise_name, weight_kg, reps, block_id, day_index, status.

If client is paused, not started, or today is not a training day → skip.

All schema fields must match `schema_definitions.md`.  
Rest time must be displayed with each exercise.

Do not allow partial workouts — each top set must be logged or missed.  
No RPE. No options. This is a discipline module.