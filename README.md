# Canvas Troubleshooting Assistant

A Streamlit-based troubleshooting application for **Instructional Designers, instructors, and course-support staff** who need to investigate Canvas course and assignment configuration issues without needing to understand Canvas APIs, JSON internals, LTI implementation details, or Python.

> **Current status:** Functional prototype moving toward deployment readiness.

---

## 1. Product Goal

The Canvas Troubleshooting Assistant turns Canvas configuration data into a structured diagnosis.

The current workflow is:

```text
Canvas JSON
    ↓
Response recognition
    ↓
Data extraction / normalization
    ↓
Deterministic troubleshooting rules
    ↓
Evidence-based diagnosis
    ↓
Instructor-friendly recommendation
```

The long-term goal is to reduce the manual investigation required when instructors or course designers are told that an assignment, module, or external learning activity is not working.

The application is **not currently student-facing**.

---

## 2. Intended Users

Primary users:

- Instructional Designers
- Course Designers
- Instructors
- Course-support staff

These users should not need coding knowledge.

The main interface should answer:

1. **What are we looking at?**
2. **What problem was detected?**
3. **What evidence supports that conclusion?**
4. **What information is still unknown?**
5. **What should the instructor or designer do next?**

Technical Canvas terminology should be hidden or translated when it is not necessary for the user.

---

## 3. Current Capabilities

The application currently supports:

- Pasting Canvas JSON.
- Uploading Canvas JSON files.
- Processing large nested Canvas responses.
- Recognizing supported Canvas response structures.
- Extracting assignment information from nested responses.
- Distinguishing an assignment ID from surrounding object IDs such as assignment-group IDs.
- Extracting module, navigation, and configuration information where supported.
- Running assignment, module, and external-tool/LTI troubleshooting checks.
- Generating evidence-based findings and recommendations.
- Generating a downloadable troubleshooting report.
- Optional PostgreSQL persistence for troubleshooting history.
- Running in **stateless mode without PostgreSQL**.

### Tested behaviors

The project has been tested with:

- Assignment responses.
- Module responses.
- Combined assignment/module data.
- Large Canvas JSON responses.
- Invalid JSON.
- Valid but unsupported JSON.
- External-tool assignments.
- Published and unpublished assignment states.
- PostgreSQL-enabled mode.
- PostgreSQL-disabled/stateless mode.

---

## 4. Important Product Decisions

### Deterministic rules establish facts

Canvas facts should be evaluated with Python rules whenever possible.

Examples:

```python
published is False
```

```python
unlock_at >= lock_at
```

```python
"external_tool" in submission_types
```

An AI/LLM should **not** be responsible for deciding these facts.

### Missing data is not automatically an error

Examples:

```json
"due_at": null
```

or:

```json
"unlock_at": null
```

do not automatically mean something is broken.

The troubleshooting engine should distinguish:

- Confirmed problem
- Evidence supporting a troubleshooting path
- Ruled-out condition
- Unknown / additional data required

### External-tool detection does not prove an LTI failure

If:

```json
"submission_types": ["external_tool"]
```

the application knows that an external learning tool is involved.

It does **not** automatically mean the external tool is broken.

The diagnostic engine should first consider available evidence such as:

- Assignment publication state
- Availability dates
- Module visibility
- Course availability
- External-tool resource information
- LTI configuration evidence

### Recommendations should be instructor-friendly

Avoid making the primary recommendation:

> Verify LTI configuration.

Prefer language such as:

> The assignment itself appears available. Because it launches through an external learning tool, verify the module/course visibility and then check the external-tool connection.

Technical evidence can remain available for support staff.

---

## 5. Current Architecture

```text
app.py
  │
  ├── extraction/
  │     ├── json_recognizer.py
  │     └── extract_json.py
  │
  ├── troubleshooting/
  │     ├── assignment_checks.py
  │     ├── module_checks.py
  │     ├── lti_checks.py
  │     └── run_checks.py
  │
  ├── reports/
  │     └── report_generator.py
  │
  └── database/                  OPTIONAL
        ├── connection.py
        ├── operations.py
        └── schema.sql
```

### Responsibility by component

