# Prepora

## Product Overview

Prepora is a production-ready online learning platform for students preparing for Pakistan Armed Forces initial tests and related competitive examinations. The platform will support structured test preparation across Army, Air Force, Navy, ASF, ISSB, Police, FPSC, PMA, and allied exam tracks through practice MCQs, mock tests, notes, analytics, and ranking, with lectures reserved for future phases.

### Product Vision

To become the most trusted digital preparation platform for defense and competitive exams in Pakistan by combining high-quality content, measurable progress tracking, and an engaging study experience.

### Product Objectives

- Help students prepare efficiently with exam-specific content and assessments.
- Provide measurable learning progress through analytics and performance insights.
- Enable competitive motivation through rankings and peer comparison.
- Support scalable content delivery across web and future mobile channels.
- Maintain strong security, reliability, and operational readiness from day one.

### Scope

In scope:

- MCQ practice by exam track, subject, topic, and difficulty.
- Timed mock tests and exam simulations.
- User progress tracking and analytics.
- Leaderboards and ranking comparisons.
- Free and premium access control.
- Subscription management and payment checkout.
- Admin tools for content, exam tracks, users, and reporting.

Out of scope for the initial release:

- Live tutoring marketplace.
- User-generated public forums.
- Full offline-first mobile functionality.
- AI-generated exam content without editorial review.

## Complete Software Requirements Specification (SRS)

### 1. Introduction

#### 1.1 Purpose

This SRS defines the product, functional behavior, quality attributes, operational needs, and delivery strategy for Prepora. It is intended for founders, product managers, designers, engineers, QA, DevOps, content teams, and security reviewers.

#### 1.2 Intended Audience

- Product leadership
- Engineering team
- QA and test engineers
- Content operations team
- DevOps and infrastructure team
- Security and compliance stakeholders

#### 1.3 Definitions

- MCQ: Multiple Choice Question
- Mock Test: Timed exam simulation modeled after a real test pattern
- Analytics: Performance metrics such as accuracy, speed, weak topics, and score trends
- Leaderboard: Ranked comparison of users or cohorts based on performance criteria
- Exam Track: A first-class exam preparation path such as Army, Air Force, Navy, ASF, ISSB, Police, FPSC, or PMA
- Exam hierarchy: Exam Track -> Exam -> Subject -> Topic -> Question

#### 1.4 Assumptions

- Users primarily access the platform via mobile web and desktop browsers.
- Content will be curated and validated by subject matter experts.
- MVP launch language is English only.
- Content language at launch is English only.
- Future internationalization, including possible Urdu support, may be added later if product priorities require it.

#### Subscription and Access Model

- User -> Subscription -> Entitlements -> Feature Access
- The system shall not rely on a hardcoded is_premium user flag.
- The subscription represents the user's subscription and access period.
- Entitlements represent the features or capabilities the user is allowed to access.
- Feature access is determined by evaluating the user's active subscription and associated entitlements.
- Payment status and subscription status are separate concepts.
- Entitlement status is a separate concept derived from subscription rules and entitlement policies.
- Feature access is the final authorization decision and is not itself a payment or subscription status.
- A successful payment does not automatically change subscription state without server-side verification and business-rule processing.
- A successful payment must not directly grant feature access without server-side verification and subscription or entitlement business-rule processing.

User
  ↓
Subscription
  ↓
Entitlements
  ↓
Feature Access

Example:
Active Premium Subscription
→ Premium Entitlements
→ Premium Mock Tests / Premium Notes / Premium Analytics
→ Access Granted

Expired, canceled, or otherwise inactive subscription
→ Entitlements are no longer active according to the subscription rules
→ Premium Feature Access is denied

#### Subscription and Payment Status Model

- Payment status states are internal normalized states: PENDING, SUCCEEDED, FAILED, CANCELED, REFUNDED, and PARTIALLY_REFUNDED.
- Subscription status states are internal normalized states: PENDING, ACTIVE, PAST_DUE, CANCELED, EXPIRED, and PAUSED.
- Entitlement status is evaluated independently from raw payment events and is activated or deactivated based on subscription rules.
- Additional states such as TRIALING may be added only if a trial feature is introduced later.

