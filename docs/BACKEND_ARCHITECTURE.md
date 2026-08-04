## 1. Backend Architecture Overview

The Prepora backend is implemented as a Clean Modular Monolith using Django 5.x and Django REST Framework. Each business domain lives in a dedicated Django app, with presentation, service, repository, and persistence concerns separated cleanly enough to keep the codebase maintainable without introducing unnecessary service sprawl.

The core architectural principles are:

- Keep DRF views thin.
- Put business rules in services.
- Keep ORM query logic in repositories.
- Use PostgreSQL as the source of truth.
- Use Redis for caching, rate limiting, and async coordination.
- Use Cloudinary for media storage and delivery.
- Keep authentication and authorization explicit and centralized.

## 2. Recommended Architecture Style

### Clean Modular Monolith

A modular monolith is the right starting point because it offers:

- Faster delivery than a distributed system.
- Easier onboarding for a small team.
- Clear boundaries that can later be extracted into services if needed.

### Layers

1. Presentation Layer
  - Django URL routing, DRF views and viewsets, serializers, and permission classes

2. Application Layer
  - Services for auth, exams, questions, notes, bookmarks, mock tests, attempts, analytics, subscriptions, payments, notifications, and admin workflows

3. Data Access Layer
  - Django ORM models and repositories
  - Query organization for content, attempts, analytics, and leaderboard data

4. Infrastructure Layer
  - PostgreSQL, Redis, Cloudinary, logging, background queues, email, and monitoring

## 3. Folder Structure

```text
backend/
├── manage.py
├── gunicorn.conf.py
├── Dockerfile
├── docker-compose.yml
├── docker-compose.prod.yml
├── .env.example
├── README.md
├── config/
│   ├── __init__.py
│   ├── asgi.py
│   ├── wsgi.py
│   ├── urls.py
│   ├── celery.py
│   └── settings/
│       ├── __init__.py
│       ├── base.py
│       ├── development.py
│       ├── production.py
│       └── testing.py
├── apps/
│   ├── common/
│   ├── accounts/
│   ├── exams/
│   ├── questions/
│   ├── notes/
│   ├── bookmarks/
│   ├── mock_tests/
│   ├── attempts/
│   ├── analytics/
│   ├── subscriptions/
│   ├── payments/
│   └── notifications/
└── tests/
```

### Folder Explanations

- backend/manage.py: Django management entry point
- backend/config/: project configuration, URL routing, ASGI/WSGI, and Celery bootstrap
- backend/config/settings/: environment-specific settings modules
- backend/apps/common/: shared base models, exceptions, pagination, renderers, and utilities
- backend/apps/accounts/: authentication, JWT sessions, profiles, RBAC roles, and permissions
- backend/apps/exams/: exam taxonomy and syllabus hierarchy
- backend/apps/questions/: question authoring, versioning, and governance
- backend/apps/notes/: Markdown and PDF study resources
- backend/apps/bookmarks/: saved revision items
- backend/apps/mock_tests/: mock test templates and sequencing
- backend/apps/attempts/: live attempt execution and scoring
- backend/apps/analytics/: student progress and weak-topic diagnostics
- backend/apps/subscriptions/: commercial plans and entitlement policies
- backend/apps/payments/: payment ledger and webhook integration
- backend/apps/notifications/: in-app notifications and announcements
- backend/tests/: integration and system-level test coverage

## 4. Layered Architecture

### Views

Views should:

- receive HTTP requests
- delegate validation to serializers
- call services
- return serialized responses

Views should not contain ORM query logic, scoring logic, or permission logic beyond DRF checks.

### Services

Services should:

- enforce business rules
- coordinate repositories and integrations
- manage transactions
- trigger cache invalidation
- enqueue background tasks

Examples include:

- Auth service
- Taxonomy service
- Question governance service
- Mock test service
- Attempt execution service
- Scoring engine service
- Analytics service
- Subscription service
- Payment service
- Notification service

### Repositories

Repositories should:

- wrap Django ORM query logic
- encapsulate persistence details
- return domain-friendly results

Repositories should not know about HTTP or UI concerns.

## 5. Django Apps Specification

The backend is organized into 12 domain apps plus 1 common shared utility app:

- accounts
- exams
- questions
- notes
- bookmarks
- mock_tests
- attempts
- analytics
- subscriptions
- payments
- notifications
- common

Each app should own its views, serializers, services, repositories, permissions, URLs, and tests, while relying on shared abstractions from `common` for repeated concerns such as pagination, error envelopes, and response rendering.

## 6. Authentication Flow

### Registration

1. User submits name, email, password, and optional phone.
2. Serializer validates the payload.
3. Password is hashed by Django.
4. A user record and related profile data are created.
5. Optional onboarding or verification flow is queued.

