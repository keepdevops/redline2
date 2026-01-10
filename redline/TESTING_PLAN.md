# Phase 5: Testing Plan - JWT Authentication & Stripe Subscription Migration

## Overview
This document outlines the comprehensive testing plan for verifying the migration from license_key-based authentication to JWT token-based authentication with Stripe subscriptions.

## Test Environment Setup

### Prerequisites
- Docker container running with updated code
- Supabase configured with:
  - `SUPABASE_URL`
  - `SUPABASE_SERVICE_KEY`
  - `SUPABASE_JWT_SECRET`
- Stripe configured with:
  - `STRIPE_SECRET_KEY`
  - `STRIPE_PUBLISHABLE_KEY`
  - `STRIPE_WEBHOOK_SECRET`
  - `STRIPE_PRICE_ID_METERED`
- S3/R2 storage configured (if using cloud storage)

### Test User Accounts
1. Create test user in Supabase Auth
2. Create Stripe test customer
3. Link Stripe customer to Supabase user

---

## Test Suite 1: JWT Authentication Flow

### 1.1 User Registration & Login
- [ ] **Test User Registration**
  - POST `/auth/signup` with email/password
  - Verify user created in Supabase
  - Verify Stripe customer created
  - Verify JWT token returned

- [ ] **Test User Login**
  - POST `/auth/login` with valid credentials
  - Verify JWT token returned
  - Verify token contains `user_id`, `email`, `stripe_customer_id`
  - Verify token stored in `localStorage` as `variosync_auth_token`

- [ ] **Test Invalid Login**
  - POST `/auth/login` with invalid credentials
  - Verify 401 error returned
  - Verify no token returned

- [ ] **Test Token Extraction**
  - Verify token extracted from `Authorization: Bearer <token>` header
  - Verify token extracted from `localStorage.getItem('variosync_auth_token')`

### 1.2 Token Validation
- [ ] **Test Valid Token**
  - Make authenticated request with valid JWT token
  - Verify `g.user_id` set correctly
  - Verify `g.email` set correctly
  - Verify `g.stripe_customer_id` set correctly

- [ ] **Test Expired Token**
  - Make request with expired token
  - Verify 401 error returned
  - Verify error message indicates expired token

- [ ] **Test Invalid Token**
  - Make request with malformed token
  - Verify 401 error returned
  - Verify error message indicates invalid token

- [ ] **Test Missing Token**
  - Make authenticated request without token
  - Verify 401 error returned
  - Verify error message indicates authentication required

---

## Test Suite 2: Route Protection

### 2.1 Protected Routes (Require Authentication)
Test all routes that use `@auth_manager.require_auth`:

- [ ] **Download Routes**
  - POST `/download` - Single file download
  - POST `/batch-download` - Batch download
  - Verify `user_id` extracted from JWT
  - Verify operations use `user_id` instead of `license_key`

- [ ] **Data Loading Routes**
  - POST `/load` - Single file load
  - POST `/load-multiple` - Multiple file load
  - POST `/load-from-path` - Load from path
  - Verify `user_id` used for storage operations

- [ ] **File Operations**
  - DELETE `/files/<filename>` - Delete file
  - POST `/upload` - Upload file
  - Verify `user_id` used for file storage paths

- [ ] **Analysis Routes**
  - POST `/analyze` - Data analysis
  - POST `/detect-outliers` - Outlier detection
  - POST `/cluster-data` - Clustering
  - POST `/predict` - Prediction
  - POST `/scale-features` - Feature scaling
  - Verify `user_id` used for operations

- [ ] **ML Routes**
  - POST `/prepare-ml-data` - ML data preparation
  - POST `/prepare-rl-state` - RL state preparation
  - Verify `user_id` used for operations

- [ ] **Converter Routes**
  - POST `/convert` - Single file conversion
  - POST `/batch-convert` - Batch conversion
  - POST `/batch-merge` - Batch merge
  - Verify `user_id` used for operations

- [ ] **API Keys Management**
  - POST `/save` - Save API keys
  - GET `/load` - Load API keys
  - POST `/test` - Test API keys
  - Verify `user_id` used for storage

### 2.2 Unprotected Routes (Public)
- [ ] **Public Routes**
  - GET `/` - Home page
  - GET `/auth/login` - Login page
  - GET `/auth/signup` - Signup page
  - Verify accessible without authentication

---

## Test Suite 3: Stripe Subscription Integration

### 3.1 Subscription Creation
- [ ] **Create Checkout Session**
  - POST `/payments/create-subscription-checkout`
  - Verify Stripe checkout session created
  - Verify session includes correct price ID
  - Verify success/cancel URLs configured

