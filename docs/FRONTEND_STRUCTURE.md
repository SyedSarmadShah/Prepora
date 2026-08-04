# Prepora Frontend Architecture & Structure Blueprint

> **Document Status:** Single Source of Truth for Frontend Implementation  
> **Target Stack:** React 19 | TypeScript | Vite | Tailwind CSS | React Router | TanStack Query v5 | Axios | React Hook Form | Zod | Zustand | Framer Motion | Lucide React | Recharts | React Hot Toast | Cloudinary Upload Widget | JWT Authentication  
> **Backend Compatibility:** 100% aligned with Django 4.2+ RESTful API Specification ([API_DESIGN.md](file:///d:/Prepora/docs/API_DESIGN.md)), [BACKEND_STRUCTURE.md](file:///d:/Prepora/docs/BACKEND_STRUCTURE.md), and [BUSINESS_WORKFLOWS.md](file:///d:/Prepora/docs/BUSINESS_WORKFLOWS.md).

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

---

## 1. Frontend Architecture Overview

The Prepora frontend architecture is engineered for high reliability, fast initial render times, accessible user experiences, and seamless real-time test execution. It targets candidates preparing for Pakistan Armed Forces initial tests (PMA, PAF, Navy, ASF, ISSB) and government competitive exams (FPSC, Police).

```
+-----------------------------------------------------------------------------------+
|                                  USER INTERFACE                                   |
|       (React 19 Components + Tailwind CSS + Framer Motion + Lucide React)        |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                                ROUTING & LAYOUTS                                  |
|         (React Router + GuestLayout / StudentLayout / AdminLayout / Guards)       |
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
|                                BACKEND API GATEWAY                                |
|             (Django REST Framework `/api/v1/` + JWT Authentication)              |
+-----------------------------------------------------------------------------------+
```

### Architectural Principles

1. **Feature-First Architecture (`src/features/`)**:
   - Code is grouped by business capabilities (e.g., `auth`, `attempt-engine`, `weak-topics`, `subscriptions`) rather than arbitrary technical layers.
   - Each feature module is self-contained with its own pages, components, hooks, services, types, validation schemas, and state definitions.

2. **Component-Driven Development**:
   - UI elements are built top-down starting from generic primitives (`src/components/ui/`) to domain-specific feature components (`src/features/*/components/`).
   - Pure presentation components are strictly decoupled from data-fetching side effects.

3. **Separation of Concerns**:
   - **Views (Pages/Components)** focus purely on visual presentation and user interactions.
   - **Custom Hooks (`use*`)** encapsulate UI business logic, query states, and event listeners.
   - **Services (`*Service.ts`)** manage raw API network calls, headers, and endpoint paths.
   - **Stores (`*Store.ts`)** maintain strictly client-only persistent or ephemeral UI state.

4. **Scalable Folder Organization**:
   - Clear distinction between global infrastructure (`src/app/`, `src/providers/`, `src/services/`) and domain features (`src/features/`).

5. **Maintainability & Type Safety**:
   - Strict TypeScript end-to-end contracts matching Django DTOs and database models.
   - Zero `any` types permitted. Strict Zod schema validation at boundary layers.

6. **Performance & Low Latency**:
   - Optimistic updates for non-destructive actions (bookmarks, notifications read state).
   - Local state buffering for low-latency assessment timer execution and auto-saving.

7. **Security-in-Depth**:
   - XSS protection via input sanitization.
   - Dual-level auth route protection (Role Guards + Entitlement Guards).

---

## 2. Complete Folder Structure

```text
src/
├── app/
│   ├── App.tsx                      # Root application entry point
│   ├── main.tsx                     # Vite mounting script
│   └── index.css                    # Tailwind CSS directives & custom utility classes
├── assets/
│   ├── icons/                       # SVG icon assets
│   ├── images/                      # Static branding assets & illustrations
│   └── logos/                       # Platform logos (Army, PAF, Navy, FPSC)
├── components/
│   ├── ui/                          # Generic design system primitives
│   │   ├── Button.tsx
│   │   ├── Input.tsx
│   │   ├── Select.tsx
│   │   ├── Card.tsx
│   │   ├── Table.tsx
│   │   ├── Badge.tsx
│   │   ├── Pagination.tsx
│   │   ├── Modal.tsx
│   │   ├── Dialog.tsx
│   │   ├── Dropdown.tsx
│   │   ├── Charts.tsx
│   │   ├── Skeleton.tsx
│   │   ├── EmptyState.tsx
│   │   ├── Spinner.tsx
│   │   └── Drawer.tsx
│   ├── shared/                      # Domain-agnostic shared components
│   │   ├── Header.tsx
│   │   ├── Footer.tsx
│   │   ├── Sidebar.tsx
│   │   ├── Navbar.tsx
│   │   ├── PageHeader.tsx
│   │   ├── ConfirmModal.tsx
│   │   └── ImageUploader.tsx        # Cloudinary Widget wrapper
│   └── feedback/                    # System feedback & boundaries
│       ├── ErrorBoundary.tsx
│       ├── GlobalLoader.tsx
│       ├── ToastContainer.tsx
│       └── OfflineBanner.tsx
├── constants/
│   ├── api.constants.ts             # API URLs, endpoints, timeouts
│   ├── routes.constants.ts          # Route path definitions
│   ├── rbac.constants.ts            # Roles & Entitlement keys
│   └── storage.constants.ts         # LocalStorage / SessionStorage keys
├── contexts/
│   ├── AuthContext.tsx              # Auth state context bridge
│   └── ThemeContext.tsx             # Color scheme preference context
├── features/                        # 21 Domain-specific feature modules
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
├── hooks/                           # Global custom React hooks
│   ├── useDebounce.ts
│   ├── useLocalStorage.ts
│   ├── useMediaQuery.ts
│   ├── useOnClickOutside.ts
│   ├── useOnlineStatus.ts
│   └── usePagination.ts
├── layouts/                         # Layout wrapper components
│   ├── GuestLayout.tsx
│   ├── StudentLayout.tsx
│   ├── AdminLayout.tsx
│   ├── DashboardLayout.tsx
│   ├── AuthLayout.tsx
│   └── ErrorLayout.tsx
├── pages/                           # Top-level route view components
│   ├── public/
│   │   ├── HomePage.tsx
│   │   ├── AboutPage.tsx
│   │   ├── PricingPage.tsx
│   │   └── ContactPage.tsx
│   ├── auth/
│   │   ├── LoginPage.tsx
│   │   ├── RegisterPage.tsx
│   │   ├── ForgotPasswordPage.tsx
│   │   └── ResetPasswordPage.tsx
│   ├── student/
│   │   ├── DashboardPage.tsx
│   │   ├── ExamTracksPage.tsx
│   │   ├── ExamDetailPage.tsx
│   │   ├── SubjectsPage.tsx
│   │   ├── TopicsPage.tsx
│   │   ├── MockTestsPage.tsx
│   │   ├── MockTestDetailPage.tsx
│   │   ├── AttemptExecutionPage.tsx
│   │   ├── AttemptResultPage.tsx
│   │   ├── AttemptReviewPage.tsx
│   │   ├── ProgressPage.tsx
│   │   ├── WeakTopicsPage.tsx
│   │   ├── NotesCatalogPage.tsx
│   │   ├── NoteDetailPage.tsx
│   │   ├── BookmarksPage.tsx
│   │   ├── NotificationsPage.tsx
│   │   ├── SubscriptionsPage.tsx
│   │   ├── PaymentsHistoryPage.tsx
│   │   ├── ProfilePage.tsx
│   │   └── SettingsPage.tsx
│   ├── admin/
│   │   ├── AdminDashboardPage.tsx
│   │   ├── AdminUsersPage.tsx
│   │   ├── AdminQuestionsPage.tsx
│   │   ├── AdminQuestionEditPage.tsx
│   │   ├── AdminQuestionReportsPage.tsx
│   │   ├── AdminSubjectsPage.tsx
│   │   ├── AdminAuditLogsPage.tsx
│   │   └── AdminRbacPage.tsx
│   └── errors/
│       ├── NotFoundPage.tsx
│       ├── UnauthorizedPage.tsx
│       └── ServerErrorPage.tsx
├── providers/                       # Context & state providers
│   ├── QueryProvider.tsx            # TanStack Query Client provider
│   ├── ToastProvider.tsx            # React Hot Toast provider
│   └── RouterProvider.tsx           # React Router provider
├── routes/                          # Routing configurations & guards
│   ├── AppRoutes.tsx                # Main router tree
│   ├── ProtectedRoute.tsx           # Authenticated user guard
│   ├── RoleGuard.tsx                # Role-based route guard
│   └── EntitlementGuard.tsx         # Subscription entitlement guard
├── services/                        # Base infrastructure network client
│   ├── api.client.ts                # Axios instance with interceptors
│   ├── storage.service.ts           # Token & storage persistence helpers
│   └── upload.service.ts            # Cloudinary & Presigned upload handler
├── store/                           # Global Zustand client stores
│   ├── useAuthStore.ts
│   ├── useThemeStore.ts
│   ├── useNotificationStore.ts
│   ├── useBookmarkStore.ts
│   ├── usePreferencesStore.ts
│   ├── useMockTestStore.ts
│   ├── useAttemptStore.ts
│   ├── useSubscriptionStore.ts
│   └── useAdminStore.ts
├── styles/                          # CSS modules & style configurations
│   ├── animations.css
│   ├── components.css
│   └── theme.css
├── types/                           # Shared global TypeScript types
│   ├── api.types.ts                 # Envelopes & pagination types
│   ├── auth.types.ts                # Roles, Entitlements, JWT payload
│   ├── domain.types.ts              # Core entity definitions
│   └── environment.d.ts             # Vite env variables definition
└── utils/                           # Pure helper functions
    ├── formatters.ts                # Currency (PKR), dates, percentage
    ├── validators.ts                # Custom format validators
    ├── error-handler.ts             # API error envelope parsing
    └── math.utils.ts                # Accuracy & score calculator helpers
```

---

## 3. Feature Modules

Every feature module follows a standard architecture pattern:

```text
src/features/<feature-name>/
├── components/                      # Modular UI components specific to feature
├── hooks/                           # Custom React hooks (Queries & Mutations)
├── services/                        # Direct Axios API caller functions
├── types/                           # Feature-specific TypeScript DTOs
├── validation/                      # Zod validation schemas
├── routes/                          # Feature sub-routes (if applicable)
└── store/                           # Local Zustand store (if feature-specific state required)
```

Below is the detailed breakdown for all 21 feature modules:

---

### 3.1 Authentication (`src/features/auth/`)
- **Pages**: `LoginPage.tsx`, `RegisterPage.tsx`, `ForgotPasswordPage.tsx`, `ResetPasswordPage.tsx`
- **Components**: `LoginForm.tsx`, `RegisterForm.tsx`, `ForgotPasswordForm.tsx`, `ResetPasswordForm.tsx`, `AuthHeader.tsx`, `AuthFooter.tsx`
- **Hooks**: `useLogin.ts`, `useRegister.ts`, `useLogout.ts`, `useForgotPassword.ts`, `useResetPassword.ts`, `useCurrentUser.ts`
- **Services**: `authService.ts` (`POST /api/v1/auth/login/`, `POST /api/v1/auth/register/`, `POST /api/v1/auth/refresh/`, `POST /api/v1/auth/logout/`, `POST /api/v1/auth/forgot-password/`, `POST /api/v1/auth/reset-password/`, `GET /api/v1/auth/me/`)
- **Types**: `auth.types.ts` (`LoginRequest`, `RegisterRequest`, `AuthResponseData`, `JwtTokens`, `UserIdentity`)
- **Validation**: `auth.schema.ts` (`loginSchema`, `registerSchema`, `forgotPasswordSchema`, `resetPasswordSchema`)
- **State**: Integrated with global `useAuthStore.ts`

---

### 3.2 Dashboard (`src/features/dashboard/`)
- **Pages**: `DashboardPage.tsx`
- **Components**: `WelcomeBanner.tsx`, `ProgressSummaryCards.tsx`, `TargetExamCard.tsx`, `RecentAttemptsList.tsx`, `WeakTopicsWidget.tsx`, `QuickPracticeCTA.tsx`
- **Hooks**: `useDashboardData.ts`
- **Services**: `dashboardService.ts` (Aggregates calls to `/api/v1/progress/summary/`, `/api/v1/weak-topics/`, `/api/v1/users/me/profile/`)
- **Types**: `dashboard.types.ts` (`DashboardSummaryDTO`, `QuickStats`)
- **Validation**: N/A (Read-only view)
- **State**: Query state via TanStack Query

---

### 3.3 Exam Tracks (`src/features/exam-tracks/`)
- **Pages**: `ExamTracksPage.tsx`, `ExamDetailPage.tsx`
- **Components**: `ExamTrackCard.tsx`, `ExamTrackGrid.tsx`, `ExamHeader.tsx`, `SubjectListSection.tsx`
- **Hooks**: `useExamTracks.ts`, `useExamTrackDetail.ts`, `useExams.ts`
- **Services**: `examTrackService.ts` (`GET /api/v1/exam-tracks/`, `GET /api/v1/exam-tracks/{slug}/`, `GET /api/v1/exams/`)
- **Types**: `examTrack.types.ts` (`ExamTrack`, `Exam`, `ExamTrackFilterParams`)
- **Validation**: `examTrack.schema.ts` (Admin track creation/editing schema)
- **State**: Query caching with 60-minute TTL

---

### 3.4 Subjects (`src/features/subjects/`)
- **Pages**: `SubjectsPage.tsx`
- **Components**: `SubjectCard.tsx`, `SubjectGrid.tsx`, `TopicCountBadge.tsx`
- **Hooks**: `useSubjects.ts`, `useSubjectDetail.ts`
- **Services**: `subjectService.ts` (`GET /api/v1/subjects/`)
- **Types**: `subject.types.ts` (`Subject`, `SubjectFilterParams`)
- **Validation**: `subject.schema.ts`
- **State**: Query caching

---

### 3.5 Topics (`src/features/topics/`)
- **Pages**: `TopicsPage.tsx`
- **Components**: `TopicItem.tsx`, `TopicList.tsx`, `TopicProgressIndicator.tsx`
- **Hooks**: `useTopics.ts`
- **Services**: `topicService.ts` (`GET /api/v1/topics/`, `PATCH /api/v1/topics/{id}/`)
- **Types**: `topic.types.ts` (`Topic`, `TopicFilterParams`)
- **Validation**: `topic.schema.ts`
- **State**: Query caching

---

### 3.6 Questions (`src/features/questions/`)
- **Pages**: `AdminQuestionsPage.tsx`, `AdminQuestionEditPage.tsx`
- **Components**: `QuestionCard.tsx`, `QuestionStem.tsx`, `OptionList.tsx`, `ExplanationBox.tsx`, `DifficultyBadge.tsx`
- **Hooks**: `useQuestions.ts`, `useQuestionDetail.ts`, `useCreateQuestion.ts`, `usePublishQuestion.ts`
- **Services**: `questionService.ts` (`GET /api/v1/questions/`, `GET /api/v1/questions/{id}/`, `POST /api/v1/questions/`, `POST /api/v1/questions/{id}/publish/`)
- **Types**: `question.types.ts` (`Question`, `QuestionOption`, `QuestionExplanation`, `QuestionStatusEnum`)
- **Validation**: `question.schema.ts` (`questionFormSchema`)
- **State**: Query state & admin workflow state

---

### 3.7 Question Reports (`src/features/question-reports/`)
- **Pages**: `AdminQuestionReportsPage.tsx`
- **Components**: `ReportQuestionModal.tsx`, `ReportCategorySelect.tsx`, `ReportTable.tsx`, `ReportStatusBadge.tsx`
- **Hooks**: `useSubmitReport.ts`, `useQuestionReports.ts`
- **Services**: `questionReportService.ts` (`POST /api/v1/question-reports/`, `GET /api/v1/admin/question-reports/`)
- **Types**: `questionReport.types.ts` (`QuestionReport`, `ReportCategoryEnum`)
- **Validation**: `questionReport.schema.ts` (`reportFormSchema`)
- **State**: Mutation state

---

### 3.8 Bookmarks (`src/features/bookmarks/`)
- **Pages**: `BookmarksPage.tsx`
- **Components**: `BookmarkButton.tsx`, `BookmarkList.tsx`, `BookmarkItemCard.tsx`, `TagFilter.tsx`
- **Hooks**: `useBookmarks.ts`, `useAddBookmark.ts`, `useRemoveBookmark.ts`
- **Services**: `bookmarkService.ts` (`GET /api/v1/bookmarks/`, `POST /api/v1/bookmarks/`, `DELETE /api/v1/bookmarks/{id}/`)
- **Types**: `bookmark.types.ts` (`Bookmark`, `BookmarkTargetTypeEnum`)
- **Validation**: `bookmark.schema.ts`
- **State**: Global optimistic store `useBookmarkStore.ts`

---

### 3.9 Mock Tests (`src/features/mock-tests/`)
- **Pages**: `MockTestsPage.tsx`, `MockTestDetailPage.tsx`
- **Components**: `MockTestCard.tsx`, `MockTestInstructions.tsx`, `NegativeMarkingWarning.tsx`, `StartTestCTA.tsx`
- **Hooks**: `useMockTests.ts`, `useMockTestDetail.ts`
- **Services**: `mockTestService.ts` (`GET /api/v1/mock-tests/`, `GET /api/v1/mock-tests/{slug}/`)
- **Types**: `mockTest.types.ts` (`MockTest`, `MockTestFilterParams`)
- **Validation**: `mockTest.schema.ts`
- **State**: Integrated with `useMockTestStore.ts`

---

### 3.10 Attempt Engine (`src/features/attempt-engine/`)
- **Pages**: `AttemptExecutionPage.tsx`
- **Components**: `AttemptHeader.tsx`, `TimerCountdown.tsx`, `QuestionNavigatorGrid.tsx`, `QuestionSlide.tsx`, `OptionSelector.tsx`, `SubmitConfirmDialog.tsx`
- **Hooks**: `useStartAttempt.ts`, `useAutoSaveProgress.ts`, `useSubmitAttempt.ts`, `useTestTimer.ts`
- **Services**: `attemptService.ts` (`POST /api/v1/mock-tests/{id}/start/`, `POST /api/v1/attempts/{id}/save-progress/`, `POST /api/v1/attempts/{id}/submit/`)
- **Types**: `attempt.types.ts` (`AttemptSession`, `AttemptAnswerDTO`, `AttemptStatusEnum`)
- **Validation**: `attempt.schema.ts`
- **State**: Dedicated local Zustand store `useAttemptStore.ts` for fast state access during assessment execution.

---

### 3.11 Attempt Results (`src/features/attempt-results/`)
- **Pages**: `AttemptResultPage.tsx`, `AttemptReviewPage.tsx`
- **Components**: `ScorecardHeader.tsx`, `AccuracyPieChart.tsx`, `TopicBreakdownTable.tsx`, `QuestionReviewCard.tsx`, `SolutionExplanationPanel.tsx`
- **Hooks**: `useAttemptResult.ts`, `useAttemptReview.ts`
- **Services**: `attemptResultService.ts` (`GET /api/v1/results/{id}/`, `GET /api/v1/results/{id}/review/`)
- **Types**: `attemptResult.types.ts` (`AttemptResult`, `QuestionReviewDTO`)
- **Validation**: N/A
- **State**: Query state

---

### 3.12 Progress Analytics (`src/features/progress-analytics/`)
- **Pages**: `ProgressPage.tsx`
- **Components**: `OverallStatsCards.tsx`, `AccuracyTrendChart.tsx`, `SubjectMasteryBarChart.tsx`, `StudyStreakWidget.tsx`
- **Hooks**: `useProgressSummary.ts`, `useTopicProgress.ts`
- **Services**: `progressService.ts` (`GET /api/v1/progress/summary/`, `GET /api/v1/progress/topics/`)
- **Types**: `progress.types.ts` (`ProgressSummary`, `TopicProgress`)
- **Validation**: N/A
- **State**: Query state

---

### 3.13 Weak Topics (`src/features/weak-topics/`)
- **Pages**: `WeakTopicsPage.tsx`
- **Components**: `WeakTopicCard.tsx`, `DeficitBadge.tsx`, `TargetedDrillCTA.tsx`, `EntitlementLockBanner.tsx`
- **Hooks**: `useWeakTopics.ts`
- **Services**: `weakTopicsService.ts` (`GET /api/v1/weak-topics/`)
- **Types**: `weakTopics.types.ts` (`WeakTopicDiagnostic`)
- **Validation**: N/A
- **State**: Query state with Entitlement Guard checks

---

### 3.14 Notes (`src/features/notes/`)
- **Pages**: `NotesCatalogPage.tsx`, `NoteDetailPage.tsx`
- **Components**: `NoteCard.tsx`, `MarkdownViewer.tsx`, `PdfDownloadButton.tsx`, `PremiumNotesLock.tsx`
- **Hooks**: `useNotes.ts`, `useNoteDetail.ts`
- **Services**: `notesService.ts` (`GET /api/v1/notes/`, `GET /api/v1/notes/{slug}/`)
- **Types**: `notes.types.ts` (`StudyNote`, `NoteFilterParams`)
- **Validation**: `notes.schema.ts`
- **State**: Query state

---

### 3.15 Subscriptions (`src/features/subscriptions/`)
- **Pages**: `SubscriptionsPage.tsx`
- **Components**: `PricingPlanCard.tsx`, `BillingToggle.tsx`, `ActiveSubscriptionBanner.tsx`, `CancelSubscriptionDialog.tsx`
- **Hooks**: `useSubscriptionPlans.ts`, `useMySubscription.ts`, `useCheckout.ts`, `useCancelSubscription.ts`
- **Services**: `subscriptionService.ts` (`GET /api/v1/subscription-plans/`, `GET /api/v1/subscriptions/me/`, `POST /api/v1/subscriptions/checkout/`, `POST /api/v1/subscriptions/cancel/`)
- **Types**: `subscription.types.ts` (`SubscriptionPlan`, `UserSubscription`, `CheckoutResponseData`)
- **Validation**: `subscription.schema.ts` (`checkoutSchema`)
- **State**: Global `useSubscriptionStore.ts`

---

### 3.16 Payments (`src/features/payments/`)
- **Pages**: `PaymentsHistoryPage.tsx`
- **Components**: `PaymentReceiptTable.tsx`, `TransactionStatusBadge.tsx`, `DownloadReceiptButton.tsx`
- **Hooks**: `usePaymentHistory.ts`
- **Services**: `paymentService.ts` (`GET /api/v1/payments/history/`)
- **Types**: `payment.types.ts` (`PaymentTransaction`, `PaymentStatusEnum`)
- **Validation**: N/A
- **State**: Query state

---

### 3.17 Notifications (`src/features/notifications/`)
- **Pages**: `NotificationsPage.tsx`
- **Components**: `NotificationBell.tsx`, `NotificationDropdown.tsx`, `NotificationItem.tsx`, `UnreadBadge.tsx`
- **Hooks**: `useNotifications.ts`, `useMarkNotificationRead.ts`
- **Services**: `notificationService.ts` (`GET /api/v1/notifications/`, `PATCH /api/v1/notifications/{id}/read/`)
- **Types**: `notification.types.ts` (`Notification`, `NotificationChannelEnum`)
- **Validation**: N/A
- **State**: Global store `useNotificationStore.ts` with unread count badge state

---

### 3.18 Admin Panel (`src/features/admin/`)
- **Pages**: `AdminDashboardPage.tsx`, `AdminUsersPage.tsx`, `AdminAuditLogsPage.tsx`, `AdminRbacPage.tsx`
- **Components**: `UserTable.tsx`, `UserStatusToggle.tsx`, `AuditLogTable.tsx`, `RoleAssignmentModal.tsx`, `AdminMetricCards.tsx`
- **Hooks**: `useAdminUsers.ts`, `useToggleUserStatus.ts`, `useAuditLogs.ts`, `useRbacRoles.ts`, `useAssignUserRole.ts`
- **Services**: `adminService.ts` (`GET /api/v1/admin/users/`, `PATCH /api/v1/admin/users/{id}/status/`, `GET /api/v1/admin/audit-logs/`, `GET /api/v1/admin/rbac/roles/`, `POST /api/v1/admin/rbac/user-roles/`)
- **Types**: `admin.types.ts` (`AdminUserDTO`, `AuditLogEntry`, `SystemRole`)
- **Validation**: `admin.schema.ts` (`assignRoleSchema`)
- **State**: `useAdminStore.ts`

---

### 3.19 Settings (`src/features/settings/`)
- **Pages**: `SettingsPage.tsx`
- **Components**: `ChangePasswordForm.tsx`, `ThemePreferenceRadio.tsx`, `NotificationPreferencesForm.tsx`
- **Hooks**: `useChangePassword.ts`
- **Services**: `settingsService.ts` (`PUT /api/v1/users/me/change-password/`)
- **Types**: `settings.types.ts` (`ChangePasswordRequest`)
- **Validation**: `settings.schema.ts` (`changePasswordSchema`)
- **State**: Local form state

---

### 3.20 Profile (`src/features/profile/`)
- **Pages**: `ProfilePage.tsx`
- **Components**: `ProfileHeader.tsx`, `ProfileEditForm.tsx`, `AvatarUploadWidget.tsx`, `PreparationGoalSelect.tsx`
- **Hooks**: `useUserProfile.ts`, `useUpdateProfile.ts`
- **Services**: `profileService.ts` (`GET /api/v1/users/me/profile/`, `PATCH /api/v1/users/me/profile/`)
- **Types**: `profile.types.ts` (`UserProfileDTO`, `UpdateProfileRequest`)
- **Validation**: `profile.schema.ts` (`updateProfileSchema`)
- **State**: Query state & user state synchronization

---

## 4. Component Architecture

The design system primitives strictly utilize Tailwind CSS and Lucide React icons for visual excellence.

```text
src/components/
├── ui/                              # Pure presentation components (Atoms & Molecules)
│   ├── Button.tsx                   # Variants: primary, secondary, outline, danger, ghost
│   ├── Input.tsx                    # Standard input with label, error text, and icon accessories
│   ├── Select.tsx                   # Accessible dropdown selector
│   ├── Card.tsx                     # Card container with Header, Content, Footer
│   ├── Table.tsx                    # Accessible responsive table with column headers
│   ├── Badge.tsx                    # Color-coded pills (Status, Difficulty, Entitlement)
│   ├── Pagination.tsx               # Page navigation with next/previous & page size selector
│   ├── Modal.tsx                    # Accessible backdrop overlay modal
│   ├── Dialog.tsx                   # Confirmation & alert modal dialogs
│   ├── Dropdown.tsx                 # Menu popovers
│   ├── Charts.tsx                   # Wrapped Recharts components (Line, Bar, Pie)
│   ├── Skeleton.tsx                 # Shimmer effect loading placeholders
│   ├── EmptyState.tsx               # Illustrative empty data views
│   ├── Spinner.tsx                  # Loading indicators
│   └── Drawer.tsx                   # Slide-out mobile drawers
```

### Component Standards & Contracts
- **Props Definition**: Every component explicitly exports an interface named `<ComponentName>Props`.
- **Ref Forwarding**: All low-level UI elements (`Input`, `Button`, `Select`) use `React.forwardRef` to integrate smoothly with React Hook Form.
- **Styling Customization**: Components accept an optional `className?: string` prop merged via `clsx` and `tailwind-merge`.

---

## 5. Routing Structure

Routing is managed via React Router (v6/v7) with centralized definitions in `src/routes/AppRoutes.tsx`.

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
                                   ├── /dashboard                  ├── /admin
                                   ├── /exams                      ├── /admin/users
                                   ├── /mock-tests                 ├── /admin/questions
                                   └── /attempt/:id                └── /admin/audit-logs
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
| `/dashboard` | `StudentLayout` | `ProtectedRoute` | `STUDENT`, etc. | `DashboardPage` |
| `/exam-tracks` | `StudentLayout` | `ProtectedRoute` | Authenticated | `ExamTracksPage` |
| `/exam-tracks/:slug` | `StudentLayout` | `ProtectedRoute` | Authenticated | `ExamDetailPage` |
| `/subjects` | `StudentLayout` | `ProtectedRoute` | Authenticated | `SubjectsPage` |
| `/topics` | `StudentLayout` | `ProtectedRoute` | Authenticated | `TopicsPage` |
| `/mock-tests` | `StudentLayout` | `ProtectedRoute` | Authenticated | `MockTestsPage` |
| `/mock-tests/:slug` | `StudentLayout` | `ProtectedRoute` | Authenticated | `MockTestDetailPage` |
| `/attempts/:id/execute` | Clean Shell | `ProtectedRoute` | Authenticated | `AttemptExecutionPage` |
| `/results/:id` | `StudentLayout` | `ProtectedRoute` | Authenticated | `AttemptResultPage` |
| `/results/:id/review` | `StudentLayout` | `ProtectedRoute` | Authenticated | `AttemptReviewPage` |
| `/progress` | `StudentLayout` | `ProtectedRoute` | Authenticated | `ProgressPage` |
| `/weak-topics` | `StudentLayout` | `EntitlementGuard` | `access:weak_topic_analytics` | `WeakTopicsPage` |
| `/notes` | `StudentLayout` | `ProtectedRoute` | Authenticated | `NotesCatalogPage` |
| `/notes/:slug` | `StudentLayout` | `EntitlementGuard` | Conditional `access:pdf_notes` | `NoteDetailPage` |
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

Authentication aligns 100% with `djangorestframework-simplejwt` specified in Section 1.5 of `API_DESIGN.md`.

```
                  AUTHENTICATION & REFRESH FLOW MATRIX
                  
     Client App                   Axios Interceptor               Django DRF API
         |                                |                             |
         |--- 1. Login Request ---------->|                             |
         |    (POST /api/v1/auth/login/)  |---------------------------->|
         |                                |                             |
         |<-- 2. Issue Access + Refresh --|<----------------------------|
         |    (Store Access in Store,     |                             |
         |     Refresh in Storage/Cookie) |                             |
         |                                |                             |
         |--- 3. Protected Request ------>| Authorization: Bearer <token>
         |                                |---------------------------->|
         |                                |<-- 4. 401 Token Expired ----|
         |                                |                             |
         |                                |-- 5. Automatic Refresh ---->|
         |                                |   (POST /api/v1/auth/refresh)|
         |                                |                             |
         |                                |<-- 6. New Access Token -----|
         |                                |                             |
         |<-- 7. Transparent Retry ------>|---------------------------->|
```

### Flow Specifications

1. **Token Storage**:
   - **Access Token (15 min TTL)**: Maintained in memory within Zustand `useAuthStore.ts` state.
   - **Refresh Token (7 days TTL)**: Stored securely in `LocalStorage` (or HttpOnly cookie when configured).

2. **Session Initialization & Restoration**:
   - At application mount (`main.tsx`), `useAuthStore.getState().initializeAuth()` executes.
   - Reads refresh token, verifies validity, and requests a fresh access token via `POST /api/v1/auth/refresh/`.

3. **Silent Queue-Based Token Refresh**:
   - If a request receives an HTTP 401 `AUTHENTICATION_FAILED` response:
   - The Axios response interceptor pauses outgoing requests and queues them.
   - Triggers a single refresh request to `/api/v1/auth/refresh/`.
   - On success, updates access token, updates default header, and retries all queued requests.
   - On failure, clears auth state and redirects to `/login?session_expired=true`.

4. **Logout Procedure**:
   - Calls `POST /api/v1/auth/logout/` with the active refresh token to revoke it in the backend database.
   - Purges local stores and resets QueryClient state.

---

## 7. State Management

Zustand is used for client-only local & persistent state. Server state is managed exclusively via TanStack Query v5.

```text
src/store/
├── useAuthStore.ts                  # Auth state, identity, roles, entitlements
├── useThemeStore.ts                 # Light/Dark mode state
├── useNotificationStore.ts          # Unread notification counter & drawer visibility
├── useBookmarkStore.ts              # Optimistic local bookmark toggles
├── usePreferencesStore.ts           # Student UX preferences (compact mode, sound)
├── useMockTestStore.ts              # Active test overview selection
├── useAttemptStore.ts               # Assessment execution session (answers, remaining time)
├── useSubscriptionStore.ts          # Active plan status & capability flags
└── useAdminStore.ts                 # Active admin filters & selection drawer state
```

### Store Schemas

#### 1. Auth Store (`useAuthStore.ts`)
```typescript
interface AuthState {
  user: UserIdentity | null;
  accessToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  roles: string[];
  entitlements: string[];
  setAuth: (user: UserIdentity, tokens: JwtTokens) => void;
  clearAuth: () => void;
  hasRole: (role: string | string[]) => boolean;
  hasEntitlement: (entitlement: string) => boolean;
}
```

#### 2. Assessment Attempt Store (`useAttemptStore.ts`)
```typescript
interface AnswerEntry {
  questionId: string;
  selectedOptionId: string | null;
  timeSpentSeconds: number;
}

interface AttemptState {
  attemptId: string | null;
  startedAt: string | null;
  serverExpiryTime: string | null;
  remainingSeconds: number;
  answers: Record<string, AnswerEntry>; // Map questionId -> AnswerEntry
  currentQuestionIndex: number;
  isSubmitting: boolean;
  initAttempt: (attemptId: string, expiryTime: string, questionsCount: number) => void;
  selectOption: (questionId: string, optionId: string) => void;
  updateTimer: (remaining: number) => void;
  resetAttempt: () => void;
}
```

---

## 8. API Layer

Network communication utilizes a configured Axios client instance (`src/services/api.client.ts`).

### Response Envelopes & Contracts (Strictly aligned with RFC 7807 and Section 1.3 of `API_DESIGN.md`)

```typescript
// Standard API Envelope Types
export interface ApiSuccessEnvelope<T> {
  success: true;
  message: string;
  data: T;
  meta: {
    timestamp: string;
    version: string;
    request_id: string;
  };
}

export interface ApiPaginatedEnvelope<T> {
  success: true;
  message: string;
  data: T[];
  meta: {
    pagination: {
      total_items: number;
      total_pages: number;
      current_page: number;
      page_size: number;
      next_page: string | null;
      previous_page: string | null;
    };
    timestamp: string;
    version: string;
    request_id: string;
  };
}

export interface ApiErrorEnvelope {
  success: false;
  error: {
    code: string;
    message: string;
    status_code: number;
    details?: Array<{ field: string; code: string; message: string }>;
    timestamp: string;
    request_id: string;
  };
}
```

### Interceptors & Retry Architecture
- **Request Interceptor**: Injects `Authorization: Bearer <access_token>` header automatically.
- **Response Interceptor**:
  - Handles 401 Unauthorized via token refresh queue.
  - Formats raw Axios errors into structured `ApiErrorEnvelope` objects.
- **Request Cancellation**: Custom hooks use `AbortController` signals to cancel stale network requests upon component unmount or fast query key navigation.
- **Presigned Upload Strategy**: Interacts with `POST /api/v1/uploads/presigned-url/` or Cloudinary Widget script to safely obtain presigned PUT upload URLs.

---

## 9. Form Validation

Forms are constructed using **React Hook Form** paired with **Zod** schemas via `@hookform/resolvers/zod`.

### Validation Strategy Matrix

| Form Name | Schema Location | Key Rules & Constraints |
| :--- | :--- | :--- |
| **Login** | `auth.schema.ts` | Email required, valid format. Password required (min 8 chars). |
| **Register** | `auth.schema.ts` | Valid email, unique rules, password policy (min 8, upper, lower, number, special), full name. |
| **Profile Update** | `profile.schema.ts` | Full name max 255, optional phone (E.164 format), valid UUID for target exam track. |
| **Question Editor** | `question.schema.ts` | Stem text required, minimum 2 options, exactly 1 option flagged correct (for single choice). |
| **Question Report** | `questionReport.schema.ts` | Category enum required (`WRONG_KEY`, `TYPO`, etc.), comment min 10 chars. |
| **Checkout** | `subscription.schema.ts` | Valid plan code enum (`PREMIUM_MONTHLY`). |

### Reusable Validation Example

```typescript
// src/features/auth/validation/auth.schema.ts
import { z } from 'zod';

export const registerSchema = z.object({
  email: z.string().email('Please enter a valid email address.'),
  password: z
    .string()
    .min(8, 'Password must be at least 8 characters.')
    .regex(/[A-Z]/, 'Password must contain at least one uppercase letter.')
    .regex(/[a-z]/, 'Password must contain at least one lowercase letter.')
    .regex(/[0-9]/, 'Password must contain at least one number.')
    .regex(/[^A-Za-z0-9]/, 'Password must contain at least one special character.'),
  full_name: z.string().min(2, 'Full name is required.').max(255),
  phone_number: z.string().optional(),
  target_exam_track_id: z.string().uuid().optional(),
});

export type RegisterFormValues = z.infer<typeof registerSchema>;
```

---

## 10. UI Layouts

Layout wrappers enforce visual hierarchy and consistent user navigation context.

```text
                             LAYOUT ARCHITECTURE
                             
   GuestLayout          StudentLayout         AdminLayout          AuthLayout
+---------------+    +---------------+     +---------------+    +---------------+
|    Header     |    | Top Nav / Bar |     | Admin Header  |    | Minimal Logo  |
+---------------+    +---------------+     +---------------+    +---------------+
|               |    | S |           |     | S |           |    |               |
| Content Area  |    | i | Content   |     | i | Admin     |    | Centered Form |
|               |    | d | Area      |     | d | Content   |    | Card          |
|               |    | e |           |     | e | Area      |    |               |
+---------------+    +---------------+     +---------------+    +---------------+
|    Footer     |    | Sticky Mobile |     | Dense Footer  |    | Simple Footer |
+---------------+    +---------------+     +---------------+    +---------------+
```

1. **Guest Layout (`GuestLayout.tsx`)**:
   - Top marketing navigation header, hero/landing structure, detailed footer with link columns.
2. **Student Layout (`StudentLayout.tsx`)**:
   - Collapsible desktop sidebar, mobile responsive bottom navigation bar, notification bell, profile popover dropdown, persistent target exam goal status.
3. **Admin Layout (`AdminLayout.tsx`)**:
   - Dense administrative sidebar navigation, audit logs trigger, environment badge (`STAGING` / `PRODUCTION`), privilege escalation notification.
4. **Dashboard Layout (`DashboardLayout.tsx`)**:
   - Specialized student dashboard shell with grid arrangement for quick analytics cards and recommended practice sets.
5. **Auth Layout (`AuthLayout.tsx`)**:
   - Centered container card with platform branding, focused distraction-free layout.
6. **Error Layout (`ErrorLayout.tsx`)**:
   - Full-page error display shell for 404 Not Found, 403 Forbidden, and 500 Server Error states.

---

## 11. Responsive Design Strategy

The application is built **mobile-first** using Tailwind CSS grid and flexbox primitives.

### Responsive Breakpoint Standard

| Breakpoint Prefix | Min Width | Target Device Class | Primary UI Adaptation |
| :--- | :--- | :--- | :--- |
| `default` | `< 640px` | Mobile phones | Stacked cards, bottom bar navigation, drawer popups |
| `sm` | `640px` | Large phones / small tablets | 2-column grid cards, condensed form groups |
| `md` | `768px` | Tablets | Dual-column dashboards, expanded table layouts |
| `lg` | `1024px` | Laptops / Desktops | Persistent sidebar, multi-column analytics |
| `xl` | `1280px` | Desktop screens | Full multi-panel assessment workspace |
| `2xl` | `1536px` | Ultra-wide displays | Centered max-width containers (`max-w-7xl`) |

### Accessibility (a11y) & Dark Mode
- **WAI-ARIA Compliance**: Interactive controls (`Modal`, `Dropdown`, `Drawer`) have proper `aria-modal`, `aria-expanded`, and `role` attributes.
- **Keyboard Navigation**: Full focus ring visibility (`focus-visible:ring-2 focus-visible:ring-primary-500`).
- **Dark Mode (Future-Ready)**: Uses CSS variable design tokens mapped in Tailwind (`bg-background text-foreground`). Dark class toggled via `useThemeStore.ts`.

---

## 12. Performance Optimization

Performance is treated as a core architectural requirement.

1. **Code Splitting & Route Splitting**:
   - Dynamic page imports via `React.lazy()` and `React.Suspense` for heavy routes (`AttemptExecutionPage`, `AdminAuditLogsPage`, `ProgressPage`).
2. **Component & Calculation Memoization**:
   - Strategic application of `useMemo` and `useCallback` for question navigation grids and complex score calculation utilities.
3. **Image & Asset Optimization**:
   - Presigned CDN URLs served via WebP/AVIF formats with explicit height/width attributes.
4. **TanStack Query v5 Caching Strategy**:
   - `staleTime: 1000 * 60 * 5` (5 minutes default for student data).
   - `staleTime: 1000 * 60 * 60` (60 minutes for taxonomy: tracks, subjects, topics).
   - `gcTime: 1000 * 60 * 30` (30 minutes garbage collection).
5. **Debounce Optimization**:
   - Search input fields use `useDebounce` hook (300ms) to eliminate redundant API requests.

---

## 13. Security

Security practices strictly enforce frontend safety guidelines.

1. **JWT Security**:
   - Short-lived access tokens kept in memory; never saved to `localStorage` to mitigate XSS exposure.
2. **XSS Prevention**:
   - All dynamic text (`notes.content_markdown`, `question_explanations.explanation_text`) sanitized via DOMPurify before rendering via `dangerouslySetInnerHTML`.
3. **CSRF Protection**:
   - Backend APIs enforce custom headers (`X-Requested-With: XMLHttpRequest`) and SameSite cookie attributes.
4. **Authorization & Entitlement Guards**:
   - Double-checked client-side route guards (`RoleGuard`, `EntitlementGuard`) backed by hard server-side Django DRF permission enforcement.
5. **Secure Communication**:
   - HTTPS enforced on all API endpoints. Secrets strictly injected via Vite environment variables (`import.meta.env.VITE_API_BASE_URL`).

---

## 14. Error Handling

Error handling provides clear, actionable feedback to users.

```
                         ERROR HANDLING LAYOUT
                         
                   Global React ErrorBoundary
                               |
       +-----------------------+-----------------------+
       |                                               |
       v                                               v
  API Errors (Axios)                            UI Runtime Errors
(RFC 7807 Envelopes)                          (Caught by Boundary)
  ├── 400 Validation -> Form Error Highlighting        └── Render Fallback UI
  ├── 401 Expired    -> Token Refresh / Login           with Retry Action
  ├── 403 Forbidden  -> 403 Page / Toast
  ├── 404 Not Found  -> 404 Page
  ├── 429 Limit      -> Rate Limit Warning Toast
  └── 500 Server     -> Global Error Toast Banner
```

1. **Global React Error Boundary (`ErrorBoundary.tsx`)**:
   - Catches unhandled React render crashes and presents a friendly recovery component.
2. **RFC 7807 Standard Error Translation**:
   - Standardized API error parser maps backend error details directly to React Hook Form fields or `react-hot-toast` alerts.
3. **Toast Notification System**:
   - Centralized alerts via `react-hot-toast` for success feedback, background auto-save acknowledgements, and network failures.
4. **Offline Resilience (`OfflineBanner.tsx`)**:
   - Monitored via `useOnlineStatus` hook. Displays top banner when internet connectivity drops during an active test attempt.

---

## 15. Testing Strategy

```text
tests/
├── unit/                            # Pure function & utility test coverage
│   ├── formatters.test.ts
│   ├── validators.test.ts
│   └── math.utils.test.ts
├── components/                      # UI primitive component tests (RTL + Vitest)
│   ├── Button.test.tsx
│   ├── Input.test.tsx
│   └── Table.test.tsx
├── features/                        # Integration feature flow tests
│   ├── auth/LoginForm.test.tsx
│   ├── attempt-engine/Timer.test.tsx
│   └── subscriptions/Checkout.test.tsx
└── e2e/                             # End-to-end user journey tests (Playwright)
    ├── auth.spec.ts
    ├── mock-test-attempt.spec.ts
    └── subscription-purchase.spec.ts
```

### Framework Selection
- **Unit & Component Testing**: Vitest + React Testing Library (RTL).
- **API Mocking**: Mock Service Worker (MSW) to mock Django REST API endpoints during testing.
- **End-to-End Testing**: Playwright for cross-browser student assessment and admin flows.

---

## 16. Development Guidelines

### 1. Naming Conventions
- **Files & Directories**:
  - Components: `PascalCase.tsx` (e.g., `QuestionCard.tsx`)
  - Hooks: `camelCase.ts` prefixed with `use` (e.g., `useAttemptStore.ts`)
  - Services/Utils/Types: `kebab-case.ts` or `camelCase.ts` (e.g., `api.client.ts`, `auth.types.ts`)
  - Feature Folders: `kebab-case` (e.g., `attempt-engine/`)

### 2. TypeScript & Code Quality Rules
- No `any` or `implicit any`. Use explicit interface or type declarations.
- Prefer `interface` for object schemas and component props; use `type` for unions/intersections.
- Unused variables trigger lint warnings; strict null checks enabled in `tsconfig.json`.

### 3. Import Order Hierarchy
```typescript
// 1. External React & Library dependencies
import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { LucideClock } from 'lucide-react';

// 2. Internal UI Primitives & Layouts
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';

// 3. Feature-specific hooks, services, & components
import { useStartAttempt } from '../hooks/useStartAttempt';

// 4. Types, Utils, & Constants
import type { MockTest } from '@/types/domain.types';
import { formatDuration } from '@/utils/formatters';
```

---

## 17. Future Scalability

The architecture is designed to support future core features seamlessly without refactoring existing feature modules.

```
                           FUTURE EXPANSION ROADMAP
                           
  +-------------------+   +-------------------+   +-------------------+
  |     AI Tutor      |   | Discussion Forum  |   |  Adaptive Testing |
  | (src/features/ai) |   | (src/features/    |   | (src/features/    |
  |                   |   |    discussions)   |   |   adaptive-engine)|
  +-------------------+   +-------------------+   +-------------------+
            |                       |                       |
            v                       v                       v
+-------------------------------------------------------------------+
|               EXISTING PREPORA FRONTEND CORE INFRASTRUCTURE       |
|    (React 19 + TanStack Query + Zustand Stores + Feature Modules)   |
+-------------------------------------------------------------------+
```

1. **AI Tutor Module (`src/features/ai-tutor/`)**:
   - Ready for WebSocket or Server-Sent Events (SSE) streaming integration for step-by-step MCQ explanation hints.
2. **Discussion Forum Module (`src/features/discussions/`)**:
   - Extends taxonomy hierarchy (`Topic` $\rightarrow$ `Thread` $\rightarrow$ `Comment`).
3. **Leaderboards & Gamification (`src/features/leaderboard/`)**:
   - Reuses existing student progress analytics models to render real-time rank tables.
4. **Verified Certificates (`src/features/certificates/`)**:
   - PDF generation rendering and verification badge viewer.
5. **Adaptive Testing Engine (`src/features/adaptive-engine/`)**:
   - Real-time Item Response Theory (IRT) question selection dynamically switching next question difficulty based on student performance.
6. **Internationalization (i18n)**:
   - Structured for easy integration of `react-i18next` for English and Urdu language toggling.
7. **PWA & Offline Mode**:
   - Ready for Workbox service worker caching for offline test taking and background sync.

---

## 18. Verification & Architectural Compliance

| Requirement / Constraint | Architecture Implementation | Status |
| :--- | :--- | :--- |
| **Backend Endpoint 1:1 Alignment** | Aligned with all 18 DRF modules in `API_DESIGN.md` | Verified |
| **Fixed Tech Stack Compliance** | React 19, TypeScript, Vite, Tailwind, TanStack Query, Zustand, Axios, Zod, React Hook Form | Verified |
| **Feature-First Architecture** | All 21 feature modules specified with explicit folder breakdowns | Verified |
| **Assessment Execution Reliability** | Dedicated `useAttemptStore.ts` with local timer & background auto-save | Verified |
| **RBAC & Entitlements** | Dual-layer guards (`RoleGuard`, `EntitlementGuard`) matching Django Enum codes | Verified |
| **RFC 7807 Error Handling** | Standard error envelopes and React Error Boundaries | Verified |
