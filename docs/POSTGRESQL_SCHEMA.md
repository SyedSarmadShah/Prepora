# Prepora PostgreSQL 15+ Physical Database Schema Specification

> **Document Status:** Complete Physical Database Blueprint  
> **Target Database Engine:** PostgreSQL 15+  
> **Target Application Framework:** Django 4.2+ ORM / Django REST Framework  
> **Author:** Principal Database Architect & Django Backend Architect  
> **Single Source of Truth:** [PROJECT_PLAN.md](file:///d:/Prepora/docs/PROJECT_PLAN.md), [DATABASE_PLAN.md](file:///d:/Prepora/docs/DATABASE_PLAN.md), [DOMAIN_MODEL.md](file:///d:/Prepora/docs/DOMAIN_MODEL.md), [BUSINESS_WORKFLOWS.md](file:///d:/Prepora/docs/BUSINESS_WORKFLOWS.md), [ER_DIAGRAM.md](file:///d:/Prepora/docs/ER_DIAGRAM.md)

---

## 1. Introduction

### 1.1 Purpose
This document provides the exhaustive physical database schema specification for **Prepora**, an enterprise-grade digital test preparation platform for Pakistan Armed Forces entry tests (PMA Long Course, PAF Initial Tests, Navy Cadet, ISSB, ASF) and allied competitive government examinations (CSS, FPSC, NTS, Police).

This specification translates the approved 32-entity conceptual ER diagram into a fully realized, production-ready PostgreSQL 15+ physical database design. It defines the exact table structures, columns, data types, nullability, default values, primary/foreign key constraints, unique constraints, check constraints, composite/partial indexes, JSONB structures, and Django ORM mappings.

### 1.2 Scope
This document covers the entirety of the Prepora persistence architecture across all nine core bounded contexts:
1. Identity & Access Management (User, UserProfile, Role, Permission, RolePermission, UserRole, RefreshToken, AuditLog)
2. Exam Taxonomy (ExamTrack, Exam, Subject, Topic)
3. Question Bank & Governance (Question, QuestionOption, QuestionExplanation, QuestionVersion, Bookmark, QuestionReport)
4. Assessment Execution Engine (MockTest, MockTestQuestion, Attempt, AttemptAnswer, AttemptResult)
5. Student Progress & Analytics (StudentProgress, WeakTopic)
6. Subscriptions & Entitlements (SubscriptionPlan, PlanEntitlement, Subscription)
7. Payments & Financial Ledger (PaymentTransaction, WebhookEventLog)
8. Communications & Notifications (Notification)
9. Study Notes & Content (Note)

### 1.3 Goals
- **Strict Single Source of Truth:** Implement the approved conceptual model without altering entities, adding unauthorized fields, or modifying relationships.
- **Enterprise ACID Reliability:** Enforce structural integrity rules, foreign key actions, and domain constraints directly within PostgreSQL.
- **High Concurrency Performance:** Support sub-100ms API query latencies during peak Pakistani exam preparation seasons via partial indexing, read-optimized denormalization, and efficient JSONB querying.
- **Flawless Django 4.2+ Compatibility:** Direct, predictable 1:1 mapping between PostgreSQL physical tables and Django ORM model definitions.

### 1.4 Target Database Version
- **PostgreSQL Engine:** PostgreSQL 15.x+ (compatible with PostgreSQL 16.x).
- **Primary Key Standard:** Native 128-bit `UUIDv4` using `gen_random_uuid()`.
- **Timestamp Standard:** `TIMESTAMPTZ` set to Universal Coordinated Time (`UTC`).
- **Semi-Structured Standard:** Binary JSON (`JSONB`) with GIN indexing for audit trails and provider webhooks.

### 1.5 Design Principles
1. **Normalization (3NF):** Core transactional and content tables are strictly normalized to Third Normal Form to prevent insert, update, and delete anomalies.
2. **Controlled Denormalization:** Read-heavy aggregates (`AttemptResult`, `StudentProgress`, `Subscription` price snapshots) are explicitly cached to eliminate multi-million row joins on real-time dashboards.
3. **Immutability & Auditability:** Published test content edits preserve historical integrity via `QuestionVersion` snapshots. Financial actions (`PaymentTransaction`, `WebhookEventLog`) and system mutations (`AuditLog`) are append-only.
4. **Soft Deletion:** Core business entities (`User`, `Question`, `Note`) utilize a `deleted_at` timestamp. Hard SQL deletes are prohibited on transactional and content data.

### 1.6 Naming Conventions
- **Table Names:** Lowercase, plural, snake_case (e.g., `users`, `user_profiles`, `mock_tests`, `attempt_answers`).
- **Column Names:** Lowercase, singular, snake_case (e.g., `email`, `created_at`, `is_active`, `passing_percentage`).
- **Primary Keys:** Standardized as `id` across all entities.
- **Foreign Keys:** Entity name singular + `_id` suffix (e.g., `user_id`, `question_id`, `mock_test_id`).
- **Booleans:** Prefix with `is_`, `has_`, or `auto_` (e.g., `is_active`, `has_passed`, `auto_renew`).
- **Timestamps:** Standardized suffix `_at` (e.g., `created_at`, `updated_at`, `deleted_at`, `submitted_at`).
- **Indexes:** Prefix with `idx_<tablename>_<column(s)>` or `idx_<tablename>_<purpose>`.
- **Unique Constraints:** Prefix with `uq_<tablename>_<column(s)>`.
- **Check Constraints:** Prefix with `chk_<tablename>_<purpose>`.

### 1.7 Schema Organization
All entities reside in the standard PostgreSQL `public` schema for initial production deployment, with structural boundaries designed to support schema-based multi-tenancy or logical database partitioning in future phases.

---

## 2. Database Extensions

The physical database relies on the following native PostgreSQL extensions:

| Extension Name | Purpose | Mandatory / Optional | Target Usage |
| :--- | :--- | :--- | :--- |
| **`pgcrypto`** | Cryptographic functions & UUID generation | **Mandatory** | Provides `gen_random_uuid()` for UUID primary key generation and HMAC hashing routines. |
| **`uuid-ossp`** | Alternative UUID generation algorithms | **Mandatory** | Fallback UUID generation utility for legacy compatibility. |
| **`pg_trgm`** | Trigram matching for fast text search | **Recommended** | High-performance ILIKE pattern matching and fuzzy searching across question stems, notes, and topics. |
| **`btree_gin`** | Composite B-tree and GIN indexing | **Recommended** | Allows multi-column composite GIN indexes combining scalar columns (e.g., `user_id`) with `JSONB` fields. |
| **`vector`** | Vector embeddings storage (`pgvector`) | **Optional (Future)** | Stores semantic vector embeddings for AI Tutor similarity searches and adaptive learning recommendations. |

---

## 3. Schema Structure

### 3.1 Public Schema Standard
All Prepora tables, enums, sequences, and indexes are deployed within the default `public` schema namespace. 

### 3.2 Database Ownership & Role-Based Privileges
PostgreSQL access is separated into three distinct operational security roles:
1. **`prepora_owner` (DDL Role):** Migration execution role with full schema modification privileges. Used exclusively by CI/CD deployment pipelines and Django migration execution tasks.
2. **`prepora_app` (DML Role):** Runtime application role assigned to Django REST Framework backend instances. Granted `SELECT`, `INSERT`, `UPDATE`, `DELETE` privileges on data tables, but prohibited from altering schema DDL.
3. **`prepora_readonly` (Analytics Role):** Read-only role used by analytics workers and BI reporting tools. Granted strict `SELECT` access to data tables, excluding sensitive credential columns.

### 3.3 Multi-Tenant / Multi-Schema Roadmap
While Phase 1 utilizes a single `public` schema with row-level tenant/exam-track isolation, the database naming and foreign key conventions support future migration to PostgreSQL schema-per-tenant (`tenant_army`, `tenant_paf`) or PostgreSQL Row-Level Security (RLS) policies without application rewrite.

---

## 4. Table Specifications

This section defines the physical specification for all 32 entities in the ER Diagram across their respective domain bounded contexts.

---

### 4.1 Identity & Access Bounded Context

#### 1. Table Specification: `users`
- **Purpose:** Core identity entity representing platform users across all operational roles.
- **Primary Key:** `id` (UUID, Default: `gen_random_uuid()`)
- **Storage Considerations:** Heap table; high index churn on `last_login_at`. Fillfactor set to 90.

##### Column Specifications:
| Column Name | Data Type | Nullable | Default Value | PK/FK | Constraints / Rules |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | NO | `gen_random_uuid()` | PK | Primary Key |
| `email` | `VARCHAR(255)` | NO | None | None | Lowercase Unique Index |
| `password_hash` | `VARCHAR(255)` | NO | None | None | Hashed Password (Argon2/PBKDF2) |
| `is_active` | `BOOLEAN` | NO | `TRUE` | None | Account operational flag |
| `is_staff` | `BOOLEAN` | NO | `FALSE` | None | Administrative portal access |
| `is_superuser` | `BOOLEAN` | NO | `FALSE` | None | System superuser flag |
| `last_login_at` | `TIMESTAMPTZ` | YES | `NULL` | None | Timestamp of last authentication |
| `created_at` | `TIMESTAMPTZ` | NO | `CURRENT_TIMESTAMP` | None | Record creation timestamp |
| `updated_at` | `TIMESTAMPTZ` | NO | `CURRENT_TIMESTAMP` | None | Record last update timestamp |
| `deleted_at` | `TIMESTAMPTZ` | YES | `NULL` | None | Soft delete timestamp |

##### Table Constraints & Indexes:
- **Primary Key:** `uq_users_id` ON (`id`)
- **Unique Constraint:** Case-insensitive unique index `idx_users_email_lower` ON `LOWER(email)` WHERE `deleted_at IS NULL`.
- **Partial Indexes:**
  - `idx_users_active_staff` ON (`is_active`, `is_staff`) WHERE `deleted_at IS NULL`.
  - `idx_users_deleted_at` ON (`deleted_at`) WHERE `deleted_at IS NOT NULL`.

---

#### 2. Table Specification: `user_profiles`
- **Purpose:** Biographical and demographic details separated from authentication credentials.
- **Primary Key:** `id` (UUID, Default: `gen_random_uuid()`)

##### Column Specifications:
| Column Name | Data Type | Nullable | Default Value | PK/FK | Constraints / Rules |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | NO | `gen_random_uuid()` | PK | Primary Key |
| `user_id` | `UUID` | NO | None | FK, UK | Unique FK -> `users(id)` ON DELETE CASCADE |
| `target_exam_track_id` | `UUID` | YES | `NULL` | FK | FK -> `exam_tracks(id)` ON DELETE SET NULL |
| `full_name` | `VARCHAR(255)` | NO | None | None | Student full legal name |
| `phone_number` | `VARCHAR(20)` | YES | `NULL` | None | E.164 phone format |
| `city` | `VARCHAR(100)` | YES | `NULL` | None | Pakistani city/region |
| `avatar_url` | `TEXT` | YES | `NULL` | None | S3 / CDN image link |
| `preparation_goal` | `TEXT` | YES | `NULL` | None | Student goal description |
| `created_at` | `TIMESTAMPTZ` | NO | `CURRENT_TIMESTAMP` | None | Record creation timestamp |
| `updated_at` | `TIMESTAMPTZ` | NO | `CURRENT_TIMESTAMP` | None | Record last update timestamp |

##### Table Constraints & Indexes:
- **Primary Key:** `uq_user_profiles_id` ON (`id`)
- **Unique Constraint:** `uq_user_profiles_user_id` ON (`user_id`)
- **Foreign Keys:**
  - `fk_user_profiles_user` FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE ON UPDATE CASCADE
  - `fk_user_profiles_exam_track` FOREIGN KEY (`target_exam_track_id`) REFERENCES `exam_tracks`(`id`) ON DELETE SET NULL ON UPDATE CASCADE
- **Indexes:** `idx_user_profiles_target_track` ON (`target_exam_track_id`)

---

#### 3. Table Specification: `roles`
- **Purpose:** Encapsulates RBAC role definitions within the system.
- **Primary Key:** `id` (UUID, Default: `gen_random_uuid()`)

##### Column Specifications:
| Column Name | Data Type | Nullable | Default Value | PK/FK | Constraints / Rules |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | NO | `gen_random_uuid()` | PK | Primary Key |
| `name` | `VARCHAR(50)` | NO | None | UK | Human-readable role name |
| `code` | `VARCHAR(50)` | NO | None | UK | System role code enum |
| `description` | `TEXT` | YES | `NULL` | None | Role responsibility details |
| `created_at` | `TIMESTAMPTZ` | NO | `CURRENT_TIMESTAMP` | None | Record creation timestamp |
| `updated_at` | `TIMESTAMPTZ` | NO | `CURRENT_TIMESTAMP` | None | Record last update timestamp |

##### Table Constraints & Indexes:
- **Primary Key:** `uq_roles_id` ON (`id`)
- **Unique Constraints:** `uq_roles_name` ON (`name`), `uq_roles_code` ON (`code`)
- **Check Constraint:** `chk_roles_code` CHECK (`code` IN ('STUDENT', 'CONTENT_EDITOR', 'SME', 'SUPPORT_AGENT', 'ADMIN', 'SUPERADMIN'))

---

#### 4. Table Specification: `permissions`
- **Purpose:** Atomic system capability for fine-grained access control.
- **Primary Key:** `id` (UUID, Default: `gen_random_uuid()`)

##### Column Specifications:
| Column Name | Data Type | Nullable | Default Value | PK/FK | Constraints / Rules |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | NO | `gen_random_uuid()` | PK | Primary Key |
| `codename` | `VARCHAR(100)` | NO | None | UK | E.g. `questions.publish` |
| `domain` | `VARCHAR(50)` | NO | None | None | E.g. `content`, `finance` |
| `action` | `VARCHAR(50)` | NO | None | None | E.g. `create`, `read`, `publish` |
| `description` | `TEXT` | YES | `NULL` | None | Permission detail |
| `created_at` | `TIMESTAMPTZ` | NO | `CURRENT_TIMESTAMP` | None | Record creation timestamp |

##### Table Constraints & Indexes:
- **Primary Key:** `uq_permissions_id` ON (`id`)
- **Unique Constraints:** `uq_permissions_codename` ON (`codename`), `uq_permissions_domain_action` ON (`domain`, `action`)

---

#### 5. Table Specification: `role_permissions`
- **Purpose:** Junction table mapping permissions to RBAC roles.
- **Primary Key:** `id` (UUID, Default: `gen_random_uuid()`)

##### Column Specifications:
| Column Name | Data Type | Nullable | Default Value | PK/FK | Constraints / Rules |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | NO | `gen_random_uuid()` | PK | Primary Key |
| `role_id` | `UUID` | NO | None | FK | FK -> `roles(id)` ON DELETE CASCADE |
| `permission_id` | `UUID` | NO | None | FK | FK -> `permissions(id)` ON DELETE CASCADE |
| `created_at` | `TIMESTAMPTZ` | NO | `CURRENT_TIMESTAMP` | None | Assignment timestamp |

##### Table Constraints & Indexes:
- **Primary Key:** `uq_role_permissions_id` ON (`id`)
- **Unique Constraint:** `uq_role_permissions_pair` ON (`role_id`, `permission_id`)
- **Foreign Keys:**
  - `fk_role_permissions_role` FOREIGN KEY (`role_id`) REFERENCES `roles`(`id`) ON DELETE CASCADE ON UPDATE CASCADE
  - `fk_role_permissions_permission` FOREIGN KEY (`permission_id`) REFERENCES `permissions`(`id`) ON DELETE CASCADE ON UPDATE CASCADE

---

#### 6. Table Specification: `user_roles`
- **Purpose:** Junction table assigning RBAC roles to users.
- **Primary Key:** `id` (UUID, Default: `gen_random_uuid()`)

##### Column Specifications:
| Column Name | Data Type | Nullable | Default Value | PK/FK | Constraints / Rules |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | NO | `gen_random_uuid()` | PK | Primary Key |
| `user_id` | `UUID` | NO | None | FK | FK -> `users(id)` ON DELETE CASCADE |
| `role_id` | `UUID` | NO | None | FK | FK -> `roles(id)` ON DELETE CASCADE |
| `assigned_by_id` | `UUID` | YES | `NULL` | FK | FK -> `users(id)` ON DELETE SET NULL |
| `assigned_at` | `TIMESTAMPTZ` | NO | `CURRENT_TIMESTAMP` | None | Assignment timestamp |

##### Table Constraints & Indexes:
- **Primary Key:** `uq_user_roles_id` ON (`id`)
- **Unique Constraint:** `uq_user_roles_pair` ON (`user_id`, `role_id`)
- **Foreign Keys:**
  - `fk_user_roles_user` FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE ON UPDATE CASCADE
  - `fk_user_roles_role` FOREIGN KEY (`role_id`) REFERENCES `roles`(`id`) ON DELETE CASCADE ON UPDATE CASCADE
  - `fk_user_roles_assigned_by` FOREIGN KEY (`assigned_by_id`) REFERENCES `users`(`id`) ON DELETE SET NULL ON UPDATE CASCADE

---

#### 7. Table Specification: `refresh_tokens`
- **Purpose:** Secure JWT refresh token management and session revocation tracking.
- **Primary Key:** `id` (UUID, Default: `gen_random_uuid()`)

##### Column Specifications:
| Column Name | Data Type | Nullable | Default Value | PK/FK | Constraints / Rules |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | NO | `gen_random_uuid()` | PK | Primary Key |
| `user_id` | `UUID` | NO | None | FK | FK -> `users(id)` ON DELETE CASCADE |
| `token` | `VARCHAR(512)` | NO | None | UK | Cryptographic refresh token string |
| `device_info` | `TEXT` | YES | `NULL` | None | Client User-Agent metadata |
| `ip_address` | `VARCHAR(45)` | YES | `NULL` | None | Client IPv4/IPv6 address |
| `is_revoked` | `BOOLEAN` | NO | `FALSE` | None | Explicit revocation flag |
| `expires_at` | `TIMESTAMPTZ` | NO | None | None | Absolute token expiration date |
| `created_at` | `TIMESTAMPTZ` | NO | `CURRENT_TIMESTAMP` | None | Issued timestamp |

##### Table Constraints & Indexes:
- **Primary Key:** `uq_refresh_tokens_id` ON (`id`)
- **Unique Constraint:** `uq_refresh_tokens_token` ON (`token`)
- **Foreign Key:** `fk_refresh_tokens_user` FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE ON UPDATE CASCADE
- **Partial Index:** `idx_refresh_tokens_lookup` ON (`token`) WHERE `is_revoked = FALSE`.

---

#### 8. Table Specification: `audit_logs`
- **Purpose:** Immutable security and administrative audit trail.
- **Primary Key:** `id` (UUID, Default: `gen_random_uuid()`)
- **Storage Considerations:** Append-only table. High insert rate. Partitioning candidate by `created_at`.

##### Column Specifications:
| Column Name | Data Type | Nullable | Default Value | PK/FK | Constraints / Rules |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | NO | `gen_random_uuid()` | PK | Primary Key |
| `actor_id` | `UUID` | YES | `NULL` | FK | FK -> `users(id)` ON DELETE SET NULL |
| `action` | `VARCHAR(100)` | NO | None | None | E.g. `USER_ROLE_ESCALATION` |
| `target_entity_type` | `VARCHAR(100)` | NO | None | None | E.g. `Question`, `Subscription` |
| `target_entity_id` | `UUID` | NO | None | None | UUID of affected record |
| `ip_address` | `VARCHAR(45)` | YES | `NULL` | None | Client IP address |
| `pre_change_state` | `JSONB` | YES | `NULL` | None | Pre-edit state snapshot |
| `post_change_state` | `JSONB` | YES | `NULL` | None | Post-edit state snapshot |
| `created_at` | `TIMESTAMPTZ` | NO | `CURRENT_TIMESTAMP` | None | Immutable log timestamp |

##### Table Constraints & Indexes:
- **Primary Key:** `uq_audit_logs_id` ON (`id`)
- **Foreign Key:** `fk_audit_logs_actor` FOREIGN KEY (`actor_id`) REFERENCES `users`(`id`) ON DELETE SET NULL ON UPDATE CASCADE
- **Indexes:**
  - `idx_audit_logs_actor_date` ON (`actor_id`, `created_at` DESC)
  - `idx_audit_logs_target` ON (`target_entity_type`, `target_entity_id`)
  - `idx_audit_logs_created_at` ON (`created_at` DESC)

---

### 4.2 Exam Taxonomy Bounded Context

#### 9. Table Specification: `exam_tracks`
- **Purpose:** Top-level category for military branches and competitive exam categories.
- **Primary Key:** `id` (UUID, Default: `gen_random_uuid()`)

##### Column Specifications:
| Column Name | Data Type | Nullable | Default Value | PK/FK | Constraints / Rules |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | NO | `gen_random_uuid()` | PK | Primary Key |
| `name` | `VARCHAR(100)` | NO | None | UK | Track name (e.g. Pakistan Army) |
| `slug` | `VARCHAR(100)` | NO | None | UK | URL slug (e.g. `pakistan-army`) |
| `description` | `TEXT` | YES | `NULL` | None | Overview narrative |
| `icon_url` | `TEXT` | YES | `NULL` | None | Track badge asset link |
| `sort_order` | `INTEGER` | NO | `0` | None | Menu display sequence |
| `is_active` | `BOOLEAN` | NO | `TRUE` | None | Publication status |
| `created_at` | `TIMESTAMPTZ` | NO | `CURRENT_TIMESTAMP` | None | Record creation timestamp |
| `updated_at` | `TIMESTAMPTZ` | NO | `CURRENT_TIMESTAMP` | None | Record last update timestamp |

##### Table Constraints & Indexes:
- **Primary Key:** `uq_exam_tracks_id` ON (`id`)
- **Unique Constraints:** `uq_exam_tracks_name` ON (`name`), `uq_exam_tracks_slug` ON (`slug`)
- **Index:** `idx_exam_tracks_active_order` ON (`is_active`, `sort_order` ASC)

---

#### 10. Table Specification: `exams`
- **Purpose:** Specific entry test course or selection exam (e.g., PMA Long Course, GDP Air Force).
- **Primary Key:** `id` (UUID, Default: `gen_random_uuid()`)

##### Column Specifications:
| Column Name | Data Type | Nullable | Default Value | PK/FK | Constraints / Rules |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | NO | `gen_random_uuid()` | PK | Primary Key |
| `exam_track_id` | `UUID` | NO | None | FK | FK -> `exam_tracks(id)` ON DELETE RESTRICT |
| `title` | `VARCHAR(150)` | NO | None | None | Exam title |
| `slug` | `VARCHAR(150)` | NO | None | UK | URL slug |
| `description` | `TEXT` | YES | `NULL` | None | Exam description |
| `sort_order` | `INTEGER` | NO | `0` | None | Display sequence |
| `is_active` | `BOOLEAN` | NO | `TRUE` | None | Operational status |
| `created_at` | `TIMESTAMPTZ` | NO | `CURRENT_TIMESTAMP` | None | Record creation timestamp |
| `updated_at` | `TIMESTAMPTZ` | NO | `CURRENT_TIMESTAMP` | None | Record last update timestamp |

##### Table Constraints & Indexes:
- **Primary Key:** `uq_exams_id` ON (`id`)
- **Unique Constraints:** `uq_exams_slug` ON (`slug`), `uq_exams_track_title` ON (`exam_track_id`, `title`)
- **Foreign Key:** `fk_exams_track` FOREIGN KEY (`exam_track_id`) REFERENCES `exam_tracks`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE
- **Index:** `idx_exams_track_active` ON (`exam_track_id`, `is_active`, `sort_order` ASC)

---

#### 11. Table Specification: `subjects`
- **Purpose:** Major academic discipline (e.g., Intelligence Tests, Physics, English).
- **Primary Key:** `id` (UUID, Default: `gen_random_uuid()`)

##### Column Specifications:
| Column Name | Data Type | Nullable | Default Value | PK/FK | Constraints / Rules |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | NO | `gen_random_uuid()` | PK | Primary Key |
| `exam_id` | `UUID` | NO | None | FK | FK -> `exams(id)` ON DELETE RESTRICT |
| `title` | `VARCHAR(150)` | NO | None | None | Subject title |
| `slug` | `VARCHAR(150)` | NO | None | UK | URL slug |
| `description` | `TEXT` | YES | `NULL` | None | Discipline overview |
| `sort_order` | `INTEGER` | NO | `0` | None | Display order |
| `is_active` | `BOOLEAN` | NO | `TRUE` | None | Operational flag |
| `created_at` | `TIMESTAMPTZ` | NO | `CURRENT_TIMESTAMP` | None | Record creation timestamp |
| `updated_at` | `TIMESTAMPTZ` | NO | `CURRENT_TIMESTAMP` | None | Record last update timestamp |

##### Table Constraints & Indexes:
- **Primary Key:** `uq_subjects_id` ON (`id`)
- **Unique Constraints:** `uq_subjects_slug` ON (`slug`), `uq_subjects_exam_title` ON (`exam_id`, `title`)
- **Foreign Key:** `fk_subjects_exam` FOREIGN KEY (`exam_id`) REFERENCES `exams`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE
- **Index:** `idx_subjects_exam_active` ON (`exam_id`, `is_active`, `sort_order` ASC)

---

#### 12. Table Specification: `topics`
- **Purpose:** Fine-grained concept area within a subject (e.g., Verbal Analogies, Newton's Laws).
- **Primary Key:** `id` (UUID, Default: `gen_random_uuid()`)

##### Column Specifications:
| Column Name | Data Type | Nullable | Default Value | PK/FK | Constraints / Rules |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | NO | `gen_random_uuid()` | PK | Primary Key |
| `subject_id` | `UUID` | NO | None | FK | FK -> `subjects(id)` ON DELETE RESTRICT |
| `title` | `VARCHAR(150)` | NO | None | None | Topic title |
| `slug` | `VARCHAR(150)` | NO | None | UK | URL slug |
| `description` | `TEXT` | YES | `NULL` | None | Concept overview |
| `sort_order` | `INTEGER` | NO | `0` | None | Display order |
| `is_active` | `BOOLEAN` | NO | `TRUE` | None | Operational flag |
| `created_at` | `TIMESTAMPTZ` | NO | `CURRENT_TIMESTAMP` | None | Record creation timestamp |
| `updated_at` | `TIMESTAMPTZ` | NO | `CURRENT_TIMESTAMP` | None | Record last update timestamp |

##### Table Constraints & Indexes:
- **Primary Key:** `uq_topics_id` ON (`id`)
- **Unique Constraints:** `uq_topics_slug` ON (`slug`), `uq_topics_subject_title` ON (`subject_id`, `title`)
- **Foreign Key:** `fk_topics_subject` FOREIGN KEY (`subject_id`) REFERENCES `subjects`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE
- **Index:** `idx_topics_subject_active` ON (`subject_id`, `is_active`, `sort_order` ASC)

---

### 4.3 Question Bank Bounded Context

#### 13. Table Specification: `questions`
- **Purpose:** Core MCQ item stem and governance state container.
- **Primary Key:** `id` (UUID, Default: `gen_random_uuid()`)

##### Column Specifications:
| Column Name | Data Type | Nullable | Default Value | PK/FK | Constraints / Rules |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | NO | `gen_random_uuid()` | PK | Primary Key |
| `topic_id` | `UUID` | NO | None | FK | FK -> `topics(id)` ON DELETE RESTRICT |
| `exam_track_id` | `UUID` | YES | `NULL` | FK | FK -> `exam_tracks(id)` ON DELETE SET NULL |
| `creator_id` | `UUID` | NO | None | FK | FK -> `users(id)` ON DELETE RESTRICT |
| `reviewer_id` | `UUID` | YES | `NULL` | FK | FK -> `users(id)` ON DELETE SET NULL |
| `stem` | `TEXT` | NO | None | None | MCQ question stem text |
| `image_url` | `TEXT` | YES | `NULL` | None | Optional diagram asset link |
| `difficulty` | `VARCHAR(20)` | NO | `'MEDIUM'` | None | Enum: `EASY`, `MEDIUM`, `HARD` |
| `status` | `VARCHAR(20)` | NO | `'DRAFT'` | None | Enum: `DRAFT`, `IN_REVIEW`, `APPROVED`, `PUBLISHED`, `ARCHIVED` |
| `active_version` | `INTEGER` | NO | `1` | None | Currently published version number |
| `created_at` | `TIMESTAMPTZ` | NO | `CURRENT_TIMESTAMP` | None | Record creation timestamp |
| `updated_at` | `TIMESTAMPTZ` | NO | `CURRENT_TIMESTAMP` | None | Record last update timestamp |
| `deleted_at` | `TIMESTAMPTZ` | YES | `NULL` | None | Soft delete timestamp |

##### Table Constraints & Indexes:
- **Primary Key:** `uq_questions_id` ON (`id`)
- **Foreign Keys:**
  - `fk_questions_topic` FOREIGN KEY (`topic_id`) REFERENCES `topics`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE
  - `fk_questions_track` FOREIGN KEY (`exam_track_id`) REFERENCES `exam_tracks`(`id`) ON DELETE SET NULL ON UPDATE CASCADE
  - `fk_questions_creator` FOREIGN KEY (`creator_id`) REFERENCES `users`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE
  - `fk_questions_reviewer` FOREIGN KEY (`reviewer_id`) REFERENCES `users`(`id`) ON DELETE SET NULL ON UPDATE CASCADE
- **Check Constraints:**
  - `chk_questions_difficulty` CHECK (`difficulty` IN ('EASY', 'MEDIUM', 'HARD'))
  - `chk_questions_status` CHECK (`status` IN ('DRAFT', 'IN_REVIEW', 'APPROVED', 'PUBLISHED', 'ARCHIVED'))
  - `chk_questions_version` CHECK (`active_version` >= 1)
- **Partial Indexes:**
  - `idx_questions_topic_status` ON (`topic_id`, `status`) WHERE `deleted_at IS NULL`.
  - `idx_questions_track_difficulty` ON (`exam_track_id`, `difficulty`, `status`) WHERE `deleted_at IS NULL`.
  - `idx_questions_published_lookup` ON (`id`, `topic_id`) WHERE `status = 'PUBLISHED' AND deleted_at IS NULL`.

---

#### 14. Table Specification: `question_options`
- **Purpose:** Selectable choices/distractors for a question.
- **Primary Key:** `id` (UUID, Default: `gen_random_uuid()`)

##### Column Specifications:
| Column Name | Data Type | Nullable | Default Value | PK/FK | Constraints / Rules |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | NO | `gen_random_uuid()` | PK | Primary Key |
| `question_id` | `UUID` | NO | None | FK | FK -> `questions(id)` ON DELETE CASCADE |
| `label` | `VARCHAR(10)` | NO | None | None | Option label (e.g. 'A', 'B', 'C', 'D') |
| `option_text` | `TEXT` | NO | None | None | Distractor text body |
| `image_url` | `TEXT` | YES | `NULL` | None | Option graphic attachment |
| `is_correct` | `BOOLEAN` | NO | `FALSE` | None | Key indicator |
| `sort_order` | `INTEGER` | NO | `0` | None | Sequence order |
| `created_at` | `TIMESTAMPTZ` | NO | `CURRENT_TIMESTAMP` | None | Record creation timestamp |

##### Table Constraints & Indexes:
- **Primary Key:** `uq_question_options_id` ON (`id`)
- **Unique Constraint:** `uq_question_options_label` ON (`question_id`, `label`)
- **Foreign Key:** `fk_question_options_question` FOREIGN KEY (`question_id`) REFERENCES `questions`(`id`) ON DELETE CASCADE ON UPDATE CASCADE
- **Index:** `idx_question_options_question` ON (`question_id`, `sort_order` ASC)
- **Partial Index:** `idx_question_options_correct` ON (`question_id`) WHERE `is_correct = TRUE`.

---

#### 15. Table Specification: `question_explanations`
- **Purpose:** Pedagogical rationale and solution guide for a question.
- **Primary Key:** `id` (UUID, Default: `gen_random_uuid()`)

##### Column Specifications:
| Column Name | Data Type | Nullable | Default Value | PK/FK | Constraints / Rules |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | NO | `gen_random_uuid()` | PK | Primary Key |
| `question_id` | `UUID` | NO | None | FK, UK | Unique FK -> `questions(id)` ON DELETE CASCADE |
| `explanation_text` | `TEXT` | NO | None | None | Markdown solution rationale |
| `key_takeaway` | `TEXT` | YES | `NULL` | None | Core concept summary |
| `reference_source` | `TEXT` | YES | `NULL` | None | Textbook / past paper reference |
| `image_url` | `TEXT` | YES | `NULL` | None | Solution diagram link |
| `created_at` | `TIMESTAMPTZ` | NO | `CURRENT_TIMESTAMP` | None | Record creation timestamp |
| `updated_at` | `TIMESTAMPTZ` | NO | `CURRENT_TIMESTAMP` | None | Record last update timestamp |

##### Table Constraints & Indexes:
- **Primary Key:** `uq_question_explanations_id` ON (`id`)
- **Unique Constraint:** `uq_question_explanations_question` ON (`question_id`)
- **Foreign Key:** `fk_question_explanations_question` FOREIGN KEY (`question_id`) REFERENCES `questions`(`id`) ON DELETE CASCADE ON UPDATE CASCADE

---

#### 16. Table Specification: `question_versions`
- **Purpose:** Immutable snapshot history of question revisions.
- **Primary Key:** `id` (UUID, Default: `gen_random_uuid()`)

##### Column Specifications:
| Column Name | Data Type | Nullable | Default Value | PK/FK | Constraints / Rules |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | NO | `gen_random_uuid()` | PK | Primary Key |
| `question_id` | `UUID` | NO | None | FK | FK -> `questions(id)` ON DELETE CASCADE |
| `created_by_id` | `UUID` | NO | None | FK | FK -> `users(id)` ON DELETE RESTRICT |
| `version_number` | `INTEGER` | NO | None | None | Sequential revision number |
| `snapshot_data` | `JSONB` | NO | None | None | Complete JSON state of stem & choices |
| `change_summary` | `TEXT` | YES | `NULL` | None | Editorial revision reason |
| `created_at` | `TIMESTAMPTZ` | NO | `CURRENT_TIMESTAMP` | None | Archival timestamp |

##### Table Constraints & Indexes:
- **Primary Key:** `uq_question_versions_id` ON (`id`)
- **Unique Constraint:** `uq_question_versions_number` ON (`question_id`, `version_number`)
- **Foreign Keys:**
  - `fk_question_versions_question` FOREIGN KEY (`question_id`) REFERENCES `questions`(`id`) ON DELETE CASCADE ON UPDATE CASCADE
  - `fk_question_versions_creator` FOREIGN KEY (`created_by_id`) REFERENCES `users`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE
- **Index:** `idx_question_versions_lookup` ON (`question_id`, `version_number` DESC)

---

#### 17. Table Specification: `bookmarks`
- **Purpose:** Allows students to save questions, notes, or mock tests for revision.
- **Primary Key:** `id` (UUID, Default: `gen_random_uuid()`)

##### Column Specifications:
| Column Name | Data Type | Nullable | Default Value | PK/FK | Constraints / Rules |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | NO | `gen_random_uuid()` | PK | Primary Key |
| `user_id` | `UUID` | NO | None | FK | FK -> `users(id)` ON DELETE CASCADE |
| `question_id` | `UUID` | YES | `NULL` | FK | FK -> `questions(id)` ON DELETE CASCADE |
| `note_id` | `UUID` | YES | `NULL` | FK | FK -> `notes(id)` ON DELETE CASCADE |
| `target_type` | `VARCHAR(50)` | NO | None | None | Enum: `QUESTION`, `NOTE`, `MOCK_TEST` |
| `target_id` | `UUID` | NO | None | None | Generic polymorphic target UUID |
| `notes_tag` | `VARCHAR(100)` | YES | `NULL` | None | User-defined organization tag |
| `created_at` | `TIMESTAMPTZ` | NO | `CURRENT_TIMESTAMP` | None | Saved timestamp |

##### Table Constraints & Indexes:
- **Primary Key:** `uq_bookmarks_id` ON (`id`)
- **Unique Constraint:** `uq_bookmarks_user_target` ON (`user_id`, `target_type`, `target_id`)
- **Foreign Keys:**
  - `fk_bookmarks_user` FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE ON UPDATE CASCADE
  - `fk_bookmarks_question` FOREIGN KEY (`question_id`) REFERENCES `questions`(`id`) ON DELETE CASCADE ON UPDATE CASCADE
  - `fk_bookmarks_note` FOREIGN KEY (`note_id`) REFERENCES `notes`(`id`) ON DELETE CASCADE ON UPDATE CASCADE
- **Check Constraint:** `chk_bookmarks_target_type` CHECK (`target_type` IN ('QUESTION', 'NOTE', 'MOCK_TEST'))
- **Index:** `idx_bookmarks_user_type` ON (`user_id`, `target_type`, `created_at` DESC)

---

#### 18. Table Specification: `question_reports`
- **Purpose:** Student error flagging and resolution tracking for content quality governance.
- **Primary Key:** `id` (UUID, Default: `gen_random_uuid()`)

##### Column Specifications:
| Column Name | Data Type | Nullable | Default Value | PK/FK | Constraints / Rules |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | NO | `gen_random_uuid()` | PK | Primary Key |
| `question_id` | `UUID` | NO | None | FK | FK -> `questions(id)` ON DELETE CASCADE |
| `reporter_id` | `UUID` | NO | None | FK | FK -> `users(id)` ON DELETE CASCADE |
| `reviewer_id` | `UUID` | YES | `NULL` | FK | FK -> `users(id)` ON DELETE SET NULL |
| `category` | `VARCHAR(50)` | NO | None | None | Flag category enum |
| `comment` | `TEXT` | NO | None | None | Student feedback details |
| `status` | `VARCHAR(20)` | NO | `'OPEN'` | None | Workflow state enum |
| `resolution_notes` | `TEXT` | YES | `NULL` | None | Reviewer resolution summary |
| `created_at` | `TIMESTAMPTZ` | NO | `CURRENT_TIMESTAMP` | None | Report timestamp |
| `resolved_at` | `TIMESTAMPTZ` | YES | `NULL` | None | Resolution timestamp |

##### Table Constraints & Indexes:
- **Primary Key:** `uq_question_reports_id` ON (`id`)
- **Foreign Keys:**
  - `fk_question_reports_question` FOREIGN KEY (`question_id`) REFERENCES `questions`(`id`) ON DELETE CASCADE ON UPDATE CASCADE
  - `fk_question_reports_reporter` FOREIGN KEY (`reporter_id`) REFERENCES `users`(`id`) ON DELETE CASCADE ON UPDATE CASCADE
  - `fk_question_reports_reviewer` FOREIGN KEY (`reviewer_id`) REFERENCES `users`(`id`) ON DELETE SET NULL ON UPDATE CASCADE
- **Check Constraints:**
  - `chk_question_reports_category` CHECK (`category` IN ('WRONG_KEY', 'TYPO', 'AMBIGUOUS_STEM', 'BAD_EXPLANATION', 'OTHER'))
  - `chk_question_reports_status` CHECK (`status` IN ('OPEN', 'UNDER_REVIEW', 'RESOLVED', 'REJECTED'))
- **Index:** `idx_question_reports_status` ON (`status`, `created_at` DESC)

---

### 4.4 Assessment Engine Bounded Context

#### 19. Table Specification: `mock_tests`
- **Purpose:** Exam template configuring parameters, timing, and access tier.
- **Primary Key:** `id` (UUID, Default: `gen_random_uuid()`)

##### Column Specifications:
| Column Name | Data Type | Nullable | Default Value | PK/FK | Constraints / Rules |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | NO | `gen_random_uuid()` | PK | Primary Key |
| `exam_track_id` | `UUID` | NO | None | FK | FK -> `exam_tracks(id)` ON DELETE RESTRICT |
| `exam_id` | `UUID` | YES | `NULL` | FK | FK -> `exams(id)` ON DELETE SET NULL |
| `created_by_id` | `UUID` | NO | None | FK | FK -> `users(id)` ON DELETE RESTRICT |
| `title` | `VARCHAR(200)` | NO | None | None | Mock test title |
| `slug` | `VARCHAR(200)` | NO | None | UK | URL slug |
| `description` | `TEXT` | YES | `NULL` | None | Test instructions |
| `duration_minutes` | `INTEGER` | NO | None | None | Allotted time in minutes |
| `total_marks` | `NUMERIC(6,2)` | NO | None | None | Maximum achievable score |
| `passing_percentage` | `NUMERIC(5,2)` | NO | None | None | Required pass threshold (0-100) |
| `negative_marking_factor` | `NUMERIC(4,2)` | NO | `0.25` | None | Penalty factor per wrong answer |
| `is_premium` | `BOOLEAN` | NO | `FALSE` | None | Entitlement restriction flag |
| `status` | `VARCHAR(20)` | NO | `'DRAFT'` | None | Enum: `DRAFT`, `PUBLISHED`, `ARCHIVED` |
| `created_at` | `TIMESTAMPTZ` | NO | `CURRENT_TIMESTAMP` | None | Record creation timestamp |
| `updated_at` | `TIMESTAMPTZ` | NO | `CURRENT_TIMESTAMP` | None | Record last update timestamp |

##### Table Constraints & Indexes:
- **Primary Key:** `uq_mock_tests_id` ON (`id`)
- **Unique Constraint:** `uq_mock_tests_slug` ON (`slug`)
- **Foreign Keys:**
  - `fk_mock_tests_track` FOREIGN KEY (`exam_track_id`) REFERENCES `exam_tracks`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE
  - `fk_mock_tests_exam` FOREIGN KEY (`exam_id`) REFERENCES `exams`(`id`) ON DELETE SET NULL ON UPDATE CASCADE
  - `fk_mock_tests_creator` FOREIGN KEY (`created_by_id`) REFERENCES `users`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE
- **Check Constraints:**
  - `chk_mock_tests_duration` CHECK (`duration_minutes` > 0)
  - `chk_mock_tests_passing` CHECK (`passing_percentage` >= 0.00 AND `passing_percentage` <= 100.00)
  - `chk_mock_tests_status` CHECK (`status` IN ('DRAFT', 'PUBLISHED', 'ARCHIVED'))
- **Partial Index:** `idx_mock_tests_published_slug` ON (`slug`) WHERE `status = 'PUBLISHED'`.

---

#### 20. Table Specification: `mock_test_questions`
- **Purpose:** Associative table mapping questions to mock tests with sequence and scoring weights.
- **Primary Key:** `id` (UUID, Default: `gen_random_uuid()`)

##### Column Specifications:
| Column Name | Data Type | Nullable | Default Value | PK/FK | Constraints / Rules |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | NO | `gen_random_uuid()` | PK | Primary Key |
| `mock_test_id` | `UUID` | NO | None | FK | FK -> `mock_tests(id)` ON DELETE CASCADE |
| `question_id` | `UUID` | NO | None | FK | FK -> `questions(id)` ON DELETE RESTRICT |
| `question_order` | `INTEGER` | NO | None | None | Position sequence in test |
| `positive_marks` | `NUMERIC(4,2)` | NO | `1.00` | None | Marks awarded for correct answer |
| `negative_marks` | `NUMERIC(4,2)` | NO | `0.25` | None | Deduction for incorrect answer |
| `created_at` | `TIMESTAMPTZ` | NO | `CURRENT_TIMESTAMP` | None | Mapping creation timestamp |

##### Table Constraints & Indexes:
- **Primary Key:** `uq_mock_test_questions_id` ON (`id`)
- **Unique Constraints:**
  - `uq_mock_test_questions_pair` ON (`mock_test_id`, `question_id`)
  - `uq_mock_test_questions_order` ON (`mock_test_id`, `question_order`)
- **Foreign Keys:**
  - `fk_mock_test_questions_test` FOREIGN KEY (`mock_test_id`) REFERENCES `mock_tests`(`id`) ON DELETE CASCADE ON UPDATE CASCADE
  - `fk_mock_test_questions_question` FOREIGN KEY (`question_id`) REFERENCES `questions`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE
- **Index:** `idx_mock_test_questions_sequence` ON (`mock_test_id`, `question_order` ASC)

---

#### 21. Table Specification: `attempts`
- **Purpose:** Active or completed student test-taking session.
- **Primary Key:** `id` (UUID, Default: `gen_random_uuid()`)
- **Storage Considerations:** High write churn. Fillfactor set to 85.

##### Column Specifications:
| Column Name | Data Type | Nullable | Default Value | PK/FK | Constraints / Rules |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | NO | `gen_random_uuid()` | PK | Primary Key |
| `user_id` | `UUID` | NO | None | FK | FK -> `users(id)` ON DELETE CASCADE |
| `mock_test_id` | `UUID` | NO | None | FK | FK -> `mock_tests(id)` ON DELETE RESTRICT |
| `status` | `VARCHAR(20)` | NO | `'IN_PROGRESS'` | None | Session state enum |
| `started_at` | `TIMESTAMPTZ` | NO | `CURRENT_TIMESTAMP` | None | Test session start time |
| `submitted_at` | `TIMESTAMPTZ` | YES | `NULL` | None | Submission / termination time |
| `total_duration_seconds` | `INTEGER` | YES | `NULL` | None | Total elapsed test time |
| `ip_address` | `VARCHAR(45)` | YES | `NULL` | None | Client IP address |
| `device_info` | `TEXT` | YES | `NULL` | None | Client User-Agent string |
| `created_at` | `TIMESTAMPTZ` | NO | `CURRENT_TIMESTAMP` | None | Record creation timestamp |
| `updated_at` | `TIMESTAMPTZ` | NO | `CURRENT_TIMESTAMP` | None | Record last update timestamp |

##### Table Constraints & Indexes:
- **Primary Key:** `uq_attempts_id` ON (`id`)
- **Foreign Keys:**
  - `fk_attempts_user` FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE ON UPDATE CASCADE
  - `fk_attempts_mock_test` FOREIGN KEY (`mock_test_id`) REFERENCES `mock_tests`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE
- **Check Constraint:** `chk_attempts_status` CHECK (`status` IN ('IN_PROGRESS', 'SUBMITTED', 'EXPIRED', 'CANCELED'))
- **Indexes:**
  - `idx_attempts_user_status_date` ON (`user_id`, `status`, `started_at` DESC)
  - `idx_attempts_test_status` ON (`mock_test_id`, `status`)

---

#### 22. Table Specification: `attempt_answers`
- **Purpose:** Individual student response for a question inside a test attempt session.
- **Primary Key:** `id` (UUID, Default: `gen_random_uuid()`)
- **Storage Considerations:** Partitioning candidate by `created_at` or hash of `attempt_id`. High write volume during submissions.

##### Column Specifications:
| Column Name | Data Type | Nullable | Default Value | PK/FK | Constraints / Rules |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | NO | `gen_random_uuid()` | PK | Primary Key |
| `attempt_id` | `UUID` | NO | None | FK | FK -> `attempts(id)` ON DELETE CASCADE |
| `question_id` | `UUID` | NO | None | FK | FK -> `questions(id)` ON DELETE RESTRICT |
| `selected_option_id` | `UUID` | YES | `NULL` | FK | FK -> `question_options(id)` ON DELETE SET NULL |
| `question_version_id` | `UUID` | YES | `NULL` | FK | FK -> `question_versions(id)` ON DELETE SET NULL |
| `time_spent_seconds` | `INTEGER` | NO | `0` | None | Time spent on item |
| `score_awarded` | `NUMERIC(5,2)` | YES | `NULL` | None | Net marks earned for item |
| `is_correct` | `BOOLEAN` | YES | `NULL` | None | Evaluation outcome flag |
| `is_skipped` | `BOOLEAN` | NO | `TRUE` | None | Unanswered indicator |
| `created_at` | `TIMESTAMPTZ` | NO | `CURRENT_TIMESTAMP` | None | Log timestamp |

##### Table Constraints & Indexes:
- **Primary Key:** `uq_attempt_answers_id` ON (`id`)
- **Unique Constraint:** `uq_attempt_answers_pair` ON (`attempt_id`, `question_id`)
- **Foreign Keys:**
  - `fk_attempt_answers_attempt` FOREIGN KEY (`attempt_id`) REFERENCES `attempts`(`id`) ON DELETE CASCADE ON UPDATE CASCADE
  - `fk_attempt_answers_question` FOREIGN KEY (`question_id`) REFERENCES `questions`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE
  - `fk_attempt_answers_option` FOREIGN KEY (`selected_option_id`) REFERENCES `question_options`(`id`) ON DELETE SET NULL ON UPDATE CASCADE
  - `fk_attempt_answers_version` FOREIGN KEY (`question_version_id`) REFERENCES `question_versions`(`id`) ON DELETE SET NULL ON UPDATE CASCADE
- **Check Constraint:** `chk_attempt_answers_time` CHECK (`time_spent_seconds` >= 0)
- **Index:** `idx_attempt_answers_lookup` ON (`attempt_id`, `question_id`)

---

#### 23. Table Specification: `attempt_results`
- **Purpose:** Scored output and performance metrics snapshot for a finalized attempt.
- **Primary Key:** `id` (UUID, Default: `gen_random_uuid()`)

##### Column Specifications:
| Column Name | Data Type | Nullable | Default Value | PK/FK | Constraints / Rules |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | NO | `gen_random_uuid()` | PK | Primary Key |
| `attempt_id` | `UUID` | NO | None | FK, UK | Unique FK -> `attempts(id)` ON DELETE CASCADE |
| `total_questions` | `INTEGER` | NO | None | None | Total question count |
| `answered_count` | `INTEGER` | NO | None | None | Count of answered items |
| `correct_count` | `INTEGER` | NO | None | None | Count of correct items |
| `wrong_count` | `INTEGER` | NO | None | None | Count of incorrect items |
| `skipped_count` | `INTEGER` | NO | None | None | Count of skipped items |
| `score_obtained` | `NUMERIC(6,2)` | NO | None | None | Net score achieved |
| `total_possible_score` | `NUMERIC(6,2)` | NO | None | None | Max possible test score |
| `accuracy_percentage` | `NUMERIC(5,2)` | NO | None | None | Accuracy % (0.00 to 100.00) |
| `has_passed` | `BOOLEAN` | NO | None | None | Pass/fail evaluation flag |
| `summary_json` | `JSONB` | YES | `NULL` | None | Topic-wise breakdown snapshot |
| `created_at` | `TIMESTAMPTZ` | NO | `CURRENT_TIMESTAMP` | None | Score snapshot timestamp |

##### Table Constraints & Indexes:
- **Primary Key:** `uq_attempt_results_id` ON (`id`)
- **Unique Constraint:** `uq_attempt_results_attempt` ON (`attempt_id`)
- **Foreign Key:** `fk_attempt_results_attempt` FOREIGN KEY (`attempt_id`) REFERENCES `attempts`(`id`) ON DELETE CASCADE ON UPDATE CASCADE
- **Check Constraints:**
  - `chk_attempt_results_accuracy` CHECK (`accuracy_percentage` >= 0.00 AND `accuracy_percentage` <= 100.00)
  - `chk_attempt_results_counts` CHECK (`answered_count` + `skipped_count` = `total_questions`)
- **Index:** `idx_attempt_results_passed_score` ON (`has_passed`, `score_obtained` DESC)

---

### 4.5 Student Progress & Analytics Bounded Context

#### 24. Table Specification: `student_progress`
- **Purpose:** Aggregated cumulative topic performance metrics per student.
- **Primary Key:** `id` (UUID, Default: `gen_random_uuid()`)

##### Column Specifications:
| Column Name | Data Type | Nullable | Default Value | PK/FK | Constraints / Rules |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | NO | `gen_random_uuid()` | PK | Primary Key |
| `user_id` | `UUID` | NO | None | FK | FK -> `users(id)` ON DELETE CASCADE |
| `topic_id` | `UUID` | NO | None | FK | FK -> `topics(id)` ON DELETE CASCADE |
| `total_attempted` | `INTEGER` | NO | `0` | None | Cumulative attempted MCQs |
| `total_correct` | `INTEGER` | NO | `0` | None | Cumulative correct MCQs |
| `total_wrong` | `INTEGER` | NO | `0` | None | Cumulative incorrect MCQs |
| `accuracy_percentage` | `NUMERIC(5,2)` | NO | `0.00` | None | Topic accuracy percentage |
| `avg_time_per_question_seconds` | `NUMERIC(6,2)` | NO | `0.00` | None | Average latency per MCQ |
| `last_practiced_at` | `TIMESTAMPTZ` | YES | `NULL` | None | Timestamp of last practice |
| `updated_at` | `TIMESTAMPTZ` | NO | `CURRENT_TIMESTAMP` | None | Last aggregate update |

##### Table Constraints & Indexes:
- **Primary Key:** `uq_student_progress_id` ON (`id`)
- **Unique Constraint:** `uq_student_progress_user_topic` ON (`user_id`, `topic_id`)
- **Foreign Keys:**
  - `fk_student_progress_user` FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE ON UPDATE CASCADE
  - `fk_student_progress_topic` FOREIGN KEY (`topic_id`) REFERENCES `topics`(`id`) ON DELETE CASCADE ON UPDATE CASCADE
- **Check Constraint:** `chk_student_progress_accuracy` CHECK (`accuracy_percentage` >= 0.00 AND `accuracy_percentage` <= 100.00)
- **Indexes:**
  - `idx_student_progress_user_accuracy` ON (`user_id`, `accuracy_percentage` ASC)
  - `idx_student_progress_topic` ON (`topic_id`)

---

#### 25. Table Specification: `weak_topics`
- **Purpose:** Diagnostic entity highlighting topic deficit areas requiring student revision.
- **Primary Key:** `id` (UUID, Default: `gen_random_uuid()`)

##### Column Specifications:
| Column Name | Data Type | Nullable | Default Value | PK/FK | Constraints / Rules |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | NO | `gen_random_uuid()` | PK | Primary Key |
| `user_id` | `UUID` | NO | None | FK | FK -> `users(id)` ON DELETE CASCADE |
| `topic_id` | `UUID` | NO | None | FK | FK -> `topics(id)` ON DELETE CASCADE |
| `mastery_score` | `NUMERIC(5,2)` | NO | None | None | Calculated mastery index (0-100) |
| `accuracy_deficit` | `NUMERIC(5,2)` | NO | None | None | Gap below target mastery |
| `recommended_practice_count` | `INTEGER` | NO | `10` | None | Recommended drill count |
| `identified_at` | `TIMESTAMPTZ` | NO | `CURRENT_TIMESTAMP` | None | Detection timestamp |
| `updated_at` | `TIMESTAMPTZ` | NO | `CURRENT_TIMESTAMP` | None | Last calculation timestamp |

##### Table Constraints & Indexes:
- **Primary Key:** `uq_weak_topics_id` ON (`id`)
- **Unique Constraint:** `uq_weak_topics_user_topic` ON (`user_id`, `topic_id`)
- **Foreign Keys:**
  - `fk_weak_topics_user` FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE ON UPDATE CASCADE
  - `fk_weak_topics_topic` FOREIGN KEY (`topic_id`) REFERENCES `topics`(`id`) ON DELETE CASCADE ON UPDATE CASCADE
- **Index:** `idx_weak_topics_user_mastery` ON (`user_id`, `mastery_score` ASC)

---

### 4.6 Subscriptions & Entitlements Bounded Context

#### 26. Table Specification: `subscription_plans`
- **Purpose:** Commercial plan offering configuration (Free vs Premium Monthly).
- **Primary Key:** `id` (UUID, Default: `gen_random_uuid()`)

##### Column Specifications:
| Column Name | Data Type | Nullable | Default Value | PK/FK | Constraints / Rules |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | NO | `gen_random_uuid()` | PK | Primary Key |
| `title` | `VARCHAR(100)` | NO | None | None | Commercial plan name |
| `code` | `VARCHAR(50)` | NO | None | UK | Enum: `FREE`, `PREMIUM_MONTHLY` |
| `description` | `TEXT` | YES | `NULL` | None | Plan marketing overview |
| `price_amount` | `NUMERIC(10,2)` | NO | None | None | Monetary price tag |
| `currency` | `VARCHAR(10)` | NO | `'PKR'` | None | ISO currency code |
| `billing_interval` | `VARCHAR(20)` | NO | None | None | Enum: `MONTHLY`, `YEARLY`, `LIFETIME` |
| `is_active` | `BOOLEAN` | NO | `TRUE` | None | Sales availability flag |
| `created_at` | `TIMESTAMPTZ` | NO | `CURRENT_TIMESTAMP` | None | Record creation timestamp |
| `updated_at` | `TIMESTAMPTZ` | NO | `CURRENT_TIMESTAMP` | None | Record last update timestamp |

##### Table Constraints & Indexes:
- **Primary Key:** `uq_subscription_plans_id` ON (`id`)
- **Unique Constraint:** `uq_subscription_plans_code` ON (`code`)
- **Check Constraints:**
  - `chk_subscription_plans_code` CHECK (`code` IN ('FREE', 'PREMIUM_MONTHLY'))
  - `chk_subscription_plans_interval` CHECK (`billing_interval` IN ('MONTHLY', 'YEARLY', 'LIFETIME'))
  - `chk_subscription_plans_price` CHECK (`price_amount` >= 0.00)

---

#### 27. Table Specification: `plan_entitlements`
- **Purpose:** Associative mapping connecting feature entitlement capability codes to subscription plans.
- **Primary Key:** `id` (UUID, Default: `gen_random_uuid()`)

##### Column Specifications:
| Column Name | Data Type | Nullable | Default Value | PK/FK | Constraints / Rules |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | NO | `gen_random_uuid()` | PK | Primary Key |
| `subscription_plan_id` | `UUID` | NO | None | FK | FK -> `subscription_plans(id)` ON DELETE CASCADE |
| `entitlement_code` | `VARCHAR(100)` | NO | None | None | Capability key e.g. `access:pdf_notes` |
| `created_at` | `TIMESTAMPTZ` | NO | `CURRENT_TIMESTAMP` | None | Mapping timestamp |

##### Table Constraints & Indexes:
- **Primary Key:** `uq_plan_entitlements_id` ON (`id`)
- **Unique Constraint:** `uq_plan_entitlements_pair` ON (`subscription_plan_id`, `entitlement_code`)
- **Foreign Key:** `fk_plan_entitlements_plan` FOREIGN KEY (`subscription_plan_id`) REFERENCES `subscription_plans`(`id`) ON DELETE CASCADE ON UPDATE CASCADE
- **Index:** `idx_plan_entitlements_lookup` ON (`subscription_plan_id`, `entitlement_code`)

---

#### 28. Table Specification: `subscriptions`
- **Purpose:** User subscription contract lifecycle and period state tracking.
- **Primary Key:** `id` (UUID, Default: `gen_random_uuid()`)

##### Column Specifications:
| Column Name | Data Type | Nullable | Default Value | PK/FK | Constraints / Rules |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | NO | `gen_random_uuid()` | PK | Primary Key |
| `user_id` | `UUID` | NO | None | FK | FK -> `users(id)` ON DELETE CASCADE |
| `subscription_plan_id` | `UUID` | NO | None | FK | FK -> `subscription_plans(id)` ON DELETE RESTRICT |
| `status` | `VARCHAR(20)` | NO | `'PENDING'` | None | Enum: `PENDING`, `ACTIVE`, `PAST_DUE`, `CANCELED`, `EXPIRED`, `PAUSED` |
| `current_period_start` | `TIMESTAMPTZ` | NO | None | None | Active cycle start timestamp |
| `current_period_end` | `TIMESTAMPTZ` | NO | None | None | Active cycle expiration timestamp |
| `auto_renew` | `BOOLEAN` | NO | `TRUE` | None | Renewal flag |
| `canceled_at` | `TIMESTAMPTZ` | YES | `NULL` | None | Cancellation timestamp |
| `safepay_sub_token` | `VARCHAR(255)` | YES | `NULL` | None | Gateway recurring agreement token |
| `created_at` | `TIMESTAMPTZ` | NO | `CURRENT_TIMESTAMP` | None | Record creation timestamp |
| `updated_at` | `TIMESTAMPTZ` | NO | `CURRENT_TIMESTAMP` | None | Record last update timestamp |

##### Table Constraints & Indexes:
- **Primary Key:** `uq_subscriptions_id` ON (`id`)
- **Foreign Keys:**
  - `fk_subscriptions_user` FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE ON UPDATE CASCADE
  - `fk_subscriptions_plan` FOREIGN KEY (`subscription_plan_id`) REFERENCES `subscription_plans`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE
- **Check Constraint:** `chk_subscriptions_status` CHECK (`status` IN ('PENDING', 'ACTIVE', 'PAST_DUE', 'CANCELED', 'EXPIRED', 'PAUSED'))
- **Partial Unique Index:** `idx_subscriptions_active_user` ON (`user_id`) WHERE `status = 'ACTIVE'`.
- **Index:** `idx_subscriptions_user_status` ON (`user_id`, `status`, `current_period_end` DESC)

---

### 4.7 Payments & Ledger Bounded Context

#### 29. Table Specification: `payment_transactions`
- **Purpose:** Immutable monetary transaction ledger for payment checkout attempts and renewals.
- **Primary Key:** `id` (UUID, Default: `gen_random_uuid()`)
- **Storage Considerations:** Append-only table. High financial compliance auditing requirements.

##### Column Specifications:
| Column Name | Data Type | Nullable | Default Value | PK/FK | Constraints / Rules |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | NO | `gen_random_uuid()` | PK | Primary Key |
| `user_id` | `UUID` | NO | None | FK | FK -> `users(id)` ON DELETE RESTRICT |
| `subscription_id` | `UUID` | YES | `NULL` | FK | FK -> `subscriptions(id)` ON DELETE SET NULL |
| `amount` | `NUMERIC(10,2)` | NO | None | None | Charged amount |
| `currency` | `VARCHAR(10)` | NO | `'PKR'` | None | Currency code |
| `status` | `VARCHAR(20)` | NO | `'PENDING'` | None | Enum: `PENDING`, `SUCCEEDED`, `FAILED`, `CANCELED`, `REFUNDED` |
| `safepay_tracker_id` | `VARCHAR(255)` | NO | None | UK | Safepay checkout tracker ID |
| `safepay_txn_id` | `VARCHAR(255)` | YES | `NULL` | None | Safepay cleared transaction ID |
| `failure_reason` | `TEXT` | YES | `NULL` | None | Gateway error details |
| `created_at` | `TIMESTAMPTZ` | NO | `CURRENT_TIMESTAMP` | None | Transaction creation timestamp |
| `updated_at` | `TIMESTAMPTZ` | NO | `CURRENT_TIMESTAMP` | None | Transaction last update timestamp |

##### Table Constraints & Indexes:
- **Primary Key:** `uq_payment_transactions_id` ON (`id`)
- **Unique Constraint:** `uq_payment_transactions_tracker` ON (`safepay_tracker_id`)
- **Foreign Keys:**
  - `fk_payment_transactions_user` FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE
  - `fk_payment_transactions_subscription` FOREIGN KEY (`subscription_id`) REFERENCES `subscriptions`(`id`) ON DELETE SET NULL ON UPDATE CASCADE
- **Check Constraints:**
  - `chk_payment_transactions_status` CHECK (`status` IN ('PENDING', 'SUCCEEDED', 'FAILED', 'CANCELED', 'REFUNDED'))
  - `chk_payment_transactions_amount` CHECK (`amount` >= 0.00)
- **Indexes:**
  - `idx_payment_transactions_user_date` ON (`user_id`, `created_at` DESC)
  - `idx_payment_transactions_tracker` ON (`safepay_tracker_id`)

---

#### 30. Table Specification: `webhook_event_logs`
- **Purpose:** Raw HTTP payment provider webhook event log for idempotency and dispute auditing.
- **Primary Key:** `id` (UUID, Default: `gen_random_uuid()`)
- **Storage Considerations:** Append-only table. Partitioning candidate by `received_at`.

##### Column Specifications:
| Column Name | Data Type | Nullable | Default Value | PK/FK | Constraints / Rules |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | NO | `gen_random_uuid()` | PK | Primary Key |
| `payment_transaction_id` | `UUID` | YES | `NULL` | FK | FK -> `payment_transactions(id)` ON DELETE SET NULL |
| `provider` | `VARCHAR(50)` | NO | `'SAFEPAY'` | None | Gateway provider name |
| `event_token` | `VARCHAR(255)` | NO | None | UK | Idempotency key from Safepay |
| `event_type` | `VARCHAR(100)` | NO | None | None | E.g. `payment.succeeded` |
| `payload` | `JSONB` | NO | None | None | Raw HTTP JSON payload body |
| `hmac_verified` | `BOOLEAN` | NO | `FALSE` | None | HMAC signature validity flag |
| `processing_status` | `VARCHAR(20)` | NO | `'PENDING'` | None | Enum: `PENDING`, `PROCESSED`, `FAILED`, `IGNORED` |
| `error_log` | `TEXT` | YES | `NULL` | None | Processing exception trace |
| `received_at` | `TIMESTAMPTZ` | NO | `CURRENT_TIMESTAMP` | None | Ingestion timestamp |
| `processed_at` | `TIMESTAMPTZ` | YES | `NULL` | None | Processing completion timestamp |

##### Table Constraints & Indexes:
- **Primary Key:** `uq_webhook_event_logs_id` ON (`id`)
- **Unique Constraint:** `uq_webhook_event_logs_token` ON (`event_token`)
- **Foreign Key:** `fk_webhook_event_logs_txn` FOREIGN KEY (`payment_transaction_id`) REFERENCES `payment_transactions`(`id`) ON DELETE SET NULL ON UPDATE CASCADE
- **Check Constraint:** `chk_webhook_event_logs_status` CHECK (`processing_status` IN ('PENDING', 'PROCESSED', 'FAILED', 'IGNORED'))
- **Index:** `idx_webhook_event_logs_token` ON (`event_token`)
- **GIN Index:** `idx_webhook_event_logs_payload` ON `payload` USING GIN

---

### 4.8 Notifications Bounded Context

#### 31. Table Specification: `notifications`
- **Purpose:** In-app and multi-channel system notifications dispatched to users.
- **Primary Key:** `id` (UUID, Default: `gen_random_uuid()`)

##### Column Specifications:
| Column Name | Data Type | Nullable | Default Value | PK/FK | Constraints / Rules |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | NO | `gen_random_uuid()` | PK | Primary Key |
| `recipient_id` | `UUID` | NO | None | FK | FK -> `users(id)` ON DELETE CASCADE |
| `title` | `VARCHAR(200)` | NO | None | None | Alert title |
| `body` | `TEXT` | NO | None | None | Alert narrative body |
| `channel` | `VARCHAR(20)` | NO | `'IN_APP'` | None | Enum: `IN_APP`, `EMAIL`, `SMS` |
| `is_read` | `BOOLEAN` | NO | `FALSE` | None | Read indicator |
| `action_url` | `TEXT` | YES | `NULL` | None | Optional deep link URL |
| `created_at` | `TIMESTAMPTZ` | NO | `CURRENT_TIMESTAMP` | None | Dispatch timestamp |
| `read_at` | `TIMESTAMPTZ` | YES | `NULL` | None | Read acknowledgment timestamp |

##### Table Constraints & Indexes:
- **Primary Key:** `uq_notifications_id` ON (`id`)
- **Foreign Key:** `fk_notifications_recipient` FOREIGN KEY (`recipient_id`) REFERENCES `users`(`id`) ON DELETE CASCADE ON UPDATE CASCADE
- **Check Constraint:** `chk_notifications_channel` CHECK (`channel` IN ('IN_APP', 'EMAIL', 'SMS'))
- **Partial Index:** `idx_notifications_unread_recipient` ON (`recipient_id`, `created_at` DESC) WHERE `is_read = FALSE`.

---

### 4.9 Notes Bounded Context

#### 32. Table Specification: `notes`
- **Purpose:** Structured academic study guides and PDF revision material attached to topics/subjects.
- **Primary Key:** `id` (UUID, Default: `gen_random_uuid()`)

##### Column Specifications:
| Column Name | Data Type | Nullable | Default Value | PK/FK | Constraints / Rules |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | `UUID` | NO | `gen_random_uuid()` | PK | Primary Key |
| `subject_id` | `UUID` | NO | None | FK | FK -> `subjects(id)` ON DELETE RESTRICT |
| `topic_id` | `UUID` | YES | `NULL` | FK | FK -> `topics(id)` ON DELETE SET NULL |
| `created_by_id` | `UUID` | NO | None | FK | FK -> `users(id)` ON DELETE RESTRICT |
| `title` | `VARCHAR(200)` | NO | None | None | Note title |
| `slug` | `VARCHAR(200)` | NO | None | UK | URL slug |
| `content_markdown` | `TEXT` | NO | None | None | Rich text markdown content |
| `pdf_asset_url` | `TEXT` | YES | `NULL` | None | Downloadable PDF S3 asset link |
| `is_premium` | `BOOLEAN` | NO | `FALSE` | None | Entitlement access restriction |
| `is_published` | `BOOLEAN` | NO | `TRUE` | None | Publication flag |
| `view_count` | `INTEGER` | NO | `0` | None | Read counter |
| `created_at` | `TIMESTAMPTZ` | NO | `CURRENT_TIMESTAMP` | None | Creation timestamp |
| `updated_at` | `TIMESTAMPTZ` | NO | `CURRENT_TIMESTAMP` | None | Last update timestamp |

##### Table Constraints & Indexes:
- **Primary Key:** `uq_notes_id` ON (`id`)
- **Unique Constraint:** `uq_notes_slug` ON (`slug`)
- **Foreign Keys:**
  - `fk_notes_subject` FOREIGN KEY (`subject_id`) REFERENCES `subjects`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE
  - `fk_notes_topic` FOREIGN KEY (`topic_id`) REFERENCES `topics`(`id`) ON DELETE SET NULL ON UPDATE CASCADE
  - `fk_notes_creator` FOREIGN KEY (`created_by_id`) REFERENCES `users`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE
- **Check Constraint:** `chk_notes_view_count` CHECK (`view_count` >= 0)
- **Index:** `idx_notes_subject_topic_pub` ON (`subject_id`, `topic_id`, `is_published`)

---

## 5. Relationships

This section catalogs all foreign key relationships across the Prepora database, specifying parent tables, child tables, cardinalities, cascade policies, and business justifications.

| Foreign Key Name | Parent Table | Child Table | Cardinality | ON DELETE | ON UPDATE | Business Reason |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `fk_user_profiles_user` | `users` | `user_profiles` | 1:1 | **CASCADE** | CASCADE | Profile exists strictly with a user account. |
| `fk_user_profiles_exam_track` | `exam_tracks` | `user_profiles` | 1:N | **SET NULL** | CASCADE | Preserves student profile if an exam track is deleted. |
| `fk_role_permissions_role` | `roles` | `role_permissions` | 1:N | **CASCADE** | CASCADE | Cleaning role removes permission mappings. |
| `fk_role_permissions_permission` | `permissions` | `role_permissions` | 1:N | **CASCADE** | CASCADE | Cleaning permission removes role mappings. |
| `fk_user_roles_user` | `users` | `user_roles` | 1:N | **CASCADE** | CASCADE | Deleting user revokes all role assignments. |
| `fk_user_roles_role` | `roles` | `user_roles` | 1:N | **CASCADE** | CASCADE | Deleting role revokes assignments from users. |
| `fk_user_roles_assigned_by` | `users` | `user_roles` | 1:N | **SET NULL** | CASCADE | Preserves role assignment history if admin account deleted. |
| `fk_refresh_tokens_user` | `users` | `refresh_tokens` | 1:N | **CASCADE** | CASCADE | Session refresh tokens revoked when user is deleted. |
| `fk_audit_logs_actor` | `users` | `audit_logs` | 1:N | **SET NULL** | CASCADE | Preserves system audit log integrity even if actor deleted. |
| `fk_exams_track` | `exam_tracks` | `exams` | 1:N | **RESTRICT** | CASCADE | Blocks deletion of an exam track if child exams exist. |
| `fk_subjects_exam` | `exams` | `subjects` | 1:N | **RESTRICT** | CASCADE | Blocks deletion of an exam if child subjects exist. |
| `fk_topics_subject` | `subjects` | `topics` | 1:N | **RESTRICT** | CASCADE | Blocks deletion of a subject if child topics exist. |
| `fk_questions_topic` | `topics` | `questions` | 1:N | **RESTRICT** | CASCADE | Blocks deletion of a topic if questions exist in it. |
| `fk_questions_track` | `exam_tracks` | `questions` | 1:N | **SET NULL** | CASCADE | Unsets optional exam track link if track is deleted. |
| `fk_questions_creator` | `users` | `questions` | 1:N | **RESTRICT** | CASCADE | Protects author user accounts linked to question items. |
| `fk_questions_reviewer` | `users` | `questions` | 1:N | **SET NULL** | CASCADE | Unsets reviewer ID if SME user account is removed. |
| `fk_question_options_question` | `questions` | `question_options` | 1:N | **CASCADE** | CASCADE | Options belong strictly to their parent question stem. |
| `fk_question_explanations_question`| `questions` | `question_explanations`| 1:1 | **CASCADE** | CASCADE | Explanations belong strictly to parent question stem. |
| `fk_question_versions_question` | `questions` | `question_versions` | 1:N | **CASCADE** | CASCADE | Revision logs belong strictly to parent question stem. |
| `fk_question_versions_creator` | `users` | `question_versions` | 1:N | **RESTRICT** | CASCADE | Protects editor accounts linked to historical versions. |
| `fk_bookmarks_user` | `users` | `bookmarks` | 1:N | **CASCADE** | CASCADE | User bookmarks deleted if student account is deleted. |
| `fk_bookmarks_question` | `questions` | `bookmarks` | 1:N | **CASCADE** | CASCADE | Bookmarks deleted if target question is removed. |
| `fk_bookmarks_note` | `notes` | `bookmarks` | 1:N | **CASCADE** | CASCADE | Bookmarks deleted if target note is removed. |
| `fk_question_reports_question` | `questions` | `question_reports` | 1:N | **CASCADE** | CASCADE | Reports deleted if target question is removed. |
| `fk_question_reports_reporter` | `users` | `question_reports` | 1:N | **CASCADE** | CASCADE | Reports deleted if student reporter is removed. |
| `fk_question_reports_reviewer` | `users` | `question_reports` | 1:N | **SET NULL** | CASCADE | Unsets reviewer ID if reviewer account is removed. |
| `fk_mock_tests_track` | `exam_tracks` | `mock_tests` | 1:N | **RESTRICT** | CASCADE | Blocks track deletion if mock tests depend on it. |
| `fk_mock_tests_exam` | `exams` | `mock_tests` | 1:N | **SET NULL** | CASCADE | Unsets specific exam reference if exam is removed. |
| `fk_mock_tests_creator` | `users` | `mock_tests` | 1:N | **RESTRICT** | CASCADE | Protects creator user account linked to mock test. |
| `fk_mock_test_questions_test` | `mock_tests` | `mock_test_questions`| 1:N | **CASCADE** | CASCADE | Mapping removed if mock test template is deleted. |
| `fk_mock_test_questions_question` | `questions` | `mock_test_questions`| 1:N | **RESTRICT** | CASCADE | Blocks question deletion if bound to a mock test. |
| `fk_attempts_user` | `users` | `attempts` | 1:N | **CASCADE** | CASCADE | Student test attempts deleted if user account removed. |
| `fk_attempts_mock_test` | `mock_tests` | `attempts` | 1:N | **RESTRICT** | CASCADE | Blocks mock test deletion if historical attempts exist. |
| `fk_attempt_answers_attempt` | `attempts` | `attempt_answers` | 1:N | **CASCADE** | CASCADE | Answers belong strictly to parent attempt session. |
| `fk_attempt_answers_question` | `questions` | `attempt_answers` | 1:N | **RESTRICT** | CASCADE | Blocks question deletion if answered in attempts. |
| `fk_attempt_answers_option` | `question_options`| `attempt_answers` | 1:N | **SET NULL** | CASCADE | Unsets option reference if distractor option is removed. |
| `fk_attempt_answers_version` | `question_versions`| `attempt_answers` | 1:N | **SET NULL** | CASCADE | Preserves answer log if version entry is pruned. |
| `fk_attempt_results_attempt` | `attempts` | `attempt_results` | 1:1 | **CASCADE** | CASCADE | Score scorecard belongs strictly to parent attempt. |
| `fk_student_progress_user` | `users` | `student_progress` | 1:N | **CASCADE** | CASCADE | Progress records deleted if student account removed. |
| `fk_student_progress_topic` | `topics` | `student_progress` | 1:N | **CASCADE** | CASCADE | Progress records deleted if topic is removed. |
| `fk_weak_topics_user` | `users` | `weak_topics` | 1:N | **CASCADE** | CASCADE | Weak topic records deleted if student account removed. |
| `fk_weak_topics_topic` | `topics` | `weak_topics` | 1:N | **CASCADE** | CASCADE | Weak topic records deleted if topic is removed. |
| `fk_plan_entitlements_plan` | `subscription_plans`| `plan_entitlements` | 1:N | **CASCADE** | CASCADE | Entitlements unmapped if plan is deleted. |
| `fk_subscriptions_user` | `users` | `subscriptions` | 1:N | **CASCADE** | CASCADE | Subscriptions removed if user account is deleted. |
| `fk_subscriptions_plan` | `subscription_plans`| `subscriptions` | 1:N | **RESTRICT** | CASCADE | Blocks plan deletion if active subscriptions refer to it. |
| `fk_payment_transactions_user` | `users` | `payment_transactions`| 1:N | **RESTRICT** | CASCADE | Financial ledgers cannot be removed by user deletion. |
| `fk_payment_transactions_sub` | `subscriptions` | `payment_transactions`| 1:N | **SET NULL** | CASCADE | Preserves financial ledger if subscription record removed. |
| `fk_webhook_event_logs_txn` | `payment_transactions`| `webhook_event_logs`| 1:N | **SET NULL** | CASCADE | Preserves raw webhook log if transaction is unlinked. |
| `fk_notifications_recipient` | `users` | `notifications` | 1:N | **CASCADE** | CASCADE | Notifications removed if recipient account deleted. |
| `fk_notes_subject` | `subjects` | `notes` | 1:N | **RESTRICT** | CASCADE | Blocks subject deletion if study notes refer to it. |
| `fk_notes_topic` | `topics` | `notes` | 1:N | **SET NULL** | CASCADE | Unsets topic reference if topic is deleted. |
| `fk_notes_creator` | `users` | `notes` | 1:N | **RESTRICT** | CASCADE | Protects author user account linked to study notes. |

---

## 6. Constraints

### 6.1 Primary Key Constraints
All 32 entities enforce primary key uniqueness using 128-bit `UUIDv4` types backed by single-column B-tree primary key indexes (`id`).

### 6.2 Unique & Composite Unique Constraints
- `users`: Lowercase unique index on `email`.
- `user_profiles`: Unique constraint on `user_id`.
- `roles`: Unique constraints on `name` and `code`.
- `permissions`: Unique constraints on `codename` and composite `(domain, action)`.
- `role_permissions`: Composite unique constraint on `(role_id, permission_id)`.
- `user_roles`: Composite unique constraint on `(user_id, role_id)`.
- `refresh_tokens`: Unique constraint on `token`.
- `exam_tracks`: Unique constraints on `name` and `slug`.
- `exams`: Unique constraint on `slug` and composite `(exam_track_id, title)`.
- `subjects`: Unique constraint on `slug` and composite `(exam_id, title)`.
- `topics`: Unique constraint on `slug` and composite `(subject_id, title)`.
- `question_options`: Composite unique constraint on `(question_id, label)`.
- `question_explanations`: Unique constraint on `question_id`.
- `question_versions`: Composite unique constraint on `(question_id, version_number)`.
- `bookmarks`: Composite unique constraint on `(user_id, target_type, target_id)`.
- `mock_tests`: Unique constraint on `slug`.
- `mock_test_questions`: Composite unique constraints on `(mock_test_id, question_id)` and `(mock_test_id, question_order)`.
- `attempt_answers`: Composite unique constraint on `(attempt_id, question_id)`.
- `attempt_results`: Unique constraint on `attempt_id`.
- `student_progress`: Composite unique constraint on `(user_id, topic_id)`.
- `weak_topics`: Composite unique constraint on `(user_id, topic_id)`.
- `subscription_plans`: Unique constraint on `code`.
- `plan_entitlements`: Composite unique constraint on `(subscription_plan_id, entitlement_code)`.
- `payment_transactions`: Unique constraint on `safepay_tracker_id`.
- `webhook_event_logs`: Unique constraint on `event_token`.
- `notes`: Unique constraint on `slug`.

### 6.3 Check Constraints
- `chk_roles_code`: Validates role code values.
- `chk_questions_difficulty`: Restricts difficulty to `EASY`, `MEDIUM`, `HARD`.
- `chk_questions_status`: Restricts status to `DRAFT`, `IN_REVIEW`, `APPROVED`, `PUBLISHED`, `ARCHIVED`.
- `chk_questions_version`: Ensures `active_version >= 1`.
- `chk_bookmarks_target_type`: Restricts target type to `QUESTION`, `NOTE`, `MOCK_TEST`.
- `chk_question_reports_category`: Restricts flag category.
- `chk_question_reports_status`: Restricts report workflow status.
- `chk_mock_tests_duration`: Ensures `duration_minutes > 0`.
- `chk_mock_tests_passing`: Restricts passing percentage between `0.00` and `100.00`.
- `chk_mock_tests_status`: Restricts status to `DRAFT`, `PUBLISHED`, `ARCHIVED`.
- `chk_attempts_status`: Restricts status to `IN_PROGRESS`, `SUBMITTED`, `EXPIRED`, `CANCELED`.
- `chk_attempt_answers_time`: Ensures `time_spent_seconds >= 0`.
- `chk_attempt_results_accuracy`: Restricts accuracy between `0.00` and `100.00`.
- `chk_attempt_results_counts`: Validates `answered_count + skipped_count = total_questions`.
- `chk_student_progress_accuracy`: Restricts accuracy between `0.00` and `100.00`.
- `chk_subscription_plans_code`: Restricts plan code.
- `chk_subscription_plans_interval`: Restricts billing interval.
- `chk_subscription_plans_price`: Ensures `price_amount >= 0.00`.
- `chk_subscriptions_status`: Restricts subscription status.
- `chk_payment_transactions_status`: Restricts payment transaction status.
- `chk_payment_transactions_amount`: Ensures `amount >= 0.00`.
- `chk_webhook_event_logs_status`: Restricts processing status.
- `chk_notifications_channel`: Restricts channel to `IN_APP`, `EMAIL`, `SMS`.
- `chk_notes_view_count`: Ensures `view_count >= 0`.

### 6.4 Partial Unique Indexes
- `idx_users_email_lower`: `CREATE UNIQUE INDEX idx_users_email_lower ON users (LOWER(email)) WHERE deleted_at IS NULL;`
- `idx_subscriptions_active_user`: `CREATE UNIQUE INDEX idx_subscriptions_active_user ON subscriptions (user_id) WHERE status = 'ACTIVE';`

---

## 7. Index Strategy

Prepora utilizes a multi-layered PostgreSQL index strategy designed to ensure sub-100ms API response times across high-traffic lookup paths.

```
INDEX DESIGN ARCHITECTURE
├── B-Tree Indexes (Standard primary key & single-column foreign key lookups)
├── Composite B-Tree Indexes (Multi-column filtering: user_id + status + date)
├── Partial Indexes (Filtered indexing: status = 'ACTIVE' / deleted_at IS NULL)
└── GIN Indexes (Semi-structured JSONB payload attribute extraction)
```

### 7.1 Index Catalog & Technical Justifications

| Index Name | Target Table | Indexed Columns | Type / Condition | Architectural Justification |
| :--- | :--- | :--- | :--- | :--- |
| `idx_users_email_lower` | `users` | `LOWER(email)` | **Partial Unique** (`deleted_at IS NULL`) | Enables fast case-insensitive login lookups without indexing deleted accounts. |
| `idx_refresh_tokens_lookup` | `refresh_tokens` | `token` | **Partial B-Tree** (`is_revoked = FALSE`) | Accelerates active JWT session validation; ignores revoked tokens. |
| `idx_user_profiles_target_track` | `user_profiles` | `target_exam_track_id` | **Standard B-Tree** | Accelerates student demographic filtering by target exam branch. |
| `idx_questions_topic_status` | `questions` | `topic_id`, `status` | **Partial Composite** (`deleted_at IS NULL`) | Optimizes practice session item fetching by topic and published state. |
| `idx_questions_track_difficulty` | `questions` | `exam_track_id`, `difficulty`, `status` | **Partial Composite** (`deleted_at IS NULL`) | Accelerates mock test item selection algorithms based on track and difficulty. |
| `idx_question_options_question` | `question_options` | `question_id`, `sort_order` ASC | **Composite B-Tree** | Speeds up fetching option sets in display sequence for test engines. |
| `idx_mock_tests_published_slug` | `mock_tests` | `slug` | **Partial Unique** (`status = 'PUBLISHED'`) | Fast slug lookups for public mock test detail pages. |
| `idx_mock_test_questions_sequence`| `mock_test_questions`| `mock_test_id`, `question_order` ASC | **Composite B-Tree** | Fetches ordered test question sequences during attempt initialization. |
| `idx_attempts_user_status_date` | `attempts` | `user_id`, `status`, `started_at` DESC | **Composite B-Tree** | Accelerates student attempt history rendering and active session checks. |
| `idx_attempt_answers_lookup` | `attempt_answers` | `attempt_id`, `question_id` | **Composite Unique** | Optimizes auto-save background API writes during live test sessions. |
| `idx_attempt_results_passed_score` | `attempt_results` | `has_passed`, `score_obtained` DESC | **Composite B-Tree** | Supports fast candidate pass statistics and percentile calculations. |
| `idx_student_progress_user_accuracy`| `student_progress`| `user_id`, `accuracy_percentage` ASC | **Composite B-Tree** | Instant rendering of student weakness dashboards sorted by lowest accuracy. |
| `idx_weak_topics_user_mastery` | `weak_topics` | `user_id`, `mastery_score` ASC | **Composite B-Tree** | Drives adaptive test recommendation engines targeting lowest mastery scores. |
| `idx_subscriptions_active_user` | `subscriptions` | `user_id` | **Partial Unique** (`status = 'ACTIVE'`) | Enforces max 1 active subscription per user; zero-cost active entitlement check. |
| `idx_payment_transactions_tracker` | `payment_transactions` | `safepay_tracker_id` | **Unique B-Tree** | Instant payment gateway tracker lookups during checkout redirection. |
| `idx_webhook_event_logs_token` | `webhook_event_logs` | `event_token` | **Unique B-Tree** | Ensures zero-duplicate processing of incoming Safepay HTTP webhooks. |
| `idx_webhook_event_logs_payload` | `webhook_event_logs` | `payload` | **GIN Index** | Enables deep JSON path querying over raw gateway payload attributes. |
| `idx_notifications_unread` | `notifications` | `recipient_id`, `created_at` DESC | **Partial Composite** (`is_read = FALSE`) | Fast retrieval of unread in-app user notifications. |
| `idx_notes_subject_topic_pub` | `notes` | `subject_id`, `topic_id`, `is_published` | **Composite B-Tree** | Accelerates study guide content catalog browsing. |

---

## 8. Enumerations

All enumerations in Prepora are implemented as standard PostgreSQL `VARCHAR` columns enforced via table-level `CHECK` constraints and mapped cleanly to Django `TextChoices` classes.

### 8.1 Enumeration Master Dictionary

#### 1. `RoleCodeEnum`
- **Target Field:** `roles.code`
- **Allowed Values:** `'STUDENT'`, `'CONTENT_EDITOR'`, `'SME'`, `'SUPPORT_AGENT'`, `'ADMIN'`, `'SUPERADMIN'`
- **Meanings:** Standard student candidate, content creator/editor, Subject Matter Expert reviewer, support staff, system administrator, platform superuser.
- **Default Value:** None (assigned via role seeding).

#### 2. `QuestionDifficultyEnum`
- **Target Field:** `questions.difficulty`
- **Allowed Values:** `'EASY'`, `'MEDIUM'`, `'HARD'`
- **Meanings:** Item difficulty level for adaptive test assembly.
- **Default Value:** `'MEDIUM'`

#### 3. `QuestionStatusEnum`
- **Target Field:** `questions.status`
- **Allowed Values:** `'DRAFT'`, `'IN_REVIEW'`, `'APPROVED'`, `'PUBLISHED'`, `'ARCHIVED'`
- **Meanings:** Editorial lifecycle governance state.
- **Default Value:** `'DRAFT'`

#### 4. `BookmarkTargetTypeEnum`
- **Target Field:** `bookmarks.target_type`
- **Allowed Values:** `'QUESTION'`, `'NOTE'`, `'MOCK_TEST'`
- **Meanings:** Polymorphic target type saved by student.
- **Default Value:** None.

#### 5. `QuestionReportCategoryEnum`
- **Target Field:** `question_reports.category`
- **Allowed Values:** `'WRONG_KEY'`, `'TYPO'`, `'AMBIGUOUS_STEM'`, `'BAD_EXPLANATION'`, `'OTHER'`
- **Meanings:** Content flaw classification.
- **Default Value:** None.

#### 6. `QuestionReportStatusEnum`
- **Target Field:** `question_reports.status`
- **Allowed Values:** `'OPEN'`, `'UNDER_REVIEW'`, `'RESOLVED'`, `'REJECTED'`
- **Meanings:** Content report resolution lifecycle state.
- **Default Value:** `'OPEN'`

#### 7. `MockTestStatusEnum`
- **Target Field:** `mock_tests.status`
- **Allowed Values:** `'DRAFT'`, `'PUBLISHED'`, `'ARCHIVED'`
- **Meanings:** Mock test publishing availability state.
- **Default Value:** `'DRAFT'`

#### 8. `AttemptStatusEnum`
- **Target Field:** `attempts.status`
- **Allowed Values:** `'IN_PROGRESS'`, `'SUBMITTED'`, `'EXPIRED'`, `'CANCELED'`
- **Meanings:** Test attempt execution session state.
- **Default Value:** `'IN_PROGRESS'`

#### 9. `SubscriptionPlanCodeEnum`
- **Target Field:** `subscription_plans.code`
- **Allowed Values:** `'FREE'`, `'PREMIUM_MONTHLY'`
- **Meanings:** Commercial product tier key.
- **Default Value:** None.

#### 10. `BillingIntervalEnum`
- **Target Field:** `subscription_plans.billing_interval`
- **Allowed Values:** `'MONTHLY'`, `'YEARLY'`, `'LIFETIME'`
- **Meanings:** Recurring charge cycle cadence.
- **Default Value:** None.

#### 11. `SubscriptionStatusEnum`
- **Target Field:** `subscriptions.status`
- **Allowed Values:** `'PENDING'`, `'ACTIVE'`, `'PAST_DUE'`, `'CANCELED'`, `'EXPIRED'`, `'PAUSED'`
- **Meanings:** Subscription lifecycle contract state.
- **Default Value:** `'PENDING'`

#### 12. `PaymentTransactionStatusEnum`
- **Target Field:** `payment_transactions.status`
- **Allowed Values:** `'PENDING'`, `'SUCCEEDED'`, `'FAILED'`, `'CANCELED'`, `'REFUNDED'`
- **Meanings:** Monetary transaction status.
- **Default Value:** `'PENDING'`

#### 13. `WebhookProcessingStatusEnum`
- **Target Field:** `webhook_event_logs.processing_status`
- **Allowed Values:** `'PENDING'`, `'PROCESSED'`, `'FAILED'`, `'IGNORED'`
- **Meanings:** Background webhook ingestion state.
- **Default Value:** `'PENDING'`

#### 14. `NotificationChannelEnum`
- **Target Field:** `notifications.channel`
- **Allowed Values:** `'IN_APP'`, `'EMAIL'`, `'SMS'`
- **Meanings:** Message dispatch channel.
- **Default Value:** `'IN_APP'`

---

## 9. Data Integrity Rules

### 9.1 Referential Integrity Governance
Foreign key deletion rules are applied at the database level to ensure consistency:
- **`ON DELETE CASCADE`:** Applied exclusively to tight ownership child entities (e.g., `user_profiles`, `question_options`, `attempt_answers`, `attempt_results`). Deleting the parent automatically cleans up child records.
- **`ON DELETE RESTRICT`:** Applied to structural taxonomy and transactional core records (e.g., deleting an `ExamTrack` with child `Exam`s, or deleting a `Question` referenced in `AttemptAnswer`s is strictly blocked by PostgreSQL).
- **`ON DELETE SET NULL`:** Applied to optional metadata links (e.g., `reviewer_id`, `assigned_by_id`, `note_id`). Deleting the referenced entity sets the column to `NULL` without destroying the primary record.

### 9.2 Soft Deletion Policy
- **Entities Under Soft Delete:** `users`, `questions`, `notes`.
- **Mechanics:** Soft-deleted entities retain a non-null `deleted_at` timestamp. Standard application queries must include `WHERE deleted_at IS NULL`.
- **Database Enforcement:** Unique indexes on soft-deleted entities include `WHERE deleted_at IS NULL` to permit re-registration or slug reuse after deletion.

### 9.3 Content Versioning & Immutability
- Once a question enters `PUBLISHED` status, inline SQL edits to `stem` or distractors are prohibited by backend application workflows.
- Updating a published question creates an archived snapshot entry in `question_versions` storing the full prior state, incrementing `active_version`.
- `AttemptAnswer` entries record both `question_id` and `question_version_id`, ensuring historical candidate performance scorecards remain completely immutable regardless of future content edits.

---

## 10. Performance Considerations

### 10.1 Connection Pooling & Scaling
- **PgBouncer Integration:** All Django application servers connect to PostgreSQL through PgBouncer in **Transaction Pooling Mode**.
- **Connection Configuration:**
  - Max client connections: 2,000.
  - Server pool size: 50 active PostgreSQL server connections.
  - Session pin prevention: Application code avoids prepared statements across transactions and un-nested temporary tables.

### 10.2 Table Partitioning Strategy
For high-volume append-only tables projecting millions of rows per season, native PostgreSQL range partitioning is designated:
1. **`attempt_answers`:** Range partitioned by `created_at` (Monthly partitions e.g. `attempt_answers_2026_08`).
2. **`audit_logs`:** Range partitioned by `created_at` (Quarterly partitions).
3. **`webhook_event_logs`:** Range partitioned by `received_at` (Monthly partitions).

### 10.3 Autovacuum & Vacuum Tuning
High-churn tables (`attempts`, `refresh_tokens`, `subscriptions`) are configured with aggressive table-level autovacuum parameters:
```
ALTER TABLE attempts SET (
    autovacuum_vacuum_scale_factor = 0.05,
    autovacuum_analyze_scale_factor = 0.02
);
```

---

## 11. Security Considerations

### 11.1 Credential & Sensitive Data Storage
- Passwords are stored in `users.password_hash` using Argon2id or PBKDF2 with SHA-256 (Django default). Plaintext password storage is physically impossible.
- Refresh tokens are stored as 512-bit cryptographic strings with explicit revocation flags.

### 11.2 Financial Data & PII Protection
- PCI-DSS Compliance: Credit card numbers, CVVs, and banking details are **NEVER** stored in PostgreSQL. All monetary payments are tokenized via Safepay.
- Sensitive gateway transaction tokens (`safepay_tracker_id`, `safepay_sub_token`) are restricted to the `prepora_app` role.

### 11.3 Immutable Security Logs
`audit_logs`, `payment_transactions`, and `webhook_event_logs` are designated append-only ledgers. `UPDATE` and `DELETE` privileges on these tables are revoked from the standard `prepora_app` DML role.

---

## 12. Django Compatibility

This schema maps 1:1 to Django 4.2+ ORM models.

### 12.1 Django Field Type Mapping Guide

| PostgreSQL Physical Type | Django ORM Field Class | Model Parameter Standard |
| :--- | :--- | :--- |
| `UUID` | `models.UUIDField` | `primary_key=True, default=uuid.uuid4, editable=False` |
| `VARCHAR(n)` | `models.CharField` | `max_length=n` |
| `TEXT` | `models.TextField` | `blank=True, null=True` (if nullable) |
| `BOOLEAN` | `models.BooleanField` | `default=True/False` |
| `INTEGER` | `models.IntegerField` | `default=0` |
| `NUMERIC(p, s)` | `models.DecimalField` | `max_digits=p, decimal_places=s` |
| `TIMESTAMPTZ` | `models.DateTimeField` | `auto_now_add=True` / `auto_now=True` / `default=timezone.now` |
| `JSONB` | `models.JSONField` | `default=dict, blank=True` |
| Foreign Key | `models.ForeignKey` | `to, on_delete=models.RESTRICT/CASCADE, db_column='...'` |
| 1:1 Foreign Key | `models.OneToOneField` | `to, on_delete=models.CASCADE, db_column='...'` |

### 12.2 Django Meta Specifications
Every Django model must define explicit `db_table` and Meta constraints matching the physical schema:
- `db_table = '<table_name>'`
- `indexes = [models.Index(fields=[...], name='idx_...')]`
- `constraints = [models.UniqueConstraint(...), models.CheckConstraint(...)]`

---

## 13. Future Scalability

The physical database schema incorporates extension slots to support future platform modules without structural breaking changes:

1. **AI Tutor Module:** Can bind an `ai_tutor_sessions` table to `users(id)` and `questions(id)`, utilizing `weak_topics` and `student_progress` to build context prompts. Vector embeddings can be stored in a `pgvector` column on `questions`.
2. **Leaderboards & Percentiles:** Supports read-replica background aggregation into an un-indexed `leaderboard_snapshots` table populated from `attempt_results`.
3. **Adaptive Computerized Testing (CAT):** `attempt_answers` captures time latency and version tracking, enabling Item Response Theory (IRT) theta scoring algorithms.
4. **Certificates & Diplomas:** A future `certificates` table can bind to `users(id)` and `attempt_results(id)`, storing verification hashes and PDF asset URLs.
5. **Video Courses & Lessons:** `video_courses` and `video_lessons` tables can attach directly to the existing `subjects` and `topics` taxonomy nodes alongside `notes`.
6. **Discussion Forum:** A future `forum_threads` table can reference `subjects(id)` or `questions(id)` and `users(id)`.
7. **Affiliate & Referral System:** An `affiliate_referrals` table can reference `users(id)` and `payment_transactions(id)`.

---

## 14. Verification Checklist

The checklist below confirms that this physical schema specification accurately implements 100% of the approved ER Diagram:

- [x] All 32 ER Diagram entities exist with exact physical table definitions.
- [x] Every primary key utilizes native `UUIDv4` (`gen_random_uuid()`).
- [x] Every foreign key relationship has explicit `ON DELETE` and `ON UPDATE` actions.
- [x] All 14 system enums are documented with allowed values, defaults, and check constraints.
- [x] Complete partial and composite index strategy documented for all high-frequency query paths.
- [x] 100% compliant with 3NF normalization rules, with documented denormalization in read snapshot tables.
- [x] 1:1 mapping compatibility with Django 4.2+ ORM constructs verified.
- [x] Audit trail, soft deletion, and immutable ledger policies fully defined.
- [x] Ready for Django models generation and zero-downtime PostgreSQL migrations.
