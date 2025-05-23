⚖️ lst_checkin_analyzer.md
Low-Level Source of Truth — Check-In Analyzer Engine

🎯 Purpose
This engine drops a check-in prompt every morning at 05:30 (client time). It collects scale weight, mood, soreness, sleep, stress, and optional notes. This log is the cornerstone of DSPy’s trend detection. Missed logs result in automatic flagging and a Job Card for coach review.

1. ✅ Inputs
Field	Type	Source	Description
user_id	string	client_profiles	Discord user ID of client
timezone_offset	string	client_profiles	Used for 05:30 local delivery trigger
paused	bool	client_profiles	Suppresses delivery if true
start_date	date	client_profiles	Suppresses delivery if future

2. 🧠 Internal State / Persistence
Field	Table	Description
checkin_logs	checkin_logs	Each check-in log is stored here
last_checkin	derived	DSPy uses this to calculate compliance

3. 🔧 Actions
Action	Trigger	Description
drop_checkin()	05:30 local (daily)	Posts prompt in Discord for check-in log
log_checkin()	Modal response	Stores all check-in fields in DB
check_for_missed()	12:00 local	If not submitted, auto-log and flag

4. 🔁 State Transitions
drop_checkin():

Posts modal with fields:

Weight (kg)

Mood (emoji scale: 💪 😐 😕)

Soreness (🟢 🟡 🔴)

Stress (🧘 ⚡ 🔥)

Sleep (😴 🔥 💤)

Notes (optional free text)

log_checkin():

All fields validated, stored in checkin_logs

Timestamped with ISO 8601

missed:

No response by 12:00 → log with status = missed

Triggers Job Card with check-in noncompliance flag

5. 📤 Output Events
Event	Format	Destination	Description
Check-in log	DB row	checkin_logs	One entry per day
Missed fallback	DB row	checkin_logs	status = missed, no metrics
DSPy flag request	Internal	DSPy flag queue	Job Card generated if missed

6. ❌ Error Handling
Condition	Handling
Client paused or start_date not reached	Suppress engine
Discord delivery fails	Retry 3x → alert to Battle Station
Modal submission invalid	Reject + prompt again
No log by 12:00	Auto-log missed + create Job Card

7. ✅ Validation & Invariants
Rule	Enforcement
Weight must be ≥ 30kg	Reject if too low (sanity check)
Mood / soreness / sleep / stress must be valid emoji	Strict enum check
Notes = optional	Can be empty
Log must include timestamp, date, and status	All enforced on write
One check-in per day per client	Unique constraint enforced by schema

8. ⏰ Timing & Execution
Action	Schedule
drop_checkin()	05:30 client time
check_for_missed()	12:00 client time

All timing logic respects timezone_offset

APScheduler runner enforces delivery + compliance checks

9. 🔗 Dependencies
System	Use
Discord bot	Sends modal for check-in
NeonDB	Logs check-ins into checkin_logs
APScheduler	Triggers both delivery + fallback
DSPy	Scans for missed/stalled patterns
Battle Station	Coach sees missed flags, Job Cards

10. 🧠 AI Build Prompt
txt
Copy
Edit
You are Cursor.

Build the Check-In Analyzer Engine using the following contract:

At 05:30 client-local time, send a Discord modal prompting for check-in:

- Weight (kg)
- Mood (💪 😐 😕)
- Soreness (🟢 🟡 🔴)
- Stress (🧘 ⚡ 🔥)
- Sleep (😴 🔥 💤)
- Notes (optional)

Client submits response via modal. It is stored in `checkin_logs` with timestamp, date, and status: "completed".

If no check-in is received by 12:00 client time → auto-log with status: "missed" and create a Job Card.

All values must be validated against emoji enums and type guards.  
No skipping, no soft failure. This check-in is mandatory for DSPy analysis.