- [ ] **Complete Subscription**
  - Complete Stripe checkout flow
  - Verify webhook received
  - Verify user `subscription_status` updated to `active`
  - Verify `stripe_customer_id` linked to user

### 3.2 Subscription Status
- [ ] **Get Subscription Info**
  - GET `/auth/user/subscription` (authenticated)
  - Verify subscription details returned
  - Verify usage information included

- [ ] **Check Active Subscription**
  - Test routes with `@require_active_subscription`
  - Verify access granted with `active` subscription
  - Verify access denied with `inactive` subscription

### 3.3 Subscription Webhooks
- [ ] **Payment Success Webhook**
  - Simulate `checkout.session.completed` event
  - Verify user subscription activated
  - Verify database updated

- [ ] **Subscription Updated Webhook**
  - Simulate `customer.subscription.updated` event
  - Verify subscription status updated
  - Verify database synchronized

- [ ] **Subscription Cancelled Webhook**
  - Simulate `customer.subscription.deleted` event
  - Verify subscription status set to `cancelled`
  - Verify access revoked

---

## Test Suite 4: Storage System

### 4.1 User Storage Operations
- [ ] **Initialize User Storage**
  - Call `user_storage.initialize_user_storage(user_id)`
  - Verify directory created with hashed `user_id`
  - Verify DuckDB database created

- [ ] **Save File**
  - POST `/user-data/files` with file data
  - Verify file saved to `user_id`-hashed path
  - Verify file metadata stored in database
  - Verify S3 upload (if enabled)

- [ ] **List Files**
  - GET `/user-data/files`
  - Verify only user's files returned
  - Verify correct `user_id` used

- [ ] **Get File**
  - GET `/user-data/files/<file_id>`
  - Verify file retrieved from correct user path
  - Verify file metadata correct

- [ ] **Save Data Table**
  - Save data table metadata
  - Verify stored with `user_id`
  - Verify retrievable by same user

- [ ] **List Data Tables**
  - GET `/user-data/tables`
  - Verify only user's tables returned

- [ ] **Get Storage Stats**
  - GET `/user-data/stats`
  - Verify stats calculated for correct user
  - Verify isolation between users

### 4.2 Path Hashing
- [ ] **Verify Path Consistency**
  - Same `user_id` always generates same hash
  - Different `user_id` generates different hash
  - Verify no collisions in test dataset

---

## Test Suite 5: Database Schema

### 5.1 Usage Storage
- [ ] **Log Session Start**
  - Call `usage_storage.log_session_start(session_id, user_id)`
  - Verify record created with `user_id`
  - Verify `license_key` optional/nullable

- [ ] **Log Hour Deduction**
  - Call `usage_storage.log_hour_deduction(user_id, hours)`
  - Verify record created with `user_id`
  - Verify queryable by `user_id`

- [ ] **Log Payment**
  - Call `usage_storage.log_payment(user_id, hours, amount)`
  - Verify record created with `user_id`
  - Verify linked to Stripe payment

- [ ] **Log Access**
  - Call `usage_storage.log_access(user_id, endpoint, method)`
  - Verify record created with `user_id`
  - Verify queryable by `user_id`

- [ ] **Get Usage History**
  - Call `usage_storage.get_usage_history(user_id)`
  - Verify only user's records returned
  - Verify correct `user_id` filtering

- [ ] **Get Payment History**
  - Call `usage_storage.get_payment_history(user_id)`
  - Verify only user's payments returned

- [ ] **Get Session History**
  - Call `usage_storage.get_session_history(user_id)`
  - Verify only user's sessions returned

- [ ] **Get Access Stats**
  - Call `usage_storage.get_access_stats(user_id)`
  - Verify stats calculated for correct user

### 5.2 Database Migration
- [ ] **Verify Schema Updates**
  - Verify `user_id` columns exist in all tables
  - Verify indexes created on `user_id` columns
  - Verify `license_key` columns still exist (for migration)

- [ ] **Test Migration Fallback**
  - Test queries with `license_key` fallback
  - Verify backward compatibility maintained

---

## Test Suite 6: Frontend Integration

### 6.1 Template Updates
- [ ] **Verify No License Key References**
  - Check all HTML templates for `license_key` references
  - Verify replaced with `authToken` / JWT token
  - Verify `localStorage` uses `variosync_auth_token`

- [ ] **Test API Calls**
  - Verify all AJAX requests include `Authorization: Bearer <token>` header
  - Verify no `X-License-Key` headers sent
  - Verify no `license_key` in request payloads

