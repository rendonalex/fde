const express = require('express');
const cors = require('cors');
const axios = require('axios');
const fs = require('fs').promises;
const path = require('path');
const { spawn } = require('child_process');

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware
app.use(cors());
app.use(express.json());

// Paths
const MOCK_DATA_DIR = path.join(__dirname, '../../mock-data');
const DEMO_DIR = path.join(__dirname, '../../demo');
const ADR1_URL = process.env.ADR1_URL || 'http://localhost:8000';
const ADR4_URL = process.env.ADR4_URL || 'http://localhost:8001';

// Helper: Run Python preprocessor
function runPreprocessor(filePath) {
  return new Promise((resolve, reject) => {
    const pythonScript = `
import sys
sys.path.insert(0, '${DEMO_DIR}')
from preprocessors import preprocess
import json
result = preprocess('${filePath}')
print(json.dumps(result))
`;

    const python = spawn('python3', ['-c', pythonScript]);
    let stdout = '';
    let stderr = '';

    python.stdout.on('data', (data) => {
      stdout += data.toString();
    });

    python.stderr.on('data', (data) => {
      stderr += data.toString();
    });

    python.on('close', (code) => {
      if (code !== 0) {
        reject(new Error(`Python preprocessor failed: ${stderr}`));
      } else {
        try {
          const result = JSON.parse(stdout);
          resolve(result);
        } catch (e) {
          reject(new Error(`Failed to parse preprocessor output: ${stdout}`));
        }
      }
    });
  });
}

// API Routes

// GET /api/claims - List all claim files
app.get('/api/claims', async (req, res) => {
  try {
    const folders = await fs.readdir(MOCK_DATA_DIR);
    const claims = [];

    for (const folder of folders) {
      const folderPath = path.join(MOCK_DATA_DIR, folder);
      const stat = await fs.stat(folderPath);

      if (stat.isDirectory() && folder !== 'README.md') {
        const files = await fs.readdir(folderPath);

        for (const file of files) {
          const filePath = path.join(folder, file);
          claims.push({
            path: filePath,
            folder: folder,
            filename: file
          });
        }
      }
    }

    res.json({ claims });
  } catch (error) {
    console.error('Error listing claims:', error);
    res.status(500).json({ error: error.message });
  }
});

// POST /api/process-claim - Process claim through ADR-1
app.post('/api/process-claim', async (req, res) => {
  try {
    const { claimPath } = req.body;
    const fullPath = path.join(MOCK_DATA_DIR, claimPath);

    console.log(`Processing claim: ${claimPath}`);

    // Step 1: Run preprocessor to convert raw claim to ExtractionResult
    console.log('  Step 1: Running IDP preprocessor...');
    const extractionResult = await runPreprocessor(fullPath);
    console.log(`  Preprocessor output: ${extractionResult.intake_channel}`);

    // Fix: Strip hyphens from tax_id (ADR-1 expects 9 digits only)
    if (extractionResult.extracted_fields.billing_provider_tax_id?.value) {
      const taxId = extractionResult.extracted_fields.billing_provider_tax_id.value;
      extractionResult.extracted_fields.billing_provider_tax_id.value = taxId.replace(/-/g, '');
    }

    // Step 2: Call ADR-1 API
    console.log('  Step 2: Calling ADR-1 API...');
    console.log('  Sending extraction_result:', JSON.stringify(extractionResult, null, 2));
    const adr1Response = await axios.post(`${ADR1_URL}/api/v1/claims/submit`, {
      extraction_result: extractionResult
    });

    console.log(`  ADR-1 response: ${adr1Response.data.extraction_status}`);

    // Return full response + original path
    res.json({
      claimPath,
      extractionResult,
      adr1Result: adr1Response.data
    });

  } catch (error) {
    console.error('Error processing claim:', error.message);
    if (error.response) {
      console.error('ADR-1 error response:', JSON.stringify(error.response.data, null, 2));
    }
    res.status(500).json({
      error: error.message,
      details: error.response?.data || null
    });
  }
});