#### Renewal Model

- The MVP must support automatic recurring monthly renewal through Safepay recurring billing.
- The MVP must also support manual renewal through a new Safepay checkout or payment flow.
- The architecture must support both automatic and manual renewal without redesigning the core subscription system.
- If a user cancels future renewal, the current paid subscription remains active until current_period_end_date.
- After the paid period ends, the subscription becomes EXPIRED unless renewed.
- Users can manually renew through a new Safepay checkout flow.

#### MVP Business Assumptions

- Safepay is the initial payment provider for the MVP.
- Prepora payment architecture remains provider-agnostic behind a provider adapter/service boundary.
- Initial plans are Free and Premium.
- Premium subscription duration is monthly.
- Renewal is monthly recurring through Safepay recurring billing.
- Pricing is configurable plan data with amount and currency fields; final pricing is not hardcoded yet.
- Initial launch currency is PKR.
- Safepay supports monthly subscriptions, automatic recurring billing, checkout/payment pages, webhooks, sandbox testing, SDKs, multiple subscription plans, free trials, security features, no monthly platform fee, and payment-based pricing.
- Free trials remain configurable and may be enabled later if product policy allows.
- Safepay has no monthly platform fee based on confirmed provider information, and charges apply when payments are received.
- Users can cancel future renewal, and premium access continues until the end of the already-paid subscription period.
- Refunds are handled manually by an administrator or payment provider until a formal refund policy is finalized, and the final refund rules must be decided before public launch.
- The application must not store raw card details.
- Payment processing is handled by Safepay, with verified and idempotent webhooks updating subscription status.
- Payment-provider-specific behavior is isolated behind the Prepora payment adapter so future providers can be integrated without rewriting core subscription and entitlement logic.

#### Safepay Event Types

- Payment events: payment.succeeded, payment.failed, payment.refunded, authorization.succeeded, authorization.reversed, void.succeeded
- Subscription events: subscription.created, subscription.canceled, subscription.ended, subscription.paused, subscription.resumed, subscription.payment.succeeded, subscription.payment.failed

#### Safepay Webhook Requirements

- The webhook endpoint must be publicly accessible over HTTPS.
- Production webhook endpoints must use TLS 1.2 or TLS 1.3.
- The endpoint must accept HTTP POST requests containing JSON payloads.
- The HMAC signature of every incoming Safepay webhook must be verified before the event is trusted.
- Invalid HMAC signatures must be rejected and must not be acknowledged as successfully processed events.
- Valid webhook events must be persisted in the database.
- The endpoint should acknowledge valid events quickly with a successful HTTP response.
- Long-running business logic should not run before acknowledgement.
- Business processing should happen asynchronously after the event has been safely persisted and acknowledged.
- Webhook processing must be idempotent.
- The Safepay event token and appropriate identifiers must be used as idempotency keys to prevent duplicate processing.
- Retry deliveries and duplicate deliveries must be handled safely.
- The webhook processor must support webhook version 2.0.0.
- Unknown future event types or event codes must not crash the webhook processor.
- Record useful webhook audit information such as event token, event type, version, timestamps, processing status, and delivery attempts where available.
- Use separate Sandbox and Production credentials and HMAC keys.
- Test webhook behavior in Safepay Sandbox before production deployment.
- Safepay webhook events must be mapped by the Safepay adapter into Prepora internal payment, subscription, entitlement, and audit states.

#### MVP Payment Flow

1. Student selects the Premium plan.
2. Prepora backend creates a payment or checkout session through the Safepay integration.
3. Student completes payment through Safepay.
4. Safepay sends a payment result or webhook to Prepora.
5. Prepora verifies the webhook securely.
6. Webhook processing is idempotent to prevent duplicate payment processing.
7. Prepora records the payment transaction.
8. Prepora activates or updates the student's subscription.
9. Prepora grants the appropriate Premium entitlements.
10. Premium access is controlled by the active subscription and entitlement rules.

