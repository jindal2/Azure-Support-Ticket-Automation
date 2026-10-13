# Application Security & Compliance — Support Ticket Automation
## Threat Model, Guardrails, and Data Integrity Policies

### 1. Security Architecture Principles

Security in the Support Ticket Automation system is enforced across code, data persistence, network transmission, and cloud CI/CD pipelines.

| Security Pillar | Implementation in System | Benefit |
| :--- | :--- | :--- |
| **Zero Secrets Policy** | No passwords, tokens, or cloud secrets committed in git history. Config loaded via environment variables. | Eliminates repository credential leaks. |
| **Input Validation** | Pydantic V2 schemas enforce strict types, non-empty whitespace bounds, and length restrictions. | Shields system against malformed payloads and injection attacks. |
| **SQL Injection Prevention** | All persistence handled via SQLAlchemy ORM parameterized queries. Raw string interpolation is strictly banned. | Completely mitigates SQL injection vulnerabilities. |
| **Audit Trail Immutability** | Audit logs (`audit_logs` table) are append-only. No API exists to modify or delete past audit events. | Ensures non-repudiation and regulatory compliance. |
| **Error Sanitization** | Custom FastAPI exception handlers return generic error messages for unhandled 500 exceptions. | Prevents exposure of internal stack traces, library versions, or server paths. |
| **OIDC Cloud Federation** | Azure deployment uses OpenID Connect workload identities instead of long-lived client secrets. | Eliminates secret rotation overhead and credential theft risks. |

---

### 2. Guardrails Against Hallucination & Financial Liability

Support automation systems risk financial and reputational liabilities if machine-learning models make unauthorized commitments to customers.

The response template engine enforces strict compliance guardrails:
1. **No Fabricated Refunds:** The system never writes responses promising monetary credits, fee waivers, or account adjustments.
2. **No False SLA Guarantees:** Response drafts state that specialists are reviewing the issue without fabricating resolution timeframes.
3. **Draft Status Disclaimer:** Automated drafts append an explicit notification: `(Draft pending human approval)`.
4. **Human Review Barrier:** Draft responses remain internal suggestions until an authorized human reviewer explicitly submits an approval with their reviewer identity.

---

### 3. Reviewer Identity & Prototype Disclosures

#### Transparent Prototype Disclosure:
In this local zero-cost demonstration prototype, the `reviewer_identity` field in `/tickets/{ticket_id}/approve` and `/tickets/{ticket_id}/reject` is a validated client-supplied string.
- **Limitation:** In the local environment, this does **not** constitute cryptographically signed or MFA-verified proof of identity.
- **Production Standard:** In a production enterprise deployment, the endpoint must be protected behind **Azure AD / Microsoft Entra ID OAuth 2.0 / JWT Bearer tokens** (or Azure App Service Authentication / Easy Auth). The user's validated UPN (`preferred_username` or `oid` claim) must be extracted directly from the verified token headers, disallowing arbitrary client-supplied identities.

---

### 4. Concurrency & Data Integrity

To prevent race conditions where concurrent ticket submissions could produce duplicate ticket records:
1. **Database Uniqueness Constraint:** The `tickets` table enforces `UNIQUE(ticket_id)` at the database engine level.
2. **Transaction Rollback:** If two requests race to insert the same ticket ID simultaneously, the SQLite database engine throws an `IntegrityError`. The transaction is rolled back immediately, and the API returns a clean `HTTP 409 Conflict`.
3. **UTC Timestamping:** All timestamps (`created_at`, `updated_at`, `approval_timestamp`, `timestamp`) are stored in strict UTC to ensure global consistency across timezones.
