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

*(Future Phases)*
6. Correlation service groups alerts into incidents.
7. AI investigator provides RAG-based analysis on incidents.
8. Frontend fetches and displays the data via the Backend API.

## Current Detection Rules
- **DET-001**: Login Failure (Multiple Failed Logins)
- **DET-002**: Malware Detected (Antivirus/EDR alerts)
- **DET-003**: Network Anomaly (Unusual traffic patterns)
- **DET-004**: Data Access (Unauthorized data access attempts)
- **DET-005**: Unknown Critical Security Event

Description:
Fallback detection rule for critical security events when no more specific rule matches.
