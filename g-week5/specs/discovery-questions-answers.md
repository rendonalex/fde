# Discovery Questions — Helix Therapeutics Pharmacovigilance

**Date**: 2026-06-01  
**Engagement**: Adverse Event Triage AI Prototype — Gate 5b Final Exam  
**Stakeholders**: Dr. Maeve Carmichael (CMO), Dr. Anil Iyer (Senior Safety Physician), Carolina Núñez-Reyes (VP Regulatory Affairs), Theo Lonergan (Head Drug Safety Operations), Greta Schäffer (Chief Compliance Officer)

---

## Discovery Question Structure

Questions are organized across the FDE funnel pattern (Broad → Narrow → Probe) and aligned with ATX assessment categories: **Volume & Time**, **Cognitive Nature**, **Data & Systems**, **Risk & Compliance**, and **Organisational**.

Focus areas for this engagement:
- Pause points where safety officers verify case details against reference safety profiles
- Judgment calls in seriousness classification per ICH E2A criteria
- Coordination work across heterogeneous report formats (EDI, PDF, fax, email, social media, clinical trial sites, literature)
- Pattern recognition in expectedness assessment against product reference safety information
- Async waits for reporter follow-up or medical literature searches

---

## Broad Funnel Questions (Work Patterns & Time Sinks)

### 1. Volume & Time
**Q1**: Walk me through how a case processing specialist spends time on a typical case from receipt to reportability decision. What are the biggest time sinks? Can you give me an example from the last week?

**What we're listening for**: 
- Categories of work (data extraction, terminology normalization, ICH E2A classification, expectedness lookup, reportability determination)
- Time spent on each activity (e.g., "20 minutes extracting from a handwritten fax PDF", "15 minutes searching reference safety information")
- Frustration points (e.g., "heterogeneous formats force me to manually transcribe", "I have to open four different documents to check expectedness")
- Context switching between tools (PV system, RxNorm, MedDRA, regulatory reference docs)

---

### 2. Cognitive Nature
**Q2**: You mentioned that case processing averages 75 minutes per case. Which parts of that 75 minutes require you to think, make judgment calls, or verify information—versus which parts feel like repetitive data entry or synthesis?

**What we're listening for**:
- Repetitive work candidates (e.g., "Extracting patient age/sex/weight from standard HCP report forms follows a pattern", "Normalizing drug names with RxNorm is mechanical")
- Judgment calls (e.g., "Deciding if an AE meets 'other medically important condition' per ICH E2A requires clinical judgment", "Assessing causality when there are concomitant medications")
- Training requirements (e.g., "A junior specialist wouldn't know when 'hospitalisation prolonged' qualifies as serious")

---

### 3. Data & Systems
**Q3**: When a new adverse event report comes in, where does the information actually come from, and how many different formats or systems do you have to access to process a single case?

**What we're listening for**:
- Input formats and their frequency (e.g., "70% come via email or fax as PDF, 20% are phone calls transcribed by intake, 10% are social media monitoring extracts")
- Number of systems consulted (e.g., "I check the PV database for duplicates, RxNorm for drug normalization, the product reference safety profile PDFs, sometimes PubMed for literature cases")
- Data quality issues (e.g., "Patient direct reports often have incomplete dosing information", "Social media extracts rarely have patient identifiers")

---

### 4. Organisational
**Q4**: Walk me through what happens after you've triaged a case as 'serious-unexpected' and recommended 15-day expedited reporting. Who reviews your recommendation, and what are they checking for?

**What we're listening for**:
- Approval gates (e.g., "Medical safety officer reviews 100% of reportability recommendations", "CMO must sign for novel serious AEs")
- Stakeholder dependencies (e.g., "Regulatory Affairs needs to be looped in for multi-jurisdictional reporting", "Quality Assurance audits a sample each quarter")
- Backlog triggers (e.g., "If we get a surge of reports and the safety officer is out, cases pile up")

---

### 5. Risk & Compliance
**Q5**: If a serious-unexpected adverse event is misclassified as non-serious or expected, and the 15-day FDA clock is missed—what are the consequences? How would you or Dr. Carmichael detect that this had happened?

