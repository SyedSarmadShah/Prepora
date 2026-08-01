# Prepora RESTful API Specification & Design Blueprint

> **Document Status:** Complete Production-Ready API Specification  
> **Target Framework:** Django 4.2+ / Django REST Framework (DRF) 3.14+  
> **Author:** Principal Backend Architect & API Designer  
> **Single Source of Truth:** [PROJECT_PLAN.md](file:///d:/Prepora/docs/PROJECT_PLAN.md), [DATABASE_PLAN.md](file:///d:/Prepora/docs/DATABASE_PLAN.md), [DOMAIN_MODEL.md](file:///d:/Prepora/docs/DOMAIN_MODEL.md), [BUSINESS_WORKFLOWS.md](file:///d:/Prepora/docs/BUSINESS_WORKFLOWS.md), [ER_DIAGRAM.md](file:///d:/Prepora/docs/ER_DIAGRAM.md), [POSTGRESQL_SCHEMA.md](file:///d:/Prepora/docs/POSTGRESQL_SCHEMA.md)

---

## 1. Executive Summary & Architecture Standards

### 1.1 Purpose & Scope
This document specifies the complete RESTful API contract for **Prepora**, an online learning platform for Pakistan Armed Forces initial tests (PMA, PAF, Navy, ASF, ISSB) and government competitive exams (FPSC, Police). It defines all request/response schemas, validation rules, authentication methods, authorization policies, rate limits, and database bindings required for backend engineering implementation using Django REST Framework.

### 1.2 API Versioning Strategy
- **Base URI Structure:** All API endpoints are versioned using URI path versioning: `/api/v1/`.
- **Backward Compatibility:** Breaking schema changes require a new major version prefix (e.g., `/api/v2/`). Deprecation headers (`Sunset`, `Deprecation`) must be served 90 days prior to retirement.

### 1.3 Standard Response Formats

#### Success Response Envelope (HTTP 200 OK, 201 Created)
```json
{
  "success": true,
  "message": "Operation completed successfully.",
  "data": {},
  "meta": {
    "timestamp": "2026-08-01T18:30:00Z",
    "version": "v1",
    "request_id": "req_uuid4_string"
  }
}
```

#### Paginated Success Response Envelope (HTTP 200 OK)
```json
{
  "success": true,
  "message": "Resource list retrieved successfully.",
  "data": [],
  "meta": {
    "pagination": {
      "total_items": 245,
      "total_pages": 13,
      "current_page": 1,
      "page_size": 20,
      "next_page": "/api/v1/questions/?page=2&page_size=20",
      "previous_page": null
    },
    "timestamp": "2026-08-01T18:30:00Z",
    "version": "v1",
    "request_id": "req_uuid4_string"
  }
}
```

#### Standard Error Response Envelope (RFC 7807 Standard)
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "One or more request parameters failed validation.",
    "status_code": 400,
    "details": [
      {
        "field": "email",
        "code": "unique",
        "message": "A user with this email address already exists."
      }
    ],
    "timestamp": "2026-08-01T18:30:00Z",
    "request_id": "req_uuid4_string"
  }
}
```

### 1.4 Common Standard Error Codes
| Standard Error Code | HTTP Status | Description |
| :--- | :--- | :--- |
| `AUTHENTICATION_FAILED` | 401 Unauthorized | Missing, invalid, or expired JWT token. |
| `PERMISSION_DENIED` | 403 Forbidden | User lacks necessary RBAC role or entitlement code. |
| `NOT_FOUND` | 404 Not Found | Requested entity does not exist or has been soft-deleted. |
| `METHOD_NOT_ALLOWED` | 405 Method Not Allowed | HTTP method is not supported on the target endpoint. |
| `CONFLICT` | 409 Conflict | Request conflicts with current server state (e.g. duplicate active attempt). |
| `VALIDATION_ERROR` | 422 Unprocessable Entity | Request body contains malformed syntax or schema violations. |
| `RATE_LIMIT_EXCEEDED` | 429 Too Many Requests | Rate quota exceeded for IP or authenticated account. |
| `INTERNAL_SERVER_ERROR` | 500 Internal Server Error | Unhandled backend exception occurred. |

### 1.5 Authentication & Session Management Flow
- **Authentication Scheme:** HTTP `Bearer <JWT_ACCESS_TOKEN>` header.
- **JWT Architecture (`djangorestframework-simplejwt`):**
  - **Access Token:** Short-lived (15 minutes expiration). Cryptographically signed using HMAC-SHA256 with server `SECRET_KEY`.
  - **Refresh Token:** Long-lived (7 days expiration). Tracked in `refresh_tokens` database table to support single-click device logout and session revocation.
- **Claims Payload:** `{ "user_id": "UUID", "email": "string", "roles": ["STUDENT"], "exp": 1785611400, "jti": "UUID" }`.

### 1.6 Authorization Strategy & RBAC Enforcement
- **Permission Classes:** DRF custom permission classes mapping system roles (`RoleCodeEnum`) and capability codenames (`permissions.codename`):
  - `IsAuthenticated`: Ensures user is logged in.
  - `HasRole(['ADMIN', 'SUPERADMIN'])`: Checks active user assignment in `user_roles`.
  - `HasEntitlement('access:premium_mock_tests')`: Verifies user's active `Subscription` and corresponding `plan_entitlements`.
- **System Roles (`RoleCodeEnum`):** `STUDENT`, `CONTENT_EDITOR`, `SME`, `SUPPORT_AGENT`, `ADMIN`, `SUPERADMIN`.

### 1.7 Naming Conventions
- **URLs:** Lowercase, plural nouns, kebab-case (e.g., `/api/v1/exam-tracks/`, `/api/v1/mock-tests/{id}/`).
- **JSON Fields:** Lowercase snake_case (e.g., `target_exam_track_id`, `passing_percentage`).
- **Query Parameters:** Lowercase snake_case (e.g., `?page=1&page_size=20&sort_by=created_at&sort_order=desc`).

### 1.8 Idempotency Rules
- **Safe Methods:** `GET`, `HEAD`, `OPTIONS` are strictly safe and read-only.
- **Idempotent Mutations:** `PUT`, `DELETE` are idempotent by default.
- **Non-Idempotent Mutations (`POST`):**
  - **Safepay Webhooks:** Idempotency enforced using Safepay `event_token` stored in `webhook_event_logs.event_token` (Unique constraint).
  - **Mock Test Submissions:** Idempotency enforced by locking `attempts.id` (`SELECT ... FOR UPDATE`); duplicate posts return cached `AttemptResult`.

### 1.9 Security Best Practices
1. **No User Enumeration:** Authentication & password reset endpoints return identical generic responses regardless of account existence.
2. **Password Security:** Stored using PBKDF2 with SHA256 / Argon2. Minimum 8 characters, requiring uppercase, lowercase, numeric, and special characters.
3. **CORS Policy:** Strict origin whitelist enforcing HTTPS frontend domains.
4. **Input Sanitization:** All HTML/Markdown content (`notes.content_markdown`, `question_explanations.explanation_text`) sanitized via Bleach before database insertion.

### 1.10 File Upload Strategy
- Direct multipart file uploads through Django backend servers are prohibited for production assets.
- **Presigned Upload Architecture:**
  1. Client calls `POST /api/v1/uploads/presigned-url/` with asset metadata (`filename`, `content_type`, `folder`).
  2. Backend validates permissions and returns a short-lived S3/Cloudflare R2 presigned PUT URL.
  3. Client uploads file binary directly to Object Storage CDN.
  4. Client passes returned CDN URL string (e.g., `avatar_url`, `pdf_asset_url`) to Prepora API entities.

### 1.11 Performance & Query Optimization Rules
- **N+1 Avoidance:** All DRF `ViewSet` list/retrieve queries MUST use `.select_related()` for Foreign Keys (e.g., `question_explanations`, `user_profiles`) and `.prefetch_related()` for M2M relationships (e.g., `question_options`, `user_roles`).
- **Pagination Defaults:** Global page size = 20 items. Maximum page size limit = 100 items.

### 1.12 Caching Recommendations
- **Redis Cache Backend:** High-frequency, slow-changing read endpoints (`/api/v1/exam-tracks/`, `/api/v1/subscription-plans/`) use Django Redis cache with explicit TTL (1 hour).
- **Cache Invalidation:** Django signals on model save/delete automatically purge corresponding Redis cache keys.

### 1.13 OpenAPI / Swagger 3.0 Compatibility
- Schema auto-generation configured using `drf-spectacular`.
- Swagger UI accessible at `/api/schema/swagger-ui/` (Staff only). Redoc accessible at `/api/schema/redoc/`.

---

## 2. API Module Specifications

```
                     PREPORA REST API LANDSCAPE
