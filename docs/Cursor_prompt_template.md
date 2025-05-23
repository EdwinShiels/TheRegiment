# 🎯 Cursor AI Prompting Guide for buildspec.yaml

## 📜 Purpose
This document provides optimal prompting strategies for leveraging the buildspec.yaml with Cursor AI to achieve maximum implementation accuracy and efficiency.

---

## 🎯 **PHASE-SPECIFIC PROMPTING**

### **Start with exact phase targeting:**
```
"Implement Phase 4 - Meal Delivery Engine according to buildspec.yaml. Focus on the meal_delivery_runner module with pydantic_schemas: ['ClientProfileSchema', 'MealLogSchema', 'MealTemplateSchema']. Ensure 06:00 client timezone delivery with pause_check_logic."
```

### **Reference specific success criteria:**
```
"Build this module to meet success criteria: 'Daily 06:00 meal protocol delivery' and '✅/❌ button logging functional' from Phase 4."
```

---

## 🔗 **DEPENDENCY-AWARE PROMPTING**

### **Always reference dependencies:**
```
"Implement Phase 8 - Infraction Monitor. This depends on phases [0,1,2,4,5,6,7]. Use the schemas from meal_logs, training_logs, cardio_logs, checkin_logs as defined in the dependencies."
```

---

## 📋 **SCHEMA-FIRST PROMPTING**

### **Lead with schema enforcement:**
```
"Create the pydantic models for Phase 2 using EXACTLY the schemas defined in docs/schema_definitions.md. Ensure ClientProfileSchema includes user_id, goal (cut|bulk|recomp), timezone_offset (UTC±X), and all fields match the buildspec pydantic_schemas array."
```

---

## 🎯 **MODULE-SPECIFIC PROMPTING**

### **Target individual modules with full context:**
```
"Build the 'timezone_manager' module from Phase 10 (src/engines/scheduler/timezone_calc.py). Implement parse_timezone_offset(), convert_utc_to_client_time(), and validate_timezone_format() with validation rules: Format UTC±X, Range UTC-12 to UTC+14."
```

---

## ⚠️ **FAILURE-MODE AWARE PROMPTING**

### **Include failure handling requirements:**
```
"Implement meal_delivery_runner with these failure modes: 'Discord timeout → retry 3x', 'No meal plan → log missed, escalate'. Include the retry logic and escalation procedures."
```

---

## 📚 **DOCTRINE-REFERENCED PROMPTING**

### **Reference the source docs:**
```
"Build this according to docs/engines/lst_meal_delivery_engine.md specifications. Follow lst_master.md naming conventions (snake_case, ISO 8601 UTC timestamps)."
```

---

## 🔄 **TESTING-INTEGRATED PROMPTING**

### **Include test coverage requirements:**
```
"Implement training_dispatcher with test coverage: ['unit: timezone calc', 'integration: Discord mock', 'fallback: retry logic'] as specified in Phase 5."
```

---

## 🚨 **ESCALATION-READY PROMPTING**

### **Reference escalation plans:**
```
"If implementation fails, follow the escalation plan: 'If training block missing → escalate to Battle Station' from Phase 5 failure_escalation_plan."
```

---

## 🎯 **OPTIMAL PROMPTING EXAMPLES**

### **🟢 GOOD - Specific Phase + Module:**
```
"Implement Phase 3 onboarding_engine module (src/engines/onboarding/engine.py). Include collect_client_data(), calculate_start_date() (next Tuesday), create_client_profile(), send_welcome_message(). Handle failure modes: 'Invalid form data → prompt retry', 'DB write failure → retry 3x, escalate'."
```

### **🟢 EXCELLENT - Full Context:**
```
"Build Phase 7 checkin_analyzer with dependencies [0,1,2,3]. Trigger at 05:30 client time daily. Use pydantic_schemas: ['ClientProfileSchema', 'CheckinLogSchema']. Implement pause_check_logic, handle emoji buttons (💪/😐/😕), validate weight 30-300kg range. Auto-flag missed by 12:00. Source: docs/engines/lst_checkin_analyzer.md"
```

### **🔴 AVOID - Vague requests:**
```
❌ "Build a Discord bot"
❌ "Make the meal system work"
❌ "Fix the database stuff"
```

---

## 🛡️ **ENFORCEMENT PROMPTING**

### **Reference the enforcement rules:**
```
"Ensure all timestamps are ISO 8601 UTC with explicit offset, no silent failures (all exceptions handled/logged), and all missed events logged with status: missed, per buildspec enforcement_rules."
```