### Login

1. User submits email and password.
2. Authentication service verifies the credentials.
3. Access token and refresh token are issued using SimpleJWT.
4. User profile and role data are returned.

### Token Handling

- Access token is short-lived.
- Refresh token is long-lived and stored securely.
- Refresh token rotation is recommended.
- Invalid or expired tokens should be rejected and logged.

## 7. Authorization

Use role-based access control with explicit permissions.

### Roles

- Student
- Content Editor
- Subject Matter Expert
- Support Agent
- Platform Administrator
- Super Administrator

### Access Rules

- Students can access their own attempts, progress, bookmarks, notifications, and subscriptions.
- Editors can manage content but cannot alter platform-wide security settings.
- SMEs can review and approve content.
- Admins manage content, users, and platform operations.
- Super admins manage global configuration and security-sensitive actions.

## 8. Middleware

Recommended middleware includes:

- request ID middleware for tracing
- CORS middleware
- authentication middleware
- authorization middleware
- request logging middleware
- rate limiting middleware
- security headers middleware
- timing middleware for latency visibility

## 9. Logging

Logging should be structured and centralized.

### What to log

- auth events
- failed login attempts
- content publish actions
- mock test submission events
- payment and subscription events
- certificate issuance
- admin escalations
- unexpected exceptions

### Logging standards

- Use structured JSON logs.
- Include request ID, user ID when available, route, and latency.
- Do not log passwords or secrets.
- Keep audit logs separate from operational logs.

## 10. Validation

Validation should happen at multiple levels.

### API Validation

- DRF serializers validate request payloads at the API boundary.
- Common validations include required fields, field length, email format, enum values, and pagination parameters.

### Service Validation

- Enforce business rules such as allowed test submission windows and premium content access.

### Database Validation

- Use foreign keys, unique constraints, check constraints, and non-null constraints.

## 11. Exception Handling

Use centralized exception handling.

### Recommended exception categories

- AuthenticationError
- AuthorizationError
- ValidationError
- NotFoundError
- ConflictError
- ExternalServiceError
- UnexpectedError

### Expectations

- return consistent error responses
- avoid leaking stack traces to clients
- log the full error internally
- map known business failures to proper HTTP status codes

## 12. Caching

Use Redis for frequently accessed, relatively stable data.

### Good cache candidates

- exam and subject lists
- public catalog data
- dashboard summaries
- leaderboard snapshots
- announcement listings
- notification counts
- progress summary snapshots

### Strategy

- Prefer cache-aside patterns.
- Use short TTLs for highly dynamic data.
- Invalidate caches on write operations.
- Avoid caching sensitive and highly personalized data without careful design.

## 13. Background Tasks

Slow work should be offloaded to background jobs.

### Good candidates

- leaderboard recomputation
- progress aggregation
- notification delivery
- certificate generation
- report generation
- email dispatch
- webhook reconciliation
- media processing updates

## 14. File Upload

Cloudinary should be used for media assets.

### Upload handling expectations

- validate file type and size before upload
- store only asset references in PostgreSQL
- support thumbnails, lecture videos, PDFs, avatars, and certificates
- ensure upload permissions are role-based

## 15. Configuration Management

Configuration should be loaded from environment variables and validated at startup.

### Required configuration areas

- app environment
- database URL
- redis URL
- JWT secrets and TTLs
- cloudinary credentials
- email provider settings
- logging level
- allowed origins
- rate limit thresholds

## 16. Dependency Injection

Use explicit service construction and shared configuration access patterns rather than framework-specific hidden wiring. In Django, dependency boundaries are typically handled through constructors, utility factories, and request-scoped helpers in views and services.

This improves testability and keeps view code clean.

## 17. Environment Variables

Recommended environment variables include:

- DATABASE_URL
- REDIS_URL
- JWT_SECRET_KEY
- JWT_ACCESS_TOKEN_EXPIRE_MINUTES
- JWT_REFRESH_TOKEN_EXPIRE_DAYS
- CLOUDINARY_CLOUD_NAME
- CLOUDINARY_API_KEY
- CLOUDINARY_API_SECRET
- APP_ENV
- LOG_LEVEL
- ALLOWED_ORIGINS

## 18. Testing Strategy

### Unit Tests

- service validation logic
- repository behavior
- auth and permission rules
- helpers and utility functions

### Integration Tests

- PostgreSQL-backed repository tests
- Redis-backed cache behavior
- auth flow tests
- external integration adapter tests

### API Tests

- protected route access
- input validation
- error handling
- rate limiting
- mock test submission flow

## 19. API Versioning

Use versioned routes such as:

- /api/v1/...
- /api/v2/... later if breaking changes are required

Versioning keeps clients stable as the platform evolves.