#### 1.5 Constraints

- Must serve a large number of concurrent learners during exam seasons.
- Must protect exam content from unauthorized exposure.
- Must remain usable on low-end devices and slower network connections.
- Must support future expansion to partner channels and additional client platforms.

### 2. Overall Description

#### 2.1 Product Perspective

Prepora is a cloud-hosted educational SaaS platform with a content management layer, learner experience layer, analytics layer, subscription and payment layer, and administration layer. The payment layer uses Safepay initially through a provider adapter boundary.

#### 2.2 User Classes

- Guest visitor
- Registered student
- Premium student
- Content editor
- Subject matter expert
- Support agent
- Platform administrator
- Super administrator

#### 2.3 Operating Environment

- Modern web browsers on mobile and desktop
- Cloud hosting with CDN, managed database, and object storage
- Analytics and monitoring services

#### 2.4 User Needs

- Structured preparation by exam type and subject
- Clear progress and weak-area visibility
- Reliable test timing and scoring
- Competitive ranking and peer benchmarking
- Clear free and premium access boundaries
- Reliable payment checkout and subscription activation through Safepay

#### 2.5 Product Principles

- Content should be discoverable in under a few taps.
- Tests must feel trustworthy, timed, and fair.
- Progress indicators should be meaningful, not cosmetic.
- Administrative workflows should minimize manual operations.
- Premium access should be controlled through subscription and entitlement rules rather than hardcoded user flags.

## Functional Requirements

### Learner Experience

FR-1 The system shall allow users to register, sign in, reset passwords, and manage profiles.

FR-2 The system shall allow users to browse exam tracks, subjects, and topics.

FR-3 The system shall allow users to practice MCQs by exam track, subject, topic, difficulty, and custom filters.

FR-4 The system shall allow users to attempt timed mock tests with configurable question counts and time limits.

FR-5 The system shall provide instant answer review with explanations where available.

FR-6 The system shall store attempt history, scores, time spent, and accuracy metrics.

FR-7 The system shall display personalized progress dashboards and analytics.

FR-8 The system shall support free and premium access control through subscription and entitlement rules.

FR-9 The system shall support subscription management, Safepay checkout, automatic recurring billing, manual subscription renewal, payment verification, transaction records, webhook processing, HMAC verification, idempotent webhook processing, subscription lifecycle tracking, and entitlement management through a provider-agnostic payment service using Safepay initially.

FR-10 The system shall support both automatic recurring monthly renewal and manual renewal through a new checkout or payment flow when a subscription expires, is canceled, is paused, is past due, or automatic renewal is disabled.

FR-11 The system shall keep payment status, subscription status, entitlement status, and feature access decisions as separate concepts in the domain model.

FR-12 The system shall map Safepay provider event types and provider-specific statuses into Prepora internal payment and subscription states through the Safepay adapter and keep Safepay-specific logic isolated behind the payment provider adapter or service boundary.

FR-13 The system shall support bookmarks, favorites, or saved questions for revision.

FR-14 The system shall support notifications or reminders for test schedules, updates, and recommended study actions.

### Content and Assessment

FR-15 The system shall allow admins to create and manage exam tracks, exams, subjects, topics, questions, answers, explanations, notes, and lecture metadata for future phases.

FR-16 The system shall support tagging content by exam track, subject, difficulty, year, and topic.

FR-17 The system shall support question randomization and test variants.

FR-18 The system shall support publishing workflows for content review and approval.

FR-19 The system shall support correction, versioning, and content audit history.

FR-20 The system shall allow students to report questions for issues such as incorrect answers, incorrect explanations, typographical errors, ambiguous questions, outdated information, or technical issues.

FR-21 The system shall allow content editors and subject matter experts to review, resolve, and track question reports.

