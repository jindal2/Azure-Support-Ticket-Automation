# Azure Cloud Deployment Plan — Support Ticket Automation
## Production Enterprise Azure Architecture

### 1. Cloud Architecture Overview

The production architecture transitions the local single-machine development environment into a scalable, secure, and resilient cloud deployment on Microsoft Azure without introducing mandatory paid dependencies.

```mermaid
graph TD
    User([Customer / Support Agent]) -->|HTTPS| FrontDoor[Azure Static Web Apps\nReact SPA]
    FrontDoor -->|REST API / HTTPS| AppService[Azure App Service Linux\nFastAPI Container]

    subgraph Monitoring & Security
        AppService --> AppInsights[Azure Application Insights\nLive Metrics & Traces]
        GitHub[GitHub Actions] -.->|OIDC Federated Auth\nNo Long-Lived Secrets| AzureAD[Microsoft Entra ID / Azure AD]
        AzureAD -.->|Scoped RBAC Role| AppService
    end

    subgraph Data Layer
        AppService -->|SQLAlchemy Connection Pool| PostgresDB[(Azure Database for PostgreSQL\nFlexible Server)]
    end
```

---

### 2. Suggested Azure Resources

1. **API Tier — Azure App Service (Linux B1 Basic or Free F1):**
   - Hosts the FastAPI backend container (`python:3.11`).
   - Supports zero-downtime deployment slots, automated TLS certificate provisioning, and container scaling.
2. **Frontend Tier — Azure Static Web Apps (Free Plan):**
   - Globally distributed content delivery network (CDN) serving the compiled Vite React single-page application with automated SSL and edge routing.
3. **Database Tier — Azure Database for PostgreSQL Flexible Server:**
   - Production persistent store replacing the local development SQLite database.
4. **Observability — Azure Application Insights:**
   - Real-time exception tracking, API endpoint response latency, request volume metrics, and distributed tracing.
5. **Identity & CI/CD — Microsoft Entra ID (Azure AD) Workload Identity Federation:**
   - Enables GitHub Actions to authenticate directly into Azure using OpenID Connect (OIDC) tokens without storing long-lived passwords or client secrets in repository settings.

---

### 3. Database Migration Strategy: SQLite to PostgreSQL

| Aspect | Local Development (SQLite) | Production Cloud (Azure PostgreSQL) |
| :--- | :--- | :--- |
| **Hosting Cost** | $0.00 (Local filesystem) | ~$15 - $25/month (Burstable B1ms tier) |
| **Concurrency** | Single-writer file lock | Multi-client ACID connection pooling with row-level locks |
| **High Availability** | None (Single file) | Automated failover, 99.99% SLA, Zone Redundancy |
| **Backup & Recovery** | Manual file copying | Automated daily snapshots & Point-In-Time Recovery (PITR) |
| **Code Changes** | Uses `DATABASE_URL="sqlite:///..."` | Uses `DATABASE_URL="postgresql://user:pass@host:5432/support_tickets"` |

#### Code Portability:
Because the application uses SQLAlchemy ORM with standard column types and clean declarative models, **zero business logic code changes** are required to switch to PostgreSQL. Updating the `DATABASE_URL` environment variable is all that is required.

---

### 4. Step-by-Step Azure Deployment Guide

#### Phase A: Manual Resource Provisioning via Azure CLI
```bash
# 1. Log in to Azure account
az login

# 2. Create resource group in a preferred region
az group create --name rg-support-automation-prod --location eastus

# 3. Create App Service plan (Linux B1)
az appservice plan create \
  --name plan-support-prod \
  --resource-group rg-support-automation-prod \
  --sku B1 \
  --is-linux

# 4. Create App Service Web App
az webapp create \
  --name support-ticket-api-app \
  --resource-group rg-support-automation-prod \
  --plan plan-support-prod \
  --runtime "PYTHON:3.11"
```

#### Phase B: Configure OIDC Federated Identity Credential
To allow GitHub Actions to deploy without long-lived client secrets:
```bash
# 1. Create an Entra ID Application Registration
APP_ID=$(az ad app create --display-name "github-actions-support-deploy" --query appId -o tsv)

# 2. Create a Service Principal
az ad sp create --id $APP_ID

# 3. Assign Website Contributor role to the App Service
SUBSCRIPTION_ID=$(az account show --query id -o tsv)
az role assignment create \
  --assignee $APP_ID \
  --role "Website Contributor" \
  --scope "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/rg-support-automation-prod/providers/Microsoft.Web/sites/support-ticket-api-app"

# 4. Create Federated Identity Credential linking to GitHub repository
az ad app federated-credential create \
  --id $APP_ID \
  --parameters '{
    "name": "gh-actions-main-branch",
    "issuer": "https://token.actions.githubusercontent.com",
    "subject": "repo:YourGitHubOrg/support-ticket-automation:ref:refs/heads/main",
    "description": "Deploy permissions for main branch",
    "audiences": ["api://AzureADTokenExchange"]
  }'
```

#### Phase C: Configure GitHub Repository Variables
In GitHub Repository **Settings > Secrets and variables > Actions**:
- **Repository Secrets:**
  - `AZURE_CLIENT_ID`: The Application (client) ID from step B1
  - `AZURE_TENANT_ID`: Your Azure Directory (tenant) ID
  - `AZURE_SUBSCRIPTION_ID`: Your Azure Subscription ID
- **Repository Variables:**
  - `AZURE_APP_NAME`: `support-ticket-api-app`

#### Phase D: Trigger Manual Deployment
1. Navigate to **Actions > Deploy Backend to Azure App Service (Manual OIDC)**.
2. Click **Run workflow**, choose target environment (`staging` or `production`), and confirm.
3. The workflow builds the package, logs in via OIDC, deploys to Azure App Service, and executes the automated health check verification against `https://support-ticket-api-app.azurewebsites.net/health`.

#### Phase E: Verification & Rollback
- **Check live health:**
  ```bash
  curl -i https://support-ticket-api-app.azurewebsites.net/health
  ```
- **Stream diagnostic logs:**
  ```bash
  az webapp log tail --name support-ticket-api-app --resource-group rg-support-automation-prod
  ```
- **Rollback:** In the event of a regression, App Service deployment slots allow instantaneous 1-click slot swapping to the previous working build:
  ```bash
  az webapp deployment slot swap \
    --resource-group rg-support-automation-prod \
    --name support-ticket-api-app \
    --slot staging \
    --target-slot production
  ```

---

### 5. Cloud Cost Control & Decommissioning

1. **Zero-Cost Principle:** The implementation requires **zero cloud expenses** to test, run, and review locally.
2. **Quota & Tier Awareness:** Azure App Service Free (F1) tier provides 60 CPU minutes per day and allows no custom domains. For continuous testing, B1 Basic tier costs approximately $0.018/hour.
3. **Decommissioning Resources:** To avoid incurring unwanted cloud costs after authorized demonstrations, delete the resource group completely:
   ```bash
   az group delete --name rg-support-automation-prod --yes --no-wait
   ```
