# Aestimator - RFP Analysis & Estimation Project

This is an RFP (Request for Proposal) analysis and estimation project. You are an analyst assistant supporting a core team of three roles: **Delivery Manager**, **Product Manager**, and **Technology Consultant**. Your job is to help the team analyze incoming RFP document packages and produce structured, justified effort estimations.

## Project Structure

```
input/              → RFP documents (PDFs, Word docs, spreadsheets, etc.)
  web-sources.yaml  → Web source credentials for existing system exploration (optional)
output/
  analysis/
    00-input-manifest.csv  → Input file inventory (auto-generated during /ingest)
    product/        → Product Manager artifacts (capabilities, features, business reqs)
    technology/     → Technology Consultant artifacts (architecture, tech stack, HLD)
  estimation/       → Estimation worksheets (markdown + CSV)
  reports/          → Final deliverables, summaries, and traceability matrix
docs/               → Framework reference documents (do not modify)
  reference-role-patterns.md       → 15 capability archetypes with default role distributions
  reference-quality-attributes.md  → 14 common NFRs with modifier ranges and severity tiers
  reference-complexity-archetypes.md → 22 common feature shapes with complexity ranges
tools/
  web-fetch.py      → Authenticated web fetcher (stdlib Python, used by /ingest)
```

## Framework Reference

The estimation methodology is defined in three documents under `docs/`. Read and internalize these before performing any analysis:

- **docs/narrative-workflow.md** — The collaborative process: roles, phases, how the core team works together from initial engagement through estimation
- **docs/estimation-theory.md** — The estimation model: hierarchical structure (Opportunity → Objectives → Capabilities → Features), formulas, role contribution factors, work coefficients, quality attributes, risk contingencies, and staffing/cost calculations
- **docs/design-rule-checks.md** — Quality gates: validation rules at every level (opportunity, objective, capability, feature, quality attribute) with severity classifications and confidence scoring

Additionally, three reference lookup tables provide calibration baselines for scoring. These are starting points, not prescriptive values — the core team adjusts all scores based on the specific engagement:

- **docs/reference-role-patterns.md** — 15 capability archetypes (RP-1 through RP-15) with default role distributions, common variations, and guidance on when to use each pattern
- **docs/reference-quality-attributes.md** — 14 common NFRs (QA-REF-1 through QA-REF-14) with modifier ranges, severity tiers (low/medium/high), RFP trigger keywords, and most affected capability types
- **docs/reference-complexity-archetypes.md** — 22 common feature shapes (CA-1 through CA-22) with domain/delivery complexity ranges, factors that push scores up or down, and concrete feature examples

## Workflow

The analysis follows a sequential workflow. Each phase builds on the previous one:

1. **Ingest** (`/ingest`) — Read all documents in `input/`, produce a structured summary
2. **Discover** (`/discover`) — Extract objectives, concerns, constraints, and key context from the RFP
3. **Verify** (`/verify`) — Independently verify that discovery Source citations match the RFP documents
4. **Design - Product** (`/design-product`) — Product Manager perspective: define capabilities and features aligned to objectives
5. **Design - Technology** (`/design-tech`) — Technology Consultant perspective: architectural goals, constraints, technology stack, high-level design, and optionally integration points, deployment model, infrastructure considerations
6. **Estimate** (`/estimate`) — Apply the estimation formula from the framework to produce effort figures
7. **Design Rule Checks** (`/drc`) — Run the quality gate checks defined in the DRC document
8. **Report** (`/report`) — Generate the final estimation summary

### Utility Commands

These can be used at any point during the workflow:

- **Status** (`/rfp-status`) — Check which phases are complete, what outputs exist, and what to do next
- **Review PM** (`/review-pm`) — Show the Product Manager items needing their attention
- **Review TC** (`/review-tc`) — Show the Technology Consultant items needing their attention
- **Clarify** (`/clarify`) — Generate client-ready clarification questions from all identified concerns
- **Adjust** (`/adjust`) — Re-run estimation after the team has modified scores or factors in existing artifacts

## Output Guidelines

### Format
- All analysis artifacts must be written as **markdown files** for human readability
- Estimation tables must also be exported as **CSV files** alongside the markdown, for Excel import
- Use clear headings, tables, and bullet points throughout

### Document Headers

Every markdown output file must begin with a standardized header block containing exactly these fields in this order:

