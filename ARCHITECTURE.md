# Architecture

## High Level Architecture
- **Frontend**: Next.js app (React, TailwindCSS, TypeScript)
- **Backend API**: FastAPI (Python) serving REST endpoints
- **Database**: PostgreSQL (with pgvector for RAG in the future)

## Data Flow
1. **Security Logs** are generated synthetically.
    ↓
2. **Normalizer** parses logs into a common schema.
    ↓
3. **Detection Engine** scans logs for matches.
    ↓
4. **Rule Registry** loads detection rules (DET-001 through DET-005).
    ↓
5. **Alerts** are created when rules match suspicious logs.
    ↓
6. **Correlation Engine** groups alerts using rules (CORR-001 through CORR-005).
    ↓
7. **Incidents** are generated with priority scoring.

*(Future Phases)*
8. AI investigator provides RAG-based analysis on incidents.
9. Frontend fetches and displays the data via the Backend API.

## Current Detection Rules
- **DET-001**: Login Failure (Multiple Failed Logins)
- **DET-002**: Malware Detected (Antivirus/EDR alerts)
- **DET-003**: Network Anomaly (Unusual traffic patterns)
- **DET-004**: Data Access (Unauthorized data access attempts)
- **DET-005**: Unknown Critical Security Event

Description:
Fallback detection rule for critical security events when no more specific rule matches.

## Current Correlation Rules
- **CORR-001**: Coordinated Authentication Attack (15 min window)
- **CORR-002**: Potential Endpoint Compromise (30 min window)
- **CORR-003**: Potential Data Exfiltration (30 min window)
- **CORR-004**: Critical Event Escalation (20 min window)
- **CORR-005**: Standalone Critical Event (0 min window)
