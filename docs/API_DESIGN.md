# API Design for Prepora

## 1. API Principles

The API should be versioned, predictable, secure, and consistent.

### Conventions

- Base path: /api/v1
- Authentication: Bearer JWT
- Response format: JSON
- Pagination: page, limit, sortBy, sortOrder
- Filtering: query parameters on list endpoints
- Errors: consistent error envelope with message, code, and details

## 2. Common Response Shape

### Success Response

```text
{
  "data": { ... },
  "message": "Success",
  "meta": {
    "page": 1,
    "limit": 20,
    "total": 100
  }
}
```

### Error Response

```text
{
  "message": "Validation failed",
  "code": "VALIDATION_ERROR",
  "details": [
    {
      "field": "email",
      "reason": "Email is required"
    }
  ]
}
```

## 3. Authentication APIs

| Method | Route | Purpose |
|---|---|---|
| POST | /api/v1/auth/register | Create a new user account |
| POST | /api/v1/auth/login | Authenticate and issue tokens |
| POST | /api/v1/auth/refresh | Refresh access token |
| POST | /api/v1/auth/logout | Revoke active session |
| POST | /api/v1/auth/forgot-password | Send password reset request |
| POST | /api/v1/auth/reset-password | Reset password using reset token |
| GET | /api/v1/auth/me | Retrieve current authenticated user |

### Request/Response Notes

- Register requires fullName, email, password, and optional phone.
- Login returns accessToken, refreshToken, and user profile.
- Refresh requires a valid refresh token.
- Forgot password should not reveal whether an account exists.

## 4. User APIs

| Method | Route | Purpose |
|---|---|---|
| GET | /api/v1/users/me | Get current profile |
| PATCH | /api/v1/users/me | Update profile |
| GET | /api/v1/users/me/progress | Retrieve personal progress summary |
| GET | /api/v1/users/me/activity | Retrieve recent activity |

## 5. Dashboard APIs

| Method | Route | Purpose |
|---|---|---|
| GET | /api/v1/dashboard/student | Student overview dashboard |
| GET | /api/v1/dashboard/analytics | Analytics view for student performance |
| GET | /api/v1/dashboard/recommendations | Suggested study actions |
| GET | /api/v1/dashboard/admin | Admin overview dashboard |

## 6. Subject APIs

| Method | Route | Purpose |
|---|---|---|
| GET | /api/v1/subjects | List subjects |
| GET | /api/v1/subjects/{subjectId} | Get a single subject |
| GET | /api/v1/subjects/{subjectId}/topics | List topics under a subject |
| POST | /api/v1/subjects | Create a subject |
| PATCH | /api/v1/subjects/{subjectId} | Update a subject |
| DELETE | /api/v1/subjects/{subjectId} | Delete or archive a subject |

## 7. Topic APIs

| Method | Route | Purpose |
|---|---|---|
| GET | /api/v1/topics | List topics |
| GET | /api/v1/topics/{topicId} | Get a single topic |
| GET | /api/v1/topics/{topicId}/questions | List questions for a topic |
| POST | /api/v1/topics | Create a topic |
| PATCH | /api/v1/topics/{topicId} | Update a topic |
| DELETE | /api/v1/topics/{topicId} | Delete or archive a topic |

## 8. Question APIs

| Method | Route | Purpose |
|---|---|---|
| GET | /api/v1/questions | List questions |
| GET | /api/v1/questions/{questionId} | Get a question |
| POST | /api/v1/questions | Create a question |
| PATCH | /api/v1/questions/{questionId} | Update a question |
| DELETE | /api/v1/questions/{questionId} | Delete or archive a question |
| POST | /api/v1/questions/{questionId}/submit-answer | Submit one answer for review or practice |

### Question API Notes

- Public question browsing should not expose correct answers.
- Admin or editor routes should allow full metadata and answer visibility.
- Question creation should validate option count and correct answer mapping.

## 9. Mock Test APIs

| Method | Route | Purpose |
|---|---|---|
| GET | /api/v1/mock-tests | List mock tests |
| GET | /api/v1/mock-tests/{mockTestId} | Get mock test details |
| GET | /api/v1/mock-tests/{mockTestId}/questions | Load questions for a test |
| POST | /api/v1/mock-tests/{mockTestId}/attempts | Start a new attempt |
| GET | /api/v1/attempts/{attemptId} | Get current attempt status |
| POST | /api/v1/attempts/{attemptId}/save-progress | Save partial progress |
| POST | /api/v1/attempts/{attemptId}/submit | Submit completed test |
| POST | /api/v1/mock-tests | Create a mock test |
| PATCH | /api/v1/mock-tests/{mockTestId} | Update a mock test |
| DELETE | /api/v1/mock-tests/{mockTestId} | Delete or archive a mock test |

