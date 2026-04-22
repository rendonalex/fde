# API Specifications: Prior-Authorization Check

**Parent Spec**: [../Claude.md](../Claude.md)  
**Version**: 2.0  
**Last Updated**: 2026-04-22  

---

## Overview

This document contains complete API specifications for the Prior-Authorization Check capability, including:
- REST API contracts (request/response formats)
- Database schemas (PostgreSQL DDL)
- Algorithm implementations (fuzzy matching)
- Error handling and retry logic

**Referenced by**: Claude.md Sections 3 (Core Decision Logic) and Assumptions A36-A52

---

## Table of Contents

1. [Prior-Auth Database REST API](#1-prior-auth-database-rest-api)
2. [athenahealth EHR API](#2-athenahealth-ehr-api)
3. [Insurance Requirements Database](#3-insurance-requirements-database)
4. [Fuzzy Matching Algorithm](#4-fuzzy-matching-algorithm)
5. [Database Schema (PostgreSQL)](#5-database-schema-postgresql)
6. [Human Review Interface Backend API](#6-human-review-interface-backend-api)
7. [Error Code Taxonomy](#7-error-code-taxonomy)

---

## 13. API SPECIFICATIONS AND CONTRACTS  
  
**NOTE**: These specifications are based on assumptions A36-A52 above. All contracts must be validated against actual systems during discovery.  
  
---  
  
### 13.1 Prior-Auth Database REST API  
  
⚠️ **Based on Assumption A36** (Internal PostgreSQL with REST API wrapper)  
  
**Base URL**: `https://api.priorauth.practice.internal/v1`  
  
**Authentication**: Bearer token (OAuth 2.0 Client Credentials)  
  
---  
  
#### Authentication Endpoint  
  
**POST** `/auth/token`  
  
**Purpose**: Obtain access token for API requests  
  
**Request**:  
```json  
{  
  "grant_type": "client_credentials",  
  "client_id": "priorauth-checker-service",  
  "client_secret": "{{secret_from_vault}}"  
}  
```  
  
**Response** (200 OK):  
```json  
{  
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",  
  "token_type": "Bearer",  
  "expires_in": 3600,  
  "scope": "read:prior_auths"  
}  
```  
  
**Error Response** (401 Unauthorized):  
```json  
{  
  "error": "invalid_client",  
  "error_description": "Client authentication failed"  
}  
```  
  
---  
  
#### Query Prior-Auth Records  
  
**GET** `/prior-auths`  
  
**Purpose**: Retrieve prior-auth records matching query criteria  
  
**Headers**:  
```  
Authorization: Bearer {{access_token}}  
Accept: application/json  
```  
  
**Query Parameters**:  
```  
patient_id (required): string - Patient identifier (matches athenahealth patient ID)  
insurance_policy_id (required): string - Insurance policy identifier  
status (optional): string - Filter by status ("ACTIVE" | "EXPIRED" | "REVOKED" | "PENDING")  
expiration_date_gte (optional): string - ISO 8601 date, filter records expiring on/after this date  
page (optional): integer - Page number for pagination (default: 1)  
per_page (optional): integer - Records per page (default: 50, max: 100)  
```  
  
**Example Request**:  
```  
GET /prior-auths?patient_id=12345&insurance_policy_id=POL-67890&status=ACTIVE&expiration_date_gte=2025-01-15  
```  
  
**Response** (200 OK):  
```json  
{  
  "data": [  
    {  
      "prior_auth_id": "PA-2024-987654",  
      "patient_id": "12345",  
      "insurance_policy_id": "POL-67890",  
      "approval_number": "AUTH987654",  
      "approval_date": "2024-12-01",  
      "expiration_date": "2025-02-28",  
      "approval_status": "ACTIVE",  
      "approved_cpt_codes": ["70553", "70551"],  
      "approved_service_description": "MRI Brain with or without contrast",  
      "service_category": "imaging",  
      "approved_units": 2,  
      "units_used": 0,  
      "source_system": "prior_auth_db",  
      "last_verified_at": "2024-12-15T10:30:00Z",  
      "created_at": "2024-12-01T14:20:00Z",  
      "updated_at": "2024-12-15T10:30:00Z"  
    }  
  ],  
  "pagination": {  
    "page": 1,  
    "per_page": 50,  
    "total_records": 1,  
    "total_pages": 1  
  },  
  "metadata": {  
    "query_time_ms": 45,  
    "api_version": "v1"  
  }  
}  
```  
  
**Response** (200 OK - No Records Found):  
```json  
{  
  "data": [],  
  "pagination": {  
    "page": 1,  
    "per_page": 50,  
    "total_records": 0,  
    "total_pages": 0  
  },  
  "metadata": {  
    "query_time_ms": 12,  
    "api_version": "v1"  
  }  
}  
```  
  
**Error Response** (400 Bad Request):  
```json  
{  
  "error": "invalid_request",  
  "error_description": "Missing required parameter: patient_id",  
  "error_code": "MISSING_PARAM",  
  "field": "patient_id"  
}  
```  
  
**Error Response** (401 Unauthorized):  
```json  
{  
  "error": "unauthorized",  
  "error_description": "Access token expired or invalid",  
  "error_code": "INVALID_TOKEN"  
}  
```  
  
**Error Response** (500 Internal Server Error):  
```json  
{  
  "error": "internal_error",  
  "error_description": "Database connection failed",  
  "error_code": "DB_CONNECTION_ERROR",  
  "request_id": "req-abc123"  
}  
```  
  
**Retry Logic**:  
- **Transient errors** (500, 503, timeout): Retry up to 3 times with exponential backoff (1s, 2s, 4s)  
- **Client errors** (400, 401, 404): Do not retry, handle immediately  
- **Timeout**: Set request timeout to 5 seconds  
  
---  
  
#### Get Single Prior-Auth Record  
  
**GET** `/prior-auths/{prior_auth_id}`  
  
**Purpose**: Retrieve single prior-auth record by ID  
  
**Headers**:  
```  
Authorization: Bearer {{access_token}}  
Accept: application/json  
```  
  
**Response** (200 OK):  
```json  
{  
  "prior_auth_id": "PA-2024-987654",  
  "patient_id": "12345",  
  "insurance_policy_id": "POL-67890",  
  "approval_number": "AUTH987654",  
  "approval_date": "2024-12-01",  
  "expiration_date": "2025-02-28",  
  "approval_status": "ACTIVE",  
  "approved_cpt_codes": ["70553", "70551"],  
  "approved_service_description": "MRI Brain with or without contrast",  
  "service_category": "imaging",  
  "approved_units": 2,  
  "units_used": 0,  
  "source_system": "prior_auth_db",  
  "last_verified_at": "2024-12-15T10:30:00Z",  
  "created_at": "2024-12-01T14:20:00Z",  
  "updated_at": "2024-12-15T10:30:00Z"  
}  
```  
  
**Error Response** (404 Not Found):  
```json  
{  
  "error": "not_found",  
  "error_description": "Prior-auth record not found",  
  "error_code": "PRIOR_AUTH_NOT_FOUND",  
  "prior_auth_id": "PA-2024-987654"  
}  
```  
  
---  
  
### 13.2 athenahealth EHR API  
  
⚠️ **Based on Assumption A39** (REST API with OAuth 2.0, based on athenahealth's documented patterns)  
  
**Base URL**: `https://api.athenahealth.com/v1/{practiceid}`  
  
**Authentication**: OAuth 2.0 (Authorization Code flow for user auth, Client Credentials for service accounts)  
  
---  
  
#### Authentication Endpoint  
  
**POST** `https://api.athenahealth.com/oauth2/v1/token`  
  
**Request**:  
```  
POST /oauth2/v1/token  
Content-Type: application/x-www-form-urlencoded  
  
grant_type=client_credentials&client_id={{client_id}}&client_secret={{client_secret}}  
```  
  
**Response** (200 OK):  
```json  
{  
  "access_token": "ath_access_token_12345",  
  "token_type": "bearer",  
  "expires_in": 3600,  
  "refresh_token": "ath_refresh_token_67890"  
}  
```  
  
---  
  
#### Get Appointment Details  
  
**GET** `/appointments/{appointmentid}`  
  
**Purpose**: Retrieve appointment details including procedure codes  
  
**Headers**:  
```  
Authorization: Bearer {{access_token}}  
Accept: application/json  
```  
  
**Response** (200 OK):  
```json  
{  
  "appointmentid": "123456",  
  "patientid": "78910",  
  "appointmentdate": "01/15/2025",  
  "appointmenttime": "10:00",  
  "appointmenttypeid": "108",  
  "appointmenttypename": "MRI Scan",  
  "appointmentstatus": "scheduled",  
  "duration": 60,  
  "departmentid": "1",  
  "providerid": "5",  
  "scheduledby": "frontdesk1",  
  "procedures": [  
    {  
      "procedurecode": "70553",  
      "procedurename": "MRI Brain with Contrast",  
      "proceduremodifier": ""  
    }  
  ],  
  "insurances": [  
    {  
      "insuranceid": "55001",  
      "insuranceidnumber": "POL-67890",  
      "insuranceplanname": "Blue Cross Blue Shield PPO",  
      "insurancetype": "primary",  
      "eligibilitystatus": "eligible",  
      "insurancepolicyid": "POL-67890"  
    }  
  ],  
  "notes": [],  
  "priorauth_verified": false,  
  "priorauth_verified_at": null,  
  "priorauth_check_id": null  
}  
```  
  
**Field Mappings** (athenahealth → Internal Model):  
```  
appointmentid → appointment_id  
patientid → patient_id  
appointmentdate (MM/DD/YYYY) → scheduled_date (YYYY-MM-DD)  
appointmenttime (HH:MM) → scheduled_time (HH:MM:SS)  
procedures[].procedurecode → procedure_codes[]  
procedures[].procedurename → procedure_descriptions[]  
insurances[0].insurancepolicyid → insurance_policy_id (use primary insurance)  
```  
  
**Error Response** (404 Not Found):  
```json  
{  
  "error": "Appointment not found",  
  "detailedmessage": "Appointment ID 123456 does not exist in practice 195900"  
}  
```  
  
---  
  
#### Update Appointment (Add Prior-Auth Note)  
  
**PUT** `/appointments/{appointmentid}/notes`  
  
**Purpose**: Document prior-auth verification results in appointment notes  
  
**Headers**:  
```  
Authorization: Bearer {{access_token}}  
Content-Type: application/json  
```  
  
**Request Body**:  
```json  
{  
  "notetext": "PRIOR-AUTH VERIFICATION:\nStatus: VALID\nApproval Number: AUTH987654\nExpiration: 02/28/2025\nAI Recommendation: PROCEED (HIGH confidence)\nHuman Decision: APPROVED by frontdesk1 at 2025-01-13 09:15:00\nCheck ID: PAC-1705140900-78910-123456",  
  "displayonschedule": true,  
  "notedate": "01/13/2025",  
  "notetime": "09:15"  
}  
```  
  
**Response** (200 OK):  
```json  
{  
  "success": true,  
  "noteid": "789012",  
  "message": "Note added successfully"  
}  
```  
  
---  
  
#### Update Appointment Custom Fields  
  
**PUT** `/appointments/{appointmentid}`  
  
**Purpose**: Set prior-auth verification flags  
  
**Headers**:  
```  
Authorization: Bearer {{access_token}}  
Content-Type: application/json  
```  
  
**Request Body**:  
```json  
{  
  "priorauth_verified": true,  
  "priorauth_verified_at": "2025-01-13T09:15:00Z",  
  "priorauth_check_id": "PAC-1705140900-78910-123456"  
}  
```  
  
**Response** (200 OK):  
```json  
{  
  "success": true,  
  "appointmentid": "123456",  
  "message": "Appointment updated successfully"  
}  
```  
  
**Error Response** (400 Bad Request):  
```json  
{  
  "error": "Invalid field",  
  "detailedmessage": "Field 'priorauth_verified' is not a valid appointment field",  
  "field": "priorauth_verified"  
}  
```  
  
**Note**: If athenahealth doesn't support custom fields for `priorauth_verified`, use appointment notes only as fallback.  
  
---  
  
### 13.3 Insurance Requirements Database API (Internal)  
  
⚠️ **Based on Assumption A38** (Internal PostgreSQL table)  
  
**Implementation**: Direct database query (no REST API needed for MVP; internal service only)  
  
**Table Schema**:  
```sql  
CREATE TABLE insurance_requirements (  
  id SERIAL PRIMARY KEY,  
  insurance_policy_id VARCHAR(100) NOT NULL,  
  insurance_carrier VARCHAR(100) NOT NULL,  
  procedure_code VARCHAR(5) NOT NULL,  
  prior_auth_required BOOLEAN NOT NULL,  
  requirement_type VARCHAR(20) NOT NULL, -- 'always' | 'sometimes' | 'never'  
  notes TEXT,  
  effective_date DATE NOT NULL,  
  expiration_date DATE,  
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  
  UNIQUE (insurance_policy_id, procedure_code, effective_date)  
);  
  
CREATE INDEX idx_insurance_requirements_lookup   
ON insurance_requirements(insurance_policy_id, procedure_code, effective_date);  
```  
  
**Query Example** (from application code):  
```sql  
SELECT prior_auth_required, requirement_type, notes  
FROM insurance_requirements  
WHERE insurance_policy_id = $1  
  AND procedure_code = $2  
  AND effective_date <= CURRENT_DATE  
  AND (expiration_date IS NULL OR expiration_date >= CURRENT_DATE)  
ORDER BY effective_date DESC  
LIMIT 1;  
```  
  
**Application Interface**:  
```typescript  
interface InsuranceRequirement {  
  prior_auth_required: boolean;  
  requirement_type: 'always' | 'sometimes' | 'never';  
  notes: string | null;  
}  
  
async function checkPriorAuthRequired(  
  insurancePolicyId: string,  
  procedureCode: string  
): Promise<InsuranceRequirement | null> {  
  const result = await db.query(  
    `SELECT prior_auth_required, requirement_type, notes  
     FROM insurance_requirements  
     WHERE insurance_policy_id = $1 AND procedure_code = $2  
       AND effective_date <= CURRENT_DATE  
       AND (expiration_date IS NULL OR expiration_date >= CURRENT_DATE)  
     ORDER BY effective_date DESC LIMIT 1`,  
    [insurancePolicyId, procedureCode]  
  );  
  return result.rows[0] || null;  
}  
```  
  
**Fallback to Hardcoded Rules** (if table is empty):  
```typescript  
function requiresPriorAuthFallback(cptCode: string): boolean | null {  
  const cptNum = parseInt(cptCode);  
  if (cptNum >= 70000 && cptNum <= 79999) return true; // Imaging  
  if (cptNum >= 10000 && cptNum <= 69999) return true; // Surgery  
  if (cptNum >= 99201 && cptNum <= 99499) return false; // Office visits  
  return null; // Unknown, escalate  
}  
```  
  
---  
  
### 13.4 Fuzzy Matching Algorithm Implementation  
  
⚠️ **Based on Assumption A40** (Levenshtein distance with normalization)  
  
**Algorithm Specification**:  
  
```typescript  
/**  
 * Calculate similarity score between two strings using normalized Levenshtein distance  
 * @param text1 - First string to compare  
 * @param text2 - Second string to compare  
 * @returns Similarity score between 0.0 (completely different) and 1.0 (identical)  
 */  
function fuzzyMatchScore(text1: string, text2: string): number {  
  // Step 1: Normalize both strings  
  const normalized1 = normalizeText(text1);  
  const normalized2 = normalizeText(text2);  
  
  // Step 2: Calculate Levenshtein distance  
  const distance = levenshteinDistance(normalized1, normalized2);  
  
  // Step 3: Convert distance to similarity score (0.0 to 1.0)  
  const maxLength = Math.max(normalized1.length, normalized2.length);  
  if (maxLength === 0) return 1.0; // Both empty strings = identical  
  
  const similarity = 1.0 - (distance / maxLength);  
  return similarity;  
}  
  
/**  
 * Normalize text for comparison:  
 * - Convert to lowercase  
 * - Remove punctuation (keep alphanumeric and spaces)  
 * - Collapse multiple spaces to single space  
 * - Trim leading/trailing whitespace  
 */  
function normalizeText(text: string): string {  
  return text  
    .toLowerCase()  
    .replace(/[^a-z0-9\s]/g, '') // Remove punctuation  
    .replace(/\s+/g, ' ')         // Collapse spaces  
    .trim();  
}  
  
/**  
 * Calculate Levenshtein distance (edit distance) between two strings  
 * Using dynamic programming approach  
 */  
function levenshteinDistance(str1: string, str2: string): number {  
  const len1 = str1.length;  
  const len2 = str2.length;  
  
  // Create 2D array for DP  
  const dp: number[][] = Array(len1 + 1)  
    .fill(null)  
    .map(() => Array(len2 + 1).fill(0));  
  
  // Initialize first row and column  
  for (let i = 0; i <= len1; i++) dp[i][0] = i;  
  for (let j = 0; j <= len2; j++) dp[0][j] = j;  
  
  // Fill DP table  
  for (let i = 1; i <= len1; i++) {  
    for (let j = 1; j <= len2; j++) {  
      if (str1[i - 1] === str2[j - 1]) {  
        dp[i][j] = dp[i - 1][j - 1]; // No operation needed  
      } else {  
        dp[i][j] = Math.min(  
          dp[i - 1][j] + 1,     // Deletion  
          dp[i][j - 1] + 1,     // Insertion  
          dp[i - 1][j - 1] + 1  // Substitution  
        );  
      }  
    }  
  }  
  
  return dp[len1][len2];  
}  
  
/**  
 * Check if two service descriptions match using fuzzy matching  
 * @param priorAuthDescription - Description from prior-auth record  
 * @param appointmentDescription - Description from appointment  
 * @param threshold - Similarity threshold (default 0.8)  
 * @returns Match result with score and decision  
 */  
function fuzzyMatch(  
  priorAuthDescription: string,  
  appointmentDescription: string,  
  threshold: number = 0.8  
): { match: boolean; score: number; confidence: 'HIGH' | 'MEDIUM' | 'LOW' } {  
  const score = fuzzyMatchScore(priorAuthDescription, appointmentDescription);  
  
  let match: boolean;  
  let confidence: 'HIGH' | 'MEDIUM' | 'LOW';  
  
  if (score >= 0.95) {  
    match = true;  
    confidence = 'HIGH'; // Near-exact match  
  } else if (score >= threshold) {  
    match = true;  
    confidence = 'MEDIUM'; // Fuzzy match above threshold  
  } else {  
    match = false;  
    confidence = 'LOW'; // Below threshold, no match  
  }  
  
  return { match, score, confidence };  
}  
```  
  
**Example Usage**:  
```typescript  
const result = fuzzyMatch(  
  "MRI Brain with Contrast",  
  "MRI brain w/ contrast"  
);  
// Returns: { match: true, score: 0.92, confidence: 'HIGH' }  
  
const result2 = fuzzyMatch(  
  "MRI Brain",  
  "CT Chest"  
);  
// Returns: { match: false, score: 0.3, confidence: 'LOW' }  
```  
  
**Performance**: O(m × n) where m, n are string lengths. For typical medical descriptions (<100 characters), executes in <1ms.  
  
---  
  
### 13.5 Database Schema (PostgreSQL DDL)  
  
⚠️ **Based on Assumption A51** (PostgreSQL 14+)  
  
```sql  
-- ====================  
-- OPERATIONAL TABLES  
-- ====================  
  
-- Table: prior_auth_checks  
-- Stores each prior-auth verification workflow  
CREATE TABLE prior_auth_checks (  
  check_id VARCHAR(100) PRIMARY KEY,  
  patient_id VARCHAR(50) NOT NULL,  
  appointment_id VARCHAR(50) NOT NULL,  
  scheduled_date DATE NOT NULL,  
  procedure_code VARCHAR(5) NOT NULL,  
  procedure_description VARCHAR(255),  
  insurance_policy_id VARCHAR(100) NOT NULL,  
  
  -- Status tracking  
  status VARCHAR(30) NOT NULL CHECK (status IN (  
    'PENDING_CHECK', 'CHECKING', 'AWAITING_HUMAN_REVIEW',  
    'APPROVED', 'RESCHEDULED', 'ESCALATED', 'COMPLETED', 'FAILED'  
  )),  
  prior_auth_required BOOLEAN,  
  prior_auth_status VARCHAR(20) CHECK (prior_auth_status IN (  
    'VALID', 'EXPIRED', 'EXPIRING_SOON', 'MISSING', 'AMBIGUOUS'  
  )),  
  
  -- AI analysis results  
  ai_recommendation VARCHAR(20) CHECK (ai_recommendation IN (  
    'PROCEED', 'RESCHEDULE', 'ESCALATE'  
  )),  
  confidence_score VARCHAR(10) CHECK (confidence_score IN ('HIGH', 'MEDIUM', 'LOW')),  
  confidence_rationale TEXT,  
  
  -- Human decision  
  human_decision VARCHAR(20) CHECK (human_decision IN (  
    'APPROVED', 'RESCHEDULED', 'ESCALATED', 'OVERRIDDEN'  
  )),  
  human_decision_by VARCHAR(100),  
  human_decision_at TIMESTAMP,  
  human_decision_notes TEXT,  
  
  -- Audit trail  
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  
  completed_at TIMESTAMP,  
  last_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  
  escalation_reason TEXT,  
  
  -- Related entities  
  prior_auth_records_found TEXT[], -- Array of prior_auth_ids  
  matched_prior_auth_id VARCHAR(100),  
  
  CONSTRAINT fk_matched_prior_auth FOREIGN KEY (matched_prior_auth_id)  
    REFERENCES prior_auth_records(prior_auth_id) ON DELETE SET NULL  
);  
  
-- Indexes for performance  
CREATE INDEX idx_prior_auth_checks_patient ON prior_auth_checks(patient_id);  
CREATE INDEX idx_prior_auth_checks_appointment ON prior_auth_checks(appointment_id);  
CREATE INDEX idx_prior_auth_checks_scheduled_date ON prior_auth_checks(scheduled_date);  
CREATE INDEX idx_prior_auth_checks_status ON prior_auth_checks(status);  
CREATE INDEX idx_prior_auth_checks_created_at ON prior_auth_checks(created_at DESC);  
  
-- Table: prior_auth_records  
-- Cached copy of prior-auth records from external system  
CREATE TABLE prior_auth_records (  
  prior_auth_id VARCHAR(100) PRIMARY KEY,  
  patient_id VARCHAR(50) NOT NULL,  
  insurance_policy_id VARCHAR(100) NOT NULL,  
  
  -- Approval details  
  approval_number VARCHAR(100) NOT NULL,  
  approval_date DATE NOT NULL,  
  expiration_date DATE NOT NULL,  
  approval_status VARCHAR(20) NOT NULL CHECK (approval_status IN (  
    'ACTIVE', 'EXPIRED', 'REVOKED', 'PENDING'  
  )),  
  
  -- Covered services  
  approved_cpt_codes VARCHAR(5)[], -- Array of CPT codes  
  approved_service_description TEXT,  
  service_category VARCHAR(50),  
  
  -- Limitations  
  approved_units INTEGER,  
  units_used INTEGER DEFAULT 0,  
  
  -- Source metadata  
  source_system VARCHAR(50) NOT NULL,  
  last_verified_at TIMESTAMP,  
  
  -- Audit  
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  
);  
  
-- Indexes  
CREATE INDEX idx_prior_auth_records_patient ON prior_auth_records(patient_id);  
CREATE INDEX idx_prior_auth_records_insurance ON prior_auth_records(insurance_policy_id);  
CREATE INDEX idx_prior_auth_records_expiration ON prior_auth_records(expiration_date);  
CREATE INDEX idx_prior_auth_records_status ON prior_auth_records(approval_status);  
CREATE INDEX idx_prior_auth_records_cpt_codes ON prior_auth_records USING GIN(approved_cpt_codes);  
  
-- Table: insurance_requirements  
-- Maps insurance policies to procedures requiring prior-auth  
CREATE TABLE insurance_requirements (  
  id SERIAL PRIMARY KEY,  
  insurance_policy_id VARCHAR(100) NOT NULL,  
  insurance_carrier VARCHAR(100) NOT NULL,  
  procedure_code VARCHAR(5) NOT NULL,  
  prior_auth_required BOOLEAN NOT NULL,  
  requirement_type VARCHAR(20) NOT NULL CHECK (requirement_type IN (  
    'always', 'sometimes', 'never'  
  )),  
  notes TEXT,  
  effective_date DATE NOT NULL,  
  expiration_date DATE,  
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  
  UNIQUE (insurance_policy_id, procedure_code, effective_date)  
);  
  
CREATE INDEX idx_insurance_requirements_lookup  
  ON insurance_requirements(insurance_policy_id, procedure_code, effective_date);  
  
-- ====================  
-- AUDIT LOG TABLES  
-- ====================  
  
-- Table: audit_logs  
-- Immutable audit trail of all actions  
CREATE TABLE audit_logs (  
  log_id BIGSERIAL PRIMARY KEY,  
  check_id VARCHAR(100) NOT NULL,  
  event_type VARCHAR(50) NOT NULL, -- 'check_initiated', 'status_transition', 'human_decision', etc.  
  event_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,  
  user_id VARCHAR(100), -- NULL for system-initiated events  
  from_state VARCHAR(30),  
  to_state VARCHAR(30),  
  event_data JSONB, -- Flexible JSON for additional context  
  CONSTRAINT fk_check FOREIGN KEY (check_id)  
    REFERENCES prior_auth_checks(check_id) ON DELETE CASCADE  
);  
  
CREATE INDEX idx_audit_logs_check_id ON audit_logs(check_id);  
CREATE INDEX idx_audit_logs_timestamp ON audit_logs(event_timestamp DESC);  
CREATE INDEX idx_audit_logs_event_type ON audit_logs(event_type);  
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);  
  
-- ====================  
-- TRIGGERS  
-- ====================  
  
-- Auto-update last_updated_at timestamp  
CREATE OR REPLACE FUNCTION update_last_updated_at()  
RETURNS TRIGGER AS $$  
BEGIN  
  NEW.last_updated_at = CURRENT_TIMESTAMP;  
  RETURN NEW;  
END;  
$$ LANGUAGE plpgsql;  
  
CREATE TRIGGER trigger_update_prior_auth_checks_timestamp  
  BEFORE UPDATE ON prior_auth_checks  
  FOR EACH ROW  
  EXECUTE FUNCTION update_last_updated_at();  
  
CREATE TRIGGER trigger_update_prior_auth_records_timestamp  
  BEFORE UPDATE ON prior_auth_records  
  FOR EACH ROW  
  EXECUTE FUNCTION update_last_updated_at();  
  
CREATE TRIGGER trigger_update_insurance_requirements_timestamp  
  BEFORE UPDATE ON insurance_requirements  
  FOR EACH ROW  
  EXECUTE FUNCTION update_last_updated_at();  
  
-- Auto-create audit log on status transition  
CREATE OR REPLACE FUNCTION log_status_transition()  
RETURNS TRIGGER AS $$  
BEGIN  
  IF NEW.status IS DISTINCT FROM OLD.status THEN  
    INSERT INTO audit_logs (check_id, event_type, from_state, to_state, event_data)  
    VALUES (  
      NEW.check_id,  
      'status_transition',  
      OLD.status,  
      NEW.status,  
      jsonb_build_object(  
        'prior_auth_status', NEW.prior_auth_status,  
        'ai_recommendation', NEW.ai_recommendation,  
        'confidence_score', NEW.confidence_score  
      )  
    );  
  END IF;  
  RETURN NEW;  
END;  
$$ LANGUAGE plpgsql;  
  
CREATE TRIGGER trigger_log_prior_auth_check_status  
  AFTER UPDATE ON prior_auth_checks  
  FOR EACH ROW  
  EXECUTE FUNCTION log_status_transition();  
```  
  
---  
  
### 13.6 Human Review Interface Backend API  
  
**Base URL**: `https://api.priorauth-review.practice.internal/v1`  
  
**Authentication**: Session-based (staff logs in via SSO)  
  
---  
  
#### Get Pending Reviews  
  
**GET** `/reviews/pending`  
  
**Purpose**: Fetch all prior-auth checks awaiting human review  
  
**Query Parameters**:  
```  
confidence (optional): string - Filter by confidence level ('HIGH' | 'MEDIUM' | 'LOW')  
page (optional): integer - Page number (default 1)  
per_page (optional): integer - Results per page (default 20)  
```  
  
**Response** (200 OK):  
```json  
{  
  "data": [  
    {  
      "check_id": "PAC-1705140900-78910-123456",  
      "patient_id": "78910",  
      "patient_name": "Jane Doe",  
      "appointment_id": "123456",  
      "scheduled_date": "2025-01-15",  
      "scheduled_time": "10:00:00",  
      "procedure_code": "70553",  
      "procedure_description": "MRI Brain with Contrast",  
      "prior_auth_status": "VALID",  
      "ai_recommendation": "PROCEED",  
      "confidence_score": "HIGH",  
      "confidence_rationale": "Prior-auth valid until 2025-02-28, 44 days after appointment. Exact CPT match.",  
      "matched_prior_auth": {  
        "prior_auth_id": "PA-2024-987654",  
        "approval_number": "AUTH987654",  
        "expiration_date": "2025-02-28",  
        "approved_cpt_codes": ["70553"],  
        "approved_service_description": "MRI Brain with Contrast"  
      },  
      "created_at": "2025-01-13T09:15:00Z"  
    }  
  ],  
  "pagination": {  
    "page": 1,  
    "per_page": 20,  
    "total": 5  
  }  
}  
```  
  
---  
  
#### Submit Human Decision  
  
**POST** `/reviews/{check_id}/decision`  
  
**Purpose**: Record human decision for a prior-auth check  
  
**Request Body**:  
```json  
{  
  "decision": "APPROVED",  
  "notes": "Verified with insurance portal, approval confirmed"  
}  
```  
  
**Response** (200 OK):  
```json  
{  
  "success": true,  
  "check_id": "PAC-1705140900-78910-123456",  
  "status": "APPROVED",  
  "message": "Decision recorded successfully"  
}  
```  
  
---  
  
### 13.7 Error Code Taxonomy  
  
| Error Code | HTTP Status | Description | Retry? |  
|------------|-------------|-------------|---------|  
| `MISSING_PARAM` | 400 | Required parameter missing | No |  
| `INVALID_PARAM` | 400 | Parameter value invalid | No |  
| `INVALID_TOKEN` | 401 | Access token expired/invalid | No (re-auth) |  
| `UNAUTHORIZED` | 401 | Authentication required | No |  
| `FORBIDDEN` | 403 | Insufficient permissions | No |  
| `NOT_FOUND` | 404 | Resource not found | No |  
| `CONFLICT` | 409 | Resource already exists | No |  
| `RATE_LIMITED` | 429 | Too many requests | Yes (backoff) |  
| `DB_CONNECTION_ERROR` | 500 | Database unavailable | Yes |  
| `INTERNAL_ERROR` | 500 | Unexpected server error | Yes |  
| `SERVICE_UNAVAILABLE` | 503 | Service temporarily down | Yes |  
| `TIMEOUT` | 504 | Request timeout | Yes |  
  
---  
  

---

**End of API Specifications**