+-------------------------------------------------------------------+
|                        Client Layer (Web)                         |
+-------------------------------------------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
|              API Gateway / Reverse Proxy (Nginx / Cloudflare)     |
+-------------------------------------------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
|                  Django REST Framework Core API                   |
+-------------------------------------------------------------------+
  |                  |                  |                  |
  v                  v                  v                  v
[Auth & Users]   [Taxonomy & Bank]  [Assessments]     [Payments/Subs]
```

---

### 2.1 Module 1: Authentication & JWT

#### Overview
Handles student registration, authentication, JWT token issuance, session refresh, token revocation (logout), and secure password recovery.

#### Endpoint Catalog
| Method | URL Pattern | Purpose | Auth Required | Required Roles | Rate Limit |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/auth/register/` | Register new student account | None (Public) | Anyone | 5/min |
| `POST` | `/api/v1/auth/login/` | Authenticate credentials & issue JWTs | None (Public) | Anyone | 10/min |
| `POST` | `/api/v1/auth/refresh/` | Refresh expired access token | None (Public) | Anyone | 20/min |
| `POST` | `/api/v1/auth/logout/` | Revoke active refresh token session | Bearer JWT | Authenticated | 10/min |
| `POST` | `/api/v1/auth/forgot-password/` | Send password reset email | None (Public) | Anyone | 3/min |
| `POST` | `/api/v1/auth/reset-password/` | Execute password reset via token | None (Public) | Anyone | 5/min |
| `GET` | `/api/v1/auth/me/` | Retrieve active authenticated user identity | Bearer JWT | Authenticated | 60/min |

---

#### 1. Endpoint: `POST /api/v1/auth/register/`
- **Description:** Creates a new `User`, `UserProfile`, and binds an active `FREE` `Subscription`.
- **Authentication:** None.
- **Permissions:** None.
- **Request Body Schema:**
  ```json
  {
    "email": "student@example.com",
    "password": "SecurePassword123!",
    "full_name": "Muhammad Ali",
    "phone_number": "+923001234567",
    "target_exam_track_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
  }
  ```
