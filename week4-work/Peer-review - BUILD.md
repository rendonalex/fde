# Peer-review - BUILD	  
  

⏺ Here's my assessment of what I can and can't build from this spec.                                                                                                                                           
                                                                                                                                                                                                               
  ---                                                                                                                                                                                                          
  Part 1: What I can build confidently                                                                                                                                                                         
                                                                                                                                                                                                               
  Data models (fully specified):                                                                                                                                                                               
  - ShiftRequirement Pydantic model with all fields, types, constraints, and enums                                                                                                                             
  - Input schema (raw_text, channel, received_at, hospital_id, servicenow_ticket_id)  
  - All enums: Channel, UnitType, ShiftStatus                                                                                                                                                                  
                    
  Processing pipeline (fully specified):  
  - Step 2 — Credential normalization: exact match, fuzzy match → CREDENTIAL_FUZZY_MAPPED, unrecognised → unrecognised_credentials_raw + flag  
  - Step 3 — unit_type normalization with the 7-value enum                                                                                                                                                     
  - Step 4 — parse_confidence scoring engine: all deduction rules from the table, minimum 0.0, no rounding  
  - Step 5 — Deduplication check on servicenow_ticket_id                                                                                                                                                       
  - Step 6 — Routing logic (≥0.85 → PENDING_MATCH, <0.85 → PENDING_COORDINATOR_REVIEW, SHIFT_DATE_PAST override)                                                                                               
                                                                                                                                                                                                               
  LLM integration (mostly specified):                                                                                                                                                                          
  - Claude claude-sonnet-4-6 with JSON mode                                                                                                                                                                    
  - Retry logic: 3× exponential backoff (2s, 4s, 8s) on HTTP 5xx/timeout                                                                                                                                       
  - Malformed JSON → retry once → LLM_OUTPUT_MALFORMED + parse_confidence = 0.0                                                                                                                                
  - Exhausted retries → LLM_UNAVAILABLE + parse_confidence = 0.0                                                                                                                                               
  - I'll draft a prompt template (spec omits this — flagged in review)                                                                                                                                         
                                                                                                                                                                                                               
  ServiceNow integration (retry rules specified):                                                                                                                                                              
  - HTTP 5xx → 3× exponential backoff; HTTP 4xx → log + alert, no retry                                                                                                                                        
  - Webhook receiver endpoint + 60-second polling fallback skeleton                                                                                                                                            
                                                                                                                                                                                                               
  Edge cases (all specified):                                                                                                                                                                                  
  - Empty/whitespace input → EMPTY_INPUT, parse_confidence = 0.0                                                                                                                                               
  - Multiple shifts in one message → extract first, flag MULTIPLE_SHIFTS_DETECTED                                                                                                                              
  - Past shift date → SHIFT_DATE_PAST, deduct 0.25, force coordinator route                                                                                                                                    
  - float/float pool → Float enum, no deduction                                                                                                                                                                
  - ACLS-style unrecognised credential → unrecognised_credentials_raw                                                                                                                                          
                                                                                                                                                                                                               
  Route decision logging (fields specified): servicenow_ticket_id, parse_confidence, parse_confidence_flags, routing_decision, timestamp                                                                       
                                                                                                                                                                                                               
  Shall I proceed to Part 2?                                                                                                                                                                                   
                                                                                                                                                                                                               
  ---                                                                                                                                                                                                          
  Part 2: What I need to clarify before building the rest  
                                                                                                                                                                                                               
  1. Language/framework — I'll assume Python with Pydantic + FastAPI for the webhook endpoint. Correct?  
  2. Data store for ShiftRequirement — The spec says "data store" but never specifies what. Options: in-memory dict (good for MVP/testing), SQLite, or PostgreSQL. Which do you want?                          
  3. Coordinator review queue mechanism — Spec says "write to coordinator queue data store" but doesn't define it (flagged in review). Is this: (a) same DB table as above with status =                       
  PENDING_COORDINATOR_REVIEW, (b) a separate message queue (Redis/SQS), or (c) just a log entry for now?                                                                                                       
  4. Credential lookup CSV — Spec says "static CSV updated by compliance team monthly" but gives no schema or sample data. I'll create a sample CSV with the codes mentioned in the glossary (RN, ICU-CERT,    
  PACU-EXP) plus the ACLS edge case. Is that enough to start?                                                                                                                                                  
  5. Fuzzy matching algorithm for credentials — Spec says "fuzzy match" with no algorithm. I'll use rapidfuzz (Levenshtein/token-sort ratio, threshold ~80%). Acceptable?  
  6. LOCATION_INCOMPLETE detection — Spec flags partial addresses but gives no programmatic rule. I'll treat an address as "complete" if it contains a street number + street name + city, and "partial"       
  otherwise. OK?                                                                                                                                                                                               
  7. POSSIBLE_MISSED_CREDENTIAL detection — No rules given. I'll use a heuristic: if preferred_attributes contains words like "certified", "licensed", "experience with", "trained in". OK?                    
  8. Required fields for −0.25/null deduction (Step 4) — The spec conditionally requires fields based on status, but scoring happens before status is set. I'll treat these as required for scoring:           
  shift_date, shift_time_start, shift_time_end, unit_type, location_address. Confirm?    
