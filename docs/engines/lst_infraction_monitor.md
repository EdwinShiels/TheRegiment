# 🚨 Low-Level Source of Truth — Infraction Monitor

## 🎯 Purpose
The Infraction Monitor is the passive compliance sentinel.  
It aggregates missed actions (meals, training, cardio, check-ins), escalates warnings, and optionally triggers accountability-based restrictions.

This engine does **not deliver anything**.  
It **scans** logs, flags repeat failures, and optionally:
- Sends private warnings
- Blocks privileges like refeeds
- Shames public rule-breakers (if configured)

---

## 🔁 Trigger

| Condition           | Value                |
|---------------------|----------------------|
| Engine Trigger      | APScheduler hourly   |
| Trigger Time (UTC)  | Every hour           |
| Action Scope        | All active clients   |

---

## ✅ Inputs

| Field             | Source Engine       | Description                          |
|------------------|---------------------|--------------------------------------|
| `user_id`        | All engines         | Unique client ID                     |
| `status`         | Meal, training, etc | `"missed"` status flag               |
| `date`           | All logs            | Daily log timestamp (client-local)   |
| `paused`         | `client_profiles`   | If true, skip this user              |
| `start_date`     | `client_profiles`   | If in future, skip delivery          |
| `goal`           | `client_profiles`   | Needed to evaluate infraction risk   |

---

## 🧠 Internal State Tracked

| Variable             | Type       | Description                              |
|----------------------|------------|------------------------------------------|
| `infraction_streak`  | int        | Number of consecutive infractions        |
| `last_infraction`    | date       | Date of last known violation             |
| `infraction_type`    | string     | `"meals"`, `"training"`, `"cardio"`, etc.|
| `warnings_sent`      | int        | Number of private alerts sent            |
| `public_callout`     | boolean    | If public shame was already triggered    |
| `blocked_refeed`     | boolean    | If client is locked from refeed access   |

---

## 🛠️ Actions

### 1. Scan Infractions (Run per user)

| If Condition                            | Then Action                               |
|----------------------------------------|-------------------------------------------|
| Missed 2+ meals in 48hr                | Create Job Card with tag: `soft compliance` |
| Missed 2+ trainings in 7 days          | Create Job Card: `training inconsistency` |
| Missed check-in 2x in a week           | Create Job Card: `non-responding client`  |
| Cardio skipped 3+ times in week        | Create Job Card: `grit violation`         |

---

### 2. Escalation Triggers (Optional config)

| Condition                              | Action                                    |
|----------------------------------------|-------------------------------------------|
| 3+ infractions in 7 days               | Send Discord DM: `“You’re slipping.”`     |
| 5 infractions in 10 days               | Add `blocked_refeed: true` to profile     |
| 7+ in 14 days                          | Post to Discord public channel (if enabled) |

---

## 🧾 Output Events

| Output Type        | Format        | Trigger Condition                           |
|--------------------|---------------|----------------------------------------------|
| `Job Card`         | DB Write      | On each rule violation                       |
| `Discord DM`       | Private Msg   | After 3+ infractions                         |
| `Refeed Block`     | DB Flag       | On reaching configured threshold             |
| `Public Callout`   | Discord Msg   | If enabled and 7+ violations in 14 days      |

---

## ⚠️ Failure Handling

| Failure Condition            | System Response                               |
|-----------------------------|-----------------------------------------------|
| No logs found               | Do nothing                                    |
| Missing user_id             | Skip this record                              |
| paused = true               | Skip all logic for this user                  |
| Log write failure           | Retry 3x then raise alert in Battle Station   |
| Invalid log structure       | Store in quarantine + flag for schema review  |

---

## 🔁 Dependencies

| Dependency         | Purpose                        |
|--------------------|--------------------------------|
| `meal_logs`        | Source of missed meal data     |
| `training_logs`    | Source of missed workouts      |
| `checkin_logs`     | Source of missed check-ins     |
| `cardio_logs`      | Source of skipped cardio       |
| `client_profiles`  | Lookup for goal, start_date    |
| `job_cards`        | Flag output for coach action   |
| Discord Bot API    | DMs or public callout messages |

---

## 📦 Sample Job Card

```json
{
  "user_id": "1248",
  "date": "2025-06-02",
  "timestamp": "2025-06-02T12:00:00Z",
  "summary": "Client missed 3 meals, 2 trainings, and 1 check-in this week.",
  "flags": ["soft_compliance", "training inconsistency"],
  "action_suggested": "DM for compliance talk. Block refeed.",
  "resolved": false
}

🧠 Notes for Cursor
This engine only reads and flags — no deliveries

Must be able to toggle public shame + refeed block in config

Must use same status: missed format across all logs

Cursor must check for paused = true and start_date > today

All outputs must write into job_cards with full flag trace