// POST /api/triage-claim - Triage claim through ADR-4 (with ADR-1 re-validation first)
app.post('/api/triage-claim', async (req, res) => {
  try {
    const { normalizedClaim } = req.body;

    console.log(`Triaging claim: ${normalizedClaim.claim_id || normalizedClaim.source_claim_ref}`);

    // Normalize array fields (convert comma-separated strings to arrays if needed)
    // This handles claims edited in the UI where form inputs store arrays as strings
    const normalizedClaimData = { ...normalizedClaim };

    const arrayFields = ['icd10_codes', 'cpt_codes', 'revenue_codes', 'low_confidence_fields',
                         'clinical_indicators_detected', 'criteria_provisions_matched'];

    for (const field of arrayFields) {
      if (normalizedClaimData[field]) {
        // If it's a string, split by comma and trim whitespace
        if (typeof normalizedClaimData[field] === 'string') {
          normalizedClaimData[field] = normalizedClaimData[field]
            .split(',')
            .map(item => item.trim())
            .filter(item => item.length > 0);
        }
        // If it's already an array, ensure all items are strings (not objects)
        else if (Array.isArray(normalizedClaimData[field])) {
          normalizedClaimData[field] = normalizedClaimData[field].map(item =>
            typeof item === 'string' ? item : String(item)
          );
        }
      }
    }

    // Step 1: Re-validate through ADR-1 ONLY if claim was HUMAN_REQUIRED
    // (Normal AUTO_COMPLETE claims skip this step)
    let adr1Response = null

    if (normalizedClaimData.extraction_status === 'HUMAN_REQUIRED') {
      console.log('  Step 1: Re-validating claim through ADR-1...');
      adr1Response = await axios.post(`${ADR1_URL}/api/v1/claims/revalidate`, {
        claim_data: normalizedClaimData
      });

      console.log(`  ADR-1 re-validation: ${adr1Response.data.extraction_status}`);

      // If still HUMAN_REQUIRED after re-validation, return to user
      if (adr1Response.data.extraction_status !== 'AUTO_COMPLETE') {
        return res.json({
          revalidationResult: adr1Response.data,
          triageResult: null,
          message: 'Claim still has incomplete fields. Please correct and try again.'
        });
      }

      // Update extraction_status and claim_id from ADR-1 response
      normalizedClaimData.extraction_status = 'AUTO_COMPLETE';
      normalizedClaimData.low_confidence_fields = [];
      normalizedClaimData.claim_id = adr1Response.data.claim_id; // Use the claim_id from ADR-1
    } else {
      console.log('  Step 1: Claim already AUTO_COMPLETE, skipping re-validation...');
    }

    // Step 2: Send to ADR-4 for triage
    console.log('  Step 2: Sending to ADR-4 for triage...');

    const adr4Response = await axios.post(`${ADR4_URL}/api/v1/classify`, normalizedClaimData);

    console.log(`  ADR-4 response: ${adr4Response.data.routing_decision}`);

    res.json({
      revalidationResult: adr1Response?.data || null,
      triageResult: adr4Response.data
    });

  } catch (error) {
    console.error('Error triaging claim:', error.message);
    if (error.response) {
      const service = error.config?.url?.includes('8001') ? 'ADR-4' : 'ADR-1';
      console.error(`${service} error response:`, JSON.stringify(error.response.data, null, 2));
    }
    res.status(500).json({
      error: error.message,
      details: error.response?.data || null
    });
  }
});

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', service: 'workflow-backend' });
});

// Start server
app.listen(PORT, () => {
  console.log(`✓ Workflow backend running on http://localhost:${PORT}`);
  console.log(`✓ Mock data directory: ${MOCK_DATA_DIR}`);
  console.log(`✓ ADR-1 API: ${ADR1_URL}`);
  console.log(`✓ ADR-4 API: ${ADR4_URL}`);
});