### Mock Test Notes

- The server should guard against duplicate active attempts where business rules require it.
- Submission should return score summary and result reference.

## 10. Result APIs

| Method | Route | Purpose |
|---|---|---|
| GET | /api/v1/results/{resultId} | Get a result detail |
| GET | /api/v1/attempts/{attemptId}/result | Get result for an attempt |
| GET | /api/v1/users/me/results | Get current user result history |
| GET | /api/v1/results/{resultId}/review | Review answer-by-answer explanation |

## 11. Leaderboard APIs

| Method | Route | Purpose |
|---|---|---|
| GET | /api/v1/leaderboards | List leaderboard snapshots |
| GET | /api/v1/leaderboards/me | Get current user ranking |
| GET | /api/v1/leaderboards/{leaderboardId} | Get a leaderboard snapshot |

## 12. Announcement APIs

| Method | Route | Purpose |
|---|---|---|
| GET | /api/v1/announcements | List announcements |
| GET | /api/v1/announcements/{announcementId} | Get a single announcement |
| POST | /api/v1/announcements | Create an announcement |
| PATCH | /api/v1/announcements/{announcementId} | Update an announcement |
| DELETE | /api/v1/announcements/{announcementId} | Delete or archive an announcement |

## 13. Admin APIs

| Method | Route | Purpose |
|---|---|---|
| GET | /api/v1/admin/users | List users |
| PATCH | /api/v1/admin/users/{userId}/status | Change account status |
| PATCH | /api/v1/admin/users/{userId}/role | Change role |
| GET | /api/v1/admin/content-queue | Review content pending approval |
| POST | /api/v1/admin/content-queue/{itemId}/approve | Approve content |
| POST | /api/v1/admin/content-queue/{itemId}/reject | Reject content |
| GET | /api/v1/admin/audit-logs | View audit logs |
| GET | /api/v1/admin/analytics | View admin analytics |

## 14. Payment APIs

| Method | Route | Purpose |
|---|---|---|
| GET | /api/v1/subscriptions/me | Retrieve current subscription |
| POST | /api/v1/subscriptions/checkout | Start checkout flow |
| GET | /api/v1/subscriptions/history | View billing history |
| POST | /api/v1/payments/webhook | Receive provider webhook |
| GET | /api/v1/payments/history | Get payment history |
| GET | /api/v1/payments/{paymentId} | Get a payment detail |

## 15. Notification APIs

| Method | Route | Purpose |
|---|---|---|
| GET | /api/v1/notifications | List notifications |
| PATCH | /api/v1/notifications/{notificationId}/read | Mark one notification as read |
| PATCH | /api/v1/notifications/read-all | Mark all notifications as read |
| DELETE | /api/v1/notifications/{notificationId} | Delete a notification |
| GET | /api/v1/notifications/preferences | Get notification preferences |
| PATCH | /api/v1/notifications/preferences | Update notification preferences |

## 16. Bookmark APIs

| Method | Route | Purpose |
|---|---|---|
| GET | /api/v1/bookmarks | List saved bookmarks |
| POST | /api/v1/bookmarks | Add a bookmark |
| DELETE | /api/v1/bookmarks/{bookmarkId} | Remove a bookmark |
| POST | /api/v1/bookmarks/toggle | Toggle a bookmark state |

## 17. Certificate APIs

| Method | Route | Purpose |
|---|---|---|
| GET | /api/v1/certificates | List certificates for current user |
| GET | /api/v1/certificates/{certificateId} | Get certificate detail |
| GET | /api/v1/certificates/{certificateId}/download | Download certificate |
| GET | /api/v1/certificates/verify/{certificateNumber} | Verify a certificate |
| POST | /api/v1/admin/certificates | Issue a certificate |

## 18. Common Status Codes

- 200 OK
- 201 Created
- 204 No Content
- 400 Bad Request
- 401 Unauthorized
- 403 Forbidden
- 404 Not Found
- 409 Conflict
- 422 Unprocessable Entity
- 429 Too Many Requests
- 500 Internal Server Error

## 19. Validation Rules

- Ensure required fields are present.
- Validate enum values and field lengths.
- Ensure ownership checks for personal resources.
- Prevent duplicate bookmarks and duplicate active attempts where necessary.
- Require role checks for admin operations.

## 20. API Design Guidance

- Keep list endpoints paginated and filterable.
- Keep mutations consistent and predictable.
- Do not expose answers in public question endpoints.
- Separate internal admin endpoints from student-facing endpoints.
- Make the backend contract stable enough for frontend teams to build confidently.
