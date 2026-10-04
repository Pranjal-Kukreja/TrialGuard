"use client"

import { useEffect, useMemo, useRef, useState } from "react"
import {
  Activity,
  Check,
  ChevronDown,
  Lock,
  Search,
  Send,
  User,
  Loader2,
  AlertTriangle,
  CheckCircle2,
  Sparkles,
  Sliders,
  RotateCcw,
  FileCheck2,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { PROTOCOLS, PATIENTS } from "@/lib/clinical-data"
import {
  getPatientsFromSupabase,
  processClinicalComment,
  updateFhirDatabase,
  type ClinicalExtractionResult,
} from "@/app/actions"
import { TrialGuardLogo } from "@/components/trialguard-logo"
import { getGatewayUrl } from "@/lib/api-config"

export type Patient = {
  patient_id: string
  trial_id: string
  name: string
  dob: string
  age: number
  sex: string
  cohort: string
  diagnosis: string
  creatinine?: string
  medications?: string[]
  clinical_data?: Record<string, any>
  report_history: any[]
}

type IntakeViewProps = {
  onSubmit: (patient: Patient, protocol: string, action: string) => void
  disqualifiedIds?: string[]
}

function evaluatePatientProfile(p: Patient, activeAction?: string) {
  const missingAge = !p.age || p.age <= 0
  const missingSex = !p.sex || p.sex.toLowerCase() === "unknown" || p.sex.trim() === ""
  const isG1 = missingAge || missingSex

  const clinical = p.clinical_data || {}
  const labs = clinical.lab_results || {}
  const alt = Number(labs.ALT?.value ?? labs.alt?.value ?? labs.ALT ?? labs.alt ?? 0)
  const ast = Number(labs.AST?.value ?? labs.ast?.value ?? labs.AST ?? labs.ast ?? 0)
  const egfr = Number(labs.eGFR?.value ?? labs.egfr?.value ?? labs.eGFR ?? labs.egfr ?? 90)
  const bili = Number(labs.total_bilirubin?.value ?? labs.bilirubin?.value ?? labs.total_bilirubin ?? labs.bilirubin ?? 0.8)
  const anc = Number(labs.ANC?.value ?? labs.anc?.value ?? labs.ANC ?? labs.anc ?? 3500)
  const isG2 = !isG1 && (alt > 200 || ast > 200 || egfr < 15 || bili > 4.0 || anc < 500)

  const protocolFacts = clinical.protocol_facts || {}
  const bleedDays = protocolFacts.days_since_major_bleed !== undefined ? Number(protocolFacts.days_since_major_bleed) : 999
  const autoimmune = Boolean(protocolFacts.active_autoimmune_disease)
  const rawCrcl = labs.creatinine_clearance?.value ?? labs.creatinine_clearance ?? (p.creatinine ? p.creatinine.match(/\d+/)?.[0] : 65) ?? 65
  const crclVal = Number(rawCrcl)

  const act = (activeAction || "").toLowerCase()
  const doseExceeded = act.includes("40 mg") || act.includes("40mg") || act.includes("60 mg") || act.includes("60mg") || act.includes("400 mg") || act.includes("400mg")
  const isRagRule = !isG1 && !isG2 && (bleedDays < 30 || autoimmune || (crclVal > 0 && crclVal < 30) || doseExceeded)

  const meds = Array.isArray(p.medications) ? p.medications.map((m: any) => String(m).toLowerCase()) : []
  const hasDdi = meds.some(m => m.includes("ketoconazole") || m.includes("clarithromycin") || (m.includes("aspirin") && meds.some(m2 => m2.includes("clopidogrel"))))
  const financialIssue = (clinical.financial?.copay > 10000) || (clinical.financial?.out_of_pocket > 10000) || (clinical.financial?.reimbursement_tier === "TIER_4_RESTRICTED")
  const isA2A = !isG1 && !isG2 && !isRagRule && (hasDdi || financialIssue)

  const isClean = !isG1 && !isG2 && !isRagRule && !isA2A

  return {
    missingAge,
    missingSex,
    isG1,
    isG2,
    isRagRule,
    isA2A,
    isClean,
    alt,
    ast,
    egfr,
    bili,
    anc,
    bleedDays,
    autoimmune,
    crclVal,
    doseExceeded,
    hasDdi,
    financialIssue,
  }
}

export function IntakeView({ onSubmit, disqualifiedIds = [] }: IntakeViewProps) {
  const [patients, setPatients] = useState<Patient[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [query, setQuery] = useState("")
  const [open, setOpen] = useState(false)
  const [selected, setSelected] = useState<Patient | null>(null)
  const [protocol, setProtocol] = useState(PROTOCOLS[0])
  const [action, setAction] = useState("Apixaban 5 mg oral twice daily")
  const containerRef = useRef<HTMLDivElement>(null)
  const modifyDrawerRef = useRef<HTMLDivElement>(null)

  const [modifyOpen, setModifyOpen] = useState(false)
  const [doctorNote, setDoctorNote] = useState("")
  const [isExtracting, setIsExtracting] = useState(false)
  const [extractionResult, setExtractionResult] = useState<ClinicalExtractionResult | null>(null)
  const [fhirSynced, setFhirSynced] = useState(false)
  const [fhirSyncing, setFhirSyncing] = useState(false)

  const isDisqualified = Boolean(selected && disqualifiedIds.includes(selected.patient_id))

  const selectedEval = useMemo(() => {
    if (!selected) return null
    return evaluatePatientProfile(selected, action)
  }, [selected, action])

  const dosingGuidelines = useMemo(() => {
    if (!selected) return null
    const meds = selected.medications || []
    const cohort = selected.cohort || ""
    const diagnosis = selected.diagnosis || ""
    const selText = `${cohort} ${diagnosis} ${meds.join(" ")}`.toLowerCase()

    let drug = "Apixaban"
    let standardDose = "Apixaban 5 mg oral twice daily"
    let escalatedDose = "Apixaban 40 mg oral twice daily"
    let standardLabel = "✓ Standard 5 mg BID (Compliant)"
    let escalatedLabel = "⚠️ Escalated 40 mg BID (Dose Violation)"

    if (selText.includes("oncology") || selText.includes("pembrolizumab") || selText.includes("carcinoma") || selText.includes("cancer")) {
      drug = "Pembrolizumab"
      standardDose = "Pembrolizumab 200 mg IV every 3 weeks"
      escalatedDose = "Pembrolizumab 400 mg IV every 3 weeks"
      standardLabel = "✓ Standard 200 mg Q3W (Compliant)"
      escalatedLabel = "⚠️ Escalated 400 mg Q3W (Dose Violation)"
    } else if (selText.includes("renal") || selText.includes("empagliflozin") || selText.includes("nephropathy")) {
      drug = "Empagliflozin"
      standardDose = "Empagliflozin 10 mg oral once daily"
      escalatedDose = "Empagliflozin 50 mg oral once daily"
      standardLabel = "✓ Standard 10 mg Daily (Compliant)"
      escalatedLabel = "⚠️ Escalated 50 mg Daily (Dose Violation)"
    } else if (selText.includes("nafld") || selText.includes("mash") || selText.includes("pioglitazone") || selText.includes("steatohepatitis")) {
      drug = "Pioglitazone"
      standardDose = "Pioglitazone 30 mg oral once daily"
      escalatedDose = "Pioglitazone 90 mg oral once daily"
      standardLabel = "✓ Standard 30 mg Daily (Compliant)"
      escalatedLabel = "⚠️ Escalated 90 mg Daily (Dose Violation)"
    }

    const actionLower = action.toLowerCase()
    const isViolation =
      actionLower.includes("40 mg") ||
      actionLower.includes("40mg") ||
      actionLower.includes("60 mg") ||
      actionLower.includes("60mg") ||
      actionLower.includes("400 mg") ||
      actionLower.includes("400mg") ||
      actionLower.includes("50 mg") ||
      actionLower.includes("50mg") ||
      actionLower.includes("90 mg") ||
      actionLower.includes("90mg")

    return {
      drug,
      standardDose,
      escalatedDose,
      standardLabel,
      escalatedLabel,
      isViolation,
    }
  }, [selected, action])

  // Synchronize and persist to FHIR Database
  async function executeFhirUpdate(res?: ClinicalExtractionResult | null, targetAction?: string) {
    if (!selected) return
    const activeRes = res || extractionResult
    if (!activeRes || !activeRes.is_valid || activeRes.is_appropriate === false) return

    setFhirSyncing(true)
    try {
      const mod = activeRes.modifications?.[0]
      const stdDrug = activeRes.standardized_drug || mod?.dosage_name || dosingGuidelines?.drug || "Apixaban"
      const dosageVal = activeRes.dosage ?? mod?.proposed_dosage ?? 5
      const unitVal = activeRes.dosage_unit || mod?.dosage_unit || "mg"
      const routeVal = activeRes.route || mod?.route || "oral"
      const freqVal = activeRes.frequency || mod?.frequency || "twice daily"
      const scheduleVal = activeRes.timing_schedule || mod?.timing_schedule || "08:00, 20:00"
      const stdAction = activeRes.standardized_action || targetAction || action

      await updateFhirDatabase(selected.patient_id, {
        standardized_action: stdAction,
        standardized_drug: stdDrug,
        dosage: dosageVal,
        dosage_unit: unitVal,
        route: routeVal,
        frequency: freqVal,
        timing_schedule: scheduleVal,
        doctor_note: doctorNote || action,
        target_fhir_field: activeRes.target_fhir_field || mod?.target_field || "MedicationRequest.dosageInstruction[0]",
      })

      const freqAbbr =
        freqVal.toLowerCase().includes("twice") || freqVal.toLowerCase().includes("bid")
          ? "BID"
          : freqVal.toLowerCase().includes("3 weeks") || freqVal.toLowerCase().includes("q3w")
          ? "IV Q3W"
          : "daily"
      const newMedStr = `${stdDrug} ${dosageVal}${unitVal} ${freqAbbr}`
      const existingMeds = Array.isArray(selected.medications) ? [...selected.medications] : []
      const drugRegex = new RegExp(stdDrug, "i")
      const updatedMeds = existingMeds.map((m) => (drugRegex.test(m) ? newMedStr : m))
      if (!updatedMeds.some((m) => drugRegex.test(m))) {
        updatedMeds.unshift(newMedStr)
      }

      const updatedPatient: Patient = {
        ...selected,
        medications: updatedMeds,
        clinical_data: {
          ...(selected.clinical_data || {}),
          prescribed_action: stdAction,
          medications: updatedMeds,
          dosage_instructions: {
            dose: Number(dosageVal) || dosageVal,
            unit: unitVal,
            frequency: freqVal,
            timing_schedule: scheduleVal,
            route: routeVal,
          },
        },
      }

      setSelected(updatedPatient)
      setPatients((prev) => prev.map((p) => (p.patient_id === selected.patient_id ? updatedPatient : p)))
      setAction(stdAction)
      setFhirSynced(true)
    } catch (err) {
      console.error("FHIR update error:", err)
    } finally {
      setFhirSyncing(false)
    }
  }

  // Apply 1-Click Protocol Remediation
  async function handleApplyRemediation(targetDose?: string) {
    if (!selected) return
    const doseToApply = targetDose || dosingGuidelines?.standardDose || "Apixaban 5 mg oral twice daily"
    setAction(doseToApply)
    const promptText = `Adjust dosage to standard ${doseToApply} per protocol guidelines.`
    setDoctorNote(promptText)
    setIsExtracting(true)
    setFhirSynced(false)

    try {
      const result = await processClinicalComment(promptText)
      setExtractionResult(result)
      if (result.is_valid && result.is_appropriate !== false) {
        await executeFhirUpdate(result, doseToApply)
      }
    } catch (err) {
      console.warn("Remediation evaluation fallback:", err)
    } finally {
      setIsExtracting(false)
    }
  }

  // Clinical LLM Extraction & Evaluation
  async function handleExtract(customText?: string) {
    const textToEval = (customText ?? doctorNote ?? action).trim()
    if (!textToEval) return
    setIsExtracting(true)
    setFhirSynced(false)
    try {
      const result = await processClinicalComment(textToEval)
      setExtractionResult(result)
      if (result.is_valid && result.is_appropriate !== false && result.standardized_action) {
        setAction(result.standardized_action)
      }
    } catch (err) {
      console.error("Clinical extraction error:", err)
    } finally {
      setIsExtracting(false)
    }
  }

  // Handle Review Submission
  async function handleSubmitClick() {
    if (!selected || isDisqualified) return

    if (extractionResult && (!extractionResult.is_valid || extractionResult.is_appropriate === false)) {
      return
    }

    if (extractionResult?.is_valid && extractionResult.is_appropriate !== false && !fhirSynced) {
      await executeFhirUpdate(extractionResult, action)
    }

    onSubmit(selected, protocol, action)
  }

  useEffect(() => {
    async function fetchPatients() {
      try {
        setIsLoading(true)
        let data: any = null

        // Try Supabase first
        try {
          data = await getPatientsFromSupabase()
        } catch (supabaseErr) {
          console.warn("Supabase fetch failed, trying local gateway /api/patients:", supabaseErr)
        }

        // Fall back to FastAPI gateway /api/patients
        if (!data || !Array.isArray(data) || data.length === 0) {
          try {
            const baseUrl = getGatewayUrl()
            const res = await fetch(`${baseUrl}/api/patients`)
            if (res.ok) {
              data = await res.json()
            }
          } catch (gatewayErr) {
            console.warn("Gateway /api/patients fetch failed:", gatewayErr)
          }
        }

        // Fall back to local PATIENTS if remote endpoints are unavailable
        if (!data || !Array.isArray(data) || data.length === 0) {
          data = PATIENTS
        }

        if (data && Array.isArray(data) && data.length > 0) {
          const mapped: Patient[] = data.map((item: any) => {
            const clinical = item.clinical_data || item
            const labResults = clinical.lab_results || {}
            const crclObj = labResults.creatinine_clearance
            const scrObj = labResults.serum_creatinine
            const crclVal = typeof crclObj === "object" ? crclObj?.value : crclObj ?? item.creatinine_clearance ?? item.crcl
            const scrVal = typeof scrObj === "object" ? scrObj?.value : scrObj ?? item.serum_creatinine ?? item.creatinine
            let renalStr = "CrCl 55 mL/min"
            if (crclVal !== undefined && crclVal !== null) {
              renalStr = `CrCl ${crclVal} mL/min`
            } else if (scrVal && scrVal !== "unknown") {
              renalStr = `Serum Cr ${scrVal} mg/dL`
            }

            return {
              patient_id: String(item.patient_id || item.id || ""),
              trial_id: String(item.trial_id || item.assigned_demo_trial_id || "NCT02415400"),
              name: String(item.name || `Patient ${item.patient_id || item.id}`),
              dob: String(item.dob || item.birth_date || "1960-01-01"),
              age: item.age !== undefined && item.age !== null ? Number(item.age) : 0,
              sex: item.sex !== undefined && item.sex !== null ? String(item.sex) : "",
              cohort: String(item.cohort || "Cohort A"),
              diagnosis: String(item.diagnosis || (clinical.diagnoses ? clinical.diagnoses[0] : "Standard Protocol")),
              creatinine: renalStr,
              medications: Array.isArray(item.medications) ? item.medications : (clinical.medications || []),
              clinical_data: clinical,
              report_history: Array.isArray(item.report_history)
                ? item.report_history
                : Array.isArray(item.adjudication_reports)
                ? item.adjudication_reports
                : [],
            }
          })
          setPatients(mapped)
          if (mapped.length > 0) {
            choose(mapped[0])
          }
        }
      } catch (error) {
        console.error("Error fetching patients:", error)
      } finally {
        setIsLoading(false)
      }
    }

    fetchPatients()
  }, [])

  const results = useMemo(() => {
    const q = query.trim().toLowerCase()
    if (!q) return patients
    return patients.filter(
      (p) =>
        p.patient_id.toLowerCase().includes(q) ||
        p.name.toLowerCase().includes(q),
    )
  }, [query, patients])

  function choose(patient: Patient) {
    setSelected(patient)
    setQuery(patient.name)
    setOpen(false)

    const pid = patient.patient_id || ""
    const meds = patient.medications || []
    const cohort = patient.cohort || ""
    const diagnosis = patient.diagnosis || ""
    const allText = `${cohort} ${diagnosis} ${meds.join(" ")}`.toLowerCase()

    // 1. Direct handler for Scenario Test Patients (G1, G2, RAG, A2A, and Clean Justified)
    const PRESETS: Record<string, { protocol: string; action: string }> = {
      P034: { protocol: "NCT02415400 - Phase II Antithrombotic Trial (Arm A: Apixaban 5mg BID)", action: "Apixaban 5 mg oral twice daily" },
      P038: { protocol: "NCT02415400 - Phase II Antithrombotic Trial (Arm A: Apixaban 5mg BID)", action: "Apixaban 5 mg oral twice daily" },
      P039: { protocol: "NCT00699998 - Renal Stratification SGLT2i Study (Cohort B)", action: "Empagliflozin 10 mg oral once daily" },
      P040: { protocol: "NCT02415400 - Cohort C Solid Tumor Oncology (Pembrolizumab 200mg Q3W)", action: "Capecitabine 1000 mg oral twice daily" },
      P035: { protocol: "NCT00809965 - NAFLD / MASH Dose Escalation Protocol (Cohort B)", action: "Pioglitazone 30 mg oral once daily" },
      P041: { protocol: "NCT00699998 - Renal Stratification SGLT2i Study (Cohort B)", action: "Empagliflozin 10 mg oral once daily" },
      P042: { protocol: "NCT00809965 - NAFLD / MASH Dose Escalation Protocol (Cohort B)", action: "Pioglitazone 30 mg oral once daily" },
      P043: { protocol: "NCT02415400 - Cohort C Solid Tumor Oncology (Pembrolizumab 200mg Q3W)", action: "Pembrolizumab 200 mg IV every 3 weeks" },
      P036: { protocol: "NCT02415400 - Phase II Antithrombotic Trial (Arm A: Apixaban 5mg BID)", action: "Apixaban 40 mg oral twice daily" },
      P044: { protocol: "NCT02415400 - Phase II Antithrombotic Trial (Arm A: Apixaban 5mg BID)", action: "Apixaban 60 mg oral twice daily" },
      P045: { protocol: "NCT02415400 - Phase II Antithrombotic Trial (Arm A: Apixaban 5mg BID)", action: "Apixaban 5 mg oral twice daily" },
      P046: { protocol: "NCT00699998 - Renal Stratification SGLT2i Study (Cohort B)", action: "Empagliflozin 10 mg oral once daily" },
      P047: { protocol: "NCT02415400 - Cohort C Solid Tumor Oncology (Pembrolizumab 200mg Q3W)", action: "Pembrolizumab 200 mg IV every 3 weeks" },
      P037: { protocol: "NCT02415400 - Cohort C Solid Tumor Oncology (Pembrolizumab 200mg Q3W)", action: "Pembrolizumab 400 mg IV every 3 weeks" },
      P048: { protocol: "NCT02415400 - Phase II Antithrombotic Trial (Arm A: Apixaban 5mg BID)", action: "Apixaban 5 mg oral twice daily" },
      P049: { protocol: "NCT02415400 - Cohort C Solid Tumor Oncology (Pembrolizumab 200mg Q3W)", action: "Pembrolizumab 200 mg IV every 3 weeks" },
      P050: { protocol: "NCT00781573 - Post-PCI Dual Therapy Protocol (Arm A)", action: "Apixaban 5 mg oral twice daily" },
      P001: { protocol: "NCT00699998 - Renal Stratification SGLT2i Study (Cohort B)", action: "Empagliflozin 10 mg oral once daily" },
      P006: { protocol: "NCT02415400 - Phase II Antithrombotic Trial (Arm A: Apixaban 5mg BID)", action: "Apixaban 5 mg oral twice daily" },
      P051: { protocol: "NCT02415400 - Phase II Antithrombotic Trial (Arm A: Apixaban 5mg BID)", action: "Apixaban 5 mg oral twice daily" },
      P052: { protocol: "NCT02415400 - Cohort C Solid Tumor Oncology (Pembrolizumab 200mg Q3W)", action: "Pembrolizumab 200 mg IV every 3 weeks" },
      P053: { protocol: "NCT00809965 - NAFLD / MASH Dose Escalation Protocol (Cohort B)", action: "Pioglitazone 30 mg oral once daily" },
      P054: { protocol: "NCT00699998 - Renal Stratification SGLT2i Study (Cohort B)", action: "Empagliflozin 10 mg oral once daily" },
    }
    if (PRESETS[pid]) {
      setProtocol(PRESETS[pid].protocol)
      setAction(PRESETS[pid].action)
      setDoctorNote(PRESETS[pid].action)
      setExtractionResult(null)
      setFhirSynced(false)
      setModifyOpen(false)
      return
    }

    // Synchronize protocol matching the patient's trial and clinical pathology
    let matchedProtocol: string | undefined
    if (allText.includes("oncology") || allText.includes("pembrolizumab") || allText.includes("carcinoma") || allText.includes("cancer")) {
      matchedProtocol = PROTOCOLS.find((p) => p.includes("Oncology")) || `${patient.trial_id} - Cohort C Solid Tumor Oncology`
    } else if (allText.includes("renal") || allText.includes("nephropathy") || allText.includes("empagliflozin") || patient.trial_id === "NCT00699998") {
      matchedProtocol = PROTOCOLS.find((p) => p.includes("Renal Stratification")) || `${patient.trial_id} - Cohort B Renal Stratification`
    } else if (allText.includes("nafld") || allText.includes("mash") || allText.includes("pioglitazone") || patient.trial_id === "NCT00809965") {
      matchedProtocol = PROTOCOLS.find((p) => p.includes("NAFLD / MASH")) || `${patient.trial_id} - Cohort B NAFLD Protocol`
    } else {
      matchedProtocol = PROTOCOLS.find((p) => p.startsWith(patient.trial_id)) || `${patient.trial_id} - ${patient.cohort}`
    }
    setProtocol(matchedProtocol)

    // Tailor default proposed action to the patient's clinical archetype and medications
    if (
      meds.some((m) => m.toLowerCase().includes("pembrolizumab")) ||
      allText.includes("oncology") ||
      allText.includes("carcinoma") ||
      allText.includes("cancer")
    ) {
      setAction("Pembrolizumab 200 mg IV every 3 weeks")
    } else if (
      meds.some((m) => m.toLowerCase().includes("empagliflozin")) ||
      allText.includes("renal") ||
      allText.includes("nephropathy") ||
      patient.trial_id === "NCT00699998"
    ) {
      setAction("Empagliflozin 10 mg oral once daily")
    } else if (
      meds.some((m) => m.toLowerCase().includes("pioglitazone")) ||
      allText.includes("nafld") ||
      allText.includes("mash") ||
      allText.includes("steatohepatitis") ||
      patient.trial_id === "NCT00809965"
    ) {
      setAction("Pioglitazone 30 mg oral once daily")
    } else if (
      meds.some((m) => m.toLowerCase().includes("apixaban")) ||
      allText.includes("atrial") ||
      patient.trial_id === "NCT00781573" ||
      patient.trial_id === "NCT02415400"
    ) {
      setAction("Apixaban 5 mg oral twice daily")
    } else {
      setAction("Apixaban 5 mg oral twice daily")
    }
    setExtractionResult(null)
    setFhirSynced(false)
    setModifyOpen(false)
  }

  return (
    <div className="min-h-screen bg-[#121212] text-white">
      <header className="flex flex-wrap items-center justify-between border-b border-[#262626] bg-[#141414]/95 px-6 py-4 backdrop-blur gap-4">
        <TrialGuardLogo className="h-9 w-auto" showSubtitle />
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center gap-2 rounded-full border border-emerald-500/30 bg-emerald-500/10 px-3.5 py-1 font-mono text-[11px] text-emerald-400">
            <span className="size-2 rounded-full bg-emerald-400 animate-ping" />
            <span>FHIR EMR Ingress Active</span>
          </div>
          <span className="rounded-full border border-[#2e2e2e] bg-[#1a1a1a] px-3.5 py-1 text-xs font-medium text-slate-300">
            Site 04 — Massachusetts General Hospital
          </span>
        </div>
      </header>

      <main className="px-4 pb-20 pt-8">
        <div className="mx-auto max-w-3xl rounded-2xl border border-[#2a2a2a] bg-[#161616] p-7 md:p-9 shadow-2xl space-y-7">
          <div className="border-b border-[#262626] pb-5">
            <h1 className="text-xl font-bold tracking-tight text-white md:text-2xl">
              Initiate Patient Adjudication Session
            </h1>
            <p className="mt-1.5 text-sm text-slate-400 leading-relaxed">
              Query trial subjects from the EHR/FHIR repository, review baseline clinical telemetry, and submit proposed medication orders for autonomous multi-agent consensus review.
            </p>
          </div>

          {/* Patient lookup combobox */}
          <div className="mt-6">
            <div className="mb-1.5 flex items-center justify-between">
              <label className="block text-xs font-medium uppercase tracking-wide text-slate-400">
                Patient Lookup {isLoading && <Loader2 className="inline ml-2 size-3 animate-spin" />}
              </label>
              {!selected && (
                <span className="text-[11px] text-amber-400 font-medium">
                  Click a patient or preset below to proceed →
                </span>
              )}
            </div>
            <div ref={containerRef} className="relative">
              <div className="flex items-center gap-2 rounded-lg border border-[#2e2e2e] bg-[#121212] px-3 focus-within:border-[#3b82f6]">
                <Search className="size-4 shrink-0 text-slate-500" />
                <input
                  value={query}
                  onChange={(e) => {
                    setQuery(e.target.value)
                    setOpen(true)
                    if (selected) setSelected(null)
                  }}
                  onFocus={() => setOpen(true)}
                  onBlur={() => window.setTimeout(() => setOpen(false), 150)}
                  placeholder={isLoading ? "Connecting to database..." : "Search by Patient ID or name…"}
                  disabled={isLoading}
                  className="h-10 w-full bg-transparent text-sm text-white placeholder:text-slate-500 focus:outline-none disabled:opacity-50"
                  aria-label="Search patients"
                />
                <ChevronDown
                  className={`size-4 shrink-0 text-slate-500 transition-transform ${
                    open ? "rotate-180" : ""
                  }`}
                />
              </div>

              {open && (
                <ul className="absolute z-20 mt-1 max-h-64 w-full overflow-auto rounded-lg border border-[#2e2e2e] bg-[#1e1e1e] py-1 shadow-xl">
                  {results.length === 0 && (
                    <li className="px-3 py-4 text-center text-sm text-slate-500">
                      No matching patients.
                    </li>
                  )}
                  {results.map((p) => {
                    const isDisqualifiedItem = disqualifiedIds.includes(p.patient_id)
                    const evalRes = evaluatePatientProfile(p)
                    const { isG1, isG2, isRagRule, isA2A, isClean } = evalRes
                    const isNonAligned = isG1 || isG2 || isRagRule || isA2A

                    return (
                      <li key={p.patient_id}>
                        <button
                          type="button"
                          onMouseDown={(e) => {
                            e.preventDefault()
                            choose(p)
                          }}
                          onClick={(e) => {
                            e.preventDefault()
                            choose(p)
                          }}
                          className={`flex w-full items-center justify-between gap-3 px-3 py-2.5 text-left hover:bg-[#2a2a2a] transition-colors ${
                            isDisqualifiedItem
                              ? "border-l-2 border-rose-600 bg-rose-950/20"
                              : isNonAligned
                              ? "border-l-2 border-amber-500/80 bg-[#161616]"
                              : isClean
                              ? "border-l-2 border-emerald-500/80 bg-emerald-950/10"
                              : ""
                          }`}
                        >
                          <span className="flex items-center gap-3">
                            <span
                              className={`flex size-8 shrink-0 items-center justify-center rounded-md ${
                                isDisqualifiedItem
                                  ? "bg-rose-600/30 text-rose-300"
                                  : isG1 || isG2
                                  ? "bg-rose-500/20 text-rose-400"
                                  : isRagRule
                                  ? "bg-amber-500/20 text-amber-400"
                                  : isA2A
                                  ? "bg-purple-500/20 text-purple-400"
                                  : isClean
                                  ? "bg-emerald-500/20 text-emerald-400"
                                  : "bg-[#121212] text-slate-400"
                              }`}
                            >
                              {isDisqualifiedItem ? <Lock className="size-4" /> : <User className="size-4" />}
                            </span>
                            <div>
                              <div className="flex flex-wrap items-center gap-2">
                                <span className="block text-sm font-medium text-white">
                                  {p.name}
                                </span>
                                {isDisqualifiedItem && (
                                  <span className="rounded bg-rose-600/30 px-1.5 py-0.5 font-mono text-[9px] font-bold text-rose-200 border border-rose-500/60">
                                    ⛔ Disqualified (3/3)
                                  </span>
                                )}
                                {!isDisqualifiedItem && isG1 && (
                                  <span className="rounded bg-rose-500/20 px-1.5 py-0.5 font-mono text-[9px] font-bold text-rose-300 border border-rose-500/30">
                                    G1 Ingress Failure
                                  </span>
                                )}
                                {isG2 && (
                                  <span className="rounded bg-rose-500/20 px-1.5 py-0.5 font-mono text-[9px] font-bold text-rose-300 border border-rose-500/30">
                                    G2 Boundary Breach
                                  </span>
                                )}
                                {isRagRule && (
                                  <span className="rounded bg-amber-500/20 px-1.5 py-0.5 font-mono text-[9px] font-bold text-amber-300 border border-amber-500/30">
                                    Protocol Deviation
                                  </span>
                                )}
                                {isA2A && (
                                  <span className="rounded bg-purple-500/20 px-1.5 py-0.5 font-mono text-[9px] font-bold text-purple-300 border border-purple-500/30">
                                    4 A2A Rejection
                                  </span>
                                )}
                                {isClean && (
                                  <span className="rounded bg-emerald-500/20 px-1.5 py-0.5 font-mono text-[9px] font-bold text-emerald-300 border border-emerald-500/30">
                                    ✓ Justified Pass
                                  </span>
                                )}
                              </div>
                              <span className="block font-mono text-xs text-slate-500">
                                {p.patient_id} · {p.diagnosis}
                              </span>
                            </div>
                          </span>
                          <span
                            className={`rounded-full border px-2 py-0.5 text-[11px] font-medium shrink-0 ${
                              isDisqualifiedItem
                                ? "border-rose-500/60 bg-rose-950/60 text-rose-300 font-bold"
                                : isG1 || isG2
                                ? "border-rose-500/40 bg-rose-500/10 text-rose-300"
                                : isRagRule
                                ? "border-amber-500/40 bg-amber-500/10 text-amber-300"
                                : isA2A
                                ? "border-purple-500/40 bg-purple-500/10 text-purple-300"
                                : isClean
                                ? "border-emerald-500/40 bg-emerald-500/10 text-emerald-300 font-semibold"
                                : "border-[#2e2e2e] bg-[#121212] text-slate-300"
                            }`}
                          >
                            {isDisqualifiedItem
                              ? "Locked Out"
                              : isG1
                              ? "Ingress Test"
                              : isG2
                              ? "Safety Corridor"
                              : isRagRule
                              ? "RAG Dosing"
                              : isA2A
                              ? "A2A Consensus"
                              : isClean
                              ? "✓ JUSTIFIED · Eligible"
                              : p.cohort}
                          </span>
                        </button>
                      </li>
                    )
                  })}
                </ul>
              )}
            </div>
          </div>

          {/* Selected patient details */}
          {selected && (
            <div className="rounded-xl border border-[#303030] bg-gradient-to-b from-[#181818] to-[#121212] p-5 md:p-6 space-y-4 shadow-xl">
              <div className="flex flex-wrap items-center justify-between gap-2 border-b border-[#262626] pb-3">
                <div className="flex items-center gap-2">
                  <div className="flex size-6 items-center justify-center rounded-full bg-emerald-500/20 text-emerald-400">
                    <Check className="size-3.5" />
                  </div>
                  <span className="text-xs font-bold uppercase tracking-wider text-emerald-400">
                    Subject Profile Loaded · Verified EMR Record
                  </span>
                </div>
                {selectedEval?.isG1 && (
                  <span className="rounded-full border border-rose-500/40 bg-rose-500/15 px-2.5 py-0.5 font-mono text-[10px] font-bold text-rose-300">
                    TEST CASE: Guardrail-1 Ingress Failure
                  </span>
                )}
                {selectedEval?.isG2 && (
                  <span className="rounded-full border border-rose-500/40 bg-rose-500/15 px-2.5 py-0.5 font-mono text-[10px] font-bold text-rose-300">
                    TEST CASE: Guardrail-2 Hard Boundary Breach
                  </span>
                )}
                {selectedEval?.isRagRule && (
                  <span className="rounded-full border border-amber-500/40 bg-amber-500/15 px-2.5 py-0.5 font-mono text-[10px] font-bold text-amber-300">
                    TEST CASE: Protocol & RAG Rules Non-Compliance
                  </span>
                )}
                {selectedEval?.isA2A && (
                  <span className="rounded-full border border-purple-500/40 bg-purple-500/15 px-2.5 py-0.5 font-mono text-[10px] font-bold text-purple-300">
                    TEST CASE: 4 A2A Pipelines Consensus Rejection
                  </span>
                )}
                <div className="flex flex-wrap items-center gap-2">
                  {selectedEval?.isClean && (
                    <span className="rounded-full border border-emerald-500/40 bg-emerald-500/15 px-2.5 py-0.5 font-mono text-[10px] font-bold text-emerald-300">
                      TEST CASE: 100% Unanimous Justified Pass
                    </span>
                  )}
                  <Button
                    size="sm"
                    disabled={isDisqualified}
                    onClick={() => !isDisqualified && onSubmit(selected, protocol, action)}
                    className="h-7.5 rounded-lg bg-[#3b82f6] hover:bg-[#2563eb] text-white font-semibold text-xs px-3 shadow-md shadow-blue-950/40"
                  >
                    <Send className="size-3 mr-1.5" />
                    Submit for AI Review →
                  </Button>
                </div>
              </div>

              {/* Dynamic Clinical Scenario Notice Box */}
              {selectedEval?.isG1 && (
                <div className="rounded-xl border border-rose-500/40 bg-rose-950/30 p-3.5 text-xs text-rose-200 leading-relaxed space-y-1">
                  <strong className="text-rose-300">Mandatory Demographics Missing:</strong>{" "}
                  {selectedEval.missingAge && selectedEval.missingSex
                    ? "Patient age is unrecorded and biological sex is empty."
                    : selectedEval.missingAge
                    ? "Patient age / birth date is unrecorded."
                    : "Biological sex is unrecorded."}{" "}
                  Triggers <strong>Guardrail-1 Ingress Validation</strong> failure per 21 CFR 312.62. Clinician resupply console will activate during adjudication session.
                </div>
              )}
              {selectedEval?.isG2 && (
                <div className="rounded-xl border border-rose-500/40 bg-rose-950/30 p-3.5 text-xs text-rose-200 leading-relaxed space-y-1">
                  <strong className="text-rose-300">Catastrophic Boundary Breach:</strong>{" "}
                  {selectedEval.alt > 200 || selectedEval.ast > 200
                    ? `ALT is ${selectedEval.alt} U/L and AST is ${selectedEval.ast} U/L (> 200 ULN limit).`
                    : selectedEval.egfr < 15
                    ? `eGFR is ${selectedEval.egfr} mL/min/1.73m² (< 15.0 ESRD floor).`
                    : selectedEval.bili > 4.0
                    ? `Total bilirubin is ${selectedEval.bili} mg/dL (> 4.0 mg/dL ceiling).`
                    : `Absolute Neutrophil Count is ${selectedEval.anc} /µL (< 500 /µL critical hematologic floor).`}{" "}
                  Triggers <strong>Guardrail-2 Immediate Short-Circuit</strong> stopping drug administration.
                </div>
              )}
              {selectedEval?.isRagRule && (
                <div className="rounded-xl border border-amber-500/40 bg-amber-950/30 p-3.5 text-xs text-amber-200 leading-relaxed space-y-1">
                  <strong className="text-amber-300">Protocol Rule Violation:</strong>{" "}
                  {selectedEval.bleedDays < 30
                    ? `Acute hemorrhage documented ${selectedEval.bleedDays} days ago (violates protocol 30-day washout).`
                    : selectedEval.doseExceeded
                    ? `Prescribed dosage (${action}) exceeds trial protocol maximum approved ceiling.`
                    : selectedEval.autoimmune
                    ? "Active autoimmune disease on systemic immunosuppressants contraindicates protocol eligibility."
                    : `Observed CrCl is ${selectedEval.crclVal} mL/min (< 30 mL/min protocol eligibility threshold).`}{" "}
                  Triggers <strong>Protocol &amp; RAG Non-Compliance</strong> rejection.
                </div>
              )}
              {selectedEval?.isA2A && (
                <div className="rounded-xl border border-purple-500/40 bg-purple-950/30 p-3.5 text-xs text-purple-200 leading-relaxed space-y-1">
                  <strong className="text-purple-300">Multi-Agent Specialist Dissent:</strong>{" "}
                  {selectedEval.hasDdi
                    ? "Severe pharmacokinetic drug-drug interaction (CYP3A4/P-gp dual inhibition) identified by Safety Specialist."
                    : "High out-of-pocket financial liability not covered under sponsor trial agreement identified by Financial Risk Specialist."}{" "}
                  Triggers <strong>A2A Specialist Consensus Rejection</strong>.
                </div>
              )}
              {selectedEval?.isClean && (
                <div className="rounded-xl border border-emerald-500/40 bg-emerald-950/30 p-3.5 text-xs text-emerald-200 leading-relaxed space-y-1">
                  <strong className="text-emerald-300">✓ Fully Compliant Trial Candidate (Status: JUSTIFIED):</strong> All demographic attributes verified (G1), organ clearance corridors normal (G2), protocol dosing compliant (RAG), and specialist agents recommend approval with 100% sponsor trial coverage ($0 liability).
                </div>
              )}

              <dl className="grid grid-cols-2 gap-x-6 gap-y-4 md:grid-cols-3 pt-1">
                <Detail label="Subject Name" value={selected.name} />
                <Detail label="Date of Birth" value={selected.dob} />
                <Detail
                  label="Age / Biological Sex"
                  value={
                    selectedEval?.isG1
                      ? "Unrecorded / Missing (21 CFR 312.62 Breach)"
                      : `${selected.age} yrs / ${selected.sex === "F" ? "Female" : selected.sex === "M" ? "Male" : selected.sex}`
                  }
                  emphasis={Boolean(selectedEval?.isG1)}
                />
                <Detail label="Stratification Cohort" value={selected.cohort} />
                <Detail label="Primary Pathology" value={selected.diagnosis} />
                <Detail
                  label="Renal Clearance (CrCl)"
                  value={selected.creatinine || "CrCl 55 mL/min"}
                  emphasis={Boolean(selected.creatinine?.includes("22") || selected.creatinine?.includes("< 30"))}
                />
                {selected.medications && selected.medications.length > 0 && (
                  <div className="col-span-2 md:col-span-3 pt-2 border-t border-[#262626]">
                    <dt className="text-[11px] font-mono uppercase tracking-wider text-slate-400 mb-1.5">
                      Active EMR Medications (Formulary Baseline)
                    </dt>
                    <dd className="flex flex-wrap gap-1.5">
                      {selected.medications.map((m, idx) => (
                        <span
                          key={idx}
                          className="rounded-md border border-[#333] bg-[#1a1a1a] px-2.5 py-1 text-xs font-medium text-slate-200"
                        >
                          💊 {m}
                        </span>
                      ))}
                    </dd>
                  </div>
                )}
              </dl>
            </div>
          )}

          {/* Protocol select */}
          <div className="mt-5">
            <label className="mb-1.5 block text-xs font-medium uppercase tracking-wide text-slate-400">
              Protocol
            </label>
            <div className="relative">
              <select
                value={protocol}
                onChange={(e) => setProtocol(e.target.value)}
                className="h-10 w-full appearance-none rounded-lg border border-[#2e2e2e] bg-[#121212] px-3 pr-9 text-sm text-white focus:border-[#3b82f6] focus:outline-none"
              >
                {PROTOCOLS.map((p) => (
                  <option key={p} value={p} className="bg-[#1e1e1e]">
                    {p}
                  </option>
                ))}
              </select>
              <ChevronDown className="pointer-events-none absolute right-3 top-1/2 size-4 -translate-y-1/2 text-slate-500" />
            </div>
          </div>

          {/* Proposed action */}
          <div className="mt-5">
            <div className="flex items-center justify-between mb-1.5">
              <label className="block text-xs font-medium uppercase tracking-wide text-slate-400">
                Proposed Clinical Action
              </label>
              <span className="text-[11px] text-slate-500">
                Quick Test Scenarios:
              </span>
            </div>

            {/* Dynamic Scenario Preset Chips */}
            {(() => {
              const selectedMeds = selected?.medications || []
              const selectedCohort = selected?.cohort || ""
              const selectedDx = selected?.diagnosis || ""
              const selText = `${selectedCohort} ${selectedDx} ${selectedMeds.join(" ")}`.toLowerCase()

              let standardDose = "Apixaban 5 mg oral twice daily"
              let escalatedDose = "Apixaban 40 mg oral twice daily"
              let standardLabel = "✓ Standard 5 mg BID (Compliant)"
              let escalatedLabel = "⚠️ Escalated 40 mg BID (Dose Violation)"

              if (selText.includes("oncology") || selText.includes("pembrolizumab") || selText.includes("carcinoma") || selText.includes("cancer")) {
                standardDose = "Pembrolizumab 200 mg IV every 3 weeks"
                escalatedDose = "Pembrolizumab 400 mg IV every 3 weeks"
                standardLabel = "✓ Standard 200 mg Q3W (Compliant)"
                escalatedLabel = "⚠️ Escalated 400 mg Q3W (Dose Violation)"
              } else if (selText.includes("renal") || selText.includes("empagliflozin") || selText.includes("nephropathy")) {
                standardDose = "Empagliflozin 10 mg oral once daily"
                escalatedDose = "Empagliflozin 50 mg oral once daily"
                standardLabel = "✓ Standard 10 mg Daily (Compliant)"
                escalatedLabel = "⚠️ Escalated 50 mg Daily (Dose Violation)"
              } else if (selText.includes("nafld") || selText.includes("mash") || selText.includes("pioglitazone") || selText.includes("steatohepatitis")) {
                standardDose = "Pioglitazone 30 mg oral once daily"
                escalatedDose = "Pioglitazone 90 mg oral once daily"
                standardLabel = "✓ Standard 30 mg Daily (Compliant)"
                escalatedLabel = "⚠️ Escalated 90 mg Daily (Dose Violation)"
              }

              return (
                <div className="mb-2 flex flex-wrap gap-2">
                  <button
                    type="button"
                    onClick={() => setAction(standardDose)}
                    className="rounded border border-emerald-800/60 bg-emerald-950/30 px-2.5 py-1 text-xs text-emerald-400 hover:bg-emerald-900/50 transition-colors"
                  >
                    {standardLabel}
                  </button>
                  <button
                    type="button"
                    onClick={() => setAction(escalatedDose)}
                    className="rounded border border-amber-800/60 bg-amber-950/30 px-2.5 py-1 text-xs text-amber-400 hover:bg-amber-900/50 transition-colors"
                  >
                    {escalatedLabel}
                  </button>
                  {selected?.medications && selected.medications.length > 0 && (
                    <button
                      type="button"
                      onClick={() => setAction(`${selected.medications[0]} standard dosing per protocol schedule`)}
                      className="rounded border border-sky-800/60 bg-sky-950/30 px-2.5 py-1 text-xs text-sky-400 hover:bg-sky-900/50 transition-colors"
                    >
                      📋 Cohort Baseline ({selected.medications[0].split(" ")[0]})
                    </button>
                  )}

                  {/* Dedicated 1-click test scenario presets organized by failure & pass modes */}
                  <div className="w-full pt-2 flex flex-col gap-2 border-t border-[#252525] mt-1">
                    {/* G1 Category */}
                    <div className="flex flex-wrap items-center gap-1.5">
                      <span className="text-[10px] font-bold text-rose-400 uppercase tracking-wider min-w-28">G1 Ingress Fail:</span>
                      <button
                        type="button"
                        onClick={() => { const pat = patients.find(p => p.patient_id === "P034"); if (pat) choose(pat); }}
                        className={`rounded border px-2 py-0.5 text-[11px] font-mono transition-colors ${
                          disqualifiedIds.includes("P034")
                            ? "border-rose-600 bg-rose-950/80 text-rose-200"
                            : "border-rose-800/60 bg-rose-950/40 text-rose-300 hover:bg-rose-900/60"
                        }`}
                      >
                        {disqualifiedIds.includes("P034") ? "P034: Locked Out" : "P034 (Age+Sex)"}
                      </button>
                      <button
                        type="button"
                        onClick={() => { const pat = patients.find(p => p.patient_id === "P038"); if (pat) choose(pat); }}
                        className="rounded border border-rose-800/60 bg-rose-950/40 px-2 py-0.5 text-[11px] font-mono text-rose-300 hover:bg-rose-900/60 transition-colors"
                      >
                        P038 (Missing Sex)
                      </button>
                      <button
                        type="button"
                        onClick={() => { const pat = patients.find(p => p.patient_id === "P039"); if (pat) choose(pat); }}
                        className="rounded border border-rose-800/60 bg-rose-950/40 px-2 py-0.5 text-[11px] font-mono text-rose-300 hover:bg-rose-900/60 transition-colors"
                      >
                        P039 (Missing Age)
                      </button>
                      <button
                        type="button"
                        onClick={() => { const pat = patients.find(p => p.patient_id === "P040"); if (pat) choose(pat); }}
                        className="rounded border border-rose-800/60 bg-rose-950/40 px-2 py-0.5 text-[11px] font-mono text-rose-300 hover:bg-rose-900/60 transition-colors"
                      >
                        P040 (21 CFR 312.62)
                      </button>
                    </div>

                    {/* G2 Category */}
                    <div className="flex flex-wrap items-center gap-1.5">
                      <span className="text-[10px] font-bold text-rose-400 uppercase tracking-wider min-w-28">G2 Boundary:</span>
                      <button
                        type="button"
                        onClick={() => { const pat = patients.find(p => p.patient_id === "P035"); if (pat) choose(pat); }}
                        className="rounded border border-rose-800/60 bg-rose-950/40 px-2 py-0.5 text-[11px] font-mono text-rose-300 hover:bg-rose-900/60 transition-colors"
                      >
                        P035 (ALT 620 U/L)
                      </button>
                      <button
                        type="button"
                        onClick={() => { const pat = patients.find(p => p.patient_id === "P041"); if (pat) choose(pat); }}
                        className="rounded border border-rose-800/60 bg-rose-950/40 px-2 py-0.5 text-[11px] font-mono text-rose-300 hover:bg-rose-900/60 transition-colors"
                      >
                        P041 (eGFR 11 ESRD)
                      </button>
                      <button
                        type="button"
                        onClick={() => { const pat = patients.find(p => p.patient_id === "P042"); if (pat) choose(pat); }}
                        className="rounded border border-rose-800/60 bg-rose-950/40 px-2 py-0.5 text-[11px] font-mono text-rose-300 hover:bg-rose-900/60 transition-colors"
                      >
                        P042 (Bilirubin 6.8)
                      </button>
                      <button
                        type="button"
                        onClick={() => { const pat = patients.find(p => p.patient_id === "P043"); if (pat) choose(pat); }}
                        className="rounded border border-rose-800/60 bg-rose-950/40 px-2 py-0.5 text-[11px] font-mono text-rose-300 hover:bg-rose-900/60 transition-colors"
                      >
                        P043 (ANC 320 Agranulocytosis)
                      </button>
                    </div>

                    {/* RAG Rules Category */}
                    <div className="flex flex-wrap items-center gap-1.5">
                      <span className="text-[10px] font-bold text-amber-400 uppercase tracking-wider min-w-28">RAG Rules:</span>
                      <button
                        type="button"
                        onClick={() => { const pat = patients.find(p => p.patient_id === "P036"); if (pat) choose(pat); }}
                        className="rounded border border-amber-800/60 bg-amber-950/40 px-2 py-0.5 text-[11px] font-mono text-amber-300 hover:bg-amber-900/60 transition-colors"
                      >
                        P036 (Overdose 40mg &rarr; Fix to Accept)
                      </button>
                      <button
                        type="button"
                        onClick={() => { const pat = patients.find(p => p.patient_id === "P044"); if (pat) choose(pat); }}
                        className="rounded border border-amber-800/60 bg-amber-950/40 px-2 py-0.5 text-[11px] font-mono text-amber-300 hover:bg-amber-900/60 transition-colors"
                      >
                        P044 (Overdose 60mg BID)
                      </button>
                      <button
                        type="button"
                        onClick={() => { const pat = patients.find(p => p.patient_id === "P045"); if (pat) choose(pat); }}
                        className="rounded border border-amber-800/60 bg-amber-950/40 px-2 py-0.5 text-[11px] font-mono text-amber-300 hover:bg-amber-900/60 transition-colors"
                      >
                        P045 (Washout 8d &lt; 30d)
                      </button>
                      <button
                        type="button"
                        onClick={() => { const pat = patients.find(p => p.patient_id === "P046"); if (pat) choose(pat); }}
                        className="rounded border border-amber-800/60 bg-amber-950/40 px-2 py-0.5 text-[11px] font-mono text-amber-300 hover:bg-amber-900/60 transition-colors"
                      >
                        P046 (CrCl 22 &lt; 30 Floor)
                      </button>
                      <button
                        type="button"
                        onClick={() => { const pat = patients.find(p => p.patient_id === "P047"); if (pat) choose(pat); }}
                        className="rounded border border-amber-800/60 bg-amber-950/40 px-2 py-0.5 text-[11px] font-mono text-amber-300 hover:bg-amber-900/60 transition-colors"
                      >
                        P047 (Autoimmune Exclusion)
                      </button>
                    </div>

                    {/* A2A Discrepancies Category */}
                    <div className="flex flex-wrap items-center gap-1.5">
                      <span className="text-[10px] font-bold text-purple-400 uppercase tracking-wider min-w-28">4 A2A Rejection:</span>
                      <button
                        type="button"
                        onClick={() => { const pat = patients.find(p => p.patient_id === "P037"); if (pat) choose(pat); }}
                        className="rounded border border-purple-800/60 bg-purple-950/40 px-2 py-0.5 text-[11px] font-mono text-purple-300 hover:bg-purple-900/60 transition-colors"
                      >
                        P037 (4-Agent Dissent)
                      </button>
                      <button
                        type="button"
                        onClick={() => { const pat = patients.find(p => p.patient_id === "P048"); if (pat) choose(pat); }}
                        className="rounded border border-purple-800/60 bg-purple-950/40 px-2 py-0.5 text-[11px] font-mono text-purple-300 hover:bg-purple-900/60 transition-colors"
                      >
                        P048 (DDI Safety Rejection)
                      </button>
                      <button
                        type="button"
                        onClick={() => { const pat = patients.find(p => p.patient_id === "P049"); if (pat) choose(pat); }}
                        className="rounded border border-purple-800/60 bg-purple-950/40 px-2 py-0.5 text-[11px] font-mono text-purple-300 hover:bg-purple-900/60 transition-colors"
                      >
                        P049 (Financial $52.8k Denial)
                      </button>
                      <button
                        type="button"
                        onClick={() => { const pat = patients.find(p => p.patient_id === "P050"); if (pat) choose(pat); }}
                        className="rounded border border-purple-800/60 bg-purple-950/40 px-2 py-0.5 text-[11px] font-mono text-purple-300 hover:bg-purple-900/60 transition-colors"
                      >
                        P050 (Triple Antiplatelet Dissent)
                      </button>
                    </div>

                    {/* Clean Passes Category */}
                    <div className="flex flex-wrap items-center gap-1.5">
                      <span className="text-[10px] font-bold text-emerald-400 uppercase tracking-wider min-w-28">Clean Passes:</span>
                      <button
                        type="button"
                        onClick={() => { const pat = patients.find(p => p.patient_id === "P001"); if (pat) choose(pat); }}
                        className="rounded border border-emerald-800/60 bg-emerald-950/40 px-2 py-0.5 text-[11px] font-mono text-emerald-300 hover:bg-emerald-900/60 transition-colors"
                      >
                        ✓ P001 (Renal SGLT2i)
                      </button>
                      <button
                        type="button"
                        onClick={() => { const pat = patients.find(p => p.patient_id === "P006"); if (pat) choose(pat); }}
                        className="rounded border border-emerald-800/60 bg-emerald-950/40 px-2 py-0.5 text-[11px] font-mono text-emerald-300 hover:bg-emerald-900/60 transition-colors"
                      >
                        ✓ P006 (AFib Standard)
                      </button>
                      <button
                        type="button"
                        onClick={() => { const pat = patients.find(p => p.patient_id === "P051"); if (pat) choose(pat); }}
                        className="rounded border border-emerald-800/60 bg-emerald-950/40 px-2 py-0.5 text-[11px] font-mono text-emerald-300 hover:bg-emerald-900/60 transition-colors"
                      >
                        ✓ P051 (Atrial Fib Pass)
                      </button>
                      <button
                        type="button"
                        onClick={() => { const pat = patients.find(p => p.patient_id === "P052"); if (pat) choose(pat); }}
                        className="rounded border border-emerald-800/60 bg-emerald-950/40 px-2 py-0.5 text-[11px] font-mono text-emerald-300 hover:bg-emerald-900/60 transition-colors"
                      >
                        ✓ P052 (Oncology Pass)
                      </button>
                      <button
                        type="button"
                        onClick={() => { const pat = patients.find(p => p.patient_id === "P053"); if (pat) choose(pat); }}
                        className="rounded border border-emerald-800/60 bg-emerald-950/40 px-2 py-0.5 text-[11px] font-mono text-emerald-300 hover:bg-emerald-900/60 transition-colors"
                      >
                        ✓ P053 (MASH Pass)
                      </button>
                      <button
                        type="button"
                        onClick={() => { const pat = patients.find(p => p.patient_id === "P054"); if (pat) choose(pat); }}
                        className="rounded border border-emerald-800/60 bg-emerald-950/40 px-2 py-0.5 text-[11px] font-mono text-emerald-300 hover:bg-emerald-900/60 transition-colors"
                      >
                        ✓ P054 (Renal SGLT2i Pass)
                      </button>
                    </div>
                  </div>
                </div>
              )
            })()}

            {/* Remediation Banner when Protocol Dose Violation is detected */}
            {dosingGuidelines?.isViolation && (
              <div className="mb-3 mt-3 rounded-xl border border-amber-500/40 bg-amber-950/30 p-3.5 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs text-amber-200 animate-in fade-in duration-200">
                <div className="flex items-start gap-2.5">
                  <AlertTriangle className="size-4 shrink-0 text-amber-400 mt-0.5" />
                  <div>
                    <span className="font-bold text-amber-300">Protocol Dosage Ceiling Exceeded:</span>{" "}
                    Proposed dose violates trial safety boundaries. Recommended compliant target:{" "}
                    <strong className="text-emerald-300 font-mono">{dosingGuidelines.standardDose}</strong>
                  </div>
                </div>
                <Button
                  type="button"
                  size="sm"
                  disabled={isExtracting}
                  onClick={() => handleApplyRemediation(dosingGuidelines.standardDose)}
                  className="shrink-0 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs h-8 px-3 rounded-lg shadow-sm transition-all"
                >
                  {isExtracting ? (
                    <Loader2 className="size-3.5 animate-spin" />
                  ) : (
                    <>
                      <Sparkles className="size-3.5 mr-1 text-slate-950" />
                      ⚡ 1-Click Fix to Standard
                    </>
                  )}
                </Button>
              </div>
            )}

            {/* Proposed Action / Prescription Input */}
            <div className="space-y-2 mt-3">
              <div className="flex items-center justify-between">
                <label className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                  <span>Prescription Order / Doctor&apos;s Narrative Note</span>
                  {fhirSynced && (
                    <span className="rounded-full bg-emerald-500/10 px-2 py-0.5 text-[10px] font-mono text-emerald-400 border border-emerald-500/30 flex items-center gap-1">
                      <Check className="size-3" /> FHIR Synced
                    </span>
                  )}
                </label>
                <button
                  type="button"
                  onClick={() => {
                    setModifyOpen((v) => {
                      const next = !v
                      if (next) {
                        setTimeout(() => modifyDrawerRef.current?.scrollIntoView({ behavior: 'smooth', block: 'nearest' }), 80)
                      }
                      return next
                    })
                  }}
                  className="flex items-center gap-1 text-xs text-sky-400 hover:text-sky-300 font-medium transition-all active:scale-95"
                >
                  <Sliders className="size-3.5" />
                  <span>{modifyOpen ? "Hide Override Panel" : "Modify Dosage / Override"}</span>
                  <ChevronDown className={`size-3 transition-transform ${modifyOpen ? "rotate-180" : ""}`} />
                </button>
              </div>

              <textarea
                value={action}
                onChange={(e) => {
                  setAction(e.target.value)
                  setDoctorNote(e.target.value)
                  setFhirSynced(false)
                  if (extractionResult) setExtractionResult(null)
                }}
                rows={3}
                placeholder="E.g., Apixaban 5 mg oral twice daily, or doctor note: 'Titrate apixiban to 5mg bid per protocol Arm A'..."
                className="w-full resize-none rounded-lg border border-slate-700/50 bg-[#0B131F] px-3 py-2.5 text-sm text-white placeholder:text-slate-500 focus:border-sky-500 focus:outline-none font-mono"
              />

              <div className="flex flex-wrap items-center justify-between gap-2 pt-1">
                <Button
                  type="button"
                  size="sm"
                  disabled={isExtracting || !action.trim()}
                  onClick={() => handleExtract(action)}
                  className="h-8 px-3 text-xs font-semibold bg-sky-600 hover:bg-sky-500 text-white rounded-lg transition-all active:scale-95 flex items-center gap-1.5"
                >
                  {isExtracting ? (
                    <>
                      <Loader2 className="size-3.5 animate-spin" />
                      Evaluating with Clinical LLM...
                    </>
                  ) : (
                    <>
                      <Sparkles className="size-3.5" />
                      Evaluate Note via Clinical LLM
                    </>
                  )}
                </Button>

                <div className="flex items-center gap-2">
                  {dosingGuidelines && (
                    <button
                      type="button"
                      onClick={() => {
                        setAction(dosingGuidelines.standardDose)
                        setDoctorNote(dosingGuidelines.standardDose)
                        setFhirSynced(false)
                        if (extractionResult) setExtractionResult(null)
                      }}
                      className="text-[11px] text-slate-400 hover:text-emerald-400 flex items-center gap-1 transition-all active:scale-95"
                    >
                      <RotateCcw className="size-3" />
                      Reset to Standard ({dosingGuidelines.drug})
                    </button>
                  )}
                </div>
              </div>
            </div>

            {/* Modify / Override Drawer */}
            {modifyOpen && (
              <div ref={modifyDrawerRef} className="mt-3 rounded-xl border border-slate-700/50 bg-[#111C2D] p-4 space-y-3 animate-in fade-in slide-in-from-top-2 duration-200">
                <div className="flex items-center justify-between border-b border-slate-700/40 pb-2.5">
                  <div>
                    <p className="text-xs font-bold text-white uppercase tracking-wide">
                      Physician Protocol Override & Clinical Rationale
                    </p>
                    <p className="text-[11px] text-amber-400 mt-0.5">
                      Enter free-text clinical narrative, doctor notes, or dosage modifications
                    </p>
                  </div>
                  <span className="rounded-full bg-amber-500/10 px-2 py-0.5 text-[10px] font-bold text-amber-400 border border-amber-500/20">
                    HITL Override Gate
                  </span>
                </div>

                <div>
                  <label className="block text-[11px] font-semibold uppercase tracking-wider text-slate-400 mb-1">
                    Doctor&apos;s Prescription Note / Narrative Rationale
                  </label>
                  <textarea
                    value={doctorNote}
                    onChange={(e) => setDoctorNote(e.target.value)}
                    rows={3}
                    placeholder="E.g., Patient exhibits stable renal function (CrCl 68 mL/min). Titrate apixiban to 5 mg oral twice daily per protocol Arm A..."
                    className="w-full resize-none rounded-lg border border-slate-700/50 bg-[#070D17] p-2.5 text-xs text-white placeholder:text-slate-500 focus:border-sky-500 focus:outline-none leading-relaxed font-mono"
                  />
                </div>

                <div className="flex gap-2">
                  <Button
                    type="button"
                    size="sm"
                    disabled={isExtracting || !doctorNote.trim()}
                    onClick={() => handleExtract(doctorNote)}
                    className="h-8 px-3 text-xs bg-sky-500 hover:bg-sky-400 text-white font-semibold rounded-lg transition-all"
                  >
                    {isExtracting ? (
                      <>
                        <Loader2 className="size-3.5 mr-1.5 animate-spin" />
                        Extracting via Clinical LLM...
                      </>
                    ) : (
                      <>
                        <Sparkles className="size-3.5 mr-1.5" />
                        Evaluate Rationale & Extract FHIR Updates
                      </>
                    )}
                  </Button>
                </div>
              </div>
            )}

            {/* AI Extraction State 1: Clinical Warning (Inappropriate or Ambiguous) */}
            {extractionResult && (!extractionResult.is_valid || extractionResult.is_appropriate === false) && (
              <div className="mt-3 rounded-xl border border-rose-500/40 bg-rose-950/40 p-4 text-rose-300 space-y-2 animate-in fade-in duration-200">
                <div className="flex items-center gap-2 font-bold text-rose-200 text-xs uppercase tracking-wider">
                  <AlertTriangle className="size-4 shrink-0 text-rose-400" />
                  ⚠️ Clinical Warning: Inappropriate or Ambiguous Doctor Note
                </div>
                <p className="text-xs text-rose-300 leading-relaxed">
                  {extractionResult.warning || extractionResult.reasoning || "The entered note does not specify an actionable medication name or numerical dosage."}
                </p>
                <div className="rounded border border-rose-800/40 bg-[#0c0507] p-2.5 text-[11px] font-mono text-slate-300">
                  <span className="text-rose-400 font-bold">Action Required:</span> Provide a recognizable medication and numerical target dosage.
                  <br />
                  <span className="text-slate-400">Example:</span> &ldquo;Titrate Apixaban to 5 mg oral twice daily per protocol Arm A&rdquo;
                </div>
              </div>
            )}

            {/* AI Extraction State 2: Extracted Data Confirmed & Appropriate */}
            {extractionResult?.is_valid && extractionResult?.is_appropriate !== false && (
              <div className="mt-3 rounded-xl border border-emerald-500/30 bg-emerald-500/10 p-4 space-y-3 animate-in fade-in duration-200">
                <div className="flex flex-wrap items-center justify-between gap-2 border-b border-emerald-500/20 pb-2.5">
                  <div className="flex items-center gap-2">
                    <CheckCircle2 className="size-4 text-emerald-400" />
                    <p className="text-sm font-bold text-emerald-300">
                      Prescription & Note Validated by Clinical LLM
                    </p>
                  </div>
                  {extractionResult.spelling_corrected && (
                    <span className="rounded-full bg-sky-500/20 border border-sky-500/40 px-2.5 py-0.5 text-[10px] font-mono text-sky-300">
                      Spelling Corrected: &ldquo;{extractionResult.original_spelling}&rdquo; &rarr; {extractionResult.standardized_drug}
                    </span>
                  )}
                </div>

                <p className="text-xs text-slate-300 leading-relaxed">
                  {extractionResult.reasoning}
                </p>

                <div className="rounded-lg bg-[#111C2D] border border-slate-700/50 p-3 text-xs space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-slate-200 font-semibold text-sm">
                      {extractionResult.standardized_drug || extractionResult.modifications?.[0]?.dosage_name || "Prescription"}
                    </span>
                    <span className="font-mono font-bold text-emerald-400 text-sm">
                      {extractionResult.dosage || extractionResult.modifications?.[0]?.proposed_dosage} {extractionResult.dosage_unit || extractionResult.modifications?.[0]?.dosage_unit || "mg"}
                    </span>
                  </div>
                  <div className="grid grid-cols-2 gap-2 text-[11px] font-mono text-slate-400 border-t border-slate-700/30 pt-2">
                    <div>
                      <span className="text-slate-500 block text-[10px] uppercase">Frequency / Route</span>
                      <span className="text-slate-200 font-medium">
                        {extractionResult.frequency || extractionResult.modifications?.[0]?.frequency || "twice daily"} ({extractionResult.route || extractionResult.modifications?.[0]?.route || "oral"})
                      </span>
                    </div>
                    <div>
                      <span className="text-slate-500 block text-[10px] uppercase">Timing Schedule</span>
                      <span className="text-sky-300 font-medium">
                        {extractionResult.timing_schedule || extractionResult.modifications?.[0]?.timing_schedule || "08:00, 20:00"}
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center justify-between text-[10px] font-mono bg-[#070D17] rounded px-2.5 py-1 border border-slate-800">
                    <span className="text-slate-500">Target FHIR Field:</span>
                    <span className="text-amber-300 font-semibold">
                      {extractionResult.target_fhir_field || extractionResult.modifications?.[0]?.target_field || "MedicationRequest.dosageInstruction[0]"}
                    </span>
                  </div>
                </div>

                <div className="flex flex-wrap items-center justify-between gap-2 pt-1">
                  <div className="text-[11px] font-mono text-emerald-300">
                    <span className="text-slate-400">Target Clinical Action:</span> {extractionResult.standardized_action || action}
                  </div>
                  <Button
                    type="button"
                    size="sm"
                    disabled={fhirSyncing}
                    onClick={() => executeFhirUpdate()}
                    className={`h-8 px-3 text-xs font-semibold rounded-lg transition-all ${
                      fhirSynced
                        ? "bg-emerald-950 text-emerald-300 border border-emerald-700/60"
                        : "bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold"
                    }`}
                  >
                    {fhirSyncing ? (
                      <Loader2 className="size-3.5 mr-1.5 animate-spin" />
                    ) : fhirSynced ? (
                      <Check className="size-3.5 mr-1.5 text-emerald-400" />
                    ) : (
                      <FileCheck2 className="size-3.5 mr-1.5" />
                    )}
                    {fhirSynced ? "FHIR Database Synchronized" : "Confirm & Update FHIR Database"}
                  </Button>
                </div>
              </div>
            )}

            {isDisqualified && (
              <div className="mt-4 rounded-xl border border-rose-500/60 bg-gradient-to-r from-rose-950/60 via-[#1a0c0e] to-[#121212] p-4 space-y-2 text-xs text-rose-200 shadow-lg shadow-rose-950/40">
                <div className="flex items-center gap-2 font-bold uppercase tracking-wide text-rose-300">
                  <Lock className="size-4 text-rose-400" />
                  ⛔ Patient ID Permanently Excluded (3/3 Retries Exhausted)
                </div>
                <p className="text-slate-300 leading-relaxed">
                  Patient <strong className="font-mono text-white underline">{selected?.patient_id}</strong> is disqualified from clinical trial intake under <strong>FDA 21 CFR 312.62 & ICH E6(R2)</strong>. The 3-iteration demographic resupply budget has been exhausted without verified demographic resolution. This enrollment portal is barred from accepting or submitting this patient ID.
                </p>
                <div className="rounded border border-rose-800/40 bg-[#0d0507] p-2 text-[11px] font-mono text-rose-400">
                  Terminal Gate Status: EXCLUDED_MAX_ITERS · 21 CFR 312.62 Ingress Lockout
                </div>
              </div>
            )}
          </div>

          {(() => {
            const isWarningBlocked = Boolean(extractionResult && (!extractionResult.is_valid || extractionResult.is_appropriate === false))
            return (
              <Button
                disabled={!selected || isDisqualified || isWarningBlocked}
                onClick={handleSubmitClick}
                className={`mt-6 h-11 w-full font-semibold transition-all ${
                  isDisqualified
                    ? "bg-rose-950/80 border border-rose-700/60 text-rose-300 cursor-not-allowed shadow-inner"
                    : isWarningBlocked
                    ? "bg-amber-950/80 border border-amber-700/60 text-amber-300 cursor-not-allowed"
                    : "bg-[#3b82f6] text-white hover:bg-[#3b82f6]/90 disabled:opacity-40"
                }`}
              >
                {isDisqualified ? (
                  <>
                    <Lock className="size-4 mr-2 text-rose-400" />
                    Cannot Submit: Patient ID Permanently Excluded (3/3)
                  </>
                ) : isWarningBlocked ? (
                  <>
                    <AlertTriangle className="size-4 mr-2 text-amber-400" />
                    Action Blocked: Resolve Clinical Warning Above
                  </>
                ) : (
                  <>
                    <Send className="size-4 mr-2" />
                    Submit for AI Review
                  </>
                )}
              </Button>
            )
          })()}
          {!selected && (
            <p className="mt-2 text-center text-xs text-slate-500">
              Select a patient to enable submission.
            </p>
          )}
        </div>
      </main>
    </div>
  )
}

function Detail({
  label,
  value,
  emphasis,
}: {
  label: string
  value: string
  emphasis?: boolean
}) {
  return (
    <div>
      <dt className="text-[11px] uppercase tracking-wide text-slate-500">
        {label}
      </dt>
      <dd
        className={`mt-0.5 text-sm ${
          emphasis ? "font-semibold text-[#f59e0b]" : "text-white"
        }`}
      >
        {value}
      </dd>
    </div>
  )
}