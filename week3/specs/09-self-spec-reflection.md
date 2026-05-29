# Prompt to build agent

Begin building the agent described in these document:
- specs/04b-capability-spec-shift-intake-parsing.md

First, tell me what you can build confidently without asking questions. Then ask for my approval to continue. Second, tell me what you need to clarify before building the rest. Then ask for my approval to continue. Third, build the parts you are confident about.


# Analysis from Claude output below

Since all tests passed after building the spec, I was not able to do a build-diagnosis as it was shown in the program walkthrough (as I had no code snippet producing an unexpected outcome -failed test). Also, since no guidance was given when such situation heppened (when all tests passed and Claude had no logic questions), then I decided after the build to ask Claude if it could find ambiguities in the spec. It found the ones referred to in Deliverable #5. Which then makes me question the coverage of the validation tests. **With more time**, I would be checking more thoroughly the validations to ensure there would be test cases covering the ambiguities found by Claude. But it also raises some questions as to why when I asked Claude to build and tell me if it had questions, it did not point to these ambiguities. Perhaps my prompt should have been more precise and also ask there for ambiguities. But due to lack of experience, this did not occur to me at the time I run the build.

In terms of what Claude code built and whether it matches my intent, I checked the agent.py and the flow there reflects the flow stated in the spec. **With more time** I would spend more time checking more closely the code to understand it better. I ran the tests in the validation plan and also all passed:

⏺ 51/51 passing. Here's what was written and one bug fixed:                                                                                                                                           
                                                                                                                                                                                                      
  tests/test_agent_integration.py (14 tests) — agent-level behavior:                                                                                                                                  
  - EC-01 (P0): Advisory lock — 409 on PARSING PATCH skips record; LLM never called                                                                                                                   
  - EC-04 (P0): Duplicate ParsedShiftRequirement write (409) → event emitted once using existing ID                                                                                                   
  - ER-01 (P0): LLM 401 → _halt = True; no PARSE_FAILED records                                                                                                                                       
  - ER-02 (P0): ServiceNow write failure → DLQ entry created; shift_parsed not emitted                                                                                                                
  - ER-02b: DLQ reconciliation succeeds → event emitted, queue cleared; or retry count incremented on continued failure                                                                               
  - HP-01: BP2 auto-proceed path → PARSED + event emitted once, no HITL write                                                                                                                         
  - HP-02: Ambiguous location → HUMAN_REVIEW + HITL entry with AMBIGUOUS_LOCATION; partial parse pre-filled                                                                                           
  - Consecutive failure counter increment/reset behavior                                                                                                                                              
                                                                                                                                                                                                      
  tests/test_hitl_service.py (8 tests) — FastAPI service:                                                                                                                                             
  - ER-03 (P0): Duplicate POST → HTTP 409 with original hitl_entry_id; exactly one record in DB                                                                                                       
  - Happy path, list, get-by-id, 404, health                                                                                                                                                          
                                                                                                                                                                                                      
  Bug fixed in hitl_service/db.py: body.get("received_at", now) returned None when the key was present but None; changed to body.get("received_at") or now.   



# Claude Output after asking what it could build confidently

