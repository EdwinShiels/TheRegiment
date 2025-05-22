🧾 lst_onboarding_engine.md
Low-Level Source of Truth — Onboarding Engine

🎯 Purpose
This engine captures all vital client metadata (goal, timezone, assigned templates, macros, cardio) and initializes their state into the client_profiles table. It can be triggered manually via Discord command or form intake.

1. ✅ Inputs
Field	Type	Source	Description
user_id	string	Discord bot	Discord user ID
timezone_offset	string	Manual (form)	Client’s local timezone (e.g., UTC+2)
goal	enum	Manual (coach-selected)	cut, bulk, or recomp
start_date	date	Coach-selected	Date when system activates (default: Tuesday)
paused	boolean	System default	Always false at creation
training_template_id	string	Coach-selected	ID of assigned training plan (e.g. steel_block_a)
meal_template_id	string	Client-selected (or A)	Plan A/B/C/D or default
macros	object	Coach-calculated	{ protein: 210, carbs: 240, fats: 70 }
cardio_minutes	int	Coach-assigned	Initial target cardio per day
block_id	string	From training template	Training block ID (if segmented)
cycle_start_date	date	Auto-set (nearest Saturday)	Meal cycle control, can override manually
height_cm	int	Manual or form	Client's height (for body comp calc)
weight_kg	float	Manual or first check-in	Starting weight at onboarding

2. 🧠 Internal State / Persistence
All fields above are stored in the client_profiles table.

paused = false at creation unless overridden

start_date is used by all runners to suppress engines before start

cycle_start_date used by Meal Engine to manage 7-day rotation

meal_template_id selection locks 7-day meal assignment

training_template_id determines what block schedule is used

No logs are written by this engine — only DB write to profile

3. 🔧 Actions
Action	Trigger	Description
submit_onboarding()	Coach or Discord /onboard	Ingests all fields and stores to DB
edit_onboarding()	Coach via UI	Updates fields (goal, plan, etc)

4. 🔁 State Transitions
On creation: inserts full client_profiles row

On edit: updates only changed fields

On paused = true: other engines skip client

On start_date > today: other engines defer start

5. 📤 Output Events
DB insert into client_profiles table

If Discord-triggered, returns success message in DM

Triggers no downstream engine

Can be read by all engines that use client_profile (Meal, Training, Check-In, etc.)

6. ❌ Error Handling
Condition	Handling
Missing timezone_offset	Reject input, prompt for fix
Missing meal_template_id	Assign default (template_a)
Missing macros	Block save, raise error
Invalid enum (goal)	Reject — must be cut, bulk, or recomp

7. ✅ Validation & Invariants
All required fields must be present at creation

macros must contain all 3 keys

paused must be boolean only

start_date must not be in past unless overridden manually

8. ⏰ Timing & Execution
Manual trigger from coach UI or Discord

Runs once per client

Must complete before any engine begins processing that user

9. 🔗 Dependencies
Dependency	Contract
discord.py bot	Discord user ID for message delivery
NeonDB	client_profiles table schema
Battle Station UI	Coach-facing edit/submit form

10. 🧠 AI Build Prompt
txt
Copy
Edit
You are Cursor.  
Build a FastAPI endpoint or Discord command that ingests a new user profile into the `client_profiles` table.  
Use the exact field list from the Onboarding Engine LST.  
Assign default values where noted, validate all enums, and reject missing data.  
Do not guess at field names — follow schema_definitions.md.  
Only allow onboarding to run once unless overridden by coach.  
Log creation timestamp in ISO 8601 UTC.  