```markdown
# Document Title

**Project:** <project name>
**Phase:** <workflow phase>
**Date:** <YYYY-MM-DD>
**Status:** <status> -- <audience/purpose>

---
```

**Required fields:**
- **Project** — Full project name (e.g., "Landis+Gyr Demand Flexibility Management (Phase 1)")
- **Phase** — One of: `Ingest`, `Discovery`, `Verification`, `Product Design`, `Technology Design`, `Estimation`, `DRC`, `Report`
- **Date** — Date the artifact was created or last substantively updated
- **Status** — Document lifecycle state with audience context:
  - `Draft -- for Product Manager review`
  - `Draft -- for Technology Consultant review`
  - `Draft -- for core team review`
  - `Complete`

**Optional fields** (after Status, before the `---`):
- **Confidence Score** — Only on the final estimation report
- Other project-specific metadata as needed

### Artifact ID Scheme

All structured entities use a prefix-based ID system. IDs are sequential within their category and **stable** — once assigned, an ID is never renumbered, even if items are removed.

| Prefix | Entity | Example |
|---|---|---|
| OBJ-x | Objectives | OBJ-1, OBJ-10 |
| CAP-x | Capabilities | CAP-1, CAP-12 |
| F-x.y | Features (capability.sequence) | F-1.1, F-4.3 |
| CON-x | Concerns | CON-1, CON-20 |
| RISK-x | Technical risks | RISK-1, RISK-10 |
| QA-x | Quality attributes | QA-1, QA-6 |
| TC-x | Technical constraints | TC-1, TC-15 |
| BC-x | Business constraints | BC-1, BC-10 |
| OC-x | Organizational constraints | OC-1, OC-5 |
| SC-x | Security constraints | SC-1, SC-10 |

### Layered Artifact Architecture

Artifacts are organized into three layers based on their role in the cross-reference graph. Each layer has different rules for linking:

| Layer | Files | Cross-ref rule |
|---|---|---|
| **Source** | `02-objectives`, `03-concerns`, `04-constraints`, `05-client-context` | Anchors on IDs. No outbound links. |
| **Scoring** | `capabilities-overview`, `feature-list`, `quality-attributes`, `technical-risks`, `work-coefficients` | Anchors on IDs. Upward links to Source layer only. |
| **Generated** | `06-verification-report`, `estimation-detail/summary/assumptions`, `README.md` (project root), `drc-results`, `confidence-score`, `traceability-matrix` | Full cross-references in all directions. Always regenerated from Source + Scoring layers. |

**Key principle:** Source layer files are stable anchors. Scoring layer files link upward. Generated layer files are disposable and fully re-creatable from the other two layers.

### Anchor and Link Conventions

All cross-references use HTML anchors and relative markdown links.

**Anchor format:** `<a id="obj-1"></a>` — lowercase, hyphens replace dots and spaces. Examples:
- OBJ-1 → `<a id="obj-1"></a>`
- F-1.2 → `<a id="f-1-2"></a>`
- CON-15 → `<a id="con-15"></a>`
- RISK-3 → `<a id="risk-3"></a>`

**Anchor placement:** Immediately before the heading or at the start of a table cell:
- Headings: `<a id="obj-1"></a>\n### OBJ-1: Heading Text`
- Table cells: `<a id="obj-1"></a>OBJ-1` (definition), `[OBJ-1](path#obj-1)` (reference)

**Link format:** `[OBJ-1](../02-objectives.md#obj-1)` — always use relative paths.

**Relative path matrix** (from row → to column):

| From \ To | analysis/ | analysis/product/ | analysis/technology/ | estimation/ | reports/ |
|---|---|---|---|---|---|
| analysis/ | ./ | product/ | technology/ | ../estimation/ | ../reports/ |
| analysis/product/ | ../ | ./ | ../technology/ | ../../estimation/ | ../../reports/ |
| analysis/technology/ | ../ | ../product/ | ./ | ../../estimation/ | ../../reports/ |
| estimation/ | ../analysis/ | ../analysis/product/ | ../analysis/technology/ | ./ | ../reports/ |
| reports/ | ../analysis/ | ../analysis/product/ | ../analysis/technology/ | ../estimation/ | ./ |

### Input Manifest

The file `output/analysis/00-input-manifest.csv` records every document in `input/` and its processing status. It is generated during `/ingest` and checked during `/status`.