**What we're listening for**:
- Regulatory consequences (e.g., "FDA warning letter, consent decree risk, personal liability for CMO")
- Detection mechanisms (e.g., "We run an audit sample quarterly", "FDA inspection would catch it", "Safety officer catches errors during review")
- Risk tolerance (e.g., "We over-report rather than under-report because the cost of a late SAE report is career-ending")

---

## Narrow Funnel Questions (Specific Pause Points & Judgment Calls)

### 6. Cognitive Nature
**Q6**: Pick a case you processed this week where the seriousness classification wasn't obvious. Walk me through how you decided whether it qualified as 'serious' per ICH E2A, and what criteria or reference materials you consulted.

**What we're listening for**:
- Specific pause points (e.g., "I had to check if a 3-day ER visit counted as 'hospitalisation' or just observation")
- Judgment criteria (e.g., "ICH E2A says 'persistent or significant disability/incapacity', so I looked for functional impact duration")
- Sources consulted (e.g., "I re-read the ICH E2A guideline", "I asked Dr. Iyer for a second opinion")
- Exception patterns (e.g., "Most cases are clear-cut death/hospitalization, but 'other medically important condition' is vague and requires clinical judgment")

---

### 7. Data & Systems
**Q7**: When you're assessing whether an adverse event is 'expected' by checking it against the product reference safety information, how do you actually do that lookup? What makes a case match versus not match?

**What we're listening for**:
- Lookup process (e.g., "I open the PDF for Solivian's reference safety profile and Ctrl+F for the MedDRA term", "If it's listed in the RSI, it's expected")
- Ambiguity handling (e.g., "Sometimes the term doesn't match exactly—'acute kidney injury' in the case but 'renal impairment' in the RSI—so I have to decide if they're synonymous")
- System limitations (e.g., "The RSI is a static PDF, not searchable by MedDRA hierarchy")

---

### 8. Cognitive Nature
**Q8**: You mentioned that heterogeneous report formats are a challenge. Walk me through a recent patient-direct report or social media monitoring extract. Where did you have to stop and interpret non-medical language, and where did you have to decide what to do about missing information?

**What we're listening for**:
- Extraction complexity (e.g., "Patient said 'I felt like I was going to pass out' — I had to map that to 'presyncope' in MedDRA")
- Missing data handling (e.g., "Social media reports often have no patient identifier, so I flag them for reporter follow-up")
- Exception rate (e.g., "About 30% of non-EDI reports require follow-up because dosing or onset date is missing")

---

### 9. Risk & Compliance
**Q9**: Tell me about the last time a case was flagged during an audit or by a regulatory inspector. What was wrong, and how did you or the team identify the gap?

**What we're listening for**:
- Audit findings (e.g., "Inspector found a case where we classified an AE as 'expected' but the term wasn't explicitly in the RSI—we had to explain our reasoning")
- Root cause (e.g., "Terminology matching ambiguity", "Safety officer missed a concomitant medication causality signal")
- Process changes (e.g., "We now require span citations to source text for every extracted field so inspectors can see the evidence")

---

### 10. Organisational
**Q10**: When a case requires reporter follow-up—say, a patient-direct report with missing dosing information—who handles that, and what happens to the case in the meantime? Does it sit in a queue, or does the 15-day clock keep running?

**What we're listening for**:
- Workflow handoffs (e.g., "Case processor flags it for follow-up, intake specialist reaches out to the reporter, case sits in 'pending' until we get a response")
- Clock management (e.g., "The 15-day clock starts at first receipt, not when we get follow-up—so we have to be aggressive about contacting reporters")
- Backlog impact (e.g., "If we can't reach the reporter in 72 hours, we process the case with what we have and document the limitation")

---

## Probe Funnel Questions (Delegation Signals & Codifiability)

### 11. Cognitive Nature
**Q11**: When you classify seriousness per ICH E2A, is there a pattern? Like, if the report mentions 'death' or 'hospitalized', do you automatically classify it as serious? Or are there ambiguous cases where you have to use clinical judgment?

**What we're listening for**:
- Codifiability (e.g., "Death, hospitalization, life-threatening are clear-cut—95% of cases fall into those buckets", "The remaining 5% under 'other medically important condition' require judgment")
- Exception rate (e.g., "Maybe 10% of cases require consultation with the safety officer because the clinical significance isn't obvious")
- Rule articulation (e.g., "If the term matches ICH E2A criteria explicitly, it's serious; if it doesn't, I check for functional impact or medical intervention required")