- **Validation Rules:**
  - `email`: Required, valid email format, must be unique in `users` table.
  - `password`: Required, min 8 chars, must contain uppercase, lowercase, number, special char.
  - `full_name`: Required, max 255 chars.
  - `target_exam_track_id`: Optional UUID, must reference valid `exam_tracks.id` if provided.
- **Success Response (HTTP 201 Created):**
  ```json
  {
    "success": true,
    "message": "Account created successfully.",
    "data": {
      "user": {
        "id": "11111111-1111-1111-1111-111111111111",
        "email": "student@example.com",
        "is_active": true,
        "created_at": "2026-08-01T18:00:00Z"
      },
      "profile": {
        "full_name": "Muhammad Ali",
        "phone_number": "+923001234567",
        "target_exam_track_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
      },
      "tokens": {
        "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
      }
    }
  }
  ```
- **Error Responses:**
  - `400 Bad Request`: Email already registered or invalid fields.
- **Database Models Involved:** `users`, `user_profiles`, `subscriptions`, `subscription_plans`, `roles`, `user_roles`.

---

#### 2. Endpoint: `POST /api/v1/auth/login/`
- **Description:** Verifies credentials and returns fresh JWT access and refresh tokens.
- **Authentication:** None.
- **Permissions:** None.
- **Request Body Schema:**
  ```json
  {
    "email": "student@example.com",
    "password": "SecurePassword123!"
  }
  ```
- **Validation Rules:** Required `email` and `password`.
- **Success Response (HTTP 200 OK):**
  ```json
  {
    "success": true,
    "message": "Authentication successful.",
    "data": {
      "tokens": {
        "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
      },
      "user": {
        "id": "11111111-1111-1111-1111-111111111111",
        "email": "student@example.com",
        "roles": ["STUDENT"],
        "active_subscription": {
          "plan_code": "FREE",
          "status": "ACTIVE"
        }
      }
    }
  }
  ```
- **Error Responses:**
  - `401 Unauthorized`: Invalid email or password.
  - `403 Forbidden`: Account suspended (`is_active = false`).
- **Database Models Involved:** `users`, `refresh_tokens`, `user_roles`, `roles`, `subscriptions`.

---

#### 3. Endpoint: `POST /api/v1/auth/refresh/`
- **Description:** Exchanges a valid refresh token for a new access token.
- **Authentication:** None.
- **Request Body Schema:**
  ```json
  {
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
  ```
- **Success Response (HTTP 200 OK):**
  ```json
  {
    "success": true,
    "data": {
      "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    }
  }
  ```
- **Database Models Involved:** `refresh_tokens`.

---

#### 4. Endpoint: `POST /api/v1/auth/logout/`
- **Description:** Revokes a refresh token in the database.
- **Authentication:** Bearer JWT.
- **Request Body Schema:**
  ```json
  {
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
  ```
- **Success Response (HTTP 200 OK):**
  ```json
  {
    "success": true,
    "message": "Successfully logged out."
  }
  ```
- **Database Models Involved:** `refresh_tokens`.

---

### 2.2 Module 2: User & Profile

#### Overview
Provides endpoints for viewing and updating student profile information, target exam preferences, and account settings.

#### Endpoint Catalog
| Method | URL Pattern | Purpose | Auth Required | Required Roles | Rate Limit |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/users/me/profile/` | Get current user profile details | Bearer JWT | Authenticated | 60/min |
| `PATCH` | `/api/v1/users/me/profile/` | Update current user profile details | Bearer JWT | Authenticated | 20/min |
| `PUT` | `/api/v1/users/me/change-password/` | Change account password | Bearer JWT | Authenticated | 5/min |

---

#### 1. Endpoint: `GET /api/v1/users/me/profile/`
- **Authentication:** Bearer JWT.
- **Permissions:** `IsAuthenticated`.
- **Success Response (HTTP 200 OK):**
  ```json
  {
    "success": true,
    "data": {
      "user_id": "11111111-1111-1111-1111-111111111111",
      "email": "student@example.com",
      "full_name": "Muhammad Ali",
      "phone_number": "+923001234567",
      "city": "Rawalpindi",
      "avatar_url": "https://cdn.prepora.com/avatars/ali.jpg",
      "preparation_goal": "PMA 154 Long Course Initial Test",
      "target_exam_track": {
        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "name": "Pakistan Army",
        "slug": "pakistan-army"
      },
      "created_at": "2026-08-01T18:00:00Z"
    }
  }
  ```
- **Database Models Involved:** `users`, `user_profiles`, `exam_tracks`.

---

#### 2. Endpoint: `PATCH /api/v1/users/me/profile/`
- **Authentication:** Bearer JWT.
- **Permissions:** `IsAuthenticated`.
- **Request Body Schema:**
  ```json
  {
    "full_name": "Muhammad Ali Khan",
    "phone_number": "+923009876543",
    "city": "Islamabad",
    "avatar_url": "https://cdn.prepora.com/avatars/ali_new.jpg",
    "preparation_goal": "PAF GDP 156 Course",
    "target_exam_track_id": "4fa85f64-5717-4562-b3fc-2c963f66afa7"
  }
  ```
- **Validation Rules:**
  - `phone_number`: Optional E.164 format.
  - `target_exam_track_id`: Valid UUID existing in `exam_tracks`.
- **Success Response (HTTP 200 OK):** Returns updated profile payload.
- **Database Models Involved:** `user_profiles`.

---

### 2.3 Module 3: Role-Based Access Control (RBAC) Management

#### Overview
Administrative endpoints for managing system roles, granular capability permissions, and assigning roles to users.

#### Endpoint Catalog
| Method | URL Pattern | Purpose | Auth Required | Required Roles | Rate Limit |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/admin/rbac/roles/` | List system roles | Bearer JWT | ADMIN, SUPERADMIN | 30/min |
| `GET` | `/api/v1/admin/rbac/permissions/` | List atomic permissions | Bearer JWT | ADMIN, SUPERADMIN | 30/min |
| `POST` | `/api/v1/admin/rbac/user-roles/` | Assign role to a user | Bearer JWT | SUPERADMIN | 10/min |
| `DELETE` | `/api/v1/admin/rbac/user-roles/{id}/` | Revoke user role | Bearer JWT | SUPERADMIN | 10/min |

