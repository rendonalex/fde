 ---                                                                                                                                                                           
  1. Does this kill the project?                                                                                                                                                
                                                                                                                                                                                
  No. The design absorbs FDA requirements without architectural collapse. The two-agent pipeline (ADR-1 intake + ADR-2 triage) already generates structured audit records and
  routes to MSO review. But 4 new compliance requirements force targeted expansions.                                                                                            
                                                            
  ---                                                                                                                                                                           
  2. Changes Required                                       
                                                                                                                                                                                
  A. deliverables/02-cognitive-work-assessment-and-delegation-analysis.md
                                                                                                                                                                                
  Location: Section "Cognitive Hotspots and Breakpoints" → add new breakpoint                                                                                                   
  Change: Insert Breakpoint 4: FDA Per-Case Audit Record Generation                                                                                                             
  - Where: After ADR-2 completes TriageRecommendation, before MSO review                                                                                                        
  - Trigger: Always (100% of cases require FDA-compliant audit record per Req 1)                                                                                                
  - Why it matters: FDA Requirement 1 mandates machine-readable audit trail with "model identity and version, source documents, extracted facts, classifications recommended,   
  human accept/modify/override action + rationale, timestamped chain of custody, 10-year retention"                                                                             
  - What's new vs. current design: Current audit trail (span citations + CoT reasoning) is insufficient. Must add:                                                              
    - Model version tracking (ADR-1 v1.0, ADR-2 v1.0 at classification time, not just agent name)                                                                               
    - Source document inventory (which files/emails/phone transcripts contributed to this case)                                                                                 
    - MSO accept/modify/override action + rationale field (not just MSO signature — substantive review proof per Req 2)                                                         
    - 10-year retention policy (currently 7-year per FDA 21 CFR 314.80; now 10-year per new guidance)                                                                           
  - Residual human effort: No change to MSO review time (15 min/case), but MSO must document substantive review (not rubber stamp)                                              
                                                                                                                                                                                
  Location: Section "Delegation Suitability Matrix"                                                                                                                             
  Change: Update ADR-2 Risk/Compliance dimension commentary                                                                                                                     
  - Add note: "FDA May 2026 guidance (AI/ML in Postmarketing Safety Reporting) mandates human review of all serious AE classifications (Req 2), signal-detection escalation for 
  3-cases-in-90-days patterns (Req 3), expectedness determination boundary (Req 4 — AI may not substitute for final expectedness determination), and 15-day clock attribution to
   AI receipt timestamp (Req 5)"                                                                                                                                                
  - Impact on delegation archetype: Agent-led + MSO Sign-Off archetype is aligned with Req 2 (MSO reviews 100% of serious classifications already). No change to archetype, but 
  MSO review SLA becomes regulatory requirement (not just operational policy).
                                                                                                                                                                                
  ---
  B. deliverables/05a-capability-spec-intake.md                                                                                                                                 
                                                                                                                                                                                
  Section 5: Entity Definitions → AECasePackage
  Change: Add new attributes to AECasePackage:                                                                                                                                  
  - source_documents: array of objects (file metadata for audit trail)                                                                                                          
    - Structure: [{ "filename": string, "format": "email|pdf|vtt|json", "received_at": timestamp, "sha256_hash": string }]                                                      
    - Purpose: FDA Requirement 1 "source documents consulted" — link each case to originating files for 10-year retention + FDA inspection                                      
  - model_version_adr1: string (e.g., "ADR-1 v1.0.2"), immutable, set at extraction time                                                                                        
    - Purpose: FDA Requirement 1 "model identity and version" — traceability if prompt/model changes                                                                            
  - Validation rule: source_documents array must be non-empty (at least one source document per case)                                                                           
                                                                                                                                                                                
  Section 7: Context Engineering Design → Prompt Structure                                                                                                                      
  Change: Add to system prompt Section 10 (Output Schema):                                                                                                                      
  - Include source_documents array in output (filename + format + timestamp + hash for each intake channel file)                                                                
  - Include model_version_adr1 in output (hardcoded in agent deployment config, e.g., "ADR-1 v1.0")                                                                             
                                                                                                                                                                                
  Section 9: Validation Design → Happy Path HP-1                                                                                                                                
  Change: Add validation criterion:                                                                                                                                             
  - source_documents array must have at least one entry with valid sha256_hash (integrity check for 10-year retention)                                                          
                                                                                                                                                                                
  Section 10: Integration Contracts → ADR-1 → PV API Write                                                                                                                      
  Change: Update Request Schema to include source_documents and model_version_adr1 fields                                                                                       
                                                                                                                                                                                
  ---                                                                                                                                                                           
  C. deliverables/05b-capability-spec-triage.md                                                                                                                                 
                                                                                                                                                                                
  Section 4: Autonomy Matrix
  Change: Update "AGENT PROPOSES, MSO REVIEWS ALL RECOMMENDATIONS" section:                                                                                                     
  - Add: FDA Requirement 2 (Human Review of All Serious AE Classifications): "Any AE that ADR-2 classifies as serious per ICH E2A criteria must receive MSO review and signature
   before the seriousness classification is final. MSO must document substantive review (not rubber stamp) — audit record must capture MSO rationale for                        
  accept/modify/override."                                                                                                                                                      
  - Add: FDA Requirement 4 (Expectedness Determination Boundary): "ADR-2 expectedness signal may inform but may not substitute for MSO's final expectedness determination. Final
   expectedness determination remains MSO's responsibility. AI-assisted recommendations of 'unexpected' must include the specific RSI section consulted and the specific span in
   the case from which unexpectedness is inferred." (Already doing this via span citations, but now it's mandatory per FDA.)                                                    
  - Add: FDA Requirement 5 (15-day Clock Attribution): "When ADR-1 first receives an AE meeting expedited reporting criteria, the 15-day FDA reporting clock is attributed to
  ADR-1 received_at timestamp, regardless of when MSO opens the case. Architectural design must ensure that AI receipt timestamps are preserved as the clock-start, not         
  human-open timestamps." (Already doing this — received_at is immutable — but now it's regulatory requirement.)                                                                
                                                                                                                
  Section 4: Autonomy Matrix → Add New Section                                                                                                                                  
  Change: Insert new section: AGENT TRIGGERS ESCALATION (FDA Signal-Detection Requirement)                                                                                      
  - FDA Requirement 3 (Signal-Detection Escalation): "When ADR-2 identifies that an incoming AE matches a pattern with three or more cases of the same MedDRA Preferred Term and
   same suspect product in a rolling 90-day window, the system must escalate the case for MSO signal-detection review within 5 business days of the third case."                
  - Architectural impact: ADR-2 must query PV case history for pattern matching:                                                                                                
    - Query: GET /api/v1/cases?product={product_name}&meddra_pt={ae_meddra_code}&date_range=90days after each classification                                                    
    - If count ≥ 3 (including current case), emit event: SIGNAL_DETECTION_ESCALATION, case_id={}, pattern={product + MedDRA PT}, case_count=3+                                  
    - Route to MSO signal-detection queue (separate from standard MSO review queue) with 5-business-day SLA                                                                     
    - MSO investigates: Is this a new safety signal? Does product RSI need updating? Does this require aggregate reporting to FDA beyond individual 15-day reports?             
  - New data contract: ADR-2 outputs new field in TriageRecommendation:                                                                                                         
    - signal_detection_flag: boolean (true if 3-cases-in-90-days pattern detected)                                                                                              
    - signal_pattern: object (product name, MedDRA PT, case count, date range) if flag true                                                                                     
                                                                                                                                                                                
  Section 5: Entity Definitions → TriageRecommendation                                                                                                                          
  Change: Add new attributes:                                                                                                                                                   
  - signal_detection_flag: boolean, required (true if 3-cases-in-90-days pattern detected per FDA Req 3)                                                                        
  - signal_pattern: nested object, nullable (only populated if signal_detection_flag == true)                                                                                   
    - Structure: { "product": string, "meddra_pt": string, "meddra_code": string, "case_count": int, "window_start": ISO 8601 date, "window_end": ISO 8601 date }
  - model_version_adr2: string (e.g., "ADR-2 v1.0.3"), immutable, set at classification time (FDA Req 1 model version tracking)                                                 
  - mso_action: enum [accepted, modified, overridden], nullable, set when MSO reviews (FDA Req 1 human action tracking)                                                         
  - mso_rationale: string, nullable, max 1000 characters (MSO substantive review documentation per FDA Req 2)                                                                   
    - Validation rule: If mso_action == modified or mso_action == overridden, mso_rationale must be non-null (MSO must document why they disagreed with agent)                  
                                                                                                                                                                                
  Section 5: Entity Definitions → AuditTrail (nested in TriageRecommendation)                                                                                                   
  Change: Update agent_version to model_version_adr2 (more explicit model tracking per FDA Req 1)                                                                               
                                                                                                                                                                                
  Section 7: Context Engineering Design → Prompt Structure                                                                                                                      
  Change: Add to system prompt Section 10 (Output Schema):                                                                                                                      
  - Include signal_detection_flag logic: "After classification, query PV API for cases with same product + MedDRA PT in past 90 days. If count ≥ 3 (including current case), set
   signal_detection_flag: true and populate signal_pattern object."                                                                                                             
  - Include model_version_adr2 in output (hardcoded in agent deployment config)
                                                                                                                                                                                
  Section 9: Validation Design → Add New Scenario                                                                                                                               
  Change: Insert new edge case: EC-6: Signal-Detection Escalation (3 Cases in 90 Days)                                                                                          
  - Input: Third case of "Hepatotoxicity" (MedDRA PT 10019692) for Tezarimab within 90 days                                                                                     
  - Expected Output:                                                                                                                                                            
    - signal_detection_flag == true                                                                                                                                             
    - signal_pattern == { "product": "Tezarimab", "meddra_pt": "Hepatotoxicity", "meddra_code": "10019692", "case_count": 3, "window_start": "2026-03-01", "window_end": 
  "2026-05-30" }                                                                                                                                                         
    - Case routed to MSO signal-detection queue with 5-business-day SLA                                                                                                         
    - MSO investigates aggregate pattern, decides: update Tezarimab RSI? File aggregate safety report to FDA? Continue monitoring?
  - Pass Criteria: 100% of 3-cases-in-90-days patterns flagged (zero false negatives on signal detection)                                                                       
                                                                                                                                                                                
  Section 10: Integration Contracts → ADR-2 → PV API Read (new query)                                                                                                           
  Change: Add new integration contract: ADR-2 → PV Case History Query (Signal Detection)                                                                                        
  - Endpoint: GET /api/v1/cases?product={product_name}&meddra_pt={ae_meddra_code}&date_range=90days                                                                             
  - Purpose: FDA Requirement 3 — query case history for 3-cases-in-90-days pattern matching                                                                                     
  - Trigger: After each TriageRecommendation complete, before MSO routing                                                                                                       
  - Response: { "case_count": int, "cases": [ { "case_id": UUID, "received_at": timestamp } ] }                                                                                 
  - Error Handling: If PV API query fails (503 or timeout), log warning but do NOT block MSO review (signal detection is supplementary, not blocking path). Alert ops if query  
  failure rate >10% over 1 hour.                                                                                                                                                
  - Cost: Single API call per case (~50ms latency). Annual cost: 6,000 queries/year × $0 (internal PV API).                                                                     
                                                                                                                                                                                
  ---                                                                                                                                                                           
  3. What Changes in Economics?                             
                                                                                                                                                                                
  Build Cost Increase: +$15K (1 week additional FDE effort for FDA compliance features)
  - Signal-detection query integration: +2 days ($3K)                                                                                                                           
  - Audit record schema expansion (source documents, model version, MSO action tracking): +2 days ($3K)                                                                         
  - MSO rationale documentation UI (substantive review proof): +2 days ($3K)                                                                                                    
  - 10-year retention policy enforcement (storage + archival workflow): +1 day ($2K)                                                                                            
  - Testing + validation (signal-detection edge cases, audit record completeness): +2 days ($4K)                                                                                
                                                                                                                                                                                
  Operational Cost Increase: +$8K/year                                                                                                                                          
  - 10-year retention vs. 7-year (storage cost): +$2K/year (3 additional years × 6,000 cases × $0.10/case/year)                                                                 
  - MSO rationale documentation (adds ~2 min per modified/overridden case): 12% override rate × 6,000 cases × 2 min × $60/hr = +$1,440/year                                     
  - Signal-detection review (MSO investigates 3-cases-in-90-days patterns): ~50 patterns/year (estimated) × 30 min MSO effort × $60/hr = +$1,500/year                           
  - Query latency (signal-detection PV API calls): negligible (50ms per case, internal API)                                                                                     
                                                                                                                                                                                
  Updated ROI:                                                                                                                                                                  
  - Build cost: $80K (baseline Wave 1) + $15K (FDA compliance) = $95K                                                                                                           
  - Annual savings: $453K (baseline) - $8K (FDA compliance ops cost) = $445K                                                                                                    
  - Payback: 95K / 445K = 2.6 months (was 2.1 months baseline)              
  - Year 1 ROI: (445K - 95K) / 95K = 368% (was 466% baseline)                                                                                                                   
                                                                                                                                                                                
  Still self-financing. FDA compliance adds 0.5 months to payback but does not break economic case.                                                                             
                                                                                                                                                                                
  ---                                                                                                                                                                           
  4. What Changes in Build at 14:00?                                                                                                                                            
                                                                                                                                                                                
  If prototype must demonstrate FDA requirements:
                                                                                                                                                                                
  Priority 1 (Must demonstrate):                                                                                                                                                
  1. Audit record completeness: Show AECasePackage with source_documents array + model_version_adr1 field populated                                                             
  2. MSO rationale tracking: Show TriageRecommendation with mso_action (accepted/modified/overridden) + mso_rationale field                                                     
  3. 15-day clock anchoring: Demonstrate received_at timestamp is preserved from ADR-1 intake (immutable) and used for SLA tracking (already in design, just call it out as FDA
  Req 5 compliance)                                                                                                                                                             
                                                                                                                                                                                
  Priority 2 (Good to demonstrate):                                                                                                                                             
  4. Signal-detection query: Show ADR-2 querying PV case history for 3-cases-in-90-days pattern, emitting SIGNAL_DETECTION_ESCALATION event when pattern detected               
                                                                                                                                                                                
  Defer to post-prototype (buildable but not demo-critical):                                                                                                                    
  5. 10-year retention policy enforcement (storage + archival workflow — operational concern, not prototype feature)                                                            
  6. MSO substantive-review UI (case processor workflow — buildable in 2 days, but not critical path for agent logic demo)                                                      
                                                                                                                                                                                
  ---                                                                                                                                                                           
  5. Summary of Changes to Files                                                                                                                                                
                                                                                                                                                                                
  ┌──────────────────────────────┬───────────────────────────────────────────┬─────────────────────────────────────────────────────────────────────────┬───────────────────┐
  │             File             │                  Section                  │                               Change Type                               │  Lines Affected   │    
  │                              │                                           │                                                                         │      (est.)       │    
  ├──────────────────────────────┼───────────────────────────────────────────┼─────────────────────────────────────────────────────────────────────────┼───────────────────┤    
  │ 02-cognitive-work-assessment │ Cognitive Hotspots → add Breakpoint 4     │ Insert new section                                                      │ +15 lines         │    
  ├──────────────────────────────┼───────────────────────────────────────────┼─────────────────────────────────────────────────────────────────────────┼───────────────────┤    
  │ 02-cognitive-work-assessment │ Delegation Suitability Matrix → ADR-2     │ Update prose                                                            │ +5 lines          │    
  │                              │ commentary                                │                                                                         │                   │    
  ├──────────────────────────────┼───────────────────────────────────────────┼─────────────────────────────────────────────────────────────────────────┼───────────────────┤    
  │ 05a-capability-spec-intake   │ Entity Definitions → AECasePackage        │ Add 2 new attributes (source_documents, model_version_adr1)             │ +20 lines         │
  ├──────────────────────────────┼───────────────────────────────────────────┼─────────────────────────────────────────────────────────────────────────┼───────────────────┤    
  │ 05a-capability-spec-intake   │ Context Engineering → Prompt Structure    │ Add to output schema                                                    │ +5 lines          │
  ├──────────────────────────────┼───────────────────────────────────────────┼─────────────────────────────────────────────────────────────────────────┼───────────────────┤    
  │ 05a-capability-spec-intake   │ Validation Design → HP-1                  │ Add validation criterion                                                │ +3 lines          │
  ├──────────────────────────────┼───────────────────────────────────────────┼─────────────────────────────────────────────────────────────────────────┼───────────────────┤    
  │ 05a-capability-spec-intake   │ Integration Contracts → PV API Write      │ Update request schema                                                   │ +5 lines          │
  ├──────────────────────────────┼───────────────────────────────────────────┼─────────────────────────────────────────────────────────────────────────┼───────────────────┤    
  │ 05b-capability-spec-triage   │ Autonomy Matrix → MSO Reviews section     │ Add FDA Req 2, 4, 5 notes                                               │ +10 lines         │
  ├──────────────────────────────┼───────────────────────────────────────────┼─────────────────────────────────────────────────────────────────────────┼───────────────────┤    
  │ 05b-capability-spec-triage   │ Autonomy Matrix → Add new section         │ Insert "AGENT TRIGGERS ESCALATION" section (FDA Req 3)                  │ +20 lines         │
  ├──────────────────────────────┼───────────────────────────────────────────┼─────────────────────────────────────────────────────────────────────────┼───────────────────┤    
  │ 05b-capability-spec-triage   │ Entity Definitions → TriageRecommendation │ Add 4 new attributes (signal_detection_flag, signal_pattern,            │ +30 lines         │
  │                              │                                           │ mso_action, mso_rationale)                                              │                   │    
  ├──────────────────────────────┼───────────────────────────────────────────┼─────────────────────────────────────────────────────────────────────────┼───────────────────┤
  │ 05b-capability-spec-triage   │ Context Engineering → Prompt Structure    │ Add signal-detection query logic to output schema                       │ +8 lines          │
  ├──────────────────────────────┼───────────────────────────────────────────┼─────────────────────────────────────────────────────────────────────────┼───────────────────┤    
  │ 05b-capability-spec-triage   │ Validation Design → Edge Cases            │ Insert new EC-6 (signal-detection escalation)                           │ +25 lines         │
  ├──────────────────────────────┼───────────────────────────────────────────┼─────────────────────────────────────────────────────────────────────────┼───────────────────┤    
  │ 05b-capability-spec-triage   │ Integration Contracts                     │ Add new contract: ADR-2 → PV Case History Query                         │ +30 lines         │
  └──────────────────────────────┴───────────────────────────────────────────┴─────────────────────────────────────────────────────────────────────────┴───────────────────┘    
                                                            
  Total: ~176 lines across 3 files (targeted additions, no rewrites)                                                                                                            
                                                            
  ---                                                                                                                                                                           
  6. What's Load-Bearing (Cannot Defer)                     
                                       
  Compliance non-negotiables (fail gate if missing):
  1. ✅ Req 1 (Per-case audit record): Add source_documents, model_version_adr1/adr2, mso_action, mso_rationale fields to data models                                           
  2. ✅ Req 2 (Human review of all serious AE classifications): Already in design (MSO reviews 100% of ADR-2 recommendations). Add note that this is now FDA regulatory         
  requirement, not just operational policy. MSO must document substantive review (not rubber stamp) — add mso_rationale field.                                                  
  3. ✅ Req 3 (Signal-detection escalation): Add 3-cases-in-90-days pattern matching to ADR-2, emit SIGNAL_DETECTION_ESCALATION event, route to MSO signal-detection queue with 
  5-day SLA                                                                                                                                                                    
  4. ✅ Req 4 (Expectedness determination boundary): Already in design (ADR-2 generates expectedness signal, MSO makes final determination). Add note that AI may not substitute
   for MSO's expectedness determination per FDA.                                                                                                                                
  5. ✅ Req 5 (15-day clock attribution): Already in design (received_at timestamp is immutable from ADR-1 intake). Add note that this is now FDA regulatory requirement (clock 
  anchors to AI receipt, not human-open timestamp).                                                                                                                            
                                                                                                                                                                                
  Nice-to-have (defer if time-constrained):                 
  - 10-year retention policy (storage + archival workflow) — operational concern, not agent logic                                                                               
  - MSO substantive-review UI enhancements — buildable post-prototype                                                                                                           
                                                                                                                                                                                
  ---                   