🍽️ lst_meal_delivery_engine.md
Low-Level Source of Truth — Meal Delivery Engine

🎯 Purpose
Delivers a rigid, 7-day meal plan to each client at 06:00 in their local timezone, with ✅ / ❌ buttons for logging compliance per meal. Tracks execution discipline, syncs to DSPy for compliance analysis, and auto-logs missed meals. Shopping list is dropped weekly, based on chosen template. No calorie display, no flexibility.

1. ✅ Inputs
Field	Type	Source	Description
user_id	string	client_profiles	Discord ID of client
meal_template_id	string	client_profiles	Template assigned to user (e.g. template_b)
cycle_start_date	date	client_profiles	Start of current 7-day meal cycle
timezone_offset	string	client_profiles	Local timezone offset (e.g. UTC+2)
paused	bool	client_profiles	Suppress engine if true
start_date	date	client_profiles	Suppress engine if start date > today

2. 🧠 Internal State / Persistence
Field	Table	Description
meal_logs	meal_logs	Stores per-meal ✅ / ❌ with timestamp
client_profiles	Global table	Holds plan assignment and timing data
meal_templates	System file	JSON of all plan templates (A/B/C/D etc)
current_day_index	derived	Auto-calculated from cycle_start_date and today

3. 🔧 Actions
Action	Trigger	Description
drop_meal_plan()	Daily at 06:00 client time	Posts meals with buttons for each meal
log_meal_click()	On ✅ / ❌ button press	Writes meal log to DB with timestamp
drop_shopping_list()	Every cycle_start_date	Sends list of ingredients + prep instructions
cycle_reset()	Every 7th day	Rotates template if user selected one

4. 🔁 State Transitions
Each ✅ / ❌ click:

Inserts into meal_logs

Logs status, timestamp, and meal_id

At 22:00 local if no click:

Auto-log status: "missed" in DB

Every 7 days:

Meal plan resets, shopping list is sent

If no selection made → fallback to template_a

5. 📤 Output Events
Event	Format	Destination	Description
Daily meal drop	Discord	Client DM/channel	Markdown post with all meals + ✅ ❌
Meal log	DB row	meal_logs	Includes user_id, timestamp, meal_id
Shopping list post	Discord	DM (weekly)	Bulk ingredient list w/ prep file
Missed meal fallback	DB row	meal_logs	status: missed if no interaction

6. ❌ Error Handling
Condition	Handling
Template missing	Default to template_a, raise Job Card
No meal log by 22:00	Auto-log as missed
Delivery fails (API error)	Retry 3x → alert → skip w/ alert in Battle Station
Client paused or not started	Skip meal drop, no log written

7. ✅ Validation & Invariants
Rule	Enforcement
Must have 3–4 meals/day	All templates must include 3–4 items
Each meal must have ✅ ❌ buttons	Auto-generated with each message
Timezone offsets must resolve valid 06:00 trigger	APScheduler checks hourly
All logs must be timestamped (ISO 8601)	Enforced by schema

8. ⏰ Timing & Execution
Action	Schedule
Meal drop	06:00 daily (client)
Shopping list drop	06:00 on cycle_start_date
Missed meal log	22:00 local (if no click)

Triggered by APScheduler (hourly tick)

All time logic adjusted by timezone_offset

9. 🔗 Dependencies
System	Use
Discord bot	Sends daily post with buttons
NeonDB	Writes meal_logs entries
APScheduler	Runs 06:00 and 22:00 checks
DSPy	Reads missed logs weekly

10. 🧠 AI Build Prompt
txt
Copy
Edit
You are Cursor.

Build the Meal Delivery Engine using the following contract:

At 06:00 client-local time, post a Discord message showing today's meals from the client’s assigned 7-day template (template_a/b/c/d). Each meal has a ✅ / ❌ button.

On button press, log a row in `meal_logs` with user_id, meal_id, timestamp, and status.

If no click is logged by 22:00, auto-log the meal as `missed`.

Every 7 days from `cycle_start_date`, post a shopping list with weights and instructions. If no new plan was selected, fallback to `template_a`.

All schema fields must match `schema_definitions.md`.
All scheduling uses `timezone_offset` and APScheduler hourly runner.
Do not allow plan edits from user side. Discipline is enforced, not requested.
