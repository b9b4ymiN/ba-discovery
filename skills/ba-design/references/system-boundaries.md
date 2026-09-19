# System Boundary Analysis

For each major responsibility, make explicit:
- what is inside vs outside the system,
- who/what owns the authoritative data,
- inputs/outputs and integration contracts,
- synchronous vs asynchronous expectations when material,
- failure, retry, recovery, and manual fallback,
- security/audit boundaries when relevant.

Prefer small components with one clear responsibility and stable interfaces. Do not decompose further unless the boundary improves reasoning, change isolation, or verification.
