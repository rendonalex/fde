import { useState, useEffect } from 'react'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:3001'

function App() {
  // State for available claims from mock-data
  const [availableClaims, setAvailableClaims] = useState([])
  const [selectedClaims, setSelectedClaims] = useState([])
  const [searchTerm, setSearchTerm] = useState('')

  // State for claim queues
  const [toBeProcessed, setToBeProcessed] = useState([])
  const [hitlQueue, setHitlQueue] = useState([])
  const [physicianReview, setPhysicianReview] = useState([])
  const [routineClaims, setRoutineClaims] = useState([])

  // State for HITL editing
  const [editingClaim, setEditingClaim] = useState(null)
  const [selectedHitlClaims, setSelectedHitlClaims] = useState([])

  // State for processing
  const [isProcessing, setIsProcessing] = useState(false)
  const [processingStatus, setProcessingStatus] = useState('')

  // Load state from localStorage on mount
  useEffect(() => {
    const saved = localStorage.getItem('claimsWorkflowState')
    if (saved) {
      const state = JSON.parse(saved)
      setToBeProcessed(state.toBeProcessed || [])
      setHitlQueue(state.hitlQueue || [])
      setPhysicianReview(state.physicianReview || [])
      setRoutineClaims(state.routineClaims || [])
    }
  }, [])

  // Save state to localStorage whenever queues change
  useEffect(() => {
    const state = {
      toBeProcessed,
      hitlQueue,
      physicianReview,
      routineClaims
    }
    localStorage.setItem('claimsWorkflowState', JSON.stringify(state))
  }, [toBeProcessed, hitlQueue, physicianReview, routineClaims])

  // Fetch available claims on mount
  useEffect(() => {
    fetchClaims()
  }, [])

  const fetchClaims = async () => {
    try {
      const response = await fetch(`${API_URL}/api/claims`)
      const data = await response.json()
      setAvailableClaims(data.claims)
    } catch (error) {
      console.error('Error fetching claims:', error)
      alert('Failed to load claims. Make sure backend is running on port 3001.')
    }
  }

  const handleClaimSelection = (claimPath) => {
    setSelectedClaims(prev =>
      prev.includes(claimPath)
        ? prev.filter(p => p !== claimPath)
        : [...prev, claimPath]
    )
  }

  const handleAddToQueue = () => {
    const newClaims = selectedClaims.map(path => ({
      path,
      addedAt: new Date().toISOString()
    }))
    setToBeProcessed(prev => [...prev, ...newClaims])
    setSelectedClaims([])
  }

  const handleProcessClaims = async () => {
    if (toBeProcessed.length === 0) return

    setIsProcessing(true)
    setProcessingStatus(`Processing ${toBeProcessed.length} claim(s)...`)

    for (let i = 0; i < toBeProcessed.length; i++) {
      const claim = toBeProcessed[i]
      setProcessingStatus(`Processing claim ${i + 1}/${toBeProcessed.length}: ${claim.path}`)

      try {
        // Call ADR-1
        const response = await fetch(`${API_URL}/api/process-claim`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ claimPath: claim.path })
        })

        const data = await response.json()

        if (!response.ok) {
          throw new Error(data.error || 'Processing failed')
        }

        const { adr1Result, extractionResult } = data

        // Check extraction_status
        if (adr1Result.extraction_status === 'HUMAN_REQUIRED') {
          // Add to HITL queue
          setHitlQueue(prev => [...prev, {
            path: claim.path,
            extractionResult,
            normalizedRecord: adr1Result,
            lowConfidenceFields: adr1Result.low_confidence_fields || [],
            addedAt: new Date().toISOString()
          }])
        } else if (adr1Result.extraction_status === 'AUTO_COMPLETE') {
          // Call ADR-4 for triage
          await triageClaim(claim.path, extractionResult, adr1Result)
        }

        // Remove from toBeProcessed
        setToBeProcessed(prev => prev.filter(c => c.path !== claim.path))

      } catch (error) {
        console.error(`Error processing ${claim.path}:`, error)
        alert(`Failed to process ${claim.path}: ${error.message}`)
      }
    }

    setIsProcessing(false)
    setProcessingStatus('')
  }

  const triageClaim = async (claimPath, extractionResult, normalizedRecordOrAdr1Result) => {
    try {
      // Build normalized claim for ADR-4
      // If this is from HITL queue, normalizedRecordOrAdr1Result has all the data
      // If this is a normal claim, normalizedRecordOrAdr1Result is just adr1Result (minimal), so build from extractionResult

      let normalizedClaim

      // Check if this is a full normalizedRecord (from HITL) or just adr1Result (from normal flow)
      if (normalizedRecordOrAdr1Result && normalizedRecordOrAdr1Result.member_id) {
        // Full normalized record from HITL queue - use directly
        normalizedClaim = normalizedRecordOrAdr1Result
      } else {
        // Normal claim - build from extractionResult + adr1Result
        const adr1Result = normalizedRecordOrAdr1Result
        normalizedClaim = {
          claim_id: adr1Result.claim_id || `temp-${Date.now()}`,
          source_claim_ref: extractionResult.source_claim_ref,
          intake_channel: extractionResult.intake_channel,
          extraction_status: adr1Result.extraction_status,
          member_id: extractionResult.extracted_fields.member_id?.value,
          member_name_last: extractionResult.extracted_fields.member_name_last?.value,
          member_name_first: extractionResult.extracted_fields.member_name_first?.value,
          date_of_service_start: extractionResult.extracted_fields.date_of_service_start?.value,
          date_of_service_end: extractionResult.extracted_fields.date_of_service_end?.value,
          payer_name: extractionResult.extracted_fields.payer_name?.value,
          icd10_codes: extractionResult.extracted_fields.icd10_codes?.value || [],
          cpt_codes: extractionResult.extracted_fields.cpt_codes?.value || [],
          prior_auth_required: extractionResult.extracted_fields.prior_auth_required?.value || false,
          prior_auth_number: extractionResult.extracted_fields.prior_auth_number?.value || null,
          claim_type: extractionResult.extracted_fields.claim_type?.value || 'PROFESSIONAL',
          billed_amount: extractionResult.extracted_fields.billed_amount?.value,
          payer_id: extractionResult.extracted_fields.payer_id?.value,
          place_of_service: extractionResult.extracted_fields.place_of_service_code?.value
        }
      }

      const response = await fetch(`${API_URL}/api/triage-claim`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ normalizedClaim })
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Triage failed')
      }

      const { triageResult, revalidationResult, message } = data

      // If re-validation failed (still HUMAN_REQUIRED), alert user
      if (!triageResult) {
        const missingFields = revalidationResult?.low_confidence_fields || []
        alert(
          `Claim re-validation failed. Still missing fields:\n${missingFields.join(', ')}\n\n${message || 'Please correct all fields and try again.'}`
        )
        return false // Triage failed, claim stays in HITL queue
      }

      // Route based on decision
      // Build claimRecord with re-validation result as adr1Result
      const claimRecord = {
        path: claimPath,
        extractionResult: null, // Not needed for display after triage
        adr1Result: revalidationResult, // Use the re-validation result
        triageResult,
        processedAt: new Date().toISOString()
      }

      if (triageResult.routing_decision === 'CLINICAL_PATH') {
        setPhysicianReview(prev => [...prev, claimRecord])
      } else if (triageResult.routing_decision === 'FAST_PATH') {
        setRoutineClaims(prev => [...prev, claimRecord])
      }

      return true // Triage succeeded

    } catch (error) {
      console.error(`Error triaging ${claimPath}:`, error)
      alert(`Failed to triage ${claimPath}: ${error.message}`)
      return false // Triage failed, claim stays in HITL queue
    }
  }

  const handleEditHitlClaim = (claim) => {
    setEditingClaim(claim)
  }

  const handleSaveHitlClaim = () => {
    // Update the claim in hitlQueue
    // Also sync extractionResult changes to normalizedRecord
    const updatedClaim = {
      ...editingClaim,
      normalizedRecord: {
        ...editingClaim.normalizedRecord,
        // Metadata from extractionResult (important!)
        source_claim_ref: editingClaim.extractionResult.source_claim_ref,
        intake_channel: editingClaim.extractionResult.intake_channel,
        // Update fields from extractionResult
        member_id: editingClaim.extractionResult.extracted_fields.member_id?.value,
        member_name_last: editingClaim.extractionResult.extracted_fields.member_name_last?.value,
        member_name_first: editingClaim.extractionResult.extracted_fields.member_name_first?.value,
        date_of_service_start: editingClaim.extractionResult.extracted_fields.date_of_service_start?.value,
        date_of_service_end: editingClaim.extractionResult.extracted_fields.date_of_service_end?.value,
        claim_type: editingClaim.extractionResult.extracted_fields.claim_type?.value || 'PROFESSIONAL',
        icd10_codes: editingClaim.extractionResult.extracted_fields.icd10_codes?.value || [],
        cpt_codes: editingClaim.extractionResult.extracted_fields.cpt_codes?.value || [],
        prior_auth_required: editingClaim.extractionResult.extracted_fields.prior_auth_required?.value || false,
        prior_auth_number: editingClaim.extractionResult.extracted_fields.prior_auth_number?.value || null,
        payer_name: editingClaim.extractionResult.extracted_fields.payer_name?.value,
        payer_id: editingClaim.extractionResult.extracted_fields.payer_id?.value,
        billed_amount: editingClaim.extractionResult.extracted_fields.billed_amount?.value,
        place_of_service: editingClaim.extractionResult.extracted_fields.place_of_service_code?.value
      }
    }

    setHitlQueue(prev => prev.map(c =>
      c.path === editingClaim.path ? updatedClaim : c
    ))
    setEditingClaim(null)
  }

  const handleHitlSelection = (claimPath) => {
    setSelectedHitlClaims(prev =>
      prev.includes(claimPath)
        ? prev.filter(p => p !== claimPath)
        : [...prev, claimPath]
    )
  }

  const handleReadyForTriage = async () => {
    if (selectedHitlClaims.length === 0) return

    setIsProcessing(true)
    setProcessingStatus(`Triaging ${selectedHitlClaims.length} HITL claim(s)...`)

    const successfullyTriaged = []

    for (const claimPath of selectedHitlClaims) {
      const claim = hitlQueue.find(c => c.path === claimPath)
      if (!claim) continue

      const triageSuccess = await triageClaim(claim.path, claim.extractionResult, claim.normalizedRecord)

      // Only remove from HITL queue if triage succeeded
      if (triageSuccess) {
        successfullyTriaged.push(claimPath)
      }
    }

    // Remove successfully triaged claims from HITL queue
    if (successfullyTriaged.length > 0) {
      setHitlQueue(prev => prev.filter(c => !successfullyTriaged.includes(c.path)))
    }

    setSelectedHitlClaims([])
    setIsProcessing(false)
    setProcessingStatus('')
  }

  const filteredClaims = availableClaims.filter(claim =>
    claim.path.toLowerCase().includes(searchTerm.toLowerCase()) ||
    claim.filename.toLowerCase().includes(searchTerm.toLowerCase())
  )

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-blue-600 text-white p-4 shadow-lg">
        <h1 className="text-2xl font-bold">Claims Processing Workflow</h1>
        <p className="text-blue-100">Greenfield Health Systems - ADR-1 & ADR-4 Demo</p>
      </div>

      <div className="container mx-auto p-6">
        {/* Processing Status */}
        {isProcessing && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
            <div className="flex items-center">
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-yellow-600 mr-3"></div>
              <span className="text-yellow-800 font-medium">{processingStatus}</span>
            </div>
          </div>
        )}

        {/* Section 1: Claim Selector */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4 text-gray-800">Select Claims</h2>

          <div className="mb-4">
            <input
              type="text"
              placeholder="Search claims..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div className="border border-gray-200 rounded-lg max-h-60 overflow-y-auto mb-4">
            {filteredClaims.map((claim) => (
              <label
                key={claim.path}
                className="flex items-center p-3 hover:bg-gray-50 cursor-pointer border-b border-gray-100 last:border-b-0"
              >
                <input
                  type="checkbox"
                  checked={selectedClaims.includes(claim.path)}
                  onChange={() => handleClaimSelection(claim.path)}
                  className="mr-3 h-4 w-4 text-blue-600 rounded"
                />
                <span className="text-sm text-gray-700">
                  <span className="font-medium">{claim.folder}</span> / {claim.filename}
                </span>
              </label>
            ))}
          </div>

          <button
            onClick={handleAddToQueue}
            disabled={selectedClaims.length === 0}
            className="w-full bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed font-medium"
          >
            Add to Queue ({selectedClaims.length})
          </button>
        </div>

        {/* Section 2: To Be Processed Queue */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold text-gray-800">
              To Be Processed ({toBeProcessed.length})
            </h2>
            <button
              onClick={handleProcessClaims}
              disabled={toBeProcessed.length === 0 || isProcessing}
              className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 disabled:bg-gray-300 disabled:cursor-not-allowed font-medium"
            >
              Process Claim(s)
            </button>
          </div>

          <div className="space-y-2">
            {toBeProcessed.length === 0 ? (
              <p className="text-gray-500 italic">No claims in queue</p>
            ) : (
              toBeProcessed.map((claim, idx) => (
                <div key={idx} className="bg-gray-50 p-3 rounded border border-gray-200">
                  <span className="text-sm font-medium text-gray-700">{claim.path}</span>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Section 3: HITL Queue */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold text-orange-600">
              Human Review Required ({hitlQueue.length})
            </h2>
            <button
              onClick={handleReadyForTriage}
              disabled={selectedHitlClaims.length === 0 || isProcessing}
              className="bg-orange-600 text-white px-6 py-2 rounded-lg hover:bg-orange-700 disabled:bg-gray-300 disabled:cursor-not-allowed font-medium"
            >
              Ready for Triage ({selectedHitlClaims.length})
            </button>
          </div>

          <div className="space-y-2">
            {hitlQueue.length === 0 ? (
              <p className="text-gray-500 italic">No claims requiring human review</p>
            ) : (
              hitlQueue.map((claim, idx) => (
                <div key={idx} className="border border-orange-200 rounded-lg p-4 bg-orange-50">
                  <div className="flex items-start justify-between">
                    <label className="flex items-start cursor-pointer flex-1">
                      <input
                        type="checkbox"
                        checked={selectedHitlClaims.includes(claim.path)}
                        onChange={() => handleHitlSelection(claim.path)}
                        className="mr-3 mt-1 h-4 w-4 text-orange-600 rounded"
                      />
                      <div className="flex-1">
                        <p className="font-medium text-gray-800">{claim.path}</p>
                        <p className="text-sm text-orange-700 mt-1">
                          Low confidence fields: {claim.lowConfidenceFields.join(', ')}
                        </p>
                      </div>
                    </label>
                    <button
                      onClick={() => handleEditHitlClaim(claim)}
                      className="ml-3 bg-orange-600 text-white px-4 py-1 rounded hover:bg-orange-700 text-sm"
                    >
                      Edit
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Section 4: Physician Review (Clinical Path) */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-semibold text-purple-600 mb-4">
            For Physician Review - Clinical Path ({physicianReview.length})
          </h2>

          <div className="space-y-3">
            {physicianReview.length === 0 ? (
              <p className="text-gray-500 italic">No claims routed to clinical review</p>
            ) : (
              physicianReview.map((claim, idx) => (
                <ClaimResultCard key={idx} claim={claim} type="clinical" />
              ))
            )}
          </div>
        </div>

        {/* Section 5: Routine Claims (Fast Path) */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-green-600 mb-4">
            Routine - Fast Path ({routineClaims.length})
          </h2>

          <div className="space-y-3">
            {routineClaims.length === 0 ? (
              <p className="text-gray-500 italic">No claims routed to fast path</p>
            ) : (
              routineClaims.map((claim, idx) => (
                <ClaimResultCard key={idx} claim={claim} type="routine" />
              ))
            )}
          </div>
        </div>
      </div>

      {/* HITL Editing Modal */}
      {editingClaim && (
        <HitlEditModal
          claim={editingClaim}
          onSave={handleSaveHitlClaim}
          onClose={() => setEditingClaim(null)}
          onChange={setEditingClaim}
        />
      )}
    </div>
  )
}

// Component for displaying claim results with expand/collapse
function ClaimResultCard({ claim, type }) {
  const [isExpanded, setIsExpanded] = useState(false)
  const bgColor = type === 'clinical' ? 'bg-purple-50' : 'bg-green-50'
  const borderColor = type === 'clinical' ? 'border-purple-200' : 'border-green-200'
  const textColor = type === 'clinical' ? 'text-purple-700' : 'text-green-700'

  return (
    <div className={`border ${borderColor} rounded-lg p-4 ${bgColor}`}>
      <div className="flex justify-between items-start">
        <div className="flex-1">
          <p className="font-medium text-gray-800">{claim.path}</p>
          <p className={`text-sm ${textColor} mt-1`}>
            Decision: {claim.triageResult.routing_decision}
            {' '}(Confidence: {(claim.triageResult.confidence * 100).toFixed(1)}%)
          </p>
        </div>
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="text-sm text-blue-600 hover:text-blue-800 font-medium"
        >
          {isExpanded ? 'Collapse' : 'Expand'}
        </button>
      </div>

      {isExpanded && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <h4 className="font-semibold text-gray-700 mb-2">Reasoning Trace:</h4>
          <p className="text-sm text-gray-600 whitespace-pre-wrap mb-3">
            {claim.triageResult.reasoning_trace}
          </p>

          <h4 className="font-semibold text-gray-700 mb-2">ADR-4 Output:</h4>
          <pre className="text-xs bg-gray-100 p-3 rounded overflow-x-auto">
            {JSON.stringify(claim.triageResult, null, 2)}
          </pre>
        </div>
      )}
    </div>
  )
}

// Modal for editing HITL claims
function HitlEditModal({ claim, onSave, onClose, onChange }) {
  const handleFieldChange = (fieldName, newValue) => {
    const updated = {
      ...claim,
      extractionResult: {
        ...claim.extractionResult,
        extracted_fields: {
          ...claim.extractionResult.extracted_fields,
          [fieldName]: {
            ...claim.extractionResult.extracted_fields[fieldName],
            value: newValue
          }
        }
      }
    }
    onChange(updated)
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-2xl w-full max-h-[80vh] overflow-y-auto">
        <h3 className="text-xl font-bold mb-4">Edit Low Confidence Fields</h3>
        <p className="text-sm text-gray-600 mb-4">{claim.path}</p>

        <div className="space-y-4">
          {claim.lowConfidenceFields.map((fieldName) => {
            const field = claim.extractionResult.extracted_fields[fieldName]
            return (
              <div key={fieldName} className="border border-gray-200 rounded p-3">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {fieldName}
                  <span className="text-orange-600 ml-2">
                    (Confidence: {(field.confidence * 100).toFixed(1)}%)
                  </span>
                </label>
                <input
                  type="text"
                  value={field.value || ''}
                  onChange={(e) => handleFieldChange(fieldName, e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-orange-500"
                />
              </div>
            )
          })}
        </div>

        <div className="flex gap-3 mt-6">
          <button
            onClick={onSave}
            className="flex-1 bg-orange-600 text-white px-6 py-2 rounded-lg hover:bg-orange-700 font-medium"
          >
            Save Changes
          </button>
          <button
            onClick={onClose}
            className="flex-1 bg-gray-200 text-gray-800 px-6 py-2 rounded-lg hover:bg-gray-300 font-medium"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  )
}

export default App