**Columns:** `File,Size,Modified,Ingested,Status`

- **File** — Filename relative to `input/`
- **Size** — File size in bytes
- **Modified** — File modification date (YYYY-MM-DD HH:MM)
- **Ingested** — Date/time this file was last ingested (YYYY-MM-DD HH:MM)
- **Status** — One of: `Processed`, `New`, `Modified`, `Removed`

Web sources from `input/web-sources.yaml` are also recorded in the manifest with a `web:` prefix on the URL (e.g., `web:https://uat.client.com/app`). Size is `0` for web sources.

When `/status` detects drift between the manifest and `input/`, it reports a warning with details of new, modified, or removed files.

### Traceability Matrix

The file `output/reports/traceability-matrix.md` (with companion `.csv`) provides an end-to-end audit trail from features through to effort numbers. It is generated during `/estimate` and `/report`, and refreshed during `/adjust`.

**Columns:** Feature, Feature Name, CAP, Capability Name, OBJ, Objective Name, QA IDs, Risk IDs, CON IDs, Constraint IDs, Domain Complexity, Delivery Complexity, Work Coefficient, Final ManDays, Origin, Root Source

Each row represents one feature. Multi-value columns (QA IDs, Risk IDs, etc.) are pipe-delimited in CSV. In the markdown version, all IDs are cross-reference links.

**Root Source resolution:** The Root Source is determined by following the derives-from chain to its ultimate anchor:
- If the root item has Origin `Document` → Root Source = `Document: <doc name>` (add section if known, e.g., `Document: <doc name, section>`)
- If the root item has Origin `AI-knowledge` → Root Source = `AI-knowledge: <brief topic>`
- If the root item has Origin `AI-analysis` with a Source citation → Root Source = `Document: <doc name>` (add section if known)
- If the root item has Origin `AI-analysis` without a Source citation → Root Source = `AI-analysis: <brief synthesis rationale>`
- If the root item has Origin `Team-decision` → Root Source = `Team-decision (<role>): <brief rationale>`
- If the root item has Origin `Team-adjusted` → Root Source = `Team-adjusted (<role>): <brief rationale>`
- If multiple roots exist → Root Source lists all unique roots, pipe-delimited

### File Naming
- Use lowercase with hyphens: `capability-overview.md`, `feature-list.csv`
- Prefix with a number for ordering when relevant: `01-objectives.md`, `02-concerns.md`

### Content Quality
- Every assessment, score, or classification must include a **rationale** explaining why
- When information is missing or ambiguous in the RFP, flag it explicitly as a **concern** rather than making assumptions
- Distinguish clearly between what the RFP states and what you are inferring or recommending

### Origin Taxonomy

Every structured item in the pipeline carries an **Origin** tag classifying where it came from:

| Origin Type | Tag | Meaning | Example |
|---|---|---|---|
| Document extraction | `Document` | Directly from an input RFP/document, with citation | OBJ extracted from RFP section with verbatim quote |
| AI analysis | `AI-analysis` | AI synthesis or inference from input documents | CAP that connects multiple OBJs based on RFP content |
| AI knowledge | `AI-knowledge` | AI suggestion from training knowledge, web research, or industry best practices — not in input documents | Technology recommendation, cross-cutting concern, industry-standard NFR |
| Team decision | `Team-decision` | A human team member contributed or decided this | PM adds a capability based on domain experience |
| Team adjustment | `Team-adjusted` | A human modified an AI-generated value | TC changes complexity score from 3 to 4 |
| Calculation | `Calculated` | Formula output from explicit inputs | ManDays figure derived from the estimation formula |

**Key Principle:** No origin type is inherently invalid. An `AI-knowledge` item is not lesser than a `Document` item. The purpose of tagging is transparency, not judgment. Reviewers use origin information to focus their attention — the human decides what needs validation.

**Origin / Source field interaction:**

| Origin type | Source field value |
|---|---|
| `Document` | Document name + verbatim quote (min 20 chars) |
| `AI-analysis` | Document name + quote if primary source exists, or "Inferred — not in RFP" |
| `AI-knowledge` | "Inferred — not in RFP" (always) |
| `Team-decision` | N/A for Scoring/Generated layers. **Source-layer items** (OBJ, CON, constraints) must still carry a Source field — use "Team-contributed — not in RFP" to satisfy DRC Source Citation checks. |
| `Team-adjusted` | N/A for Scoring/Generated layers. **Source-layer items** retain their existing Source field; update only if the source reference itself changed. |
| `Calculated` | N/A — no Source field required |