## 20. Rate Limiting

Apply rate limiting for:

- login attempts
- password reset requests
- public search and browse endpoints
- mock test submission attempts
- content-heavy endpoints

Use Redis-backed counters and limit by IP and user identity where appropriate.

## 21. Why This Architecture Scales

This architecture is scalable because it separates concerns clearly:

- PostgreSQL handles durable relational data and transactional consistency.
- Redis handles fast reads, rate limiting, and temporary state.
- Background tasks move expensive work off the request path.
- Cloudinary handles media delivery efficiently.
- Repositories and services make the system maintainable as features grow.
- The modular monolith can later evolve into a distributed system if traffic and team size justify it.

## 22. Recommended Delivery Approach

Start with:

- one Django application boundary per domain app
- one PostgreSQL database
- one Redis instance
- Cloudinary for media
- strong module boundaries from day one
- background job processing for non-blocking workflows

That gives a strong foundation for MVP delivery and future scale.

## 11. Exception Handling

Use centralized exception handling.

### Recommended exception categories

- AuthenticationError
- AuthorizationError
- ValidationError
- NotFoundError
- ConflictError
- ExternalServiceError
- UnexpectedError

### Expectations

- return consistent error responses
- avoid leaking stack traces to clients
- log the full error internally
- map known business failures to proper HTTP status codes

## 12. Caching

Use Redis for frequently accessed, relatively stable data.

### Good cache candidates

- subject and topic lists
- public exam catalog data
- dashboard summaries
- leaderboard snapshots
- announcement listings
- notification counts
- progress summary snapshots

### Strategy

- Prefer cache-aside patterns.
- Use short TTLs for highly dynamic data.
- Invalidate caches on write operations.
- Avoid caching sensitive and highly personalized data without careful design.

## 13. Background Tasks

Slow work should be offloaded to background jobs.

### Good candidates

- leaderboard recomputation
- progress aggregation
- notification delivery
- certificate generation
- report generation
- email dispatch
- webhook reconciliation
- media processing updates

## 14. File Upload

Cloudinary should be used for media assets.

### Upload handling expectations

- validate file type and size before upload
- store only asset references in PostgreSQL
- support thumbnails, lecture videos, PDFs, avatars, and certificates
- ensure upload permissions are role-based

## 15. Configuration Management

Configuration should be loaded from environment variables and validated at startup.

### Required configuration areas

- app environment
- database URL
- redis URL
- jwt secrets and TTLs
- cloudinary credentials
- email provider settings
- logging level
- allowed origins
- rate limit thresholds

## 16. Dependency Injection

Use explicit dependency boundaries for:

- database session
- current user
- repository instances
- service instances
- cache client
- external integrations

This improves testability and keeps route code clean.

## 17. Environment Variables

Recommended environment variables include:

- DATABASE_URL
- REDIS_URL
- JWT_SECRET_KEY
- JWT_ACCESS_TOKEN_EXPIRE_MINUTES
- JWT_REFRESH_TOKEN_EXPIRE_DAYS
- CLOUDINARY_CLOUD_NAME
- CLOUDINARY_API_KEY
- CLOUDINARY_API_SECRET
- APP_ENV
- LOG_LEVEL
- ALLOWED_ORIGINS

## 18. Testing Strategy

### Unit Tests

- service validation logic
- repository behavior
- auth and permission rules
- helpers and utility functions

### Integration Tests

- PostgreSQL-backed repository tests
- Redis-backed cache behavior
- auth flow tests
- external integration adapter tests

### API Tests

- protected route access
- input validation
- error handling
- rate limiting
- mock test submission flow

## 19. API Versioning

Use versioned routes such as:

- /api/v1/...
- /api/v2/... later if breaking changes are required

Versioning keeps clients stable as the platform evolves.

## 20. Rate Limiting

Apply rate limiting for:

- login attempts
- password reset requests
- public search and browse endpoints
- mock test submission attempts
- content-heavy endpoints

Use Redis-backed counters and limit by IP and user identity where appropriate.

## 21. Why This Architecture Scales

This architecture is scalable because it separates concerns clearly:

- PostgreSQL handles durable relational data and transactional consistency.
- Redis handles fast reads, rate limiting, and temporary state.
- Background tasks move expensive work off the request path.
- Cloudinary handles media delivery efficiently.
- Repositories and services make the system maintainable as features grow.
- The modular monolith can later evolve into a distributed system if traffic and team size justify it.

## 22. Recommended Delivery Approach

Start with:

- one Django application boundary per domain app
- one PostgreSQL database
- one Redis instance
- Cloudinary for media
- strong module boundaries from day one
- background job processing for non-blocking workflows

That gives a strong foundation for MVP delivery and future scale.
