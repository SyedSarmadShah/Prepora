# Frontend Architecture for Prepora

## 1. Overview

The frontend should be built as a modern, mobile-first Next.js application that feels trustworthy, fast, and focused on learning. The product is not a generic content portal; it must support high-friction actions such as timed mock tests, answer review, dashboards, analytics, notes, videos, subscriptions, and admin operations.

## 2. Technology Stack

- Next.js for routing, SSR, SEO, and app structure
- TypeScript for safe contracts and maintainability
- Tailwind CSS for layout and styling
- ShadCN UI for consistent, accessible design primitives
- TanStack Query for server-state management
- Framer Motion for focused UI transitions and engagement moments

## 3. Frontend Principles

- Use server rendering for public and SEO-sensitive pages.
- Keep business logic out of pages and into feature modules.
- Use TanStack Query for backend-driven data.
- Keep UI state local unless it truly needs global scope.
- Prioritize accessibility and mobile usability.
- Keep the student experience fast and distraction-free.

## 4. Folder Structure

```text
app/
  (public)/
  (auth)/
  (student)/
  (admin)/
  globals.css
  layout.tsx
  page.tsx
components/
  ui/
  layout/
  shared/
features/
  auth/
  dashboard/
  practice/
  mock-tests/
  results/
  leaderboard/
  notes/
  videos/
  profile/
  settings/
  subscriptions/
  notifications/
  admin/
lib/
  api/
  auth/
  utils/
  constants/
hooks/
store/
types/
public/
tests/
```

### Folder Explanation

- app/: route-level organization and layouts
- components/ui/: reusable design system primitives
- components/layout/: headers, sidebars, footers, page chrome
- features/: domain-specific modules such as auth, practice, and admin
- lib/: API layer, auth helpers, constants, formatting helpers
- hooks/: reusable hooks for data fetching, form logic, and interaction patterns
- store/: light client-side global state only where needed
- types/: shared TypeScript models and API response contracts
- public/: static assets and media placeholders
- tests/: unit, component, and end-to-end tests

## 5. Routing Strategy

### Route Groups

- Public routes: home, about, pricing, login, signup, 404
- Student routes: dashboard, practice, mock tests, results, leaderboard, notes, videos, profile, settings
- Admin routes: admin dashboard, question management, subject management, users, analytics

### Routing Principles

- Public pages should be SEO-friendly and server-rendered.
- Auth pages should be lightweight and focused.
- Student pages should be highly interactive and data-rich.
- Admin pages should be structured and dense for power users.

## 6. Layouts

### Public Layout

- top nav
- hero and content sections
- footer
- CTA-driven structure

### Auth Layout

- minimal layout with a centered panel
- clear focus on sign-in and sign-up actions

### Student Layout

- sidebar or top navigation on mobile
- profile access and notifications
- persistent study context

### Admin Layout

- heavier sidebar navigation
- content management and analytics panels
- clear hierarchy for operations

## 7. Components

### Shared UI Components

- Button
- Input
- Select
- Modal
- Drawer
- Table
- Card
- Badge
- Alert
- Tabs
- Skeleton
- Breadcrumb

### Feature Components

- question runner
- answer option list
- mock test timer
- result summary card
- leaderboard table
- video player shell
- note reader shell
- admin content editor panel
- analytics chart container

## 8. Reusable UI System

The design system should standardize:

- spacing scale
- typography scale
- color tokens for states and brand usage
- form layout patterns
- empty states and loading states
- modal and drawer interactions
- accessible focus styles

## 9. Feature-Based Architecture

The product should be organized by learning and operational features:

- auth
- dashboard
- practice
- mock-tests
- results
- leaderboard
- notes
- videos
- profile
- settings
- subscriptions
- notifications
- admin

Each feature module should own:

- UI components
- data hooks
- mutation hooks
- local helpers
- feature-specific validation logic

## 10. State Management

### Server State

Use TanStack Query for:

- user profile
- dashboard data
- practice data
- mock test detail
- results and reviews
- leaderboard snapshots
- notifications and bookmarks
- subscription status

### Client State

Use local state or lightweight global state for:

- theme preference
- mobile sidebar visibility
- test timer UI state
- draft form inputs
- temporary filters

## 11. API Layer

The frontend should interact with the backend through a dedicated API layer.

### Responsibilities

- centralize HTTP requests
- attach JWT auth headers
- normalize response shapes
- handle errors consistently
- support pagination and filters
- avoid direct ad-hoc fetches from components

### Communication Pattern

- public pages fetch server-rendered data where possible
- authenticated pages use TanStack Query to fetch and mutate data
- test submission and result generation flow through clear mutation states

## 12. Authentication

The frontend should support:

- login
- signup
- password reset
- token refresh behavior
- redirected access after login
- clear handling for expired sessions

Auth state should be restored at app startup and protected routes should avoid flashing unauthorized content.

## 13. Protected Routes

Route protection should happen at multiple layers:

- middleware for entry-level redirect behavior
- layout guards for role-based access
- page-level checks for fine-grained authorization

## 14. Error Handling

The UI should have consistent error states for:

- network failures
- validation errors
- authorization failures
- empty states
- payment issues
- upload failures

Errors should be actionable rather than purely informational.

## 15. Loading States

Use appropriate loading patterns:

- skeletons for lists and cards
- spinners for small actions
- full-page loading for auth restore and test initialization
- progressive loading for dashboards and analytics

## 16. Theme Support

The product should support:

- light and dark mode
- user preference persistence
- accessible contrast and semantic color usage

## 17. Responsive Design

The UI must be mobile-first and support:

- small-screen navigation
- compact forms and cards
- sticky test controls
- adaptive tables and detail views
- readable content consumption on phones and tablets

## 18. Accessibility

Accessibility must be built in from the start.

Required considerations:

- keyboard navigation
- visible focus states
- semantic markup
- form labels and error descriptions
- color contrast
- non-color cues for correctness and status
- screen-reader-friendly navigation

## 19. SEO

Public pages should be optimized for search and sharing.

SEO focus areas:

- landing pages
- exam category pages
- subject and topic pages
- announcement pages if public
- metadata and Open Graph support
- clean canonical URLs

## 20. Performance Optimization

Performance should be treated as a first-class requirement.

Recommended optimizations:

- server components where practical
- route-based code splitting
- lazy loading for charts, editors, and media-heavy widgets
- optimized image and video loading
- TanStack Query caching for stable lists and dashboards
- memoization only where it clearly helps

## 21. How Pages Communicate with the Backend

### Public pages

- fetch exam catalog, landing content, public notes previews, and announcements

### Auth pages

- send login, signup, and password reset requests

### Student pages

- use queries and mutations for dashboard data, practice sets, attempts, results, progress, bookmarks, notifications, and certificates

### Test pages

- start attempts, save progress, submit tests, and receive results asynchronously

### Admin pages

- fetch content queue, manage questions and subjects, manage users, and view analytics through admin-specific APIs

## 22. Summary

The frontend should be a feature-driven, mobile-first, accessible, and scalable Next.js application. The architecture should allow a fast MVP while staying strong enough for future growth into analytics, subscriptions, and broader content operations.