### Administration and Operations

FR-22 The system shall provide role-based dashboards for admins, editors, and support staff.

FR-23 The system shall allow administrators to manage users, suspensions, reports, subscription states, and support actions.

FR-24 The system shall provide reporting on usage, completion, engagement, and content performance.

FR-25 The system shall log key actions for security and operational auditing.

FR-26 The system shall process Safepay webhook version 2.0.0 events, safely handle retries and duplicate deliveries, persist valid webhook events, and use the Safepay event token as a unique idempotency key.

FR-27 The system shall preserve provider fields needed for reconciliation, including Safepay event token, Safepay tracker, Safepay subscription ID, Safepay plan ID, Safepay transaction ID, payment amount, currency, payment status, subscription status, current billing cycle, current period start date, current period end date, last paid date, and provider metadata.

FR-28 The system shall support Safepay sandbox testing for checkout, webhook, and renewal workflows before production launch.

## Non Functional Requirements

### Performance

- Core pages should load quickly on mobile networks.
- Mock test submission and scoring should complete with minimal delay.
- The system should remain responsive during exam-season traffic spikes.
- Subscription and payment workflows should complete reliably and support idempotent webhook handling.

### Availability and Reliability

- Target high availability for the learner-facing platform.
- Support graceful degradation for non-critical features during partial outages.
- Maintain backup and disaster recovery procedures.

### Usability

- Interface should be simple enough for students with mixed digital literacy.
- Key actions should be reachable with minimal navigation depth.
- Content consumption and test-taking should work well on small screens.

### Security

- Enforce strong authentication and authorization.
- Protect user data, exam content, and administrative functions.
- Log sensitive operations and security-relevant events.

### Maintainability

- Architecture should separate learner, admin, content, and analytics concerns.
- Codebase should be modular and testable.
- Operational tooling should support safe deployments and rollbacks.

### Compatibility

- Support major modern browsers.
- Ensure good behavior on common Android and iOS browser environments.

### Accessibility

- Support keyboard navigation and readable color contrast.
- Provide accessible form controls and clear focus states.
- Ensure test experiences do not rely solely on color or motion.

## User Roles

### Guest Visitor

- Browse public marketing pages.
- Preview limited exam offerings or samples.
- Register or sign in.

### Registered Student

- Practice MCQs and mock tests.
- View available learning content and notes.
- Track progress and rankings.
- Save questions and review history.

### Premium Student

- Access premium content and premium learning paths.
- Receive enhanced analytics or exclusive mock exams.

### Content Editor

- Create and maintain questions and notes, and prepare lecture metadata for future phases.
- Submit content for review.

### Subject Matter Expert

- Validate accuracy of exam content.
- Review explanations and topic coverage.

### Support Agent

- Assist users with account or content access issues.
- View limited user support context.

### Platform Administrator

- Manage users, roles, content, reports, and platform settings.
- Approve publishing workflows.

### Super Administrator

- Manage all system settings, security policies, and critical platform controls.

## User Stories

- As a student, I want to choose my target exam so that I can study the right syllabus.
- As a student, I want to solve MCQs by topic so that I can strengthen weak areas.
- As a student, I want timed mock tests so that I can practice under real exam pressure.
- As a student, I want instant scoring and explanations so that I can learn from mistakes quickly.
- As a student, I want to see progress trends so that I know whether I am improving.
- As a student, I want to compare my performance with others so that I stay motivated.
- As a student, I want to read notes so that I can revise important concepts efficiently.
- As an admin, I want to publish new questions safely so that content quality remains high.
- As an admin, I want to see usage analytics so that I can understand what students need most.
- As a support agent, I want to resolve account issues efficiently so that users are not blocked from study.

## Feature List

### Student Features

- Account registration and login
- Exam track selection and learning paths
- MCQ practice mode
- Mock test mode
- Answer explanations
- Progress dashboard
- Analytics and weak-topic insights
- Leaderboards and rankings, notes library
- Favorites and revisit lists
- Subscription management and payment history
- Automatic and manual subscription renewal
- Question reporting and issue tracking

