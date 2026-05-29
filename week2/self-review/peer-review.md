# 1-scenario5-cognitive-map.md

## 1. Jobs to be Done (JtDs) Decomposition

### JtD-1: Verify insurance eligibility for scheduled visit

> 2. **Data retrieval** (MEDIUM): Pull from athenahealth → query Availity API

Why medium cognitive zone for an API call?

> 3. **Diagnosis** (HIGH for exceptions): ~30% fail auto-verify [A1], requiring interpretation of Availity response codes, patient history, prior verification dates

Diagnosis is not part of insurance eligibility verification, is it? Should this line here?

> 4. **Decision** (MEDIUM→HIGH): Accept verification / escalate / re-query with different parameters

What's the point of re-query? Is there a case for this?

> **Lived vs. Documented work gap**: 
>- **Documented**: "Verify insurance via Availity for all scheduled appointments"
>- **Lived**: Dana's tacit rule (visible in Artefact 5.3): "Refresh verification if >6 months, especially for chronic patients on stable insurance" — front-desk doesn't consistently apply this [A3], causing billing failures

Was this for insurance eligibility verification via Availity? I think it was about the authorization status via athenahealth (JtD-2).

### JtD-2: Determine prior authorization status and chase pending PAs

> **Trigger**: Scheduled procedure/imaging/referral visit approaching (typically 5-7 days before) 

"5-7 days" seems vague. How do we choose the exact trigger time?

> **Actor**: Dana (primarily) with front-desk support for submission  

Why is Dana the primary actor here? Shouldn't front-desk do this work?

> **Key systems**: athenahealth (PA submission), insurer portals (varying), Dana's Google Sheet (chase tracker)  

Where did insurer portals (varying) come from? Were they mentioned in the scenario?

> **Decision** (VERY HIGH): When to chase (Humana: always 6 days, not 5; UnitedHealthcare Choice: 6-7 days; Aetna: sometimes fast, unpredictable)

Why does it have very high cognitive zone? Isn't it simple to just query the approvals in advance based on the insurer rules?

> - **System → Human**: Insurer portal doesn't update; requires phone call (unstructured)

Where did Insurer portal come from?

> - **Dana → Physician**: Denial requires additional clinical documentation

Does a physician provide the additional documentation? Aren't the previous procedures stored in athenahealth, so front-desk can do that?

> - **Lived**: Dana maintains insurer-specific chase timing in her head and Google Sheet (Artefact 5.1) [A7].

I think "in her head" shouldn't be here. Dana does not do the prior authorization status check - front-desk does that using the Dana's Google Sheet.

## 6. Delegation Archetype Assignment (Preliminary)

> | **Interpret Availity failure codes** | **Agent-led + Human Oversight** | Pattern-learnable (30% exception rate), but requires Dana's validation initially; escalation path for Medicaid managed care |

Why is this not automatic (rule-based)? Availity has some documented API with failure codes - why is Dana involved here?

> | **Determine re-verification timing** | **Agent-led + Human Oversight** | Tacit rule can be encoded (>6mo for chronic patients), but needs Dana to validate rule completeness |

Why is this not automatic (rule-based)?

> | **Determine when to chase PA** | **Agent-led + Human Oversight** | Insurer-specific patterns are learnable from Dana's Google Sheet; agent can recommend chase timing, Dana approves |

Why is this not automatic (rule-based)?

> | **Interpret PA denial & resubmit** | **Human-led + Agent Support** | Agent can surface denial reason and suggest resubmission docs (e.g., "Wellpath colonoscopy: attach prior visit note"), Dana decides |

IMO, for Wellpath we should have a rule to always submit these extra documents instead of extending the approval time with resubmissions.
