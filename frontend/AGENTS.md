# AGENTS.md

# NurseKonnect Frontend

## Overview

NurseKonnect Frontend is a modern, secure, responsive React application that consumes the NurseKonnect Django REST API.

The frontend connects patients and nurses through a simple, fast, mobile-first user experience.

Primary goals:

- Minimalistic design
- Excellent usability
- Healthcare-grade privacy
- Secure JWT authentication
- Responsive mobile experience
- Clean component architecture
- Strong TypeScript typing
- Production readiness

---

# Technology Stack

Mandatory:

```text
React 19+
TypeScript
Vite
Tailwind CSS
shadcn/ui
TanStack Query
React Router
Axios
React Hook Form
Zod
```

Optional:

```text
Socket.IO Client
Leaflet
OpenStreetMap
```

---

# Project Structure

```text
frontend/

├── public/
│
├── src/
│
│   ├── app/
│   │
│   ├── api/
│   │
│   ├── auth/
│   │
│   ├── components/
│   │
│   ├── features/
│   │   ├── patients/
│   │   ├── nurses/
│   │   ├── requests/
│   │   ├── tracking/
│   │   ├── visits/
│   │   ├── ratings/
│   │   └── notifications/
│   │
│   ├── hooks/
│   │
│   ├── layouts/
│   │
│   ├── pages/
│   │
│   ├── routes/
│   │
│   ├── services/
│   │
│   ├── stores/
│   │
│   ├── types/
│   │
│   ├── utils/
│   │
│   └── lib/
│
├── tests/
│
└── docs/
```

---

# Design Philosophy

The UI should feel:

- Modern
- Clean
- Professional
- Healthcare focused

Avoid:

- Excessive animations
- Clutter
- Complex navigation
- Unnecessary dashboards

Use:

- Cards
- Tables
- Drawers
- Dialogs
- Sheets
- Tabs

from shadcn/ui.

---

# Authentication

The frontend must support:

```text
JWT Access Token
JWT Refresh Token
```

Backend provides:

```text
POST /api/auth/register/
POST /api/auth/login/
POST /api/auth/logout/
POST /api/auth/refresh/
POST /api/auth/verify-email/
POST /api/auth/verify-phone/
```

---

# JWT Security Rules

Never store JWT tokens in:

```text
localStorage
```

or

```text
sessionStorage
```

Preferred:

```text
HttpOnly Secure Cookies
```

If backend constraints require storage:

```text
Memory Store + Refresh Rotation
```

must be used.

---

# Axios Configuration

Create:

```text
src/api/client.ts
```

Features:

- Base URL
- Authorization handling
- Refresh token handling
- Automatic retry
- Global error handling

---

# Authentication Pages

Implement:

```text
Login

Register Patient

Register Nurse

Forgot Password

Reset Password

Verify Email

Verify Phone
```

---

# Route Protection

Create:

```text
ProtectedRoute
```

and

```text
RoleBasedRoute
```

Supported roles:

```text
PATIENT
NURSE
ADMIN
```

---

# Layouts

Create:

```text
PublicLayout

PatientLayout

NurseLayout

AdminLayout
```

---

# Patient Features

## Dashboard

Display:

```text
Active Requests

Completed Visits

Favorite Nurses

Recent Notifications
```

---

## Profile

Support:

```text
View Profile

Update Profile

Medical Information

Emergency Contacts

Dependents
```

---

## Nearby Nurses

Consume:

```text
GET /api/nurses/nearby/
```

Display nurses as cards.

Each card should show:

```text
Profile Photo

Name

Specialization

Rating

Distance

Estimated Travel Time

Availability
```

---

## Nurse Cards

Use responsive cards.

Example sections:

```text
Avatar

Nurse Name

Specialization

Distance

ETA

Rating

Book Nurse Button
```

---

## Care Requests

Support:

```text
Create Request

List Requests

View Request

Cancel Request
```

Use forms with validation.

---

## Tracking

Display:

```text
Assigned Nurse

Journey Status

ETA

Current Progress
```

Use:

```text
Leaflet
OpenStreetMap
```

for maps.

---

# Nurse Features

## Dashboard

Display:

```text
Pending Requests

Accepted Requests

Today's Visits

Notifications
```

---

## Profile

Support:

```text
Edit Profile

Upload Credentials

Manage Availability

Manage Travel Radius

Manage Specializations
```

---

## Request Management

Support:

```text
Accept Request

Start Journey

Arrived

Start Visit

Complete Visit
```

---

## Live Tracking

Support periodic GPS updates.

Frontend sends:

```json
{
  "latitude": -1.286389,
  "longitude": 36.817223
}
```

to backend.

---

# Location Services

Frontend obtains GPS using:

```javascript
navigator.geolocation
```

Required for:

- Patient requests
- Nurse location updates
- Tracking

---

# API Explorer

The frontend should automatically consume all backend endpoints.

Create:

```text
Developer API Page
```

Features:

- Endpoint name
- Method
- URL
- Description
- Sample response

Display endpoints in cards.

Purpose:

Internal testing and administration.

---

# Forms

Use:

```text
React Hook Form
Zod
```

for all forms.

Requirements:

- Validation
- Error messages
- Type safety

---

# State Management

Use:

```text
TanStack Query
```

for server state.

Use:

```text
React Context
```

for authentication.

Avoid Redux.

---

# Notifications

Display:

```text
Request Accepted

Journey Started

Nurse Arrived

Visit Completed

Warnings
```

Use:

```text
Toast Notifications
```

and

```text
Notification Center
```

---

# UI Components

Create reusable:

```text
AppCard

StatusBadge

DistanceBadge

RatingBadge

LoadingSpinner

EmptyState

ErrorState

PageHeader

ProtectedRoute
```

---

# Accessibility

Requirements:

- Keyboard navigation
- ARIA labels
- Focus states
- Screen reader compatibility

---

# Security Requirements

Mandatory:

```text
JWT Authentication

Protected Routes

Role-Based Access

Input Validation

XSS Protection

CSRF Protection

Secure Cookies

HTTPS Only

Content Security Policy
```

---

# Performance Requirements

Use:

```text
Code Splitting

Lazy Loading

Route Based Chunks

Query Caching

Image Optimization
```

Prevent:

```text
Unnecessary Re-renders

Large Bundles

Duplicate API Requests
```

---

# Error Handling

Implement:

```text
404 Page

403 Page

500 Page

Offline Page
```

Global API error handling required.

---

# Testing

Use:

```text
Vitest

React Testing Library
```

Requirements:

```text
Unit Tests

Component Tests

Integration Tests
```

Target:

```text
90%+ coverage
```

---

# Documentation

Create:

```text
docs/
```

Include:

```text
architecture.md

routing.md

authentication.md

components.md

api-integration.md
```

---

# Definition of Done

Frontend is complete when:

1. Authentication works.
2. JWT refresh works.
3. Role-based routing works.
4. Patients can discover nurses.
5. Nurse cards display correctly.
6. Care requests can be created.
7. Journey tracking works.
8. Maps display correctly.
9. API endpoints are consumed.
10. Endpoint explorer page exists.
11. Forms are validated.
12. UI is mobile responsive.
13. Accessibility checks pass.
14. Tests pass.
15. Documentation is complete.

---

# Golden Rule

The frontend must never expose protected healthcare information to unauthorized users.

Only:

- The patient
- The assigned nurse
- Authorized administrators

may view protected medical data.

All pages, components, routes, API calls, and UI states must enforce this rule.


