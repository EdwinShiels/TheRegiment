✅ Lower Source of Truth (LST) Authoring Checklist
Use this when breaking down a system module from HST to LST.

1. Define Inputs
🔲 What data enters this module?
🔲 Where does it come from (source or upstream module)?
🔲 What format is it in (JSON, YAML, float, string, etc.)?
🔲 What is its frequency or trigger condition (interval, event, etc.)?
🔲 What is the valid value range or constraints?

2. Define Internal State
🔲 What information must be remembered between executions?
🔲 What variables are stored in memory?
🔲 Which values persist across sessions or ticks?
🔲 What are the data types and expected formats?
🔲 Are there derived values that must be recalculated on update?

3. Define Actions
🔲 What operations can this module perform?
🔲 What are the function names and their parameters?
🔲 What triggers each action (input condition, internal state, rule)?
🔲 What happens to state or outputs when the action executes?

4. Describe State Transitions
🔲 When an action runs, how does internal state change?
🔲 What calculations or transformations occur?
🔲 Which values are updated, created, or deleted?
🔲 Are transitions atomic or composed of multiple steps?

5. Define Output Events
🔲 What outputs are emitted from this module?
🔲 In what format are the outputs structured?
🔲 Where do the outputs go (downstream module, API, user interface)?
🔲 Under what conditions are outputs emitted?
🔲 Are outputs batched, streamed, or event-driven?

6. Error Handling and Edge Cases
🔲 What happens if inputs are invalid or missing?
🔲 What are the fail-safe defaults?
🔲 How does the system retry, delay, or bypass failed operations?
🔲 Are there known edge cases that must be guarded against?
🔲 What should never happen (assertions)?

7. Validation and Invariants
🔲 What must always be true before and after each execution?
🔲 What data types, formats, or value ranges must be enforced?
🔲 Are there rules for consistency between values?
🔲 What postconditions can be used to verify correct behavior?

8. Timing and Execution Constraints
🔲 How often does this module run (interval, event, schedule)?
🔲 Are there timeouts, delays, or cooldowns?
🔲 Can this module run concurrently or must it be sequential?

9. Dependencies
🔲 What other modules, services, or data does this depend on?
🔲 What contracts or data formats must those dependencies satisfy?
🔲 What happens if a dependency fails?

10. Output Specification for AI Prompts
🔲 What exact prompt should be given to an AI system to generate this module?
🔲 Does the LST specify function names, types, triggers, and outputs clearly enough to produce working code?
🔲 Can this LST be pasted into Cursor or GPT without modification and be understood in full?

✅ When This Checklist Is Complete:
The AI can build this module without assumptions

You can test and debug it predictably

The module is fully interchangeable and composable

🧠 A Few Best Practices to Make It Even Smoother
You’ve got the right list — here’s how to use it with discipline and speed:

Best Practice	Why It Matters
Fill this out per HST module (not generically)	Forces module-level clarity
Use examples (JSON snippets, error states)	Makes Cursor output more reliable
Mark optional fields clearly	Prevents overengineering in V1
Add "AI Build Prompt" at bottom of each LST	You can literally copy/paste to Cursor