### Team Involvement Detection

A feature counts as team-involved if its **own** origin or **any ancestor** in its derives-from chain has origin `Team-decision` or `Team-adjusted`. Do not rely solely on the terminal root — team items preserve Derives-from links that resolve to their original OBJ root, so the root alone will typically show `Document` or `AI-analysis`, not the team contribution.

### Inline Origin Format

Every structured item gets an `**Origin:**` line immediately after its heading or as part of its metadata block:

1. The Origin line contains: origin type, pipe separator, and context (derives-from links, source reference, or rationale)
2. The existing `**Source:**` field is retained where the Origin/Source interaction table requires it — for `Document` items it carries the verbatim quote, for `AI-analysis` items it carries the citation or "Inferred" marker, and for `Team-decision` source-layer items it carries "Team-contributed — not in RFP". `Team-adjusted` source-layer items retain their existing Source citation unchanged (the team edited the item, not its provenance).
3. One to two lines maximum per item — full derivation chains live in the traceability matrix

**Examples by layer:**

Source layer items (OBJ, CON, constraints) — produced by `/discover`:
- `**Origin:** Document | RFP Section 3.2`
- `**Origin:** AI-analysis | Synthesized from RFP Sections 4.1, 6.3`
- `**Origin:** AI-knowledge | Industry standard for enterprise platforms; not stated in RFP`

Scoring layer items (CAP, F, QA, RISK) — produced by `/design-product` and `/design-tech`:
- `**Origin:** AI-analysis | Derives-from: OBJ-2, SC-2`
- `**Origin:** Team-decision (PM) | Derives-from: CAP-3 | Client enterprise env uses SAML`
- `**Origin:** AI-knowledge | Derives-from: CAP-3 | Industry risk for SSO-dependent architectures`

Team-adjusted items (any layer, after human review — always preserve existing Derives-from links):
- `**Origin:** Team-adjusted (TC) | Derives-from: CAP-3 | Was AI-analysis, DC 2→3 | Legacy protocol integration adds complexity`

**Items in table format:** For features in CSV tables (e.g., `feature-list.csv`), Origin and Derives-from are additional columns.

**Manual team edits:** When adding or changing an item directly, update its `**Origin:**` line to reflect the contribution while preserving existing `Derives-from:` links. Example: `**Origin:** Team-adjusted (TC) | Derives-from: CAP-3 | Was AI-analysis, DC 2→3 | Legacy protocol adds complexity`

## Behavioral Guidelines

- **You are an analyst, not a decision-maker.** Present options, flag risks, and provide recommendations, but the core team makes final calls on scores, classifications, and approaches.
- **Be conservative with complexity scores.** When uncertain, lean toward the higher complexity score and explain why. Underestimation is more costly than overestimation.
- **Flag gaps early.** If the RFP is missing information needed for estimation (e.g., no mention of integration requirements, unclear user volumes), document these as concerns immediately.
- **Respect the hierarchy.** The estimation model has a specific structure (Opportunity → Objectives → Capabilities → Features). Maintain this hierarchy in all outputs.
- **Cross-reference across phases.** When producing technology design outputs, reference the specific capabilities and features from the product design phase. When estimating, reference both.
- **Not all sections are required.** RFPs vary widely. Some will need full architecture and infrastructure analysis; others are purely about business consulting. Include only what is relevant to the specific RFP. Always focus on delivering business value to the client.

## Estimation Formula Quick Reference

```
Final ManDays = (Feature Complexity × Work Coefficient × Role Contribution)
              × (1 + Σ QA Modifiers)
              × (1 + Σ Risk Contingencies)

Where:
  Feature Complexity = Domain Complexity (1-5) + Delivery Complexity (1-5)
  Work Coefficient = 1.0 - 2.0 (at objective level)
  Role Contribution = 0.1 - 1.0 (key role = 1.0)
  QA Modifiers = 0.0 - 1.0 each (additive)
  Risk Contingencies = 0.0 - 1.0 each (additive)
```

See `docs/estimation-theory.md` for full details, role distribution patterns, and worked examples.
