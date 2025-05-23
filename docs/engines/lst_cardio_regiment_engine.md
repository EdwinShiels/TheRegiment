🏃 lst_cardio_regiment_engine.md
Low-Level Source of Truth — Cardio Regiment Engine

🎯 Purpose
Delivers daily cardio assignment based on the client’s current phase (cut, bulk, recomp). Logs duration (actual vs assigned), enforces compliance, and reports missed or underperformed sessions to DSPy. Designed to harden discipline, not to accommodate preference.

1. ✅ Inputs
Field	Type	Source	Description
user_id	string	client_profiles	Discord ID of the client
cardio_minutes	int	client_profiles	Coach-assigned daily cardio duration target
timezone_offset	string	client_profiles	Used for 06:00 delivery
start_date	date	client_profiles	Suppresses delivery if future
paused	bool	client_profiles	Suppresses engine if true

2. 🧠 Internal State / Persistence
Field	Table	Description
cardio_logs	cardio_logs	Stores daily actual_minutes + status
client_profiles	client_profiles	Reads cardio_minutes & scheduling
last_7_day_curve	DSPy-derived	Used to calculate underperformance streaks

3. 🔧 Actions
Action	Trigger	Description
drop_cardio_block()	06:00 daily (client)	Sends assigned cardio with prompt + explanation
log_cardio()	User response via modal	Stores actual_minutes in cardio_logs
check_for_skip()	22:00 daily (client)	Auto-log as missed if no response

4. 🔁 State Transitions
drop_cardio_block():

Uses cardio_minutes from profile

Delivers Discord message with rigid instruction, zone guidance, and reminder

log_cardio():

Client enters minutes completed via modal

If actual_minutes < assigned → status = underperformed

If matched or exceeded → status = completed

missed:

No entry by 22:00 → auto-log status = missed, actual_minutes = 0

5. 📤 Output Events
Event	Format	Destination	Description
Daily cardio message	Discord	Client DM/channel	Markdown post with assignment & modal
Cardio log entry	DB row	cardio_logs	Timestamp, assigned, actual, status
Missed auto-log	DB row	cardio_logs	Triggers if no entry by 22:00

6. ❌ Error Handling
Condition	Handling
Client paused or start date not reached	Skip engine
Discord post fails	Retry 3x → escalate to Battle Station
Invalid minutes input	Reject + reprompt with constraint explanation
No log by 22:00	Auto-log as missed, flag if repeat

7. ✅ Validation & Invariants
Rule	Enforcement
Input must be integer ≥ 0	Enforced in modal UI
Actual must be logged daily	22:00 check writes missed if absent
Assigned value always pulled from profile	No dynamic assignment
Status must be: completed, underperformed, or missed	Locked enum

8. ⏰ Timing & Execution
Action	Schedule
drop_cardio_block()	06:00 client time
log_cardio()	Anytime post-drop
check_for_skip()	22:00 client time

Engine must be timezone-aware (via timezone_offset)

APScheduler checks every hour for drops + checks

9. 🔗 Dependencies
System	Use
Discord bot	Cardio drop + modal capture
NeonDB	Writes to cardio_logs
APScheduler	Handles drop + 22:00 enforcement
DSPy	Reads logs for compliance trends

10. 🧠 AI Build Prompt
txt
Copy
Edit
You are Cursor.

Build the Cardio Regiment Engine using the following contract:

At 06:00 client-local time, send a Discord message assigning the client their daily cardio task (from their `cardio_minutes` field in `client_profiles`).  
The message should explain that cardio is mandatory, target Zone 2–3, and must be logged by the end of the day.

Client logs cardio via modal with `actual_minutes`.  
If actual < assigned → status = `underperformed`.  
If actual = assigned or more → status = `completed`.  
If no entry by 22:00 → auto-log as `missed`.

Cardio logs are written to `cardio_logs` with user_id, timestamp, assigned_minutes, actual_minutes, and status.

Follow all validation, timing, and trigger rules from LST_Master.md.  
No flexibility, no excuses, no skipping logs.