| Component | Responsibility |
|---|---|
| `app.py` | Streamlit UI and application workflow |
| `extraction/json_recognizer.py` | Determines which supported Canvas structures are present |
| `extraction/extract_json.py` | Extracts and normalizes useful Canvas information |
| `troubleshooting/assignment_checks.py` | Assignment availability/submission checks |
| `troubleshooting/module_checks.py` | Module-related checks |
| `troubleshooting/lti_checks.py` | External-tool/LTI diagnostic logic |
| `troubleshooting/run_checks.py` | Coordinates available troubleshooting checks |
| `reports/report_generator.py` | Generates downloadable troubleshooting reports |
| `database/connection.py` | Optional PostgreSQL connection |
| `database/operations.py` | Optional persistence/history operations |
| `database/schema.sql` | PostgreSQL schema |

---

## 6. Canonical Assignment Information

The extractor currently aims to normalize useful assignment information into a structure similar to:

```python
{
    "assignment_id": "...",
    "assignment_group_id": "...",
    "course_id": "...",
    "name": "...",
    "published": True,
    "workflow_state": "published",
    "due_at": None,
    "unlock_at": None,
    "lock_at": None,
    "submission_types": ["external_tool"],
    "allowed_attempts": -1,
    "points_possible": 100.0,
    "grading_type": "percent",
    "external_tool": {...}
}
```

### Important ID distinction

A Canvas response may contain many fields named `id`.

For example:

```text
Assignment Group ID → 1202969
Assignment ID       → 6981111
Course ID           → 242191
```

Do not identify an assignment by simply selecting the first `id` in a nested JSON response.

The assignment object should be identified from its surrounding structure and assignment-specific fields.

---

## 7. Troubleshooting Result Model

The project is moving toward a standardized diagnostic result such as:

```python
{
    "issue": "External tool / LTI troubleshooting required",
    "category": "LTI / External Tool",
    "severity": "Information",
    "confidence": "Needs more data",
    "evidence": [
        "Assignment is published",
        "Resource link ID is present"
    ],
    "required_data": [
        "Module visibility",
        "Course availability",
        "LTI tool configuration"
    ],
    "recommendation": "..."
}
```

Future troubleshooting rules should follow this evidence-based approach.

---

## 8. Database Modes

PostgreSQL is now **optional**.

The application must remain fully usable when persistence is disabled.

### Stateless mode — recommended for initial deployment

```env
DATABASE_ENABLED=false
```

Expected behavior:

```text
Canvas data
    ↓
Troubleshooting
    ↓
Diagnosis
    ↓
Report
```

No PostgreSQL connection should be required.

### Persistent mode

```env
DATABASE_ENABLED=true
```

PostgreSQL can optionally store:

- Courses
- Assignments
- Troubleshooting runs
- Troubleshooting findings
- Historical results

Database history is an optional feature, not part of the core diagnostic engine.

---

## 9. Local Setup

### Clone the repository

```bash
git clone https://github.com/apate332/canvas-troubleshooting-assistant.git
cd canvas-troubleshooting-assistant
```

### Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Start the application

```bash
python -m streamlit run app.py
```

The application should work in stateless mode without PostgreSQL.

---

## 10. Optional PostgreSQL Setup

Only configure PostgreSQL if troubleshooting history/persistence is required.

Example local `.env`:

```env
DATABASE_ENABLED=true

DB_HOST=localhost
DB_PORT=5432
DB_NAME=canvas_troubleshooter
DB_USER=postgres
DB_PASSWORD=your_local_password
```

Never commit `.env`.

Apply the database schema from:

```text
database/schema.sql
```

When PostgreSQL is disabled:

```env
DATABASE_ENABLED=false
```

the application should skip saving/history operations and continue troubleshooting normally.

---

## 11. Security Rules

Never commit:

- `.env`
- Database passwords
- GitHub personal access tokens
- Canvas access tokens
- Real student data
- Real Canvas responses containing sensitive information
- `secure_params`
- Production credentials
- Local virtual environments

The repository should contain application code and safe configuration/documentation only.

Real Canvas troubleshooting data should be supplied at runtime and handled according to organizational policy.

---

## 12. Current UI Direction

The application should feel like a **diagnostic workspace**, not an analytics dashboard.

The intended information hierarchy is:

