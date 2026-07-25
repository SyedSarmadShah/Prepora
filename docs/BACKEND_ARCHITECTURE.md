# Backend Architecture for Prepora

## 1. Overview

Prepora needs a scalable, modular backend that can support student learning flows, assessment execution, progress tracking, ranked leaderboards, media delivery, and admin operations. The recommended approach is a modular monolith first, with clear separation between HTTP layer, application services, data access, and external integrations.

The core architectural principles are:

- Keep the API layer thin.
- Put business logic in services.
- Keep persistence logic in repositories.
- Use PostgreSQL as the source of truth.
- Use Redis for caching, rate limiting, and async coordination.
- Use Cloudinary for media storage and delivery.
- Keep authentication and authorization explicit and centralized.

## 2. Recommended Architecture Style

### Modular Monolith

A modular monolith is the best starting point because it offers:

- Faster delivery than a distributed system.
- Easier onboarding for a small team.
- Clear boundaries that can later be extracted into services if needed.

### Layers

1. Presentation Layer
   - FastAPI routers and controllers
   - Request validation and response formatting

2. Application Layer
   - Services for auth, practice, mock tests, results, progress, subscriptions, notifications, certificates, and admin workflows

3. Data Access Layer
   - SQLAlchemy models and repositories
   - Query organization for content, attempts, analytics, and leaderboard data

4. Infrastructure Layer
   - PostgreSQL, Redis, Cloudinary, logging, background queues, email, and monitoring

## 3. Folder Structure

```text
app/
  main.py
  api/
    v1/
      controllers/
      routes/
      dependencies/
  core/
    config/
    security/
    logging/
    exceptions/
    middleware/
    constants/
  db/
    session/
    base/
    migrations/
  models/
  schemas/
  repositories/
  services/
  tasks/
  integrations/
    cloudinary/
    redis/
    email/
  cache/
  utils/
  tests/
```

### Folder Explanations

- app/main.py: application bootstrap, router registration, middleware setup, startup hooks
- app/api/: API entry points and versioned routes
- app/api/v1/controllers/: thin HTTP handlers
- app/api/v1/routes/: route registration and grouping
- app/api/v1/dependencies/: reusable dependencies such as auth, role checks, db session, pagination helpers
- app/core/: shared infrastructure and cross-cutting concerns
- app/db/: session and migration setup
- app/models/: SQLAlchemy entities
- app/schemas/: request/response validation models
- app/repositories/: data access layer
- app/services/: business logic orchestration
- app/tasks/: background jobs and async workflows
- app/integrations/: external clients for Cloudinary, Redis, email, and similar systems
- app/cache/: cache strategy helpers and TTL handling
- app/utils/: shared utility functions
- app/tests/: unit, integration, and API tests

## 4. Layered Architecture

### Controllers

Controllers should:

- receive HTTP requests
- parse request payloads
- call services
- return serialized responses

Controllers should not contain SQL queries, scoring logic, or permission logic.

### Services

Services should:

- enforce business rules
- coordinate repositories and integrations
- manage transactions
- trigger cache invalidation
- enqueue background tasks

Examples include:

- Auth service
- Practice service
- Mock test submission service
- Result generation service
- Progress aggregation service
- Subscription service
- Certificate service
- Notification service
- Leaderboard service

### Repositories

Repositories should:

- wrap SQLAlchemy query logic
- encapsulate persistence details
- return domain-friendly results

Repositories should not know about HTTP or UI concerns.

## 5. Repositories

Recommended repositories:

- user_repository
- subject_repository
- topic_repository
- question_repository
- option_repository
- mock_test_repository
- attempt_repository
- result_repository
- progress_repository
- bookmark_repository
- notification_repository
- subscription_repository
- payment_repository
- certificate_repository
- announcement_repository
- leaderboard_repository

Each repository should be responsible for a clear data boundary and should implement reusable query patterns for list, detail, create, update, delete, and aggregate operations.

## 6. Authentication Flow

### Registration

1. User submits name, email, password, and optional phone.
2. Server validates the payload.
3. Password is hashed.
4. A user record is created.
5. Optional onboarding or verification flow is queued.

### Login

1. User submits email and password.
2. Server verifies the password.
3. Access token and refresh token are issued.
4. User profile is returned.

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

- Students can access their own attempts, progress, bookmarks, and notifications.
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

- Pydantic schemas validate request payloads at the API boundary.
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

Use FastAPI dependency injection for:

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

- one FastAPI application
- one PostgreSQL database
- one Redis instance
- Cloudinary for media
- strong module boundaries from day one
- background job processing for non-blocking workflows

That gives a strong foundation for MVP delivery and future scale.