### Content Features

- Question authoring and editing
- Exam track, subject, and topic taxonomy
- Explanations and references
- Publish and review workflow
- Question report review and resolution

### Platform Features

- Role-based access control
- Admin dashboard
- User management
- Audit logs
- Reports and analytics exports
- Notifications and announcements
- Subscription and entitlement management
- Payment verification and webhook processing
- Safepay webhook v2.0.0 processing and idempotency controls
- Safepay adapter integration behind the payment service boundary

## MVP Features

The MVP should focus on validating core learning value and retention.

- Student registration and login
- Exam track selection
- MCQ practice with scoring
- Timed mock tests
- Basic explanations
- Progress tracking dashboard
- Core content management with review, approval, publishing, versioning, and question-report workflows
- Basic analytics for user activity and performance
- Premium subscriptions
- Monthly Premium subscriptions
- Free and premium access control
- Subscription management
- Automatic and manual renewal flows
- Subscription cancellation
- Subscription expiration handling
- Failed renewal handling
- Payment checkout
- Payment webhook processing
- HMAC webhook verification
- Idempotent webhook processing
- Basic subscription and payment history
- Premium entitlement management
- Question reporting
- Basic notes

## Final Business Decisions

### Pricing

Free Plan:
- Price: Rs.0 PKR/month
- Includes limited MCQ practice, sample mock tests, basic analytics, and limited notes.

Premium Plan:
- Price: Rs.499 PKR/month
- Monthly recurring subscription.
- Includes unlimited MCQs, premium mock tests, advanced analytics, and premium notes.

Currency:
- PKR


### Refund Policy

Refunds are manually reviewed.

Refund eligibility:
- Payment deducted but premium access not activated.
- Duplicate payments.
- Verified technical billing failures.

Refund window:
- 7 days after payment.

Non-refundable:
- User changed mind.
- User consumed premium content.
- Accidental purchase.


### Free Trial Policy

Free trials are disabled for MVP.

The platform will use a permanent free plan with limited features.

Free trials may be introduced later after product validation.


### Past Due Grace Period

Default grace period:
- 7 days.

During grace period:
- Premium access remains active.
- Payment retries may occur.

After grace period:
- Subscription becomes EXPIRED if payment is not recovered.

Content Governance Policy

Every question must have:
- Creator
- Reviewer
- Approval status
- Last reviewed date
- Source/reference
- Version history

## Future Features

- AI-assisted study recommendations
- Adaptive testing based on performance
- Full mobile apps for Android and iOS as a much later future initiative
- Offline saved study packs
- Referral and affiliate programs
- Discussion forums and peer study groups
- Personalized revision scheduler
- Advanced leaderboards by city, batch, or institution
- Certificate or readiness scorecards
- Future internationalization and regional language support
- Partnerships with academies and institutions

## Product Roadmap

### Phase 1: Foundation

- Define taxonomy for exam tracks, subjects, topics, and difficulty.
- Design learner journey and content model.
- Build core test-taking and content consumption experience.

### Phase 2: Learning Core

- Launch MCQ practice and mock tests.
- Add explanations and notes.
- Introduce basic progress tracking.

### Phase 3: Engagement

- Improve analytics and study recommendations.
- Introduce notifications and reminders.

### Phase 4: Web Platform Scale and Monetization

- Optimize the web platform for growing user traffic and exam-season demand.
- Improve scalability, performance, caching, database efficiency, and operational reliability.
- Introduce advanced analytics and cohort insights.
- Optimize monetization, billing, conversion, and entitlement management.
- Introduce additional subscription plans if validated by user demand.
- Improve payment reliability and subscription renewal flows.
- Improve Premium conversion, retention, and subscription renewal rates.
- Continue expanding and improving the web platform based on user feedback and usage data.

### Phase 5: Ecosystem Expansion

