🧠 lst_dspy_flag_engine.md
Low-Level Source of Truth — DSPy Flag Engine

🎯 Purpose
The DSPy Flag Engine runs every Sunday at 22:00 UTC. It scans all logs from the previous 7 days, detects compliance failures, stagnation patterns, and discipline violations, and emits a Job Card per flagged client. It never adjusts plans — it only observes, calculates, and escalates.

1. ✅ Inputs
Field	Type	Source	Description
training_logs	dataset	training_logs	Used to check top set compliance, PR trends
meal_logs	dataset	meal_logs	Used to detect missed meals
checkin_logs	dataset	checkin_logs	Used to detect missed days and weight stalling
cardio_logs	dataset	cardio_logs	Used to detect underperformance
client_profiles	table	client_profiles	Needed for goal reference and timezone

2. 🧠 Internal State / Persistence
Field	Table	Description
job_cards	job_cards	Stores output cards per client per week
flag_history	DSPy cache	Tracks which flags have fired previously

3. 🔧 Actions
Action	Trigger	Description
scan_weekly_logs()	Sunday 22:00 UTC	Runs weekly scan on all active clients
generate_job_card()	On flag detection	Assembles job card with summary + suggestions

4. 🔁 State Transitions
scan_weekly_logs():

Aggregates logs by user

Calculates:

Missed logs (meals, training, check-ins)

Stalled lifts (same weight >2 weeks)

Weight stalling (weight static with 100% compliance)

Cardio missed/underperformed 3x+

generate_job_card():

Creates job_cards entry with:

Summary string

List of triggered flags

Action suggestion

resolved: false

5. 📤 Output Events
Event	Format	Destination	Description
Weekly Job Card	DB row	job_cards	One per client with any flags
Coach Alert	Discord	Battle Station	Optional alert ping for violations

6. ❌ Error Handling
Condition	Handling
Client paused or no data	Skip, no card generated
DB read fails	Retry 3x → log in error buffer
Flags can't be computed	Insert job card with "flag_parse_error"

7. ✅ Validation & Invariants
Rule	Enforcement
One job card per client per week	Enforced via date and user_id combo
Flags must match enum list	e.g. missed_checkin, weight_stall
Suggestion must be predefined strings	e.g. "callout", "reassign", "pause"
Summary must be concise (<500 chars)	Truncated if too long

8. ⏰ Timing & Execution
Action	Schedule
scan_weekly_logs()	Sunday 22:00 UTC

Global runner (not client-local)

Must finish < 15 minutes (non-blocking)

9. 🔗 Dependencies
System	Use
NeonDB	Read/write log + job_card data
DSPy Core	Pattern detection, escalation logic
Discord Bot	Sends coach alerts (optional)
Battle Station	UI renders flagged clients

10. 🧠 AI Build Prompt
txt
Copy
Edit
You are Cursor.

Build the DSPy Flag Engine using the following contract:

Every Sunday at 22:00 UTC, scan the logs for all clients over the past 7 days.

Check for:
- Missed meals (2+)
- Missed workouts (2+)
- Missed check-ins (1)
- Cardio missed or underperformed (3+ times)
- Lifts that have not progressed for 3+ attempts
- Weight stall despite 100% meal compliance

For each flagged client, generate a Job Card.  
Job Card must contain:
- user_id
- date (week ending)
- summary string (<500 chars)
- list of flags
- suggestion string (coach action)
- resolved = false

Write to `job_cards` table.  
All fields must match `JobCardSchema` in `schema_definitions.md`.  
No action should be taken by DSPy itself — only Coach decides what to do.
