"Begin building the agent described in these document:
- specs/04b-capability-spec-shift-intake-parsing.md

First, tell me what you can build confidently without asking questions. Then ask for my approval to continue. Second, tell me what you need to clarify before building the rest. Then ask for my approval to continue. Third, build the parts you are confident about."
Claude Output

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




