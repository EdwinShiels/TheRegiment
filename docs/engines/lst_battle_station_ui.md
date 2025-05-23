🖥️ lst_battle_station_ui.md
Low-Level Source of Truth — Battle Station UI

🎯 Purpose
This is your high-command dashboard — the control tower of The Regiment. It gives you real-time visibility into all clients, flags, logs, meal/cardio/macros sliders, and the ability to assign new plans or pause clients.

This is a coach-only interface.
Clients never interact with this.
Built for ruthless visibility, accountability, and control.

🧱 Top-Level Layout
1. 🔲 Client Cards (Dashboard View)
Rendered in a grid layout, 1 card per client

Live status at a glance:

✅ Meals Today

🏋️ Training Logged

⚖️ Check-In Done

🔥 Infractions

🎯 Goal

⚠️ Flags (if any)

🕒 Timezone

Clicking a client card opens their detailed view.

2. 🧠 Job Cards Panel (Top Banner)
Live list of open DSPy-generated Job Cards

Sorted by severity + age

Each card includes:

Client ID + name

Flag(s)

Suggested action

Button: Resolve (marks as handled)

📂 Client Detail View
Section A: Client Profile
Field	Editable?	Notes
Discord handle	No	Auto-linked
Goal	Yes	cut, bulk, recomp
Start Date	Yes	Must be ≤ today
Paused	Yes	Toggle = engine skip
Timezone Offset	Yes	Format: UTC+X
Height / Weight	Yes	Used for comp/macro calc

Section B: Assignments
Assignment	Type	Interaction
Training Template	Dropdown	Choose from training_templates DB
Meal Template	Dropdown	A/B/C/D (rotating) or custom plan ID
Cardio Minutes	Slider	0 → 90 min/day
Macros	Sliders	P / C / F (locked to sum if enabled)

Each change triggers an "Apply" button that writes directly to client_profiles.

Section C: Logs Viewer
Tabs for:

Meals

Training

Cardio

Check-ins

Each tab shows:

7-day table with ✅ / ❌ / ⚠️ per log

PR tracking (for lifts)

Weight chart with 7-day moving average

Soreness / Mood emoji over time

🛠️ UI Actions & Writebacks
Action	DB Change	Notes
Assign new training plan	client_profiles	Effective from today
Apply new macros	client_profiles	Affects next meal cycle
Pause / unpause client	client_profiles	All engines respect this field
Resolve job card	job_cards.resolved=true	Removes it from dashboard
Edit timezone / goal	client_profiles	Real-time effect

🧾 Output Events
UI Action	Resulting DB Change
Apply Macros / Cardio	client_profiles updated
Assign Plan (Meal/Train)	Template ID saved
Job Card Resolved	resolved: true flag set

✅ Validation & Constraints
Constraint	Enforcement
No client can have empty macros	Block "Apply" unless valid
Meal template must be valid ID	Drop if not A/B/C/D or in templates table
Goal must be one of allowed enums	Cut, Bulk, Recomp only
Paused = true disables write actions	Locks form fields until unpaused

🧠 AI Build Prompt
txt
Copy
Edit
You are Cursor.

Build the Battle Station UI using the following spec:

Main view = dashboard of all clients (as cards).  
Each card shows live compliance state, timezone, flags.  
Top bar shows all open Job Cards.  
Clicking a client opens detail view with:

- Profile editor
- Training / Meal / Cardio assignment
- Macro and cardio sliders
- History of logs per engine
- Weight curve
- Button to resolve flags

All changes write to `client_profiles` or `job_cards`.  
UI must enforce validation rules for macros, goals, templates.  
Paused clients should be greyed out and non-editable.

This UI is for coaches only. Clients never access this.