Part 1 — What I can build confidently, no questions needed                                                                                                                                          
                                                                                                                                                                                                      
  Assuming Python (Pydantic + httpx). Everything below is fully specified in the doc.                                                                                                                 
                                                                                                                                                                                                      
  Data models (§3) — All three entities with exact fields, types, constraints, and state machine rules:                                                                                               
  - ShiftRequest with u_status enum and transition rules                                                                                                                                              
  - ParsedShiftRequirement with unique constraint, schema lock note, immutability rules                                                                                                               
  - HITLQueueEntry with u_failure_reason enum and state machine                                                                                                                                       
                                                                                                                                                                                                      
  All four HTTP clients (§7) — with exact error handling per status code, retry backoff (4s/8s/16s), and timeouts:
  - ServiceNow poll (§7.1): GET QUEUED records, batch 10, FIFO, all error codes
  - ServiceNow PATCH (§7.2): status updates, advisory lock semantics, 409=success                                                                                                                     
  - ServiceNow POST (§7.3): ParsedShiftRequirement write, ordering constraint before event emit
  - Claude Sonnet API (§7.4): exact model claude-sonnet-4-6, retry on 529, halt on 401, route to HUMAN_REVIEW after 60s LLM unavailability                                                            
                                                                                                                                                                                                      
  Context engineering (§8) — built as a runtime-assembled system prompt:                                                                                                                              
  - Role block, output schema, confidence scoring rules, important rules (§8.1)                                                                                                                       
  - SpecialtyCode and CredentialCode dictionaries loaded from config at startup (§8.2)                                                                                                                
  - HospitalLocation lookup with ambiguity handling (§8.3)                                                                                                                                            
  - Per-field confidence scoring rules embedded verbatim (§8.4)                                                                                                                                       
  - All 3 few-shot examples (§8.5)                                                                                                                                                                    
                                                                                                                                                                                                      
  Core logic:                                                                                                                                                                                         
  - confidence_score = min(specialty, datetime_start, datetime_end, location, credential) (§8.4)                                                                                                      
  - Schema validation: specialty code in dict, credential codes in dict, datetime_start future check, malformed JSON → 1 retry → HUMAN_REVIEW                                                         
  - BP1/BP2 routing at threshold 0.85                                                                                                                                                                 
  - 10-consecutive-failure ops alert counter                                                                                                                                                          
                                                                                                                                                                                                      
  Main poll loop — 30-second interval, advisory lock via PARSING PATCH before LLM call, full MT-1.0 → MT-1.7 orchestration                                                                            
                                                                                                                                                                                                      
  Config file — YAML with specialty dict, credential dict, location lookup; supports agent restart to refresh                                                                                         
                                                                                                                                                                                                      
  Stubs with correct interfaces (these don't exist yet per the spec):                                                                                                                                 
  - HITL Queue client (§7.5): writes to a local JSON file matching the exact request/response schema; swappable for the real service in weeks 2–3
  - Event bus emit (§9): logs shift_parsed event locally with correct payload; no-op until real bus is wired                                                                                          
  - Dead-letter queue: local JSON file; reconciliation cron reads it; alerts if depth > 10                  
                                                                                                                                                                                                      
  ---                                                                                                                                                                                                 
  Ready to build all of the above. Approve to continue to Part 2?                                                                                                                                     
                                                                                                                                                                                                      
  ---             
  Part 2 — What I need to clarify before building the rest                                                                                                                                            
                                                                                                                                                                                                      
  Four open questions. The spec names these as deferred or undecided.
                                                                                                                                                                                                      
  Q1 — Internal HITL Queue API (§7.5): The spec says it's built weeks 2–3. My stub writes to a local JSON file with the exact interface. Do you want me to also build a minimal FastAPI service       
  implementing that interface now, so you can test the full BP1 path end-to-end? Or leave it as a stub until the real service exists?                                                                 
                                                                                                                                                                                                      
  Q2 — Event bus for shift_parsed (MT-1.7): The spec says "internal event bus or ServiceNow workflow trigger." My stub logs the event locally. For production: (a) write a trigger record to a new    
  ServiceNow table, (b) HTTP POST to a webhook URL, or (c) something else? This determines what I wire in the production path.
                                                                                                                                                                                                      
  Q3 — Dead-letter queue persistence: Local JSON file works for weeks 1–2. Should I build it against a ServiceNow table (keeps all data in one system) or keep it as a local file with a note to      
  migrate?
                                                                                                                                                                                                      
  Q4 — Ops alert channel: The spec says "configured at deployment." For the alert in MT-1.5 and the 10-consecutive-failure trigger, should I implement: (a) log to stderr only for now, (b) Slack     
  webhook (if you have one), or (c) leave it as a pluggable adapter with a TODO comment?
                                                                                                                                                                                                      
  ---             
  Approve Part 1 build and answer the four questions when ready.


  # Claude output after Claude did the build and tests were run:


⏺ Now let's install dependencies and run the tests:      
                                                        
⏺ Bash(pip install -q -r requirements.txt 2>&1 | tail -5)
  ⎿  (eval):1: command not found: pip                   
                                            
⏺ Bash(python3 -m pip install -q -r requirements.txt 2>&1 | tail -8)
  ⎿    WARNING: The script httpx is installed in '/Users/Alexandra_Rendon/Library/Python/3.9/bin' which is not on PATH.
       Consider adding this directory to PATH or, if you prefer to suppress this warning, use --no-warn-script-location.
       WARNING: The script distro is installed in '/Users/Alexandra_Rendon/Library/Python/3.9/bin' which is not on PATH.                                                                              
     … +5 lines (ctrl+o to expand)                       
  ⎿  (timeout 2m)                                                                                                                                                                                     
                                                                                   
⏺ Bash(python3 -m pytest tests/ -v 2>&1)                                                                                                                                                              
  ⎿  ============================= test session starts ==============================                                                                                                                 
     platform darwin -- Python 3.9.6, pytest-8.4.2, pluggy-1.6.0 -- /Library/Developer/CommandLineTools/usr/bin/python3
     cachedir: .pytest_cache                                                                                                                                                                          
     … +28 lines (ctrl+o to expand)                                                                                                                                                                   
                                                                                                                                                                                                      
⏺ 29/29 passing.                                                                                                                                                                                      
                                                                                                                                                                                                      
⏺ 29/29 tests pass. Here's what was built and the technical decisions made:                                                                                                                           
                                                                                                                                                                                                      
  ---                                                                                                                                                                                                 
  What was built                                                                                                                                                                                      
                                                                                                                                                                                                      
  week3/                                                                                                                                                                                              
  ├── agent/                                                                                                                                                                                          
  │   ├── models.py          — ShiftRequest, ParsedShiftRequirement, HITLQueueEntry, LLMExtractionResult                                                                                              
  │   ├── config.py          — Settings (pydantic-settings) + DomainConfig (YAML loader)                                                                                                              
  │   ├── alerts.py          — stderr + optional Slack webhook                                                                                                                                        
  │   ├── agent.py           — full MT-1.0→MT-1.7 poll loop + reconciliation cron                                                                                                                     
  │   ├── clients/                                                                                                                                                                                    
  │   │   ├── servicenow.py  — poll, PATCH, POST with exact error codes from §7                                                                                                                       
  │   │   ├── llm.py         — Claude API with 529 retry (4/8/16s), 401 halt, JSON retry                                                                                                              
  │   │   ├── hitl_queue.py  — HTTP client for HITL service                                                                                                                                           
  │   │   └── event_bus.py   — POST to EVENT_BUS_URL or log locally                                                                                                                                   
  │   └── core/                                                                                                                                                                                       
  │       ├── scorer.py      — min() formula from §8.4                                                                                                                                                
  │       ├── validator.py   — datetime future check, dict lookups, confidence capping                                                                                                                
  │       ├── prompt.py      — assembles full system prompt from config + few-shots                                                                                                                   
  │       └── dead_letter.py — SQLite-backed DLQ with pop/push/retry/depth                                                                                                                            
  ├── hitl_service/                                                                                                                                                                                   
  │   ├── main.py            — FastAPI: POST/GET /internal/api/v1/hitl-queue                                                                                                                          
  │   └── db.py              — SQLite backend, 409 on duplicate shift_request_id                                                                                                                      
  ├── config/dictionaries.yaml                                                                                                                                                                        
  ├── tests/                 — 29 tests: scorer, validator, LLM client, full flow scenarios                                                                                                           
  ├── .env.example                                                                                                                                                                                    
  ├── requirements.txt                                                                                                                                                                                
  ├── run_agent.py                                                                                                                                                                                    
  └── run_hitl_service.py                                                                                                                                                                             
                                                                                                                                                                                                      
  Technical decisions made                                                                                                                                                                            
                                                                                                                                                                                                      
  ┌───────────────────┬────────────────────────────────────────────┬────────────────────────────────────────────────────────────────────────────┐                                                     
  │     Question      │                  Decision                  │                                 Rationale                                  │
  ├───────────────────┼────────────────────────────────────────────┼────────────────────────────────────────────────────────────────────────────┤                                                     
  │ HITL Queue API    │ FastAPI + SQLite on port 8001              │ Testable locally; matches §7.5 interface exactly; swappable for production │
  ├───────────────────┼────────────────────────────────────────────┼────────────────────────────────────────────────────────────────────────────┤                                                     
  │ Event bus         │ HTTP POST to EVENT_BUS_URL; no-op if unset │ Zero-dependency default; wires to any webhook in production                │                                                     
  ├───────────────────┼────────────────────────────────────────────┼────────────────────────────────────────────────────────────────────────────┤                                                     
  │ Dead-letter queue │ SQLite (dead_letter.db)                    │ Persistent, no external deps; reconciliation cron runs every 5 min         │                                                     
  ├───────────────────┼────────────────────────────────────────────┼────────────────────────────────────────────────────────────────────────────┤                                                     
  │ Ops alerts        │ stderr JSON + optional SLACK_WEBHOOK_URL   │ Structured logs work with any log aggregator; Slack for paging             │
  ├───────────────────┼────────────────────────────────────────────┼────────────────────────────────────────────────────────────────────────────┤                                                     
  │ Concurrency       │ asyncio.gather over poll batch             │ All I/O is async; 10 records process concurrently per cycle                │
  └───────────────────┴────────────────────────────────────────────┴────────────────────────────────────────────────────────────────────────────┘                                                     
                                                            
  To run locally: copy .env.example → .env, fill in credentials, then python3 run_hitl_service.py in one terminal and python3 run_agent.py in another.                                                
                                                            
✻ Sautéed for 9m 26s      