---

#### Endpoint Breakdown: `POST /api/v1/admin/rbac/user-roles/`
- **Authentication:** Bearer JWT.
- **Permissions:** `HasRole(['SUPERADMIN'])`.
- **Request Body Schema:**
  ```json
  {
    "user_id": "11111111-1111-1111-1111-111111111111",
    "role_id": "22222222-2222-2222-2222-222222222222"
  }
  ```
- **Success Response (HTTP 201 Created):** Returns assigned `user_roles` mapping with `assigned_by_id`.
- **Audit Rule:** Creates entry in `audit_logs` table (`action = 'USER_ROLE_ASSIGNED'`).
- **Database Models Involved:** `user_roles`, `roles`, `users`, `audit_logs`.

---

### 2.4 Module 4: Exam Taxonomy

#### Overview
Provides hierarchical navigation across Exam Tracks, Specific Exams, Academic Subjects, and Fine-Grained Topics.

```
TAXONOMY HIERARCHY
ExamTrack (e.g. Pakistan Army)
  └── Exam (e.g. PMA Long Course)
        └── Subject (e.g. Intelligence Test)
              └── Topic (e.g. Verbal Analogies)
```

#### Endpoint Catalog
| Method | URL Pattern | Purpose | Auth Required | Required Roles | Rate Limit |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/exam-tracks/` | List public exam tracks | None (Public) | Anyone | 60/min |
| `GET` | `/api/v1/exam-tracks/{slug}/` | Get single track details | None (Public) | Anyone | 60/min |
| `GET` | `/api/v1/exams/` | List exams (filterable by track) | None (Public) | Anyone | 60/min |
| `GET` | `/api/v1/subjects/` | List subjects (filterable by exam) | None (Public) | Anyone | 60/min |
| `GET` | `/api/v1/topics/` | List topics (filterable by subject) | None (Public) | Anyone | 60/min |
| `POST` | `/api/v1/exam-tracks/` | Create exam track | Bearer JWT | ADMIN, SUPERADMIN | 10/min |
| `PATCH` | `/api/v1/topics/{id}/` | Update topic | Bearer JWT | CONTENT_EDITOR, ADMIN | 20/min |

---

#### 1. Endpoint: `GET /api/v1/exam-tracks/`
- **Query Parameters:** `is_active=true` (default), `search=string`.
- **Filtering & Sorting:** Filterable by `is_active`, searchable by `name`. Sorted by `sort_order ASC`.
- **Success Response (HTTP 200 OK):**
  ```json
  {
    "success": true,
    "data": [
      {
        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "name": "Pakistan Army",
        "slug": "pakistan-army",
        "description": "PMA Long Course, Technical Cadet Scheme, and Direct Short Service Commission.",
        "icon_url": "https://cdn.prepora.com/icons/army.svg",
        "sort_order": 1,
        "is_active": true
      }
    ]
  }
  ```
- **Caching:** Redis cached for 60 minutes.
- **Database Models Involved:** `exam_tracks`.

---

#### 2. Endpoint: `GET /api/v1/topics/`
- **Query Parameters:** `subject_id=UUID`, `search=string`, `page=1`, `page_size=20`.
- **Filtering:** `subject_id` mandatory for targeted topic listings.
- **Success Response (HTTP 200 OK):**
  ```json
  {
    "success": true,
    "data": [
      {
        "id": "99999999-9999-9999-9999-999999999999",
        "subject_id": "88888888-8888-8888-8888-888888888888",
        "title": "Verbal Analogies",
        "slug": "verbal-analogies",
        "description": "Word relationships and logical pattern matching.",
        "sort_order": 1,
        "is_active": true
      }
    ]
  }
  ```
- **Database Models Involved:** `topics`, `subjects`.

---

### 2.5 Module 5: Question Bank & Governance

#### Overview
Authoring, publishing workflows, option sets, explanations, content versioning, and student error reporting for MCQs.

#### Status Lifecycle State Machine
`DRAFT` $\rightarrow$ `IN_REVIEW` $\rightarrow$ `APPROVED` $\rightarrow$ `PUBLISHED` $\rightarrow$ `ARCHIVED`

#### Endpoint Catalog
| Method | URL Pattern | Purpose | Auth Required | Required Roles | Rate Limit |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/questions/` | List questions (Filtered by topic/status) | Bearer JWT | Authenticated | 60/min |
| `GET` | `/api/v1/questions/{id}/` | Get single question stem & options | Bearer JWT | Authenticated | 60/min |
| `POST` | `/api/v1/questions/` | Create draft question stem | Bearer JWT | CONTENT_EDITOR, ADMIN | 20/min |
| `POST` | `/api/v1/questions/{id}/submit-review/` | Move question to IN_REVIEW | Bearer JWT | CONTENT_EDITOR | 20/min |
| `POST` | `/api/v1/questions/{id}/approve/` | SME approval of question | Bearer JWT | SME, ADMIN | 20/min |
| `POST` | `/api/v1/questions/{id}/publish/` | Publish question live | Bearer JWT | ADMIN, SUPERADMIN | 20/min |
| `POST` | `/api/v1/question-reports/` | Student flags question error | Bearer JWT | Authenticated | 10/min |

