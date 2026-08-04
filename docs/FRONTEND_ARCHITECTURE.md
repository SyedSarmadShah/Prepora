# Prepora Frontend Architecture & Structure Blueprint

> **Document Status:** Single Source of Truth for Frontend Implementation
> **Target Stack:** React 19 | TypeScript | Vite | Tailwind CSS | React Router | TanStack Query v5 | Axios | React Hook Form | Zod | Zustand | Framer Motion | Lucide React | Recharts | React Hot Toast | Cloudinary Upload Widget | JWT Authentication
> **Backend Compatibility:** 100% aligned with Django REST Framework API design and the backend architecture defined in [BACKEND_STRUCTURE.md](docs/BACKEND_STRUCTURE.md) and [API_DESIGN.md](docs/API_DESIGN.md).

---

## Table of Contents
1. [Frontend Architecture Overview](#1-frontend-architecture-overview)
2. [Complete Folder Structure](#2-complete-folder-structure)
3. [Feature Modules](#3-feature-modules)
4. [Component Architecture](#4-component-architecture)
5. [Routing Structure](#5-routing-structure)
6. [Authentication Flow](#6-authentication-flow)
7. [State Management](#7-state-management)
8. [API Layer](#8-api-layer)
9. [Form Validation](#9-form-validation)
10. [UI Layouts](#10-ui-layouts)
11. [Responsive Design Strategy](#11-responsive-design-strategy)
12. [Performance Optimization](#12-performance-optimization)
13. [Security](#13-security)
14. [Error Handling](#14-error-handling)
15. [Testing Strategy](#15-testing-strategy)
16. [Development Guidelines](#16-development-guidelines)
17. [Future Scalability](#17-future-scalability)
18. [Verification & Architectural Compliance](#18-verification--architectural-compliance)

---

## 1. Frontend Architecture Overview

The Prepora frontend architecture is designed for fast initial render times, accessible user experiences, and seamless real-time test execution. It is built as a feature-driven React 19 application powered by Vite, with domain logic organized into reusable feature modules rather than framework-specific page conventions.

```
+-----------------------------------------------------------------------------------+
|                                  USER INTERFACE                                   |
|          (React 19 Components + Tailwind CSS + Framer Motion + Icons)            |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                                ROUTING & LAYOUTS                                  |
|            (React Router + GuestLayout / StudentLayout / AdminLayout)            |
+-----------------------------------------------------------------------------------+
                 |                                                 |
                 v                                                 v
+---------------------------------+               +---------------------------------+
|          SERVER STATE           |               |          CLIENT STATE           |
|  (TanStack Query v5 + Axios)    |               |        (Zustand Stores)         |
+---------------------------------+               +---------------------------------+
                 |                                                 |
                 v                                                 v
+-----------------------------------------------------------------------------------+
|                                BACKEND API LAYER                                  |
|                (Django REST Framework `/api/v1/` + JWT Authentication)          |
+-----------------------------------------------------------------------------------+
```

### Architectural Principles

1. **Feature-First Architecture (`src/features/`)**:
   - Code is grouped by business capabilities such as `auth`, `mock-tests`, `attempt-engine`, `subscriptions`, and `admin`.
   - Each feature module owns its components, hooks, services, types, validation schemas, and state definitions.

2. **Component-Driven Development**:
   - UI elements are built from reusable primitives in `src/components/ui/` and domain-specific feature components in `src/features/*/components/`.
   - Presentation components remain decoupled from data-fetching side effects.

3. **Separation of Concerns**:
   - **Views** focus on rendering and user interactions.
   - **Custom Hooks** encapsulate UI logic, query states, and event handlers.
   - **Services** manage raw API calls, headers, and endpoint paths.
   - **Stores** maintain strictly client-only persistent or ephemeral UI state.

4. **Scalable Folder Organization**:
   - Clear separation between global infrastructure (`src/app/`, `src/providers/`, `src/services/`) and domain features (`src/features/`).

5. **Maintainability & Type Safety**:
   - Strict TypeScript contracts align with backend DTOs and domain models.
   - Zod validates forms and request payloads at the edge.

6. **Performance & Low Latency**:
   - Optimistic updates for non-destructive actions.
   - Local state buffering for test execution and auto-save workflows.

7. **Security-in-Depth**:
   - Route protection uses role guards and entitlement guards.
   - JWT handling is centralized in the API client and auth store.

---

## 2. Complete Folder Structure

```text
src/
├── app/
│   ├── App.tsx
│   ├── main.tsx
│   └── index.css
├── assets/
│   ├── icons/
│   ├── images/
│   └── logos/
├── components/
│   ├── ui/
│   ├── shared/
│   └── feedback/
├── constants/
│   ├── api.constants.ts
│   ├── routes.constants.ts
│   ├── rbac.constants.ts
│   └── storage.constants.ts
├── contexts/
│   ├── AuthContext.tsx
│   └── ThemeContext.tsx
├── features/
│   ├── admin/
│   ├── attempt-engine/
│   ├── attempt-results/
│   ├── auth/
│   ├── bookmarks/
│   ├── dashboard/
│   ├── exam-tracks/
│   ├── mock-tests/
│   ├── notes/
│   ├── notifications/
│   ├── payments/
│   ├── profile/
│   ├── progress-analytics/
│   ├── question-reports/
│   ├── questions/
│   ├── settings/
│   ├── subjects/
│   ├── subscriptions/
│   ├── topics/
│   └── weak-topics/
├── hooks/
├── layouts/
├── pages/
├── providers/
├── routes/
├── services/
├── store/
├── styles/
├── types/
└── utils/
```

### Folder Explanation

- `src/app/`: React entry point, app bootstrap, and global styles.
- `src/assets/`: static assets and branding resources.
- `src/components/ui/`: reusable design system primitives.
- `src/components/shared/`: headers, footers, navigation, and cross-cutting reusable UI.
- `src/components/feedback/`: loaders, banners, and error boundaries.
- `src/features/`: domain-specific modules for the product surface.
- `src/layouts/`: layout wrappers used by routed views.
- `src/pages/`: top-level route views.
- `src/providers/`: query, toast, and router providers.
- `src/routes/`: route definitions and guard composition.
- `src/services/`: Axios client and storage helpers.
- `src/store/`: Zustand client stores.
- `src/styles/`: CSS and theme configuration.
- `src/types/`: shared TypeScript types.
- `src/utils/`: pure helper functions.

---

## 3. Feature Modules

Every feature module follows a standard architecture pattern:

```text
src/features/<feature-name>/
├── components/
├── hooks/
├── services/
├── types/
├── validation/
├── routes/
└── store/
```

Below is the detailed breakdown for the core feature modules:

### 3.1 Authentication (`src/features/auth/`)
- Pages: `LoginPage.tsx`, `RegisterPage.tsx`, `ForgotPasswordPage.tsx`, `ResetPasswordPage.tsx`
- Hooks: `useLogin.ts`, `useRegister.ts`, `useLogout.ts`, `useForgotPassword.ts`, `useResetPassword.ts`, `useCurrentUser.ts`
- Services: `authService.ts`
- Validation: `auth.schema.ts`
- State: Integrated with global auth store

### 3.2 Dashboard (`src/features/dashboard/`)
- Pages: `DashboardPage.tsx`
- Hooks: `useDashboardData.ts`
- Services: `dashboardService.ts`
- State: TanStack Query

### 3.3 Exam Tracks (`src/features/exam-tracks/`)
- Pages: `ExamTracksPage.tsx`, `ExamDetailPage.tsx`
- Hooks: `useExamTracks.ts`, `useExamTrackDetail.ts`, `useExams.ts`
- Services: `examTrackService.ts`
- Validation: `examTrack.schema.ts`

### 3.4 Subjects (`src/features/subjects/`)
- Pages: `SubjectsPage.tsx`
- Hooks: `useSubjects.ts`, `useSubjectDetail.ts`
- Services: `subjectService.ts`

### 3.5 Topics (`src/features/topics/`)
- Pages: `TopicsPage.tsx`
- Hooks: `useTopics.ts`
- Services: `topicService.ts`

### 3.6 Questions (`src/features/questions/`)
- Pages: `AdminQuestionsPage.tsx`, `AdminQuestionEditPage.tsx`
- Hooks: `useQuestions.ts`, `useQuestionDetail.ts`, `useCreateQuestion.ts`, `usePublishQuestion.ts`
- Services: `questionService.ts`

### 3.7 Question Reports (`src/features/question-reports/`)
- Pages: `AdminQuestionReportsPage.tsx`
- Hooks: `useSubmitReport.ts`, `useQuestionReports.ts`
- Services: `questionReportService.ts`

### 3.8 Bookmarks (`src/features/bookmarks/`)
- Pages: `BookmarksPage.tsx`
- Hooks: `useBookmarks.ts`, `useAddBookmark.ts`, `useRemoveBookmark.ts`
- Services: `bookmarkService.ts`

### 3.9 Mock Tests (`src/features/mock-tests/`)
- Pages: `MockTestsPage.tsx`, `MockTestDetailPage.tsx`
- Hooks: `useMockTests.ts`, `useMockTestDetail.ts`
- Services: `mockTestService.ts`

### 3.10 Attempt Engine (`src/features/attempt-engine/`)
- Pages: `AttemptExecutionPage.tsx`
- Hooks: `useStartAttempt.ts`, `useAutoSaveProgress.ts`, `useSubmitAttempt.ts`, `useTestTimer.ts`
- Services: `attemptService.ts`

### 3.11 Attempt Results (`src/features/attempt-results/`)
- Pages: `AttemptResultPage.tsx`, `AttemptReviewPage.tsx`
- Hooks: `useAttemptResult.ts`, `useAttemptReview.ts`
- Services: `attemptResultService.ts`

### 3.12 Progress Analytics (`src/features/progress-analytics/`)
- Pages: `ProgressPage.tsx`
- Hooks: `useProgressSummary.ts`, `useTopicProgress.ts`
- Services: `progressService.ts`

### 3.13 Weak Topics (`src/features/weak-topics/`)
- Pages: `WeakTopicsPage.tsx`
- Hooks: `useWeakTopics.ts`
- Services: `weakTopicsService.ts`

### 3.14 Notes (`src/features/notes/`)
- Pages: `NotesCatalogPage.tsx`, `NoteDetailPage.tsx`
- Hooks: `useNotes.ts`, `useNoteDetail.ts`
- Services: `notesService.ts`

### 3.15 Subscriptions (`src/features/subscriptions/`)
- Pages: `SubscriptionsPage.tsx`
- Hooks: `useSubscriptionPlans.ts`, `useMySubscription.ts`, `useCheckout.ts`, `useCancelSubscription.ts`
- Services: `subscriptionService.ts`

### 3.16 Payments (`src/features/payments/`)
- Pages: `PaymentsHistoryPage.tsx`
- Hooks: `usePaymentHistory.ts`
- Services: `paymentService.ts`

### 3.17 Notifications (`src/features/notifications/`)
- Pages: `NotificationsPage.tsx`
- Hooks: `useNotifications.ts`, `useMarkNotificationRead.ts`
- Services: `notificationService.ts`

### 3.18 Admin Panel (`src/features/admin/`)
- Pages: `AdminDashboardPage.tsx`, `AdminUsersPage.tsx`, `AdminAuditLogsPage.tsx`, `AdminRbacPage.tsx`
- Hooks: `useAdminUsers.ts`, `useToggleUserStatus.ts`, `useAuditLogs.ts`, `useRbacRoles.ts`, `useAssignUserRole.ts`
- Services: `adminService.ts`

### 3.19 Settings (`src/features/settings/`)
- Pages: `SettingsPage.tsx`
- Hooks: `useChangePassword.ts`
- Services: `settingsService.ts`

### 3.20 Profile (`src/features/profile/`)
- Pages: `ProfilePage.tsx`
- Hooks: `useUserProfile.ts`, `useUpdateProfile.ts`
- Services: `profileService.ts`

---

## 4. Component Architecture

The design system primitives strictly utilize Tailwind CSS and Lucide React icons for consistent visual language.

```text
src/components/
├── ui/
│   ├── Button.tsx
│   ├── Input.tsx
│   ├── Select.tsx
│   ├── Card.tsx
│   ├── Table.tsx
│   ├── Badge.tsx
│   ├── Pagination.tsx
│   ├── Modal.tsx
│   ├── Dialog.tsx
│   ├── Dropdown.tsx
│   ├── Charts.tsx
│   ├── Skeleton.tsx
│   ├── EmptyState.tsx
│   ├── Spinner.tsx
│   └── Drawer.tsx
├── shared/
└── feedback/
```

### Component Standards & Contracts
- Every component exports an explicit props interface.
- Low-level UI elements should be compatible with React Hook Form.
- Components accept a `className` prop merged through utility helpers.

---

## 5. Routing Structure

Routing is managed via React Router with centralized definitions in `src/routes/AppRoutes.tsx`.

```
                         AppRoutes Overview
                                |
        +-----------------------+-----------------------+
        |                                               |
        v                                               v
  Public Routes                                 Protected Routes
(GuestLayout)                                   (Auth Guards)
  ├── /                                                 |
  ├── /about                             +--------------+--------------+
  ├── /pricing                           |                             |
  ├── /login                             v                             v
  └── /register                   Student Routes                  Admin Routes
                                 (StudentLayout)                 (AdminLayout)
```

### Complete Route Map

| Path Pattern | Layout | Guard Required | Roles / Entitlements | Component View |
| :--- | :--- | :--- | :--- | :--- |
| `/` | `GuestLayout` | Public | Anyone | `HomePage` |
| `/about` | `GuestLayout` | Public | Anyone | `AboutPage` |
| `/pricing` | `GuestLayout` | Public | Anyone | `PricingPage` |
| `/login` | `AuthLayout` | Public (Unauth only) | Anyone | `LoginPage` |
| `/register` | `AuthLayout` | Public (Unauth only) | Anyone | `RegisterPage` |
| `/forgot-password` | `AuthLayout` | Public | Anyone | `ForgotPasswordPage` |
| `/reset-password` | `AuthLayout` | Public | Anyone | `ResetPasswordPage` |
| `/dashboard` | `StudentLayout` | `ProtectedRoute` | Authenticated | `DashboardPage` |
| `/exam-tracks` | `StudentLayout` | `ProtectedRoute` | Authenticated | `ExamTracksPage` |
| `/exam-tracks/:slug` | `StudentLayout` | `ProtectedRoute` | Authenticated | `ExamDetailPage` |
| `/subjects` | `StudentLayout` | `ProtectedRoute` | Authenticated | `SubjectsPage` |
| `/topics` | `StudentLayout` | `ProtectedRoute` | Authenticated | `TopicsPage` |
| `/mock-tests` | `StudentLayout` | `ProtectedRoute` | Authenticated | `MockTestsPage` |
| `/mock-tests/:slug` | `StudentLayout` | `ProtectedRoute` | Authenticated | `MockTestDetailPage` |
| `/attempts/:id/execute` | `StudentLayout` | `ProtectedRoute` | Authenticated | `AttemptExecutionPage` |
| `/results/:id` | `StudentLayout` | `ProtectedRoute` | Authenticated | `AttemptResultPage` |
| `/results/:id/review` | `StudentLayout` | `ProtectedRoute` | Authenticated | `AttemptReviewPage` |
| `/progress` | `StudentLayout` | `ProtectedRoute` | Authenticated | `ProgressPage` |
| `/weak-topics` | `StudentLayout` | `EntitlementGuard` | Required analytics entitlement | `WeakTopicsPage` |
| `/notes` | `StudentLayout` | `ProtectedRoute` | Authenticated | `NotesCatalogPage` |
| `/notes/:slug` | `StudentLayout` | `EntitlementGuard` | Conditional note entitlement | `NoteDetailPage` |
| `/bookmarks` | `StudentLayout` | `ProtectedRoute` | Authenticated | `BookmarksPage` |
| `/notifications` | `StudentLayout` | `ProtectedRoute` | Authenticated | `NotificationsPage` |
| `/subscriptions` | `StudentLayout` | `ProtectedRoute` | Authenticated | `SubscriptionsPage` |
| `/payments/history` | `StudentLayout` | `ProtectedRoute` | Authenticated | `PaymentsHistoryPage` |
| `/profile` | `StudentLayout` | `ProtectedRoute` | Authenticated | `ProfilePage` |
| `/settings` | `StudentLayout` | `ProtectedRoute` | Authenticated | `SettingsPage` |
| `/admin` | `AdminLayout` | `RoleGuard` | `ADMIN`, `SUPERADMIN` | `AdminDashboardPage` |
| `/admin/users` | `AdminLayout` | `RoleGuard` | `ADMIN`, `SUPERADMIN` | `AdminUsersPage` |
| `/admin/questions` | `AdminLayout` | `RoleGuard` | `CONTENT_EDITOR`, `SME`, `ADMIN` | `AdminQuestionsPage` |
| `/admin/questions/:id` | `AdminLayout` | `RoleGuard` | `CONTENT_EDITOR`, `SME`, `ADMIN` | `AdminQuestionEditPage` |
| `/admin/question-reports` | `AdminLayout` | `RoleGuard` | `CONTENT_EDITOR`, `ADMIN` | `AdminQuestionReportsPage` |
| `/admin/audit-logs` | `AdminLayout` | `RoleGuard` | `SUPERADMIN` | `AdminAuditLogsPage` |
| `/admin/rbac` | `AdminLayout` | `RoleGuard` | `SUPERADMIN` | `AdminRbacPage` |
| `/unauthorized` | `ErrorLayout` | Public | Anyone | `UnauthorizedPage` |
| `*` | `ErrorLayout` | Public | Anyone | `NotFoundPage` |

---

## 6. Authentication Flow

Authentication aligns with the Django REST Framework API and SimpleJWT token handling.

```
                  AUTHENTICATION & REFRESH FLOW MATRIX
                  
     Client App                   Axios Interceptor               Django DRF API
         |                                |                             |
         |--- 1. Login Request ---------->|                             |
         |    (POST /api/v1/auth/login/)  |---------------------------->|
         |                                |                             |
         |<-- 2. Issue Access + Refresh --|<----------------------------|
         |                                |                             |
         |--- 3. Protected Request ------>| Authorization: Bearer <token>
         |                                |---------------------------->|
         |                                |<-- 4. 401 Token Expired ----|
         |                                |                             |
         |                                |-- 5. Automatic Refresh ---->|
         |                                |   (POST /api/v1/auth/refresh/)|
         |                                |                             |
         |                                |<-- 6. New Access Token -----|
         |                                |                             |
         |<-- 7. Transparent Retry ------>|---------------------------->|
```

### Flow Specifications

1. **Token Storage**:
   - Access token is maintained in memory within the auth store.
   - Refresh token is stored securely in local storage or an HttpOnly cookie when configured.

2. **Session Initialization & Restoration**:
   - On application mount, auth state initialization restores the session from refresh token state.
   - A fresh access token is requested if the refresh token is valid.

3. **Silent Queue-Based Token Refresh**:
   - Axios interceptors handle 401 responses.
   - Pending requests are queued while refresh runs.
   - Successful refresh updates the token and retries queued requests.
   - Failed refresh clears auth state and redirects to login.

4. **Logout Procedure**:
   - Logout revokes the refresh token on the backend.
   - Local stores and query cache are cleared.

---

## 7. State Management

Zustand is used for client-only local and persistent state. Server state is managed exclusively via TanStack Query v5.

```text
src/store/
├── useAuthStore.ts
├── useThemeStore.ts
├── useNotificationStore.ts
├── useBookmarkStore.ts
├── usePreferencesStore.ts
├── useMockTestStore.ts
├── useAttemptStore.ts
├── useSubscriptionStore.ts
└── useAdminStore.ts
```

### Store Schemas

#### 1. Auth Store (`useAuthStore.ts`)
- Stores the current user, access token, roles, and entitlements.
- Exposes `setAuth`, `clearAuth`, `hasRole`, and `hasEntitlement` helpers.

#### 2. Assessment Attempt Store (`useAttemptStore.ts`)
- Stores the current attempt session, remaining time, selected answers, and submit state.
- Supports fast updates during active test execution.

---

## 8. API Layer

Network communication uses a configured Axios client instance in `src/services/api.client.ts`.

### Response Envelopes & Contracts

- API responses follow consistent success and error envelopes.
- Pagination metadata is standardized for list endpoints.
- Errors are translated into structured objects for forms and toast handling.

### Interceptors & Retry Architecture

- Request interceptors attach `Authorization: Bearer <access_token>` automatically.
- Response interceptors handle token refresh, error normalization, and request retry.
- Abort signals are used to cancel stale requests.
- Cloudinary upload flows are isolated behind a dedicated upload service.

---

## 9. Form Validation

Forms are constructed using React Hook Form paired with Zod schemas.

### Validation Strategy Matrix

| Form Name | Schema Location | Key Rules & Constraints |
| :--- | :--- | :--- |
| Login | `auth.schema.ts` | Email required, password required, valid format. |
| Register | `auth.schema.ts` | Email, name, password policy, optional phone. |
| Profile Update | `profile.schema.ts` | Name limits, optional phone, valid target exam data. |
| Question Editor | `question.schema.ts` | Required stem, minimum options, exactly one correct option. |
| Question Report | `questionReport.schema.ts` | Enum category and comment length. |
| Checkout | `subscription.schema.ts` | Valid plan code. |

---

## 10. UI Layouts

Layout wrappers enforce visual hierarchy and consistent navigation context.

1. **Guest Layout (`GuestLayout.tsx`)**:
   - Marketing header, content sections, and footer.
2. **Student Layout (`StudentLayout.tsx`)**:
   - Collapsible navigation, notifications, and persistent study context.
3. **Admin Layout (`AdminLayout.tsx`)**:
   - Dense administrative navigation and analytics panels.
4. **Auth Layout (`AuthLayout.tsx`)**:
   - Centered authentication card with focused form flow.
5. **Error Layout (`ErrorLayout.tsx`)**:
   - Shell for 404, 403, and 500 states.

---

## 11. Responsive Design Strategy

The application is built mobile-first using Tailwind CSS grid and flexbox primitives.

### Responsive Breakpoint Standard

| Breakpoint Prefix | Min Width | Target Device Class | Primary UI Adaptation |
| :--- | :--- | :--- | :--- |
| `default` | `< 640px` | Mobile phones | Stacked cards, bottom navigation, drawers |
| `sm` | `640px` | Large phones / small tablets | 2-column cards, condensed forms |
| `md` | `768px` | Tablets | Dual-column dashboards, expanded tables |
| `lg` | `1024px` | Laptops / Desktops | Persistent sidebar, multi-column analytics |
| `xl` | `1280px` | Desktop screens | Full multi-panel assessment workspace |
| `2xl` | `1536px` | Ultra-wide displays | Centered max-width containers |

### Accessibility & Theme Handling
- Interactive controls include accessible ARIA attributes.
- Keyboard navigation and visible focus states are required.
- Light and dark mode support uses CSS tokens and a persisted theme preference.

---

## 12. Performance Optimization

Performance is treated as a core architectural requirement.

1. **Code Splitting & Route Splitting**:
   - Heavy routes and feature modules should load lazily.
2. **Component & Calculation Memoization**:
   - Apply memoization only when it clearly benefits complex UI or calculations.
3. **Image & Asset Optimization**:
   - Use optimized asset delivery and lazy loading for media-heavy views.
4. **TanStack Query v5 Caching Strategy**:
   - Use sensible stale times for stable lists and highly dynamic data.
5. **Debounce Optimization**:
   - Search and filter inputs should debounce requests.

---

## 13. Security

Security practices strictly enforce frontend safety guidelines.

1. **JWT Security**:
   - Access tokens stay in memory; refresh tokens are stored securely.
2. **XSS Prevention**:
   - Rendered rich content should be sanitized before display.
3. **CSRF Protection**:
   - Requests should respect backend cookie and header requirements.
4. **Authorization & Entitlement Guards**:
   - Route guards are backed by server-side DRF permissions.
5. **Secure Communication**:
   - API base URLs and upload configuration are injected through environment variables.

---

## 14. Error Handling

Error handling provides clear, actionable feedback to users.

1. **Global React Error Boundary**:
   - Catches unhandled render crashes and shows a recovery component.
2. **Structured API Error Translation**:
   - Backend error envelopes are mapped to form errors and toasts.
3. **Toast Notification System**:
   - Success, warning, and failure feedback is centralized.
4. **Offline Resilience**:
   - An offline banner can surface connectivity loss during active use.

---

## 15. Testing Strategy

```text
tests/
├── unit/
├── components/
├── features/
└── e2e/
```

### Framework Selection
- Unit and component testing use Vitest and React Testing Library.
- API mocking uses Mock Service Worker.
- End-to-end testing uses Playwright.

---

## 16. Development Guidelines

### 1. Naming Conventions
- Components: `PascalCase.tsx`
- Hooks: `camelCase.ts` prefixed with `use`
- Services, utils, types, and constants use consistent camelCase or kebab-case module names.
- Feature folders use kebab-case.

### 2. TypeScript & Code Quality Rules
- No `any` or implicit `any`.
- Prefer explicit interfaces for props and data contracts.
- Keep imports organized and deterministic.

### 3. Import Order Hierarchy
```typescript
// 1. External dependencies
import React from 'react';
import { useQuery } from '@tanstack/react-query';

// 2. Internal UI primitives
import { Button } from '@/components/ui/Button';

// 3. Feature-specific hooks and services
import { useStartAttempt } from '../hooks/useStartAttempt';

// 4. Types and utilities
import type { MockTest } from '@/types/domain.types';
```

---

## 17. Future Scalability

The architecture is designed to support future features without refactoring existing feature modules.

1. AI tutor and guided practice modules can be added as separate feature folders.
2. Discussion and community features can extend the existing routing and state patterns.
3. Certificate, leaderboard, and adaptive testing modules can reuse the existing query and store architecture.
4. Internationalization and offline support can be added incrementally.

---

## 18. Verification & Architectural Compliance

The frontend architecture is considered compliant when it remains aligned with the following rules:

- The stack remains React 19, TypeScript, Vite, Tailwind CSS, React Router, TanStack Query, Axios, Zustand, Zod, and React Hook Form.
- Route organization remains feature-driven and stays independent of framework-specific page conventions.
- Shared UI concerns stay inside reusable components, layouts, and providers.
- Server state continues to flow through TanStack Query rather than ad hoc fetch logic.
- Authentication and authorization remain coordinated with the backend API design.

This document is the frontend implementation blueprint and should stay synchronized with [FRONTEND_STRUCTURE.md](docs/FRONTEND_STRUCTURE.md).