```text
Canvas Troubleshooting Assistant

Input

Assignment
  Assignment name
  Course ID
  Assignment ID
  Status

Diagnosis
  What appears wrong
  What we know
  What still needs checking
  Recommended next step

Assignment Details
  Optional technical/configuration information

Download Report

Previous Runs
  Only when persistence is enabled
```

Avoid unnecessary KPI/statistic cards that do not help troubleshoot the current issue.

The current diagnosis should be visually dominant.

---

## 13. Testing Philosophy

Do not judge a change only by whether Python runs.

Each troubleshooting rule should be tested against controlled scenarios.

Examples:

| Scenario | Expected behavior |
|---|---|
| Published external-tool assignment | Do not claim LTI is broken; identify next evidence required |
| Unpublished assignment | Confirm publishing issue |
| Unlock date after lock date | Confirm availability-date problem |
| Missing due date | Do not automatically report an error |
| Non-LTI assignment | Do not produce LTI findings |
| Missing publishing information | Report that publishing status cannot be verified |
| Unsupported valid JSON | Recognize as unsupported/unknown without crashing |
| Invalid JSON | Fail gracefully |

When changing extraction logic, verify that the correct nested Canvas object is selected.

---

## 14. Deployment Direction

The recommended deployment progression is:

```text
CURRENT
Streamlit + JSON + Rules
        ↓
PHASE 1
Stateless + deployment-ready dependencies
        ↓
PHASE 2
Docker + company-approved hosting + authentication
        ↓
PHASE 3
Canvas API integration
        ↓
PHASE 4
Optional LLM assistance
        ↓
MATURE PRODUCT
Automated Canvas evidence retrieval
+ deterministic diagnosis
+ instructor-friendly explanation
+ escalation support
```

### Phase 1 — Current priority

- Keep PostgreSQL optional.
- Simplify `requirements.txt`.
- Ensure a fresh environment can run the application.
- Improve automated tests.
- Dockerize the application.
- Update documentation.

### Phase 2 — Internal pilot

Work with the organization to determine:

- Hosting platform
- Authentication / SSO
- Network access
- Logging requirements
- Data-handling requirements
- Production ownership

### Phase 3 — Canvas API integration

The long-term user experience should not require instructors to understand or manually collect JSON.

With approved Canvas API access, the application could retrieve the necessary:

- Course information
- Assignment information
- Module/module-item information
- Availability settings
- External-tool information

Only the minimum permissions required for troubleshooting should be requested.

### Phase 4 — LLM assistance

An LLM may later be used to:

1. Understand an instructor's natural-language problem description.
2. Select the appropriate troubleshooting path.
3. Convert structured evidence into a clear explanation.
4. Help create an escalation summary when the issue cannot be resolved automatically.

The LLM should **not replace deterministic Canvas checks**.

Preferred architecture:

```text
Instructor problem description
        ↓
LLM: understand problem type
        ↓
Canvas evidence
        ↓
Deterministic rule engine
        ↓
Structured facts / unknowns
        ↓
LLM: explain and recommend
        ↓
Instructor-friendly diagnosis
```

Do not send large raw Canvas responses to an LLM when normalized evidence is sufficient.

Any production LLM integration must follow organizational privacy/security approval.

---

## 15. Known Limitations

Current limitations include:

- Canvas data is still supplied manually.
- No direct Canvas API integration.
- No automatic changes are made to Canvas.
- Troubleshooting coverage is not complete.
- Diagnosis is limited by the evidence present in the supplied data.
- External-tool/LTI health cannot be fully verified from assignment data alone.
- Some Canvas response structures still require additional validation.
- The application is a prototype and has not yet completed an internal production deployment review.

---

## 16. Git / Team Workflow

Before starting work:

```bash
git pull
```

For significant changes, create a branch:

```bash
git checkout -b feature/descriptive-name
```

After making changes:

```bash
git status
git add .
git commit -m "Describe the change"
git push -u origin feature/descriptive-name
```

Use a Pull Request when merging significant changes into `main`.

Never commit credentials or real Canvas/student data.

---

## 17. Current Development Priorities

Work in approximately this order:

1. Verify stateless mode remains stable.
2. Simplify and validate `requirements.txt`.
3. Test installation in a fresh Python environment.
4. Expand controlled diagnostic tests.
5. Standardize diagnostic output across assignment/module/LTI checks.
6. Improve instructor-facing wording.
7. Add Docker configuration.
8. Build and run the Docker image locally.
9. Document company deployment requirements.
10. Plan Canvas API integration with Canvas administrators.
11. Evaluate an LLM layer only after the deterministic diagnostic foundation and organizational data requirements are clear.