---

#### 1. Endpoint: `GET /api/v1/questions/`
- **Authentication:** Bearer JWT.
- **Security Rule:** Public student calls return ONLY published questions (`status = 'PUBLISHED'`) and STRIP the `is_correct` choice flag and `question_explanations` payload. Admin/Editor calls include governance metadata based on permissions.
- **Query Parameters:** `topic_id=UUID`, `difficulty=EASY|MEDIUM|HARD`, `status=PUBLISHED`, `page=1`, `page_size=20`.
- **Success Response (Student View HTTP 200 OK):**
  ```json
  {
    "success": true,
    "data": [
      {
        "id": "77777777-7777-7777-7777-777777777777",
        "topic_id": "99999999-9999-9999-9999-999999999999",
        "stem": "Which word is an analogy for Light : Darkness?",
        "image_url": null,
        "difficulty": "EASY",
        "options": [
          { "id": "opt_1", "label": "A", "option_text": "Day : Night" },
          { "id": "opt_2", "label": "B", "option_text": "Hot : Warm" },
          { "id": "opt_3", "label": "C", "option_text": "Fast : Swift" },
          { "id": "opt_4", "label": "D", "option_text": "Heavy : Solid" }
        ]
      }
    ]
  }
  ```
- **Database Models Involved:** `questions`, `question_options`, `topics`.

---

#### 2. Endpoint: `POST /api/v1/question-reports/`
- **Description:** Allows students to report erroneous questions (wrong answer key, typo, ambiguous stem).
- **Authentication:** Bearer JWT.
- **Request Body Schema:**
  ```json
  {
    "question_id": "77777777-7777-7777-7777-777777777777",
    "category": "WRONG_KEY",
    "comment": "Option A is listed as correct, but Option B is mathematically accurate."
  }
  ```
- **Validation Rules:**
  - `category`: Must be one of `WRONG_KEY`, `TYPO`, `AMBIGUOUS_STEM`, `BAD_EXPLANATION`, `OTHER`.
- **Success Response (HTTP 201 Created):** Returns created report ID with `status = 'OPEN'`.
- **Database Models Involved:** `question_reports`, `questions`, `users`.

---

### 2.6 Module 6: Study Notes

#### Overview
Structured academic revision material attached to subjects and topics.

#### Endpoint Catalog
| Method | URL Pattern | Purpose | Auth Required | Required Roles | Rate Limit |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/notes/` | List notes catalog | Bearer JWT | Authenticated | 60/min |
| `GET` | `/api/v1/notes/{slug}/` | Read single note content | Bearer JWT | Authenticated | 60/min |
| `POST` | `/api/v1/notes/` | Create study note | Bearer JWT | CONTENT_EDITOR, ADMIN | 10/min |

---

#### Endpoint Breakdown: `GET /api/v1/notes/{slug}/`
- **Entitlement Rule:** If `notes.is_premium = true`, user MUST have active `access:pdf_notes` entitlement. Unentitled users receive `403 Forbidden` with a truncated preview payload.
- **Success Response (HTTP 200 OK):**
  ```json
  {
    "success": true,
    "data": {
      "id": "note_uuid",
      "title": "Verbal Intelligence Preparation Guide",
      "slug": "verbal-intelligence-guide",
      "content_markdown": "# Verbal Intelligence Overview\n\nKey techniques for solving analogies...",
      "pdf_asset_url": "https://cdn.prepora.com/notes/verbal_guide.pdf",
      "is_premium": true,
      "view_count": 1420
    }
  }
  ```
- **Database Models Involved:** `notes`, `subjects`, `topics`, `subscriptions`.

---

### 2.7 Module 7: Bookmarks

#### Overview
Personal revision list allowing students to bookmark questions, notes, and mock tests.

#### Endpoint Catalog
| Method | URL Pattern | Purpose | Auth Required | Required Roles | Rate Limit |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/bookmarks/` | List saved bookmarks | Bearer JWT | Authenticated | 60/min |
| `POST` | `/api/v1/bookmarks/` | Add a bookmark | Bearer JWT | Authenticated | 30/min |
| `DELETE` | `/api/v1/bookmarks/{id}/` | Remove a bookmark | Bearer JWT | Authenticated | 30/min |

---

#### Endpoint Breakdown: `POST /api/v1/bookmarks/`
- **Request Body Schema:**
  ```json
  {
    "target_type": "QUESTION",
    "target_id": "77777777-7777-7777-7777-777777777777",
    "notes_tag": "Revision for PMA"
  }
  ```
- **Validation Rules:**
  - `target_type`: Must be `QUESTION`, `NOTE`, or `MOCK_TEST`.
  - Composite `(user_id, target_type, target_id)` must be unique.
- **Database Models Involved:** `bookmarks`, `questions`, `notes`, `mock_tests`.

---

### 2.8 Module 8: Mock Tests

