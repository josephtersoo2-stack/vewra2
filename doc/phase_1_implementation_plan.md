# VEWRA Phase 1 Implementation Plan (Pro Edition)

**Version:** 2.0  
**Status:** Development Roadmap  
**Objective:** Deliver a production-ready foundation for the VEWRA YouTube Task, Tracking, and Rewards platform with secure backend validation, reliable mobile tracking, and scalable architecture.

---

# 1. Phase 1 Mission

Phase 1 establishes the complete earning workflow. Users must be able to register, discover approved YouTube tasks, complete valid watching sessions through the mobile browser, and receive verified rewards from the backend.

The backend remains the source of truth for authentication, progress validation, reward calculation, and wallet transactions. The mobile application only collects tracking information and presents the user experience.

---

# 2. Phase 1 Deliverables

## User System

- Registration and authentication
- JWT access and refresh tokens
- Secure token storage on mobile
- User profile foundation
- Account lifecycle handling

## Video Task Platform

- Admin-managed YouTube tasks
- Video metadata management
- YouTube ID extraction and validation
- Task activation and availability controls
- Randomised search instructions

## Tracking Engine

- Full in-app browser experience
- YouTube navigation support
- Video ID detection
- Playback state detection
- Watch progress collection
- Resume previous sessions
- Protection against duplicate rewards

## Wallet System

- User wallet creation
- Transaction ledger
- Reward calculation service
- Balance history
- Audit-friendly earning records

## Administration

- Django Admin management
- Task monitoring
- User session monitoring
- Wallet transaction review

---

# 3. System Architecture

```
Flutter Mobile App
        |
        |
Django REST API
        |
        |
PostgreSQL Database
        |
Redis + Celery Background Services
```

The application follows a domain-based structure:

- Authentication Domain
- Task Domain
- Tracking Domain
- Reward Domain
- Wallet Domain
- Administration Domain

---

# 4. Backend Implementation Roadmap

## 4.1 Project Foundation

Tasks:

- Configure Django project
- Configure PostgreSQL
- Configure environment management
- Configure Redis
- Configure Celery
- Configure API versioning
- Configure automated testing

Completion criteria:

- Backend runs locally through Docker
- Database migrations work correctly
- API health endpoint responds successfully

---

## 4.2 Authentication Module

Implementation:

- Custom user model preparation
- JWT authentication
- Registration endpoint
- Login endpoint
- Refresh endpoint
- Current user endpoint

Security requirements:

- Password hashing
- Token validation
- Rate limiting
- Authentication required for protected endpoints

---

## 4.3 Video Task Module

VideoTask model:

- youtube_url
- video_id
- title
- description
- keywords
- thumbnail_url
- reward_type
- reward_config
- active status
- timestamps

Supported reward modes:

### Per Time

Example:

```
60 seconds watched = 10 coins
```

### Watch All

Example:

```
95% completion = fixed reward
```

### Target

Example:

```
300 seconds watched = fixed reward
```

---

## 4.4 Watch Session Engine

Responsibilities:

- Create user video sessions
- Store progress
- Resume interrupted watching
- Prevent progress reduction
- Detect completion

Rules:

- Progress only increases
- Completed videos cannot reward again
- Client calculations are ignored
- Backend validates all earning events

---

## 4.5 Reward Engine

Create a dedicated reward service responsible for:

- Calculating eligible rewards
- Applying reward rules
- Creating wallet transactions
- Preventing duplicate payouts

Reward calculations must be:

- Deterministic
- Unit tested
- Independent from API views

---

## 4.6 Wallet Ledger

Wallet architecture:

```
Wallet
 |
 |
 WalletTransaction
```

Rules:

- Never modify balances without a transaction record
- Every earning event creates a ledger entry
- Maintain transaction history permanently

---

# 5. API Development Plan

## Authentication

```
POST /api/v1/auth/register/
POST /api/v1/auth/login/
POST /api/v1/auth/refresh/
GET  /api/v1/auth/me/
```

## Tasks

```
GET  /api/v1/tasks/
GET  /api/v1/tasks/{id}/
POST /api/v1/tasks/{id}/start/
```

## Tracking

```
POST /api/v1/tracking/progress/
```

Payload:

```json
{
 "session_id": 1,
 "video_id": "youtube_id",
 "current_time": 120,
 "delta_seconds": 10
}
```

Backend actions:

- Validate ownership
- Validate video
- Update progress
- Calculate reward
- Create transaction

## Wallet

```
GET /api/v1/wallet/
GET /api/v1/wallet/transactions/
```

---

# 6. Flutter Application Roadmap

## Core Setup

- App architecture
- Routing
- Theme system
- API client
- Secure storage
- Error handling

## Features

```
lib/
├── core/
├── features/
│   ├── auth/
│   ├── tasks/
│   ├── browser/
│   ├── wallet/
│   └── profile/
└── services/
```

---

# 7. Browser Tracking System

Technology:

- flutter_inappwebview
- JavaScript injection
- Native Flutter event handling

Tracking responsibilities:

- Detect YouTube video ID
- Monitor playback state
- Read player time
- Detect pauses and seeks
- Send progress updates

Event frequency:

- Periodic sync every few seconds
- Immediate sync on important events

---

# 8. Testing Strategy

## Backend Testing

Required tests:

- Authentication tests
- Task creation tests
- Permission tests
- Tracking validation tests
- Reward calculation tests
- Wallet ledger tests
- Security tests

## Mobile Testing

Required tests:

- Login flow
- API integration
- WebView loading
- Tracking events
- Session recovery

---

# 9. Security Requirements

- JWT protected APIs
- Request throttling
- Input validation
- Server-side reward calculation
- Transaction auditing
- Secure environment variables
- Logging for suspicious activity

---

# 10. Deployment Preparation

Before Phase 1 completion:

- Docker production configuration
- Database migration strategy
- Environment documentation
- API documentation
- Error monitoring preparation
- Backup strategy

---

# 11. Phase 1 Acceptance Criteria

The phase is complete when:

- [ ] User can register and authenticate
- [ ] Admin can create YouTube tasks
- [ ] Users can view available tasks
- [ ] Users receive personalised instructions
- [ ] WebView functions as a normal browser
- [ ] Correct videos are detected automatically
- [ ] Watching progress persists
- [ ] Rewards are calculated correctly
- [ ] Wallet transactions are recorded
- [ ] Duplicate earning is impossible
- [ ] APIs are secured
- [ ] Automated tests pass

---

# 12. Development Order

1. Backend foundation
2. Authentication
3. Video task management
4. Watch session engine
5. Reward and wallet system
6. Flutter authentication
7. Task screens
8. WebView tracking engine
9. Full integration testing
10. Production hardening

This roadmap provides the foundation required before implementing membership, referrals, advanced rewards, analytics, and custom administration features.