- Add adaptive learning and AI-assisted guidance.
- Launch partner and institutional features.
- Expand into broader competitive exam coverage.

## Milestones

- Milestone 1: Product scope and information architecture approved
- Milestone 2: UX wireframes and learning journey finalized
- Milestone 3: Content model and admin workflows defined
- Milestone 4: MVP development completed
- Milestone 5: Internal QA and content verification completed
- Milestone 6: Beta release to a pilot student group
- Milestone 7: Production launch
- Milestone 8: Post-launch analytics review and iteration

## Development Timeline

The following is a realistic high-level timeline for a production-quality MVP.

### Weeks 1-2

- Finalize product requirements and architecture.
- Design system structure and content taxonomy.
- Define content governance and admin workflows.

### Weeks 3-6

- Build learner registration, login, and profile management.
- Implement exam browsing and practice flows.
- Set up content management foundations.

### Weeks 7-10

- Implement mock tests, scoring, explanations, analytics basics, Safepay checkout integration, automatic and manual renewal flows, subscription activation, payment status updates, and webhook-driven subscription updates.
- Add notes consumption flows.
- Build admin tools for content and user management.

### Weeks 11-12

- Perform QA, performance tuning, security review, Safepay payment/subscription verification, and sandbox-based webhook and renewal validation.
- Conduct content validation and pilot testing.
- Validate refund-policy readiness before launch.
- Prepare production deployment and launch readiness.

### Post-Launch

- Monitor usage, retention, and content effectiveness.
- Release iterative improvements every 2-4 weeks.

## Risks

- Content accuracy risk: incorrect questions or explanations can damage trust.
- Scalability risk: exam-season traffic may exceed planned capacity.
- Engagement risk: users may churn if progress feedback is weak.
- Security risk: exam content or accounts may be targeted for abuse.
- Operational risk: content publishing workflows may create bottlenecks.
- Product-market risk: students may prefer offline or low-cost alternatives.
- Compliance risk: handling user data without clear policies can create exposure.

## Recommended Technology Stack

The stack should optimize for scalability, maintainability, fast development, and strong operational control.

### Frontend

- Modern component-based web application framework
- Responsive design system optimized for mobile-first learning
- Strong client-side state management for test workflows and analytics views

### Backend

- API-first backend architecture
- Modular services for auth, content, assessment, analytics, and notifications
- Background processing for scoring, reporting, and scheduled tasks

### Data Layer

- Relational database for users, content, attempts, and roles
- Separate records for subscriptions, payment transactions, webhook events, and entitlements
- Support one-to-many relationship from subscription records to payment transaction records
- Do not rely on a single payment record as proof of active Premium access
- Preserve Safepay fields where relevant: Safepay event token, Safepay tracker, Safepay subscription ID, Safepay plan ID, Safepay transaction ID, payment amount, currency, payment status, subscription status, current billing cycle, current period start date, current period end date, last paid date, and provider metadata
- Object storage for lecture media and attachments
- Caching layer for performance-sensitive reads

### Infrastructure

- Cloud hosting with autoscaling
- CDN for static assets and media delivery
- Observability stack with logs, metrics, and tracing

### Operational Tooling

- CI/CD pipelines
- Infrastructure as code
- Centralized secrets management
- Automated backups and environment segregation

### Stack Selection Guidance

- Choose technologies that the team can operate well for several years.
- Prioritize ecosystem maturity, hiring availability, and long-term maintainability.
- Avoid over-engineering early; introduce service decomposition only when scale demands it.

## Security Requirements