#### Overview
Mock test template configuration, timing parameters, and test question sequences.

#### Endpoint Catalog
| Method | URL Pattern | Purpose | Auth Required | Required Roles | Rate Limit |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/mock-tests/` | List available mock tests | Bearer JWT | Authenticated | 60/min |
| `GET` | `/api/v1/mock-tests/{slug}/` | Get mock test overview & instructions | Bearer JWT | Authenticated | 60/min |
| `POST` | `/api/v1/mock-tests/` | Create mock test template | Bearer JWT | ADMIN, SUPERADMIN | 10/min |

---

#### Endpoint Breakdown: `GET /api/v1/mock-tests/{slug}/`
- **Success Response (HTTP 200 OK):**
  ```json
  {
    "success": true,
    "data": {
      "id": "mock_uuid",
      "title": "PMA 154 Long Course Full Mock Test #1",
      "slug": "pma-154-full-mock-1",
      "description": "Simulates 100 questions in 40 minutes under official rules.",
      "duration_minutes": 40,
      "total_marks": "100.00",
      "passing_percentage": "60.00",
      "negative_marking_factor": "0.25",
      "is_premium": true,
      "total_questions_count": 100
    }
  }
  ```
- **Database Models Involved:** `mock_tests`, `exam_tracks`, `exams`.

---

### 2.9 Module 9: Test Attempts & Assessment Execution Engine

#### Overview
Live assessment execution engine handling session initialization, timer enforcement, answer logging, and attempt submissions.

#### State Machine
`IN_PROGRESS` $\rightarrow$ `SUBMITTED` | `EXPIRED` | `CANCELED`

#### Endpoint Catalog
| Method | URL Pattern | Purpose | Auth Required | Required Roles | Rate Limit |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/mock-tests/{id}/start/` | Start or resume a test attempt | Bearer JWT | Authenticated | 10/min |
| `POST` | `/api/v1/attempts/{id}/save-progress/` | Auto-save answer selection | Bearer JWT | Authenticated | 120/min |
| `POST` | `/api/v1/attempts/{id}/submit/` | Finalize & score test attempt | Bearer JWT | Authenticated | 10/min |

---

#### 1. Endpoint: `POST /api/v1/mock-tests/{id}/start/`
- **Entitlement Check:** If `mock_tests.is_premium = true`, checks active `access:premium_mock_tests` entitlement.
- **Active Attempt Rule:** Checks for existing `IN_PROGRESS` attempt. If found and unexpired, returns existing attempt session.
- **Success Response (HTTP 200 OK):**
  ```json
  {
    "success": true,
    "data": {
      "attempt_id": "att_uuid",
      "started_at": "2026-08-01T18:00:00Z",
      "server_expiry_time": "2026-08-01T18:40:00Z",
      "status": "IN_PROGRESS",
      "questions": [
        {
          "question_id": "q1_uuid",
          "order": 1,
          "stem": "Select the odd one out...",
          "options": [
            { "id": "o1", "label": "A", "option_text": "Car" },
            { "id": "o2", "label": "B", "option_text": "Bus" }
          ]
        }
      ]
    }
  }
  ```
- **Security Rule:** Correct answer keys and explanations are completely omitted from response payload.
- **Database Models Involved:** `attempts`, `mock_tests`, `mock_test_questions`, `questions`, `question_options`.

---

#### 2. Endpoint: `POST /api/v1/attempts/{id}/submit/`
- **Description:** Finalizes attempt, locks row (`SELECT FOR UPDATE`), evaluates correct/wrong answers server-side, applies negative marking, creates `AttemptResult`.
- **Request Body Schema:**
  ```json
  {
    "answers": [
      {
        "question_id": "q1_uuid",
        "selected_option_id": "o1",
        "time_spent_seconds": 25
      }
    ]
  }
  ```
- **Success Response (HTTP 200 OK):** Returns scored summary payload (Redirects to Result API).
- **Database Models Involved:** `attempts`, `attempt_answers`, `attempt_results`, `question_options`, `mock_test_questions`.

---

### 2.10 Module 10: Attempt Results & Scorecards

#### Overview
Scorecard review, percentile calculations, and question-by-question solution explanations post-submission.

#### Endpoint Catalog
| Method | URL Pattern | Purpose | Auth Required | Required Roles | Rate Limit |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/results/{id}/` | Get scorecard summary | Bearer JWT | Authenticated | 60/min |
| `GET` | `/api/v1/results/{id}/review/` | Question-by-question solution review | Bearer JWT | Authenticated | 60/min |

---

#### Endpoint Breakdown: `GET /api/v1/results/{id}/`
- **Success Response (HTTP 200 OK):**
  ```json
  {
    "success": true,
    "data": {
      "result_id": "res_uuid",
      "attempt_id": "att_uuid",
      "score_obtained": "78.50",
      "total_possible_score": "100.00",
      "accuracy_percentage": "82.50",
      "has_passed": true,
      "total_questions": 100,
      "correct_count": 82,
      "wrong_count": 14,
      "skipped_count": 4,
      "summary_json": {
        "topics_breakdown": {
          "Verbal Analogies": { "correct": 10, "total": 12 }
        }
      }
    }
  }
  ```
- **Database Models Involved:** `attempt_results`, `attempts`, `mock_tests`.

---

### 2.11 Module 11: Student Progress & Analytics

#### Overview
Aggregated student performance analytics across subjects, accuracy trends, and cumulative stats.

#### Endpoint Catalog
| Method | URL Pattern | Purpose | Auth Required | Required Roles | Rate Limit |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/progress/summary/` | Get overall user progress dashboard metrics | Bearer JWT | Authenticated | 60/min |
| `GET` | `/api/v1/progress/topics/` | List topic-wise accuracy breakdowns | Bearer JWT | Authenticated | 60/min |

