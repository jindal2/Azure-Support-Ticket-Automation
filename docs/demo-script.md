# 3 to 5 Minute Technical Demonstration Script — Support Ticket Automation
## AI-Assisted Support Ticket Automation Walkthrough

This script provides an exact, structured walkthrough suitable for your technical presentation or video demonstration recording.

---

### Phase 1: Project Overview & Architecture (0:00 – 0:30)

**Spoken Talking Points:**
> "Hello. Today I am presenting the Support Ticket Automation system, an AI-assisted support ticket processing and triage platform.
> 
> The system tackles support backlog challenges by automating initial classification, priority scoring, team routing, extractive summarization, and response drafting for four core domains: Billing, Technical, Access, and General.
> 
> Most importantly, the system is designed with a strict human-in-the-loop review architecture. No automated draft is ever released to a customer without human authorization. The entire system is built with zero-cost open-source tools: Python, FastAPI, SQLite, scikit-learn, React, and Vite, while remaining completely ready for Microsoft Azure deployment."

**Screen Action:**
- Show the browser running the React dashboard at `http://localhost:5173`.
- Point out the clean enterprise design, the system metrics overview cards at the top, and the green "Backend: Online" health badge.

---

### Phase 2: Ingesting Standard Support Ticket (0:30 – 1:15)

**Spoken Talking Points:**
> "Let's demonstrate a standard ticket submission. In the Create Ticket panel, I'll load our sample preset for a double charge billing enquiry.
> 
> When I click 'Ingest & Process', the FastAPI backend processes the request in milliseconds."

**Screen Action:**
- In the **Load Sample Scenario** dropdown, select `Billing: Double Charge` (fills ID `BILL-101` and message `"I was charged twice on my credit card for the monthly subscription."`).
- Click **Ingest & Process Ticket**.
- The Ticket Inspector modal opens automatically.
- Point out:
  1. **Predicted Category:** `Billing` (highlighting the scikit-learn TF-IDF + Logistic Regression classification).
  2. **Confidence Score:** ~45% (well above random chance baseline of 25% for 4 categories).
  3. **Priority:** `MEDIUM` (standard operational issue).
  4. **Assigned Team:** `Billing Support`.
  5. **Extractive Summary:** Accurately extracts the primary issue without hallucinating facts.
  6. **Draft Customer Response:** Polite template acknowledging the charge without making unverified promises of refunds.
  7. **Review Status:** `PENDING_REVIEW` (awaiting human sign-off).

---

### Phase 3: Handling Ambiguity & Critical Risk Overrides (1:15 – 1:45)

**Spoken Talking Points:**
> "Now let's demonstrate the system's safety and uncertainty handling. In real life, customer queries can be ambiguous or represent critical system emergencies.
> 
> Let's submit a ticket reporting a widespread production outage: `CRITICAL OUTAGE: Entire production service is down, all users receiving 500 errors`."

**Screen Action:**
- Select the `Critical Outage (Safety Override)` preset or `Ambiguous` preset.
- Click **Ingest & Process Ticket**.
- In the Inspector modal, show:
  1. **Priority:** Escalated to `CRITICAL`.
  2. **Review Status:** Marked with an amber warning badge: `⚠ NEEDS REVIEW`.
  3. **Explanation:** The deterministic safety rules detected a widespread failure and overrode standard routing to flag the ticket for urgent human attention.

---

### Phase 4: Duplicate Ticket Validation & HTTP 409 Handling (1:45 – 2:15)

**Spoken Talking Points:**
> "Data integrity is critical. If a client network retries a submission or an agent submits a duplicate ticket ID, the system must not create duplicate records.
> 
> Watch what happens if I attempt to re-submit the existing ticket ID."

**Screen Action:**
- Type an already created ticket ID (e.g. `BILL-101`) into the Ticket ID field with any message.
- Click **Ingest & Process Ticket**.
- Point out the red validation alert:
  `"Duplicate Ticket ID Conflict (HTTP 409): Ticket ID 'BILL-101' already exists in database."`
- Explain: *"This is protected both by input validation and an atomic database unique constraint in SQLite, preventing duplicate database records."*

---

### Phase 5: Human Review Approval & Rejection Workflow (2:15 – 2:45)

**Spoken Talking Points:**
> "Now let's inspect the Human Review panel inside the ticket inspector. Newly created drafts are never marked READY on creation.
> 
> For our billing ticket, I enter my reviewer name, check the mandatory confirmation box, and click 'Approve & Mark READY'."

**Screen Action:**
- In the Review Panel for `BILL-101`:
  1. Reviewer identity: `Agent Sarah Jenkins`.
  2. Check: `I confirm this response has been verified and meets support guidelines.`
  3. Click **Approve & Mark READY**.
  4. The status immediately updates to a green badge: `✓ READY`.
- Now open another ticket (e.g. `GEN-001` or `AMB-001`):
  1. Enter rejection reason: `"Customer requested custom enterprise SLA terms. Draft needs revision."`
  2. Click **Reject Draft**.
  3. Status updates to `✕ REJECTED`.

---

### Phase 6: Audit History & Real-Time Dashboard Metrics (2:45 – 3:15)

**Spoken Talking Points:**
> "Every action taken on a ticket is permanently recorded in the immutable audit trail table."

**Screen Action:**
- Scroll down in the modal to the **Audit Trail & Action History** section.
- Point out the chronological timeline:
  - Event 1: `CREATED` by `SYSTEM_AI_ROUTER` (Initial status `PENDING_REVIEW`).
  - Event 2: `APPROVED` by `Agent Sarah Jenkins` (Transition `PENDING_REVIEW → READY`).
- Close the modal and show the **Dashboard Overview Cards** at the top:
  - Point out that **Total Ingested**, **Needs Review**, **Ready (Approved)**, and **Rejected** counters have dynamically updated based on actual database records.

---

### Phase 7: Automated Tests & Held-Out Classifier Evaluation (3:15 – 4:00)

**Spoken Talking Points:**
> "To guarantee code reliability and ML reproducibility, the repository includes a comprehensive automated test suite and held-out evaluation script."

**Terminal Action:**
- Switch to terminal and run pytest:
  ```powershell
  .\backend\venv\Scripts\python.exe -m pytest -v backend/tests
  ```
- Point out: **All 28 tests pass**, covering health, ML uncertainty, priority overrides, validation, duplicate rejection (409), approvals, state transitions, audit trail, and metrics.
- Run the held-out classifier evaluation script:
  ```powershell
  .\backend\venv\Scripts\python.exe backend/scripts/evaluate_model.py
  ```
- Point out: **87.5% out-of-sample accuracy** on 16 held-out test samples with per-category precision, recall, F1-scores, and confusion matrix.

---

### Phase 8: Azure Architecture, OIDC CI/CD, & Cost Control (4:00 – 5:00)

**Spoken Talking Points:**
> "Finally, let's discuss our production Azure architecture:
> 
> 1. In Azure, the React frontend deploys to Azure Static Web Apps, and the FastAPI container deploys to Azure App Service Linux.
> 2. The local SQLite database seamlessly migrates to Azure Database for PostgreSQL Flexible Server with zero ORM code changes.
> 3. Our GitHub Actions workflow (`deploy-azure.yml`) is configured for manual execution using Azure OpenID Connect (OIDC) Workload Identity Federation. This means zero long-lived secrets or passwords are stored in GitHub.
> 4. For cost control: local development costs zero dollars. In Azure, resources can be provisioned in the free or basic B1 tier and decommissioned immediately after testing.
> 
> Thank you! I am now happy to answer any technical questions."