---

### 12. Risk & Compliance
**Q12**: If an AI agent classified a case as 'non-serious' and recommended 'periodic reporting only', but it was actually serious-unexpected and required 15-day expedited reporting—what would be the consequence? How would you detect that error before it caused harm?

**What we're listening for**:
- Error consequence (e.g., "FDA late-reporting violation, consent decree risk, CMO personal liability")
- Detection mechanisms (e.g., "Safety officer reviews 100% of recommendations before submission", "Quarterly audit sample", "FDA inspection")
- Risk tolerance (e.g., "We would over-report borderline cases rather than under-report—cost of false positive is low, cost of false negative is catastrophic")

---

### 13. Cognitive Nature
**Q13**: For expectedness assessment—matching an adverse event to the product reference safety information—what percentage of cases are clear matches versus ambiguous? What makes a case ambiguous?

**What we're listening for**:
- Clear match rate (e.g., "80% of cases are straightforward—'headache' is listed in the RSI for Phaedora, so it's expected")
- Ambiguity patterns (e.g., "Sometimes the reported term is more specific than the RSI term—'hemorrhagic stroke' in the case but only 'cerebrovascular event' in the RSI")
- Resolution criteria (e.g., "We use MedDRA hierarchy—if the High Level Term matches, we consider it expected")

---

### 14. Organisational
**Q14**: If an AI agent could extract structured data from heterogeneous report formats (PDF, email, phone transcripts, social media) and flag low-confidence extractions for human review—would you be comfortable with that? What confidence threshold would you require before you'd trust the extraction?

**What we're listening for**:
- Human trust (e.g., "If the agent shows me the source text span and a confidence score, I'd trust it for routine fields like patient age/sex")
- Confidence threshold (e.g., "For required fields, I'd want 85%+ confidence—otherwise route to human review")
- Review appetite (e.g., "I'd rather review 20% of cases flagged by the agent than manually extract from 100% of cases")

---

### 15. Risk & Compliance
**Q15**: What would it take to document the criteria you use to recommend reportability—'15-day expedited', 'periodic only', or 'non-reportable'? Could you articulate the decision logic right now, or is it something you'd need to work with Dr. Iyer to codify?

**What we're listening for**:
- Codifiability (e.g., "Serious + unexpected = 15-day per FDA 21 CFR 314.80, that's clear", "The edge cases are when causality is unclear due to concomitant medications")
- Documentation feasibility (e.g., "Dr. Iyer could probably write the criteria in a few hours with examples", "It would take a week to cover all the edge cases")
- Stakeholder alignment (e.g., "Dr. Iyer and Carolina Núñez-Reyes would need to agree on multi-jurisdictional reportability variance before we could codify it")

---

## Notes on Using These Questions

- **Start with Q1-Q5 (Broad Funnel)** to map work patterns, time sinks, and organizational dependencies.
- **Zoom into Q6-Q10 (Narrow Funnel)** once you've identified high-leverage areas (e.g., seriousness classification, expectedness assessment, heterogeneous format extraction).
- **Probe with Q11-Q15** to assess delegation readiness: codifiability, exception rate, risk tolerance, human trust, and documentation feasibility.
- **Listen for lived vs. documented process**: If the stakeholder says "we follow ICH E2A strictly" but then describes five judgment calls, probe for the actual criteria they use in practice.
- **Watch for contradictions**: If Dr. Iyer says "case processing is straightforward" but also mentions "75-minute average per case with a backlog", dig into where the complexity lives.
- **Quantify everything**: "About how many cases per month require follow-up?", "What percentage of reports are social media extracts?", "How often does a case get flagged during audit?"

---

**Next Steps**:
1. Conduct discovery calls with Dr. Iyer (case processing lived experience), Theo Lonergan (operations/backlog), Greta Schäffer (compliance/audit trail), Carolina Núñez-Reyes (multi-jurisdictional reportability).
2. Use post-call debrief to map lived process, identify pause points and judgment calls, assess ATX dimensions.
3. Draft ATX assessment scores and delegation matrix for ADR-1 (intake/extraction) and ADR-2 (seriousness/expectedness/reportability triage).