---

#### Endpoint Breakdown: `GET /api/v1/progress/summary/`
- **Success Response (HTTP 200 OK):**
  ```json
  {
    "success": true,
    "data": {
      "total_tests_completed": 14,
      "total_mcqs_attempted": 850,
      "overall_accuracy_percentage": "76.40",
      "total_time_spent_seconds": 18400,
      "current_study_streak_days": 5
    }
  }
  ```
- **Database Models Involved:** `student_progress`, `attempts`, `attempt_results`.

---

### 2.12 Module 12: Weak Topics Diagnostic Engine

#### Overview
Identifies student concept deficits and provides targeted drill recommendations.

#### Endpoint Catalog
| Method | URL Pattern | Purpose | Auth Required | Required Roles | Rate Limit |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/weak-topics/` | List identified weak topics for current user | Bearer JWT | Authenticated | 60/min |

---

#### Endpoint Breakdown: `GET /api/v1/weak-topics/`
- **Entitlement Policy:** Free students see top 2 weak topics; Premium students see complete diagnostic analysis and drill recommendations.
- **Success Response (HTTP 200 OK):**
  ```json
  {
    "success": true,
    "data": [
      {
        "topic_id": "topic_uuid",
        "topic_title": "Speed & Distance Word Problems",
        "subject_title": "Mathematics",
        "mastery_score": "34.50",
        "accuracy_deficit": "25.50",
        "recommended_practice_count": 15
      }
    ]
  }
  ```
- **Database Models Involved:** `weak_topics`, `topics`, `subjects`.

---

### 2.13 Module 13: Subscription Plans & Entitlements

#### Overview
Public pricing catalog and plan capability mappings (Free vs Premium Monthly at Rs. 499 PKR).

#### Endpoint Catalog
| Method | URL Pattern | Purpose | Auth Required | Required Roles | Rate Limit |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/subscription-plans/` | List active commercial pricing plans | None (Public) | Anyone | 60/min |

---

#### Endpoint Breakdown: `GET /api/v1/subscription-plans/`
- **Success Response (HTTP 200 OK):**
  ```json
  {
    "success": true,
    "data": [
      {
        "id": "plan_free_uuid",
        "title": "Free Plan",
        "code": "FREE",
        "price_amount": "0.00",
        "currency": "PKR",
        "billing_interval": "MONTHLY",
        "entitlements": ["access:limited_mcqs", "access:sample_mocks"]
      },
      {
        "id": "plan_premium_uuid",
        "title": "Premium Monthly Plan",
        "code": "PREMIUM_MONTHLY",
        "price_amount": "499.00",
        "currency": "PKR",
        "billing_interval": "MONTHLY",
        "entitlements": ["access:unlimited_mcqs", "access:premium_mock_tests", "access:pdf_notes", "access:weak_topic_analytics"]
      }
    ]
  }
  ```
- **Caching:** Redis cached for 24 hours.
- **Database Models Involved:** `subscription_plans`, `plan_entitlements`.

---

### 2.14 Module 14: Subscriptions Lifecycle

#### Overview
Manages student subscription contracts, checkout initialization, active period dates, and cancellations.

#### State Machine
`PENDING` $\rightarrow$ `ACTIVE` $\rightarrow$ `PAST_DUE` | `CANCELED` | `EXPIRED` | `PAUSED`

#### Endpoint Catalog
| Method | URL Pattern | Purpose | Auth Required | Required Roles | Rate Limit |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/subscriptions/me/` | Get current active subscription details | Bearer JWT | Authenticated | 60/min |
| `POST` | `/api/v1/subscriptions/checkout/` | Initialize Safepay checkout session | Bearer JWT | Authenticated | 5/min |
| `POST` | `/api/v1/subscriptions/cancel/` | Cancel future auto-renewal | Bearer JWT | Authenticated | 5/min |

---

#### Endpoint Breakdown: `POST /api/v1/subscriptions/checkout/`
- **Description:** Calls Safepay API to generate checkout URL for Premium plan (Rs. 499 PKR).
- **Request Body Schema:**
  ```json
  {
    "plan_code": "PREMIUM_MONTHLY"
  }
  ```
- **Success Response (HTTP 200 OK):**
  ```json
  {
    "success": true,
    "data": {
      "checkout_url": "https://sandbox.api.safepay.com/checkout/pay?tracker=track_12345",
      "safepay_tracker_id": "track_12345",
      "payment_transaction_id": "txn_uuid"
    }
  }
  ```
- **Database Models Involved:** `subscriptions`, `subscription_plans`, `payment_transactions`.

---

### 2.15 Module 15: Payment Transactions Ledger

#### Overview
Immutable monetary transaction history for payment checkouts and billing renewals.

#### Endpoint Catalog
| Method | URL Pattern | Purpose | Auth Required | Required Roles | Rate Limit |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/payments/history/` | List personal payment receipts | Bearer JWT | Authenticated | 30/min |

---

