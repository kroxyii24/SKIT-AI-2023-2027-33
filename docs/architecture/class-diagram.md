# Class Diagram — Core Domain

```mermaid
classDiagram
    class User {
        +UUID id
        +string full_name
        +string phone_number
        +string email
        +string hashed_password
        +UserRole role
        +string preferred_language
        +bool is_active
        +bool is_verified
    }

    class DoctorProfile {
        +UUID id
        +UUID user_id
        +string medical_council_reg_no
        +string specialization
        +int years_experience
        +bool is_verified_by_admin
        +ConsultationTier default_consultation_tier
        +float average_rating
    }

    class EducationalVideo {
        +UUID id
        +UUID doctor_id
        +string title
        +string video_url
        +string language
        +string category
        +bool is_approved
        +int view_count
    }

    class Appointment {
        +UUID id
        +UUID patient_id
        +UUID doctor_id
        +string scheduled_at
        +ConsultationTier consultation_tier
        +AppointmentStatus status
    }

    class ChatSession {
        +UUID id
        +UUID user_id
        +string language
    }

    class ChatMessage {
        +UUID id
        +UUID session_id
        +string role
        +string content
        +string sources
        +float confidence_score
        +bool was_emergency_flagged
    }

    class KnowledgeSource {
        +UUID id
        +string title
        +string publisher
        +string source_url
        +bool is_active
        +int ingested_chunk_count
    }

    class AuditLog {
        +UUID id
        +UUID actor_user_id
        +string action
        +string target_type
        +string target_id
    }

    User "1" --> "0..1" DoctorProfile : has
    DoctorProfile "1" --> "*" EducationalVideo : uploads
    User "1" --> "*" Appointment : books (as patient)
    DoctorProfile "1" --> "*" Appointment : receives
    User "1" --> "*" ChatSession : starts
    ChatSession "1" --> "*" ChatMessage : contains
```

## Notes
- `DoctorProfile` is a 1:0..1 extension of `User` rather than a separate hierarchy — a doctor is a user first, with additional fields layered on. This matches the RBAC design: role changes on the same `User` row rather than creating a new identity.
- `AuditLog` intentionally has no outgoing relationships modeled — it references other entities by loosely-typed `target_type`/`target_id` string pairs rather than foreign keys, since it must be able to log actions against any entity type without schema coupling, and must remain insertable even if the referenced row is later deleted.