---

# AI / ChatGPT Handoff Context

If you are an AI assistant helping a collaborator continue this project, use the following as the project's source-of-truth context.

## Product identity

This is an **instructor/course-designer Canvas troubleshooting assistant**.

It is **not currently a student-facing chatbot**.

The goal is to help nontechnical instructors, Instructional Designers, and course-support staff investigate Canvas configuration problems efficiently.

## Architecture rules

1. **Do not replace deterministic troubleshooting rules with an LLM.**
2. Use Python/rules to establish Canvas facts.
3. Treat missing evidence as unknown rather than automatically as an error.
4. Do not assume an external-tool assignment means LTI is broken.
5. Preserve evidence behind every diagnosis.
6. Recommendations should distinguish confirmed problems from possible causes and missing evidence.
7. Keep PostgreSQL optional.
8. The application must work with `DATABASE_ENABLED=false`.
9. Do not expose database implementation details in the primary instructor UI.
10. Do not require the user to understand JSON/LTI/API terminology in the final product.
11. Do not commit or request real credentials, access tokens, student data, or sensitive Canvas data.
12. Do not confuse assignment-group IDs with assignment IDs.
13. Do not add charts/statistics unless they directly improve troubleshooting.
14. The current JSON workflow is a prototype input mechanism; the long-term direction is approved Canvas API integration.
15. An eventual LLM should operate primarily on structured/normalized diagnostic evidence, not raw large Canvas payloads.

## Current development stage

The project is transitioning from a working local prototype to **deployment readiness**.

The immediate focus is:

```text
Stateless operation
    ↓
Clean dependencies
    ↓
Fresh-environment testing
    ↓
Automated diagnostic tests
    ↓
Docker
    ↓
Internal deployment planning
```

Do not jump directly to Canvas API or LLM integration before stabilizing this foundation.

## When helping with code

Before proposing a change:

1. Inspect the existing relevant file/function.
2. Preserve working behavior unless the change explicitly replaces it.
3. Make one architectural change at a time.
4. Run syntax/tests after changes.
5. Test behavior with controlled Canvas scenarios.
6. Avoid inventing Canvas semantics that have not been verified.
7. Prefer clear, maintainable Python over clever abstractions.
8. Keep the instructor-facing UI simple and human-readable.

## Key files

Start here depending on the task:

```text
UI / workflow
→ app.py

Recognition
→ extraction/json_recognizer.py

Canvas extraction / normalization
→ extraction/extract_json.py

Assignment diagnostics
→ troubleshooting/assignment_checks.py

Module diagnostics
→ troubleshooting/module_checks.py

External-tool / LTI diagnostics
→ troubleshooting/lti_checks.py

Check orchestration
→ troubleshooting/run_checks.py

Optional persistence
→ database/connection.py
→ database/operations.py

Reports
→ reports/report_generator.py
```

## Recommended first question for a new AI session

After reading this README, inspect the current Git status and the specific file related to the requested task before suggesting code changes.

The repository may have progressed beyond this README, so confirm the current implementation rather than assuming every future-planning item has already been completed.

## Remote Backend Deployment

### Current Setup

The Chrome extension currently communicates with a FastAPI backend running locally at:

`http://127.0.0.1:8000`

The backend runs the Python troubleshooting logic and communicates with ASU CreateAI to generate troubleshooting guidance.

Because the backend currently runs locally, the **Diagnose Problem** feature only works while the FastAPI service is running on the developer's computer.

### Future Deployment

For the extension to work independently from the developer's computer, the FastAPI backend will need to be deployed to an ASU-approved hosting environment.

The hosted environment will need to support:

- Python
- FastAPI and Uvicorn
- HTTPS
- Secure environment variables
- Outbound access to the ASU CreateAI API

The CreateAI service key must remain on the backend and must not be stored in the browser extension or committed to GitHub.

Once an approved backend is available, the extension's backend URL can be changed from the local development address to the hosted HTTPS address.

### Backend Health Check

The backend provides:

`GET /health`

This can be used to verify that the troubleshooting service is running before diagnosing application issues.