# Use Case Diagram

```mermaid
flowchart LR
    Citizen((Citizen))
    ASHA((ASHA Worker))
    Doctor((Doctor))
    Admin((Admin))

    subgraph JanSwasthya AI System
        UC1[Ask health question via AI chat]
        UC2[Browse disease information]
        UC3[Browse government schemes]
        UC4[Watch educational videos]
        UC5[Book doctor appointment]
        UC6[Register as doctor]
        UC7[Upload educational video]
        UC8[Manage appointment availability]
        UC9[Verify doctor applications]
        UC10[Approve/reject videos]
        UC11[View analytics dashboard]
        UC12[Receive emergency guidance]
    end

    Citizen --> UC1
    Citizen --> UC2
    Citizen --> UC3
    Citizen --> UC4
    Citizen --> UC5
    Citizen --> UC12
    ASHA --> UC1
    ASHA --> UC2
    ASHA --> UC3
    Doctor --> UC6
    Doctor --> UC7
    Doctor --> UC8
    Admin --> UC9
    Admin --> UC10
    Admin --> UC11

    UC1 -.includes.-> UC12
```

## Notes
- Emergency guidance (`UC12`) is modeled as an `<<includes>>` relationship on the chat use case, not a standalone trigger — it's a mandatory subflow evaluated on every chat message, not something a user separately invokes.
- ASHA workers use the same citizen-facing surfaces (chat, disease explorer, schemes) rather than a separate portal in v1 — a dedicated ASHA workflow (bulk patient outreach tracking, etc.) is flagged as future scope, not built in this phase, to keep scope realistic for 10 months.