---

## 🎖️ **SUCCESS CRITERIA VALIDATION**

### **End with validation requests:**
```
"After implementation, validate against success criteria: 'Check-in prompts delivered 05:30 client time', 'Multi-field data capture functional', 'Auto-flagging missed check-ins by 12:00' from Phase 7."
```

---

## 📝 **PROMPTING TEMPLATE STRUCTURE**

### **Use this template for optimal results:**

```
[ACTION] Phase [NUMBER] - [PHASE_NAME] 
[MODULE]: [module_name] ([file_path])
[DEPENDENCIES]: [list dependencies from buildspec]
[SCHEMAS]: [pydantic_schemas array from buildspec]
[FUNCTIONS]: [specific functions to implement]
[TRIGGERS]: [timing/trigger requirements]
[FAILURE_MODES]: [specific failure handling]
[SUCCESS_CRITERIA]: [validation requirements]
[SOURCE_DOC]: [reference to specific LST file]
```

### **Example using template:**
```
IMPLEMENT Phase 6 - Cardio Regiment Engine
MODULE: cardio_regiment (src/engines/cardio/regiment.py)
DEPENDENCIES: [0,1,2,3]
SCHEMAS: reads ["client_profiles.cardio_minutes"], writes ["cardio_logs"]
FUNCTIONS: get_cardio_assignment(), send_cardio_protocol(), log_cardio_completion(), calculate_compliance_status()
TRIGGERS: piggyback on meal delivery 06:00
FAILURE_MODES: No assignment → use default 30min, Invalid minutes → prompt retry
SUCCESS_CRITERIA: Daily cardio targets delivered, Minutes logging functional, Status tracking
SOURCE_DOC: docs/engines/lst_cardio_regiment_engine.md
```

---

## 🎯 **KEY SUCCESS FACTORS**

1. **Be Military-Precise** - Reference exact phase numbers, module names, file paths
2. **Schema-First Approach** - Always reference the pydantic_schemas arrays
3. **Include Context** - Dependencies, triggers, timing requirements
4. **Failure-Aware** - Include failure modes and escalation procedures
5. **Validation-Ready** - Reference success criteria for verification

---

## 🚀 **ADVANCED PROMPTING TECHNIQUES**

### **Multi-Phase Coordination:**
```
"Implement Phase 8 Infraction Monitor that coordinates with Phase 4 (meal logs), Phase 5 (training logs), Phase 6 (cardio logs), and Phase 7 (checkin logs). Ensure job_card generation follows JobCardSchema and triggers escalation per buildspec escalation_thresholds."
```

### **Cross-Reference Validation:**
```
"Validate this implementation against docs/schema_definitions.md, ensure timezone handling matches lst_master.md global field definitions, and follow failure escalation procedures from buildspec.yaml Phase [X]."
```

### **Integration-Focused:**
```
"Build Phase 11 Discord integration ensuring compatibility with Phase 4 meal delivery, Phase 5 training dispatcher, and Phase 7 checkin analyzer. Handle button interactions for ✅/❌ responses and modal forms per buildspec interaction_handlers."
```

---

## 🏗️ **BUILD PROGRESS TRACKING**

### **Mandatory Phase Completion Prompting:**
```
"After implementing Phase [X], update docs/audit_log/build_progress.md with:
- Files Created: [actual file paths]
- Schemas Used: [from buildspec pydantic_schemas]  
- Triggers: [timing/scheduler info]
- Failure Modes: [handled failure scenarios]
- Validation: Confirmed against buildspec.yaml Phase [X]
- Notes: [any deviations or issues]

Mark Phase [X] as ✅ COMPLETE and update status to PENDING for Phase [X+1]."
```

### **Validation-First Prompting:**
```
"Before marking Phase [X] complete, validate:
- All files match buildspec.yaml expectations
- Pydantic schemas properly implemented  
- Dependencies correctly integrated
- Success criteria achieved
- Failure modes handled per spec

If any misalignments found, PAUSE and document in escalation log."
```

### **Audit Trail Prompting:**
```
"Document this implementation in build_progress.md using the standard format. Include any schema mismatches, skipped files, or cursor errors in the Notes section. Do not proceed to next phase without audit trail completion."
```

---

**Remember:** This buildspec is designed for zero ambiguity. Leverage that precision in your prompts for maximum Cursor AI effectiveness. 