# Database Design

## ER overview

```mermaid
erDiagram
  USERS ||--o{ BEHAVIOR_SAMPLES : has
  USERS ||--o{ LOGIN_ATTEMPTS : creates
  USERS ||--o{ SESSIONS : owns
  USERS ||--o{ PENDING_CHALLENGES : receives

  USERS {
    int id PK
    string name
    string email UK
    blob password_hash
    blob pin_hash
    datetime created_at
  }
  BEHAVIOR_SAMPLES {
    int id PK
    int user_id FK
    float typing_duration
    float avg_key_interval
    int backspace_count
    float mouse_distance
    float avg_mouse_speed
    float login_hour
    datetime created_at
  }
  LOGIN_ATTEMPTS {
    int id PK
    int user_id FK
    string email
    float trust_score
    string prediction
    string status
    string reason
    datetime created_at
  }
```

## Why these tables?
- `users`: identity and hashed secrets
- `behavior_samples`: baseline behavioral measurements used for ML training
- `login_attempts`: audit/anomaly history
- `sessions`: local authenticated sessions
- `pending_challenges`: temporary low-trust fallback PIN challenges