- Support secure authentication with strong password policies and optional MFA for admins.
- Enforce role-based authorization on all protected routes and APIs.
- Protect against common web threats such as injection, cross-site scripting, and CSRF.
- Encrypt sensitive data in transit and at rest.
- Store secrets securely and rotate them regularly.
- Log authentication, content changes, publishing actions, and privilege changes.
- Rate-limit sensitive endpoints such as login, password reset, and scoring submissions.
- Protect premium or restricted content from unauthorized access.
- Maintain audit trails for admin actions and content approvals.
- Prepora must not store raw card details or sensitive payment credentials.
- Payment credentials must be handled by Safepay.
- Webhook signatures and events must be verified according to Safepay's integration requirements.
- Safepay webhook endpoints must use HTTPS with TLS 1.2 or TLS 1.3.
- Webhook endpoints must accept HTTP POST JSON payloads and reject invalid HMAC signatures.
- Webhook acknowledgements must be fast, with business processing deferred after persistence where appropriate.
- Webhook processing must be idempotent.
- Payment status must not be trusted solely from frontend redirects or client-side data.
- The backend must verify payment status through a trusted server-side mechanism before activating Premium access.
- Payment and subscription actions must be auditable.
- Safepay-specific behavior must remain isolated behind a provider adapter/service boundary.

## Scalability Requirements

- Support growth from pilot users to large national-scale student cohorts.
- Scale read-heavy content delivery efficiently through caching and CDN usage.
- Handle burst traffic during admission and exam seasons.
- Separate media delivery from transactional API traffic.
- Design the database schema for large numbers of attempts, questions, and content revisions.
- Allow horizontal scaling of stateless application services.
- Ensure analytics and reporting workloads do not slow down the core learning experience.

## Deployment Strategy

### Environments

- Development
- QA or staging
- Production

### Release Approach

- Use staged deployments with pre-production validation.
- Run smoke checks and content sanity checks before production promotion.
- Support rollback procedures for failed releases.
- Separate feature rollout from infrastructure rollout when possible.

### Operational Controls

- Use versioned releases and change approval for production changes.
- Monitor application health, API latency, and error rates.
- Establish backup verification and disaster recovery drills.

## Maintenance Strategy

- Maintain a regular release cadence for fixes and enhancements.
- Review analytics to identify weak points in content, UX, and retention.
- Refresh exam content regularly to stay aligned with current patterns.
- Perform security reviews and dependency updates on a recurring schedule.
- Track technical debt explicitly and reserve capacity for refactoring.
- Monitor content quality through approvals, user feedback, and audit sampling.
- Use support tickets and user feedback to guide roadmap prioritization.

## Success Metrics

- Registration-to-active-user conversion rate
- Practice completion rate
- Mock test completion rate
- Weekly active users
- Content engagement per exam category
- Score improvement over time
- Retention across 7, 30, and 90 days
- Leaderboard participation rate
- Support ticket volume and resolution time
- Free-to-premium conversion rate
- Subscription renewal rate
- Payment checkout completion rate
- Payment webhook success rate
- Automatic renewal success rate
- Manual renewal success rate
- Safepay checkout success rate
- Safepay webhook verification success rate
- Subscription activation latency after payment confirmation

## Confirmed Product Decisions

- English-only MVP launch
- Payments and subscriptions are MVP features
- Free and premium access model
- Automatic and manual renewal are both supported in the MVP subscription model
- Question reporting is an MVP feature
- Exam Track is a first-class product entity
- Safepay is the initial MVP payment provider behind a provider-agnostic payment architecture
- Safepay commercial assumptions include no monthly platform fee based on confirmed provider information
- Safepay recurring billing is confirmed for the MVP
- Automatic monthly subscription renewal is supported
- Manual renewal through a new checkout is also supported
- Safepay webhooks are the authoritative asynchronous mechanism for payment and subscription lifecycle updates
- HMAC verification is required for Safepay webhook security
- Webhook processing must be idempotent and retry-safe
- Payment status, subscription status, and entitlement state are separate concepts
- Advanced AI, mobile, offline, forums, referrals, and institutional features remain future roadmap items

## Conclusion

Prepora should be built as a disciplined, content-driven learning platform with strong assessment workflows, measurable progress, and a scalable operating model. The MVP should prove learning value quickly, while the architecture and product design should leave room for national-scale growth, premium monetization, and future expansion into broader exam preparation markets.