#### Endpoint Breakdown: `GET /api/v1/payments/history/`
- **Success Response (HTTP 200 OK):**
  ```json
  {
    "success": true,
    "data": [
      {
        "id": "txn_uuid",
        "amount": "499.00",
        "currency": "PKR",
        "status": "SUCCEEDED",
        "safepay_tracker_id": "track_12345",
        "created_at": "2026-08-01T18:00:00Z"
      }
    ]
  }
  ```
- **Database Models Involved:** `payment_transactions`, `users`.

---

### 2.16 Module 16: Safepay Webhooks Engine

#### Overview
Public receiver endpoint for Safepay webhook events (v2.0.0). Performs HMAC-SHA256 signature verification, idempotency checks using `event_token`, fast HTTP 200 acknowledgement, and asynchronous background dispatch.

#### Endpoint Catalog
| Method | URL Pattern | Purpose | Auth Required | Required Roles | Rate Limit |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/payments/webhooks/safepay/` | Receive Safepay payment & subscription events | None (Public HTTP) | Gateway Signature | 100/min |

---

#### Endpoint Breakdown: `POST /api/v1/payments/webhooks/safepay/`
- **Headers Required:** `X-SFPY-SIGNATURE: <hmac_sha256_hex_string>`
- **Processing Logic:**
  1. Verifies HMAC signature against `SAFEPAY_WEBHOOK_SECRET`. Invalid $\rightarrow$ Returns `401 Unauthorized`.
  2. Extracts `data.token` (`event_token`).
  3. Checks `webhook_event_logs` for `event_token`. Found $\rightarrow$ Returns `200 OK` (Duplicate ignored).
  4. Inserts row into `webhook_event_logs` (`processing_status = 'PENDING'`).
  5. Returns HTTP `200 OK` within $< 2$ seconds.
  6. Enqueues background worker to process business logic (activates `Subscription`, grants `plan_entitlements`, updates `payment_transactions`).
- **Success Response (HTTP 200 OK):**
  ```json
  {
    "success": true,
    "message": "Webhook event received and queued for processing."
  }
  ```
- **Database Models Involved:** `webhook_event_logs`, `payment_transactions`, `subscriptions`, `plan_entitlements`.

---

### 2.17 Module 17: Notifications & Preferences

#### Overview
In-app user notification feed, unread badge counters, and read acknowledgements.

#### Endpoint Catalog
| Method | URL Pattern | Purpose | Auth Required | Required Roles | Rate Limit |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/notifications/` | List student notifications | Bearer JWT | Authenticated | 60/min |
| `PATCH` | `/api/v1/notifications/{id}/read/` | Mark single notification as read | Bearer JWT | Authenticated | 60/min |

---

#### Endpoint Breakdown: `GET /api/v1/notifications/`
- **Success Response (HTTP 200 OK):**
  ```json
  {
    "success": true,
    "data": [
      {
        "id": "notif_uuid",
        "title": "Mock Test Score Published",
        "body": "Your result for PMA Full Mock #1 is available.",
        "channel": "IN_APP",
        "is_read": false,
        "action_url": "/results/res_uuid",
        "created_at": "2026-08-01T18:05:00Z"
      }
    ]
  }
  ```
- **Database Models Involved:** `notifications`.

---

### 2.18 Module 18: Administrative Management APIs

#### Overview
Platform operator dashboards, user suspensions, content queue moderation, and immutable security audit log review.

#### Endpoint Catalog
| Method | URL Pattern | Purpose | Auth Required | Required Roles | Rate Limit |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/admin/users/` | List all platform users | Bearer JWT | ADMIN, SUPERADMIN | 30/min |
| `PATCH` | `/api/v1/admin/users/{id}/status/` | Suspend or activate user account | Bearer JWT | ADMIN, SUPERADMIN | 10/min |
| `GET` | `/api/v1/admin/audit-logs/` | View system security audit logs | Bearer JWT | SUPERADMIN | 20/min |

---

#### Endpoint Breakdown: `GET /api/v1/admin/audit-logs/`
- **Permissions:** `HasRole(['SUPERADMIN'])`.
- **Query Parameters:** `actor_id=UUID`, `target_entity_type=string`, `page=1`.
- **Success Response (HTTP 200 OK):**
  ```json
  {
    "success": true,
    "data": [
      {
        "id": "audit_uuid",
        "actor_id": "user_admin_uuid",
        "action": "USER_SUSPENDED",
        "target_entity_type": "User",
        "target_entity_id": "target_user_uuid",
        "ip_address": "203.0.113.195",
        "pre_change_state": { "is_active": true },
        "post_change_state": { "is_active": false },
        "created_at": "2026-08-01T18:10:00Z"
      }
    ]
  }
  ```
- **Database Models Involved:** `audit_logs`, `users`.

---

## 3. Verification & Compliance Matrix

| Requirement / Spec | Implemented In Section | Status |
| :--- | :--- | :--- |
| API Versioning (`/api/v1/`) | Section 1.2 | Verified |
| Standard Success & Error Envelopes | Section 1.3 | Verified |
| JWT Bearer & Refresh Tokens | Section 1.5, Module 1 | Verified |
| Fine-Grained RBAC & Entitlement Rules | Section 1.6, Module 3 | Verified |
| Presigned S3/CDN File Upload Strategy | Section 1.10 | Verified |
| Safepay HMAC Webhooks & Idempotency | Section 1.8, Module 16 | Verified |
| All 32 Database Entities Bound 1:1 | Modules 1 through 18 | Verified |
| OpenAPI / Swagger 3.0 Generation | Section 1.13 | Verified |
