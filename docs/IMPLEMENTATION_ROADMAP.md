# Prepora Implementation Roadmap & Technical Delivery Plan

> **Document Status:** Official Master Implementation Blueprint  
> **Author:** Technical Project Manager & Principal Systems Architect  
> **Target Stack:** Django 5.x / DRF 3.15+ | React 19 + TypeScript + Vite | PostgreSQL 16+ | Docker Compose | Safepay Gateway  
> **Single Source of Truth Alignment:** [PROJECT_PLAN.md](file:///d:/Prepora/docs/PROJECT_PLAN.md), [DATABASE_PLAN.md](file:///d:/Prepora/docs/DATABASE_PLAN.md), [DOMAIN_MODEL.md](file:///d:/Prepora/docs/DOMAIN_MODEL.md), [BUSINESS_WORKFLOWS.md](file:///d:/Prepora/docs/BUSINESS_WORKFLOWS.md), [API_DESIGN.md](file:///d:/Prepora/docs/API_DESIGN.md), [BACKEND_STRUCTURE.md](file:///d:/Prepora/docs/BACKEND_STRUCTURE.md), [FRONTEND_STRUCTURE.md](file:///d:/Prepora/docs/FRONTEND_STRUCTURE.md), [POSTGRESQL_SCHEMA.md](file:///d:/Prepora/docs/POSTGRESQL_SCHEMA.md)

---

## 1. Overview & Delivery Strategy

This document establishes the official phase-by-phase implementation roadmap for **Prepora**, a production-grade online preparation SaaS platform for Pakistan Armed Forces entry tests (PMA, PAF, Navy, ISSB, ASF) and competitive government examinations (FPSC, Police).

The roadmap translates all architectural blueprints in `/docs` into an incremental, test-driven delivery sequence. Development is partitioned into **10 sequential phases**. Each phase specifies concrete tasks across the Backend, Frontend, Database, and Testing layers, concluding with an explicit Definition of Done.

```
+-----------------------------------------------------------------------------------+
|                            PREPORA PHASE DELIVERY FLOW                            |
+-----------------------------------------------------------------------------------+
  Phase 1: Foundations & Infrastructure Setup
     │
     ▼
  Phase 2: Identity, Credentials & RBAC Access Control
     │
     ▼
  Phase 3: Core Exam Taxonomy & Syllabus Hierarchy
     │
     ▼
  Phase 4: Question Bank & Editorial Quality Governance
     │
     ▼
  Phase 5: Practice Engine, Revision Notes & Student Bookmarks
     │
     ▼
  Phase 6: Timed Mock Tests & Server-Side Scoring Engine
     │
     ▼
  Phase 7: Analytics Engine, Performance Trends & Weak Topics
     │
     ▼
  Phase 8: Safepay Monetization, Subscriptions & Entitlements
     │
     ▼
  Phase 9: Operator Admin Panel, Content Queue & System Auditing
     │
     ▼
  Phase 10: Production Hardening, Multi-Stage Docker & Launch Readiness
+-----------------------------------------------------------------------------------+
```

---

## 2. Phase Breakdown

---

### Phase 1: Project Initialization & Infrastructure

#### Objective
Establish a clean, working local development foundation featuring containerized Docker Compose orchestration, Django 5.x REST backend shell, React 19 + TypeScript + Vite frontend shell, and PostgreSQL 16 database connectivity.

#### Backend Tasks
- [ ] Initialize Django 5.x project layout with modular settings directory (`config/settings/base.py`, `development.py`, `production.py`, `testing.py`).
- [ ] Configure `apps/common` app with abstract models (`TimeStampedUUIDModel`, `SoftDeleteModel`), RFC 7807 error formatters, custom exception handlers, and standard JSON renderers.
- [ ] Configure environment variable loading strategy using `python-dotenv`.
- [ ] Install and configure `django-cors-headers` middleware for local frontend cross-origin requests.
- [ ] Create public health check API endpoint (`GET /api/health/`) returning system runtime status.
- [ ] Create `backend/Dockerfile` and `backend/.dockerignore`.

#### Frontend Tasks
- [ ] Initialize React 19 + TypeScript project shell via Vite inside `frontend/`.
- [ ] Set up Tailwind CSS directives (`index.css`), color tokens, and font primitives.
- [ ] Build base infrastructure services (`src/services/api.client.ts`, `src/services/storage.service.ts`).
- [ ] Configure central layout primitives (`GuestLayout`, `GlobalLoader`) and environment constants (`VITE_API_BASE_URL`).
- [ ] Build dev status page testing Frontend → Backend communication via `/api/health/`.
- [ ] Create `frontend/Dockerfile` and `frontend/.dockerignore`.

#### Database Tasks
- [ ] Configure PostgreSQL 16 service in root `docker-compose.yml` with health checks and persistent volume (`postgres_data`).
- [ ] Create initialization script to ensure `pgcrypto` and `uuid-ossp` extensions are enabled in PostgreSQL.
- [ ] Configure Django `DATABASES` connection settings using environment variables (`DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`).

#### Testing Tasks
- [ ] Write unit test for `/api/health/` endpoint verifying 200 OK HTTP response.
- [ ] Test local multi-container startup via `docker compose up --build`.
- [ ] Verify PostgreSQL data persistence by restarting database container and confirming state retention.

#### Definition of Done
Backend, Frontend, and PostgreSQL containers spin up successfully via `docker compose up`, database retains volume state across restarts, `/api/health/` returns JSON status `200 OK`, and the frontend dev page renders clean connected status.

---

### Phase 2: Authentication & User Management

#### Objective
Implement identity registration, credential login, JWT token management with rotatable refresh tokens, Role-Based Access Control (RBAC), and student profile maintenance.

#### Backend Tasks
- [ ] Create `apps/accounts` Django app.
- [ ] Implement `User`, `UserProfile`, `Role`, `Permission`, `RolePermission`, `UserRole`, `RefreshToken`, and `AuditLog` Django ORM models.
- [ ] Configure `djangorestframework-simplejwt` for 15-minute access tokens and 7-day rotatable refresh tokens.
- [ ] Build authentication REST endpoints (`POST /api/v1/auth/register/`, `POST /api/v1/auth/login/`, `POST /api/v1/auth/refresh/`, `POST /api/v1/auth/logout/`, `GET /api/v1/users/me/profile/`, `PATCH /api/v1/users/me/profile/`).
- [ ] Implement custom DRF permission classes (`IsAuthenticated`, `HasRole`).
- [ ] Create `seed_roles` management command populating standard RBAC roles (`STUDENT`, `CONTENT_EDITOR`, `SME`, `SUPPORT_AGENT`, `ADMIN`, `SUPERADMIN`) and initial permission grants.
- [ ] Connect Django `post_save` signals to auto-create `UserProfile` and bind `FREE` subscription tier on user registration.

#### Frontend Tasks
- [ ] Build `auth` and `profile` feature modules (`src/features/auth/`, `src/features/profile/`).
- [ ] Build `LoginPage`, `RegisterPage`, `ForgotPasswordPage`, `ResetPasswordPage`, and `ProfilePage`.
- [ ] Implement Zod validation schemas (`loginSchema`, `registerSchema`, `updateProfileSchema`) with React Hook Form.
- [ ] Implement `useAuthStore` Zustand store managing user identity, access tokens, and role evaluation methods (`hasRole`).
- [ ] Configure Axios response interceptor for transparent queue-based token refresh on HTTP 401 errors.
- [ ] Build `ProtectedRoute` and `RoleGuard` route wrapper components.

#### Database Tasks
- [ ] Apply database migrations for `users`, `user_profiles`, `roles`, `permissions`, `role_permissions`, `user_roles`, `refresh_tokens`, and `audit_logs` tables.
- [ ] Ensure partial indexes `idx_users_email_lower` (case-insensitive email lookup) and `idx_refresh_tokens_lookup` are created.
- [ ] Execute `seed_roles` command to populate default system permissions and RBAC roles.

#### Testing Tasks
- [ ] Write backend unit tests for password hashing, user registration validation, and JWT token refresh issuance.
- [ ] Write integration tests verifying RBAC permission checks reject unauthorized role access.
- [ ] Write frontend component tests for registration and login forms validating error feedback.

#### Definition of Done
Users can register new accounts, authenticate, receive JWT tokens, silently refresh expired sessions, update profile target exam tracks, and navigate protected frontend routes according to assigned RBAC roles.

---

### Phase 3: Exam Taxonomy & Syllabus Hierarchy

#### Objective
Implement the complete educational domain hierarchy (`ExamTrack -> Exam -> Subject -> Topic`) and expose cached public catalog browsing.

#### Backend Tasks
- [ ] Create `apps/exams` Django app.
- [ ] Implement `ExamTrack`, `Exam`, `Subject`, `Topic` Django ORM models with automatic slug generation and sorting order.
- [ ] Build taxonomy REST API endpoints (`GET /api/v1/exam-tracks/`, `GET /api/v1/exam-tracks/{slug}/`, `GET /api/v1/exams/`, `GET /api/v1/subjects/`, `GET /api/v1/topics/`).
- [ ] Integrate Redis caching for public taxonomy endpoints to ensure sub-50ms query response times.
- [ ] Implement cache invalidation signals purging taxonomy keys whenever models are created or updated.
- [ ] Create `seed_taxonomy` management command populating Pakistan Armed Forces exam tracks (Army, Air Force, Navy, ISSB, ASF, FPSC).

#### Frontend Tasks
- [ ] Build `exam-tracks`, `subjects`, and `topics` feature modules (`src/features/exam-tracks/`, `src/features/subjects/`, `src/features/topics/`).
- [ ] Build `ExamTracksPage`, `ExamDetailPage`, `SubjectsPage`, and `TopicsPage`.
- [ ] Implement TanStack Query custom hooks (`useExamTracks`, `useExamTrackDetail`, `useSubjects`, `useTopics`) with 60-minute stale time.
- [ ] Render visual catalog grids displaying track icons, descriptions, subject counts, and syllabus topic lists.

#### Database Tasks
- [ ] Apply database migrations for `exam_tracks`, `exams`, `subjects`, and `topics` tables.
- [ ] Create unique constraints on slug fields and composite indexes (`idx_exams_track_active`, `idx_subjects_exam_active`, `idx_topics_subject_active`).
- [ ] Execute `seed_taxonomy` command to seed initial exam tracks, subjects, and topic nodes.

#### Testing Tasks
- [ ] Write backend unit tests for taxonomy hierarchy queries and slug resolution.
- [ ] Write API integration tests verifying public taxonomy read endpoints work for unauthenticated visitors.
- [ ] Verify Redis cache hit/miss behavior and automatic cache clearing on model modifications.

#### Definition of Done
The educational syllabus hierarchy is fully seeded in PostgreSQL, exposed via fast cached REST APIs, and rendered on responsive frontend catalog pages allowing students to select their target exam track.

---

### Phase 4: Question Bank & Content Quality Governance

#### Objective
Implement MCQ item authoring, distractor option sets, pedagogical explanations, multi-stage editorial governance workflow (`DRAFT -> IN_REVIEW -> APPROVED -> PUBLISHED -> ARCHIVED`), version control snapshots, and student question issue reporting.

#### Backend Tasks
- [ ] Create `apps/questions` Django app.
- [ ] Implement `Question`, `QuestionOption`, `QuestionExplanation`, `QuestionVersion`, `QuestionSource`, and `QuestionReport` Django ORM models.
- [ ] Enforce editorial status state machine transitions and duty separation rule (`creator_id != reviewer_id` for publication).
- [ ] Implement automatic `QuestionVersion` snapshot creation on modification of published questions.
- [ ] Build REST API endpoints for question authoring (`/api/v1/questions/`), status transitions (`/api/v1/questions/{id}/publish/`), and student report submission (`POST /api/v1/question-reports/`).
- [ ] Implement correct answer key stripping in student-facing question serializers.

#### Frontend Tasks
- [ ] Build `questions` and `question-reports` feature modules (`src/features/questions/`, `src/features/question-reports/`).
- [ ] Build Question Editor component for Content Editors and SMEs (stem text, distractors, correct key toggle, explanation, source reference).
- [ ] Build Report Question modal dialog allowing students to flag question errors (`WRONG_KEY`, `TYPO`, `AMBIGUOUS_STEM`).
- [ ] Build Question Governance dashboard for SMEs to review, approve, or reject draft questions with feedback.

#### Database Tasks
- [ ] Apply database migrations for `questions`, `question_options`, `question_explanations`, `question_versions`, `question_sources`, and `question_reports` tables.
- [ ] Enforce domain check constraints (`chk_questions_difficulty`, `chk_questions_status`, `chk_question_reports_category`, `chk_question_reports_status`).
- [ ] Create partial index `idx_questions_published_lookup` optimizing queries for published items.

#### Testing Tasks
- [ ] Write unit tests for question status state machine verifying invalid status jumps are rejected.
- [ ] Write integration tests verifying content creators cannot approve their own questions.
- [ ] Test version snapshot creation ensuring historical test attempts retain reference to their original `QuestionVersion`.

#### Definition of Done
Editors can author MCQs with distractor choices and explanations, SMEs can formally review and approve items, updating published questions creates immutable version snapshots, and students can submit issue reports.

---

### Phase 5: Practice Sessions & Bookmarks

#### Objective
Enable topic-wise MCQ practice sessions with instant answer reveals, personal revision bookmarks, and study guide note consumption.

#### Backend Tasks
- [ ] Create `apps/notes` and `apps/bookmarks` Django apps.
- [ ] Implement `Note` and `Bookmark` Django ORM models.
- [ ] Build practice MCQ retrieval API supporting filtering by exam track, subject, topic, and difficulty.
- [ ] Build REST APIs for managing student bookmarks (`GET /api/v1/bookmarks/`, `POST /api/v1/bookmarks/`, `DELETE /api/v1/bookmarks/{id}/`).
- [ ] Build REST APIs for notes catalog and note detail consumption (`GET /api/v1/notes/`, `GET /api/v1/notes/{slug}/`).

#### Frontend Tasks
- [ ] Build `bookmarks` and `notes` feature modules (`src/features/bookmarks/`, `src/features/notes/`).
- [ ] Build interactive MCQ Practice Runner component with instant answer checking, distractor highlights, and explanation accordion.
- [ ] Build `BookmarksPage` with filtering by tag/type and optimistic bookmark toggle buttons.
- [ ] Build `NotesCatalogPage` and `NoteDetailPage` featuring Markdown rendering and PDF download CTAs.
- [ ] Implement `useBookmarkStore` Zustand store for optimistic UI bookmark updates.

#### Database Tasks
- [ ] Apply database migrations for `notes` and `bookmarks` tables.
- [ ] Add unique constraint `uq_bookmarks_user_target` preventing duplicate bookmark entries per student.
- [ ] Create partial index `idx_bookmarks_user_type` optimizing saved item queries.

#### Testing Tasks
- [ ] Write backend API tests verifying practice question queries return items without leaking correct answer flags prior to student selection.
- [ ] Write integration tests for bookmark creation, duplication rejection, and deletion.
- [ ] Test Markdown sanitization on study note detail views.

#### Definition of Done
Students can engage in topic-wise MCQ practice with instant explanation feedback, save questions or notes to their personal bookmark drawer, and consume study notes.

---

### Phase 6: Mock Tests & Attempt Engine

#### Objective
Implement timed mock test blueprints, real-time assessment execution engine, server-side timer enforcement, negative marking scoring calculations, and detailed post-test result reviews.

#### Backend Tasks
- [ ] Create `apps/mock_tests` and `apps/attempts` Django apps.
- [ ] Implement `MockTest`, `MockTestQuestion`, `Attempt`, `AttemptAnswer`, and `AttemptResult` Django ORM models.
- [ ] Build test initialization API (`POST /api/v1/mock-tests/{id}/start/`) generating an active session with server expiry timestamp.
- [ ] Build progress auto-save API (`POST /api/v1/attempts/{id}/save-progress/`).
- [ ] Implement server-side scoring engine (`POST /api/v1/attempts/{id}/submit/`) executing positive mark additions, negative marking deductions, accuracy %, pass/fail evaluation, and aggregate snapshot generation in an atomic transaction.
- [ ] Enforce entitlement checks blocking non-premium users from accessing premium mock tests.

#### Frontend Tasks
- [ ] Build `mock-tests`, `attempt-engine`, and `attempt-results` feature modules (`src/features/mock-tests/`, `src/features/attempt-engine/`, `src/features/attempt-results/`).
- [ ] Build `MockTestsPage` and `MockTestDetailPage` with negative marking warnings and start confirmation modals.
- [ ] Build fullscreen `AttemptExecutionPage` featuring countdown timer, question palette navigator, option selector, auto-save buffer, and submit confirmation dialog.
- [ ] Build `AttemptResultPage` and `AttemptReviewPage` displaying total score, accuracy breakdown charts, and item-by-item solution reviews.
- [ ] Implement `useAttemptStore` Zustand store managing live test timer state and response buffers.

#### Database Tasks
- [ ] Apply database migrations for `mock_tests`, `mock_test_questions`, `attempts`, `attempt_answers`, and `attempt_results` tables.
- [ ] Enforce domain check constraints (`chk_attempts_status`, `chk_attempt_results_accuracy`, `chk_attempt_results_counts`).
- [ ] Create composite indexes (`idx_attempts_user_status_date`, `idx_attempt_answers_lookup`).

#### Testing Tasks
- [ ] Write unit tests for server-side scoring engine validating negative marking deduction math (e.g., +1.00 for correct, -0.25 for incorrect).
- [ ] Test auto-submission cutoff logic when test duration expires.
- [ ] Write integration tests verifying idempotent handling on duplicate test submission requests.

#### Definition of Done
Students can start timed mock test simulations, answer questions under real-time countdown constraints, submit tests for atomic server-side scoring (including negative marking), and inspect scorecard summaries and solution explanations.

---

### Phase 7: Analytics Dashboard & Weak Topics

#### Objective
Aggregate learner performance metrics over time, calculate topic mastery levels, render progress charts, and generate diagnostic weak-topic recommendations.

#### Backend Tasks
- [ ] Create `apps/analytics` Django app.
- [ ] Implement `StudentProgress` and `WeakTopic` Django ORM models.
- [ ] Build progress aggregation service executed asynchronously via Celery background tasks upon mock test or practice attempt completion.
- [ ] Build diagnostic engine identifying syllabus topics where student accuracy falls below target benchmarks (e.g. < 60%).
- [ ] Build REST API endpoints (`GET /api/v1/progress/summary/`, `GET /api/v1/progress/topics/`, `GET /api/v1/weak-topics/`).
- [ ] Enforce entitlement gate restricting advanced weak-topic analytics to Premium subscribers.

#### Frontend Tasks
- [ ] Build `dashboard`, `progress-analytics`, and `weak-topics` feature modules (`src/features/dashboard/`, `src/features/progress-analytics/`, `src/features/weak-topics/`).
- [ ] Build `DashboardPage` featuring student welcome header, target exam badge, quick stats, recent attempt list, and study CTAs.
- [ ] Build `ProgressPage` rendering Recharts visual graphs (Accuracy Trends over time, Subject Mastery bars).
- [ ] Build `WeakTopicsPage` displaying diagnostic deficit cards and targeted practice drill buttons.

#### Database Tasks
- [ ] Apply database migrations for `student_progress` and `weak_topics` tables.
- [ ] Add unique constraints (`uq_student_progress_user_topic`, `uq_weak_topics_user_topic`).
- [ ] Create partial indexes (`idx_student_progress_user`, `idx_weak_topics_user_deficit`) optimizing dashboard queries.

#### Testing Tasks
- [ ] Write unit tests for progress calculation algorithms verifying cumulative accuracy and total attempts logic.
- [ ] Write integration tests verifying weak-topic diagnostic triggers execute when student scores drop below accuracy thresholds.
- [ ] Test Celery background task execution for score aggregation.

#### Definition of Done
Student dashboards display real-time performance summaries, visual progress charts render historical accuracy trends, and weak syllabus topics are accurately identified with targeted revision CTAs.

---

### Phase 8: Payments & Subscriptions (Safepay Integration)

#### Objective
Implement commercial subscription plans, dynamic entitlement feature authorization, Safepay checkout integration, HMAC webhook processing, and automatic/manual subscription renewal lifecycles.

#### Backend Tasks
- [ ] Create `apps/subscriptions` and `apps/payments` Django apps.
- [ ] Implement `SubscriptionPlan`, `Entitlement`, `PlanEntitlement`, `Subscription`, `PaymentTransaction`, and `WebhookEventLog` Django ORM models.
- [ ] Implement `SafepayAdapter` managing Safepay REST API communications and HMAC-SHA256 signature verification routines.
- [ ] Build public Safepay webhook receiver API (`POST /api/v1/payments/webhooks/safepay/`) with HMAC check and idempotency token verification.
- [ ] Implement subscription state machine (`PENDING -> ACTIVE -> PAST_DUE -> CANCELED -> EXPIRED`) with a 7-day past-due grace period policy.
- [ ] Create `seed_subscription_plans` management command populating Free and Premium (Rs. 499 PKR/month) plans and entitlement bindings.
- [ ] Build checkout REST endpoints (`POST /api/v1/subscriptions/checkout/`, `GET /api/v1/subscriptions/me/`, `GET /api/v1/payments/history/`).

#### Frontend Tasks
- [ ] Build `subscriptions` and `payments` feature modules (`src/features/subscriptions/`, `src/features/payments/`).
- [ ] Build `SubscriptionsPage` featuring Free vs Premium comparison table, active subscription badge, auto-renew controls, and checkout CTA.
- [ ] Integrate Safepay checkout redirect flow and handle payment success/failure callback landings.
- [ ] Build `PaymentsHistoryPage` displaying payment transaction receipts and status pills.
- [ ] Implement `EntitlementGuard` router component protecting premium features (`access:premium_mock_tests`, `access:weak_topic_analytics`, `access:pdf_notes`).

#### Database Tasks
- [ ] Apply database migrations for `subscription_plans`, `entitlements`, `plan_entitlements`, `subscriptions`, `payment_transactions`, and `webhook_event_logs` tables.
- [ ] Create unique index `uq_webhook_event_token` on Safepay event token enforcing strict idempotency.
- [ ] Execute `seed_subscription_plans` command to seed initial commercial plans and entitlement mappings.

#### Testing Tasks
- [ ] Write unit tests for Safepay HMAC signature validation ensuring invalid signatures are rejected with HTTP 401.
- [ ] Test webhook idempotency guaranteeing duplicate event tokens return HTTP 200 without duplicate state updates.
- [ ] Test subscription state machine verifying entitlements remain active during 7-day grace period and deactivate upon expiration.
- [ ] Execute complete end-to-end checkout and renewal testing in Safepay Sandbox environment.

#### Definition of Done
Students can purchase Premium subscriptions via Safepay checkout, payment webhooks are processed safely with HMAC verification and idempotency controls, entitlements dynamically regulate feature access, and subscription renewals update billing states cleanly.

---

### Phase 9: Operator Admin Panel & System Operations

#### Objective
Implement comprehensive administrative management tools for user management, role assignments, content review queues, student question report resolutions, system audit logging, and platform metrics.

#### Backend Tasks
- [ ] Build administrative REST endpoints in `accounts`, `questions`, `payments`, and `common` apps.
- [ ] Build user administration APIs (`GET /api/v1/admin/users/`, `PATCH /api/v1/admin/users/{id}/status/`).
- [ ] Build audit log inspection API (`GET /api/v1/admin/audit-logs/`).
- [ ] Build RBAC role assignment API (`POST /api/v1/admin/rbac/user-roles/`).
- [ ] Configure custom Django Admin interfaces for all models with search indexing, filters, and inline sub-editors.

#### Frontend Tasks
- [ ] Build `admin` feature module (`src/features/admin/`).
- [ ] Build `AdminLayout` featuring collapsible sidebar navigation, search bar, and user session badge.
- [ ] Build `AdminDashboardPage`, `AdminUsersPage`, `AdminQuestionsPage`, `AdminQuestionReportsPage`, `AdminAuditLogsPage`, and `AdminRbacPage`.
- [ ] Enforce `RoleGuard` restricting access to administrative views based on operator role (`CONTENT_EDITOR`, `SME`, `ADMIN`, `SUPERADMIN`).

#### Database Tasks
- [ ] Ensure database index support for admin search filters (`idx_users_active_staff`, `idx_audit_logs_actor_date`, `idx_question_reports_status`).

#### Testing Tasks
- [ ] Write integration tests verifying standard student accounts receive HTTP 403 Forbidden when attempting to access admin APIs.
- [ ] Test user suspension/activation workflow.
- [ ] Test question report resolution state transition and reviewer note recording.

#### Definition of Done
Platform administrators, content editors, and SMEs have secure operational interfaces to manage user accounts, review content, resolve student reports, assign RBAC roles, and inspect immutable system audit logs.

---

### Phase 10: Production Hardening & Launch Readiness

#### Objective
Finalize production containerization, multi-stage Docker builds, Nginx reverse proxy configuration, HTTPS/TLS termination, Gunicorn WSGI tuning, database backup automation, monitoring, and final end-to-end system verification.

#### Backend Tasks
- [ ] Finalize `config/settings/production.py` enforcing `DEBUG = False`, strict HTTPS headers, Sentry error logging, and SMTP email backend.
- [ ] Create production Gunicorn configuration (`gunicorn.conf.py`) and startup entrypoint scripts.
- [ ] Configure Redis production caching and Celery worker background process queues.

#### Frontend Tasks
- [ ] Configure production Vite bundle optimization (`npm run build`).
- [ ] Create Nginx web server container serving optimized static assets and proxying `/api/` requests to Gunicorn backend container.

#### Database Tasks
- [ ] Configure automated PostgreSQL production backup script (`pg_dump` cron schedule).
- [ ] Tune database connection pooling (`CONN_MAX_AGE`) and performance parameters for concurrent production loads.

#### Testing Tasks
- [ ] Execute complete End-to-End (E2E) smoke validation cycle: Student Registration → Practice Session → Timed Mock Test → Safepay Checkout → Premium Feature Authorization → Admin Audit Log Inspection.
- [ ] Perform security vulnerability audit verifying no secrets, unhandled exceptions, or CORS wildcards exist in production builds.
- [ ] Perform responsive design verification across Mobile, Tablet, and Desktop screen viewports.

#### Definition of Done
The full Prepora platform builds cleanly into production containers, serves securely over HTTPS, executes error-free E2E workflows, and possesses automated backup, caching, and error-monitoring mechanisms ready for public launch.

---

## 3. Estimated Git Branching Strategy

To maintain clean repository management and isolated feature development, all work will be executed in feature branches corresponding to the roadmap phases:

```text
main (Production Branch)
 └── develop (Staging / Integration Branch)
      ├── feature/project-initialization      (Phase 1)
      ├── feature/authentication              (Phase 2)
      ├── feature/exam-taxonomy               (Phase 3)
      ├── feature/question-bank               (Phase 4)
      ├── feature/practice-sessions           (Phase 5)
      ├── feature/mock-tests                  (Phase 6)
      ├── feature/analytics-dashboard         (Phase 7)
      ├── feature/payments-subscriptions      (Phase 8)
      ├── feature/admin-panel                 (Phase 9)
      └── feature/production-deployment       (Phase 10)
```

### Git Branch Inventory

1. `feature/project-initialization` — Phase 1: Django, React + Vite, PostgreSQL 16 & Docker Compose setup.
2. `feature/authentication` — Phase 2: JWT Auth, user registration, login, SimpleJWT rotation, RBAC models.
3. `feature/exam-taxonomy` — Phase 3: Exam tracks, exams, subjects, topics models, APIs, and cached catalog UI.
4. `feature/question-bank` — Phase 4: MCQ authoring, options, explanations, editorial workflow, versioning, reports.
5. `feature/practice-sessions` — Phase 5: Practice session runner, bookmarks engine, study notes Markdown views.
6. `feature/mock-tests` — Phase 6: Timed mock test templates, fullscreen test execution, server-side scoring.
7. `feature/analytics-dashboard` — Phase 7: Learner dashboard, progress trend charts, weak-topic diagnostics.
8. `feature/payments-subscriptions` — Phase 8: Safepay integration, checkout flow, HMAC webhooks, entitlement gating.
9. `feature/admin-panel` — Phase 9: Admin dashboard, user management, editorial review queue, audit log inspection.
10. `feature/production-deployment` — Phase 10: Production Docker builds, Nginx setup, Gunicorn tuning, security hardening.