### 6.2 Authentication Flow
- [ ] **Login Flow**
  - User logs in via `/auth/login`
  - Verify token stored in `localStorage`
  - Verify redirect to dashboard
  - Verify no `license_key` in URL

- [ ] **Payment Success Flow**
  - Complete Stripe checkout
  - Verify redirect to `/payments/subscription-success`
  - Verify no `license_key` in URL
  - Verify token-based authentication maintained

- [ ] **Dashboard Access**
  - Access dashboard after login
  - Verify authenticated API calls work
  - Verify user data loaded correctly

---

## Test Suite 7: Error Handling

### 7.1 Authentication Errors
- [ ] **Missing Token**
  - Make authenticated request without token
  - Verify clear error message
  - Verify 401 status code

- [ ] **Invalid Token**
  - Make request with invalid token
  - Verify clear error message
  - Verify 401 status code

- [ ] **Expired Token**
  - Make request with expired token
  - Verify clear error message
  - Verify 401 status code
  - Verify frontend handles token refresh

### 7.2 Authorization Errors
- [ ] **Inactive Subscription**
  - Access premium route without active subscription
  - Verify 403 error returned
  - Verify clear error message

- [ ] **User Isolation**
  - User A tries to access User B's data
  - Verify access denied
  - Verify data isolation maintained

---

## Test Suite 8: Integration Tests

### 8.1 Complete User Journey
- [ ] **New User Flow**
  1. User signs up
  2. User logs in
  3. User creates Stripe subscription
  4. User uploads file
  5. User downloads data
  6. User performs analysis
  7. Verify all operations use `user_id`
  8. Verify no `license_key` references

- [ ] **Existing User Migration**
  1. User with legacy `license_key` logs in
  2. Verify JWT token issued
  3. Verify operations work with `user_id`
  4. Verify backward compatibility maintained

### 8.2 Multi-User Isolation
- [ ] **Data Isolation**
  - User A uploads file
  - User B cannot access User A's file
  - User B uploads different file
  - Verify both users see only their files

- [ ] **Usage Tracking Isolation**
  - User A performs operations
  - User B performs operations
  - Verify usage tracked separately
  - Verify stats calculated per user

---

## Test Suite 9: Performance & Load

### 9.1 Token Validation Performance
- [ ] **Token Validation Speed**
  - Measure time to validate JWT token
  - Verify < 10ms per validation
  - Verify no performance degradation

### 9.2 Database Query Performance
- [ ] **User ID Index Performance**
  - Query usage history by `user_id`
  - Verify index used
  - Verify query time acceptable

---

## Test Suite 10: Security

### 10.1 Token Security
- [ ] **Token Storage**
  - Verify tokens stored securely in `localStorage`
  - Verify tokens not logged
  - Verify tokens not exposed in URLs

- [ ] **Token Validation**
  - Verify JWT signature validated
  - Verify token expiration checked
  - Verify token issuer validated

### 10.2 User Isolation Security
- [ ] **Path Traversal Prevention**
  - Attempt to access other user's files via path manipulation
  - Verify access denied

- [ ] **SQL Injection Prevention**
  - Attempt SQL injection via `user_id` parameter
  - Verify parameterized queries used

---

## Test Execution Checklist

### Pre-Testing
- [ ] Environment variables configured
- [ ] Docker container running
- [ ] Database initialized
- [ ] Test users created
- [ ] Stripe test mode configured

### During Testing
- [ ] Execute all test suites sequentially
- [ ] Document any failures
- [ ] Verify error messages are clear
- [ ] Check logs for errors

### Post-Testing
- [ ] Review all test results
- [ ] Fix any identified issues
- [ ] Re-run failed tests
- [ ] Document test results

---

## Success Criteria

All tests must pass for Phase 5 to be considered complete:

1. ✅ All authentication flows work with JWT tokens
2. ✅ All routes protected with `@require_auth` work correctly
3. ✅ Stripe subscription integration functional
4. ✅ Storage system uses `user_id` correctly
5. ✅ Database schema supports `user_id` queries
6. ✅ Frontend uses JWT tokens (no `license_key`)
7. ✅ User data isolation maintained
8. ✅ Error handling clear and informative
9. ✅ Performance acceptable
10. ✅ Security requirements met

---

## Notes

- During migration period, `license_key` parameters are optional for backward compatibility
- After migration period, `license_key` support can be removed
- All new code should use `user_id` from JWT tokens exclusively
- Monitor logs for any `license_key` usage during transition period
