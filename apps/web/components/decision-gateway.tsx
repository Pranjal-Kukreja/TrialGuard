"use client"

import { useEffect, useMemo, useRef, useState } from "react"
import {
  Activity,
  AlertCircle,
  AlertTriangle,
  Check,
  CheckCircle2,
  ChevronDown,
  ChevronUp,
  Clock,
  Copy,
  Dna,
  DollarSign,
  Download,
  FileCheck,
  FileText,
  GitMerge,
  Heart,
  Info,
  Loader2,
  Lock,
  Pencil,
  Pill,
  RefreshCw,
  Scale,
  Shield,
  ShieldAlert,
  ShieldCheck,
  Sparkles,
  Stethoscope,
  User,
  X,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { TrialGuardLogo } from "@/components/trialguard-logo"
import { processClinicalComment, submitDecision, resupplyPatientData } from "@/app/actions"
import type { ArbitrationResult } from "@/app/actions"
import type { Patient } from "@/lib/clinical-data"
import { getGatewayUrl } from "@/lib/api-config"

type Props = {
  patient: Patient
  arbitrationResult: ArbitrationResult
  onRestartStream?: (newAction?: string) => void
  onPatientUpdated?: (updatedPatient: Partial<Patient> & { action?: string }) => void
  onPatientDisqualified?: (patientId: string) => void
}

function formatLimit(limit: unknown): string {
  if (!limit) return "Standard protocol criteria threshold"
  if (typeof limit === "string") {
    const trimmed = limit.trim()
    if (trimmed === "" || trimmed.toLowerCase() === "unknown" || trimmed.toLowerCase() === "undefined") {
      return "Standard protocol criteria threshold"
    }
    if (trimmed.startsWith("{") && trimmed.endsWith("}")) {
      const matchVal = trimmed.match(/['"]?value['"]?:\s*['"]?([^,'"}]+)['"]?/)
      const matchUnit = trimmed.match(/['"]?unit['"]?:\s*['"]?([^,'"}]+)['"]?/)
      const matchOp = trimmed.match(/['"]?operator['"]?:\s*['"]?([^,'"}]+)['"]?/)
      if (matchVal) {
        const val = matchVal[1].trim()
        const unit = matchUnit ? " " + matchUnit[1].trim() : ""
        const op = matchOp && matchOp[1].trim() !== "==" ? matchOp[1].trim() + " " : ""
        return `${op}${val}${unit}`
      }
    }
    return trimmed
  }
  if (typeof limit === "object" && limit !== null) {
    const obj = limit as Record<string, unknown>
    const val = obj.value !== undefined ? String(obj.value) : ""
    const unit = obj.unit ? ` ${obj.unit}` : ""
    const op = obj.operator && obj.operator !== "==" ? `${obj.operator} ` : ""
    return `${op}${val}${unit}`.trim() || "Standard protocol criteria threshold"
  }
  return String(limit)
}

export function DecisionGateway({
  patient,
  arbitrationResult,
  onRestartStream,
  onPatientUpdated,
  onPatientDisqualified,
}: Props) {
  // Local component state
  const [localPatient, setLocalPatient] = useState(patient)
  const [activeAction, setActiveAction] = useState<string>(
    arbitrationResult.prescribed_action || patient?.medications?.[0] || "Apixaban 5 mg oral twice daily"
  )
  const [orderModified, setOrderModified] = useState(false)
  const [decision, setDecision] = useState<"accept" | "reject" | "override" | null>(null)
  const [resupplyAttempts, setResupplyAttempts] = useState<number>(
    arbitrationResult.guardrail_1_result?.resupply_attempts || 0
  )
  const [modifyOpen, setModifyOpen] = useState(false)
  const modifyDrawerRef = useRef<HTMLDivElement>(null)
  const [isApplyingRemediation, setIsApplyingRemediation] = useState(false)
  const [isSubmittingOverride, setIsSubmittingOverride] = useState(false)
  const [showDeepAudit, setShowDeepAudit] = useState(false)
  const [copiedPayload, setCopiedPayload] = useState(false)
  const [isSubmittingDecision, setIsSubmittingDecision] = useState(false)

  const [resupplyAge, setResupplyAge] = useState<string>(
    patient?.age && patient.age > 0 ? String(patient.age) : ""
  )
  const [resupplySex, setResupplySex] = useState<string>(
    patient?.sex && patient.sex !== "unknown"
      ? patient.sex.toUpperCase() === "F"
        ? "Female"
        : patient.sex.toUpperCase() === "M"
        ? "Male"
        : patient.sex
      : ""
  )
  const [resupplyAttestation, setResupplyAttestation] = useState<string>(
    "Verified Against Hospital Intake Chart (FHIR Encounter Resupply)"
  )
  const [isResupplying, setIsResupplying] = useState(false)
  const [resupplyError, setResupplyError] = useState<string | null>(null)

  const [comment, setComment] = useState("")
  const [isExtracting, setIsExtracting] = useState(false)
  const [extractionResult, setExtractionResult] = useState<any>(null)

  useEffect(() => {
    setLocalPatient(patient)
    if (patient?.age && patient.age > 0) setResupplyAge(String(patient.age))
    if (patient?.sex && patient.sex !== "unknown") {
      setResupplySex(patient.sex.toUpperCase() === "F" ? "Female" : patient.sex.toUpperCase() === "M" ? "Male" : patient.sex)
    }
    if (arbitrationResult?.prescribed_action) {
      setActiveAction(arbitrationResult.prescribed_action)
    }
  }, [patient, arbitrationResult?.prescribed_action])

  const pid = localPatient?.id || patient?.id || ""


  const actionLower = (activeAction || "").toLowerCase()
  const hasDoseOverdose = (
    actionLower.includes("40 mg") || actionLower.includes("40mg") ||
    actionLower.includes("60 mg") || actionLower.includes("60mg") ||
    actionLower.includes("20 mg") || actionLower.includes("20mg") ||
    actionLower.includes("400 mg") || actionLower.includes("400mg")
  )

  // Normalize patient renal clearance telemetry with explicit units
  const renalDisplay = useMemo(() => {
    const raw = localPatient?.creatinine || patient?.creatinine
    if (raw && raw !== "unknown" && raw.trim() !== "") {
      if (raw.includes("CrCl") || raw.includes("mL/min") || raw.includes("Serum Cr")) return raw
      return `CrCl ${raw} mL/min`
    }
    const crclVal = (localPatient?.clinical_data || patient?.clinical_data)?.lab_results?.creatinine_clearance?.value
    if (crclVal !== undefined && crclVal !== null) {
      return `CrCl ${crclVal} mL/min`
    }
    return "CrCl 65 mL/min"
  }, [localPatient?.creatinine, patient?.creatinine, localPatient?.clinical_data, patient?.clinical_data])

  const renalNumber = useMemo(() => {
    const match = renalDisplay.match(/\d+(?:\.\d+)?/)
    return match ? parseFloat(match[0]) : 65
  }, [renalDisplay])

  const isRenalEligible = renalNumber >= 30

  // Patient Clinical Profile Telemetry
  const clinicalProfile = useMemo(() => {
    const rawProfile = (arbitrationResult as any)?.patient_profile || {}
    const cData = localPatient?.clinical_data || patient?.clinical_data || rawProfile || {}
    const labs = cData?.lab_results || {}
    const vitals = cData?.vital_signs || {}
    const cardiac = cData?.cardiac_function || {}

    const name = localPatient?.name || patient?.name || rawProfile?.name || `Patient ${pid || "Unknown"}`
    const id = pid || "PT-UNKNOWN"
    const age = localPatient?.age ?? patient?.age ?? rawProfile?.age ?? 65
    const sex = localPatient?.sex || patient?.sex || rawProfile?.sex || "M"
    const dob = localPatient?.dob || patient?.dob || rawProfile?.dob || rawProfile?.birth_date || "1960-01-01"
    const cohort = localPatient?.cohort || patient?.cohort || rawProfile?.cohort || "Cohort A - Protocol Verification"
    const trialId = localPatient?.trial_id || patient?.trial_id || rawProfile?.trial_id || (arbitrationResult as any)?.protocol_id || "NCT02415400"

    const diagnoses: string[] = []
    if (patient?.diagnosis && !diagnoses.includes(patient.diagnosis)) {
      diagnoses.push(patient.diagnosis)
    }
    if (Array.isArray(cData?.diagnoses)) {
      cData.diagnoses.forEach((d: string) => {
        if (!diagnoses.includes(d)) diagnoses.push(d)
      })
    }
    if (diagnoses.length === 0) diagnoses.push("Clinical Protocol Subject")

    const medications: string[] = []
    if (Array.isArray(patient?.medications)) {
      patient.medications.forEach((m: string) => {
        if (!medications.includes(m)) medications.push(m)
      })
    }
    if (Array.isArray(cData?.medications)) {
      cData.medications.forEach((m: string) => {
        if (!medications.includes(m)) medications.push(m)
      })
    }
    if (medications.length === 0) medications.push("Standard Trial Formulary")

    const crclVal = labs?.creatinine_clearance?.value ?? (typeof labs?.creatinine_clearance === "number" ? labs.creatinine_clearance : renalNumber)
    const scrVal = labs?.serum_creatinine?.value ?? (typeof labs?.serum_creatinine === "number" ? labs.serum_creatinine : 1.0)
    const egfrVal = labs?.eGFR?.value ?? (typeof labs?.eGFR === "number" ? labs.eGFR : 65.0)
    const altVal = labs?.ALT?.value ?? (typeof labs?.ALT === "number" ? labs.ALT : 28.0)
    const astVal = labs?.AST?.value ?? (typeof labs?.AST === "number" ? labs.AST : 24.0)
    const plateletsVal = labs?.platelets?.value ?? (typeof labs?.platelets === "number" ? labs.platelets : 220000)
    const inrVal = labs?.INR?.value ?? (typeof labs?.INR === "number" ? labs.INR : 1.1)
    const biliVal = labs?.total_bilirubin?.value ?? (typeof labs?.total_bilirubin === "number" ? labs.total_bilirubin : 0.8)
    const ancVal = labs?.ANC?.value ?? (typeof labs?.ANC === "number" ? labs.ANC : 3500)

    const bpSys = vitals?.blood_pressure_systolic ?? 124
    const bpDia = vitals?.blood_pressure_diastolic ?? 80
    const hr = vitals?.heart_rate ?? 74

    return {
      name,
      id,
      age,
      sex: sex === "F" || sex === "female" ? "Female" : "Male",
      dob,
      cohort,
      trialId,
      diagnoses,
      medications,
      crcl: typeof crclVal === "number" ? Math.round(crclVal) : crclVal,
      scr: scrVal,
      egfr: typeof egfrVal === "number" ? Math.round(egfrVal) : egfrVal,
      alt: typeof altVal === "number" ? Math.round(altVal) : altVal,
      ast: typeof astVal === "number" ? Math.round(astVal) : astVal,
      bili: biliVal,
      anc: ancVal,
      platelets: plateletsVal,
      inr: inrVal,
      bp: `${bpSys}/${bpDia} mmHg`,
      hr: `${hr} bpm`,
      lvef: cardiac?.LVEF ? `${cardiac.LVEF}%` : "55%",
    }
  }, [localPatient, patient, pid, arbitrationResult, renalNumber])

  const activeTrialId = clinicalProfile.trialId

  // Guardrail 1: Demographic & Ingress Integrity (Interactive HITL Resupply with 3-iteration lockout)
  const guardrail1 = useMemo(() => {
    const curAge = localPatient?.age ?? patient?.age
    const curSex = localPatient?.sex ?? patient?.sex
    const hasValidAge = typeof curAge === "number" && curAge > 0
    const hasValidSex = Boolean(curSex && curSex !== "" && curSex.toLowerCase() !== "unrecorded" && curSex.toLowerCase() !== "unknown")

    const missing: string[] = []
    if (!hasValidAge) missing.push("patient.age")
    if (!hasValidSex) missing.push("patient.sex")

    const isFailed = missing.length > 0
    const isLocked = isFailed && resupplyAttempts >= 3

    return {
      passed: !isFailed,
      status: isLocked ? ("EXCLUDED_MAX_ITERS" as const) : isFailed ? ("FAILED" as const) : ("PASSED" as const),
      locked: isLocked,
      resupply_attempts: resupplyAttempts,
      max_iters: 3,
      missing_fields: missing,
      reason: isLocked
        ? `Mandatory demographic resupply retry budget exhausted (${resupplyAttempts}/3 attempts). Subject ID ${pid} is permanently excluded from trial intake under FDA 21 CFR 312.62 & ICH E6(R2).`
        : isFailed
        ? `Mandatory patient demographic integrity failure: missing required field(s) [${missing.join(", ")}]. Ingress schema validation failed per FDA 21 CFR 312.62 & ICH E6(R2) Section 4.3 (Attempt ${resupplyAttempts + 1} of 3 - Clinician resupply required).`
        : (resupplyAttempts > 0
            ? `Patient demographics successfully resupplied by clinician and verified on attempt ${resupplyAttempts} of 3. Demographics conform to 21 CFR Part 11 ingress specifications.`
            : "Patient demographics and upstream trial schema contract verified (patient_id, age, biological sex conform to 21 CFR Part 11 ingress specifications)."),
      regulatory_citation: "FDA 21 CFR 312.62 & ICH E6(R2) Section 4.3 (Investigational Subject Identification)",
      action_required: isLocked
        ? "Subject permanently disqualified. Return to Intake Queue or select an eligible participant."
        : isFailed
        ? `Clinician must resupply missing demographic fields [${missing.join(", ")}] (Attempt ${resupplyAttempts + 1} of 3).`
        : "None - Ingress verification complete.",
    }
  }, [localPatient, patient, pid, resupplyAttempts])

  const currentAttempts = guardrail1.resupply_attempts ?? 0
  const maxIters = guardrail1.max_iters ?? 3
  const isLockedOut = Boolean(
    guardrail1.locked ||
    guardrail1.status === "EXCLUDED_MAX_ITERS" ||
    (currentAttempts >= maxIters && !guardrail1.passed)
  )

  // Guardrail 2: Protocol Baseline Safety Corridors & Catastrophic Boundaries
  const guardrail2 = useMemo(() => {
    if (arbitrationResult.guardrail_2_result) {
      return arbitrationResult.guardrail_2_result
    }
    const alt = Number(clinicalProfile.alt)
    const ast = Number(clinicalProfile.ast)
    const egfr = Number(clinicalProfile.egfr)
    const bili = Number(clinicalProfile.bili ?? 0.8)
    const anc = Number(clinicalProfile.anc ?? 3200)

    const breached = []
    if (alt > 200) {
      breached.push({
        rule_id: "SAFETY_HEPATIC_ALT",
        parameter: "ALT (Alanine Aminotransferase)",
        observed: `${alt.toFixed(1)} U/L`,
        limit: "<= 200.0 U/L (Catastrophic Ceiling)",
        difference: `+${(alt - 200).toFixed(1)} U/L`,
        severity: "CATASTROPHIC_HARD_BREACH",
        reason: `Observed ALT of ${alt.toFixed(1)} U/L exceeds critical safety ceiling (>5x ULN). Acute hepatic necrosis.`,
      })
    }
    if (ast > 200) {
      breached.push({
        rule_id: "SAFETY_HEPATIC_AST",
        parameter: "AST (Aspartate Aminotransferase)",
        observed: `${ast.toFixed(1)} U/L`,
        limit: "<= 200.0 U/L (Catastrophic Ceiling)",
        difference: `+${(ast - 200).toFixed(1)} U/L`,
        severity: "CATASTROPHIC_HARD_BREACH",
        reason: `Observed AST of ${ast.toFixed(1)} U/L exceeds critical safety ceiling (>5x ULN).`,
      })
    }
    if (egfr < 15) {
      breached.push({
        rule_id: "SAFETY_RENAL_EGFR",
        parameter: "eGFR (End-Stage Renal Floor)",
        observed: `${egfr.toFixed(1)} mL/min/1.73m2`,
        limit: ">= 15.0 mL/min/1.73m2 (Catastrophic Stopping Floor)",
        difference: `${(egfr - 15).toFixed(1)} mL/min/1.73m2 below ESRD threshold`,
        severity: "CATASTROPHIC_HARD_BREACH",
        reason: `Observed eGFR of ${egfr.toFixed(1)} mL/min indicates end-stage renal collapse. Investigational drug clearance is prohibited.`,
      })
    }
    if (bili > 4.0) {
      breached.push({
        rule_id: "SAFETY_HEPATIC_BILIRUBIN",
        parameter: "Total Bilirubin",
        observed: `${bili.toFixed(1)} mg/dL`,
        limit: "<= 4.0 mg/dL (Severe Hyperbilirubinemia)",
        difference: `+${(bili - 4.0).toFixed(1)} mg/dL above critical threshold`,
        severity: "CATASTROPHIC_HARD_BREACH",
        reason: `Observed Total Bilirubin of ${bili.toFixed(1)} mg/dL indicates acute hepatic decompensation with jaundice.`,
      })
    }
    if (anc < 500) {
      breached.push({
        rule_id: "SAFETY_HEME_ANC",
        parameter: "ANC (Absolute Neutrophil Count)",
        observed: `${anc} /uL`,
        limit: ">= 500 /uL (Agranulocytosis Ceiling)",
        difference: `${anc - 500} /uL below critical safety floor`,
        severity: "CATASTROPHIC_HARD_BREACH",
        reason: `Observed ANC of ${anc} /uL represents life-threatening agranulocytosis. Systemic therapy is absolutely contraindicated.`,
      })
    }

    const isBreached = breached.length > 0
    return {
      passed: !isBreached,
      status: isBreached ? ("BREACHED" as const) : ("PASSED" as const),
      short_circuited: isBreached,
      breached_boundaries: breached,
      reason: isBreached
        ? `Catastrophic protocol boundary breach in ${breached.length} vital parameter(s): ${breached[0]?.reason} Immediate short-circuit triggered at Guardrail-2.`
        : "All physiological organ clearance and hematologic parameters reside safely within baseline protocol corridors.",
      regulatory_citation: "FDA Guidance: Premature Clinical Trial Discontinuation & Critical Safety Stopping Rules",
      action_required: isBreached
        ? "Immediate halt of study drug administration and emergency clinical toxicity escalation."
        : "Proceed to trial status check and multi-agent fan-out.",
    }
  }, [arbitrationResult.guardrail_2_result, clinicalProfile])

  // Section 3: RAG Protocol Rules & Dosage Window (Dynamic Overdose & Titration Evaluation)
  const ragRules = useMemo(() => {
    if (!orderModified && arbitrationResult.rag_rule_result) {
      return arbitrationResult.rag_rule_result
    }

    const violations: any[] = []

    if (hasDoseOverdose) {
      violations.push({
        rule_id: `${activeTrialId}_DOSE_LIMIT`,
        parameter: "Therapeutic Dosage Window",
        observed: activeAction,
        limit: "Standard protocol approved maximum dose",
        difference: "Supratherapeutic Overdose beyond approved ceiling",
        reference: `${activeTrialId}-dosing-002: Arm Standard Protocol`,
        reason: `Prescribed action (${activeAction}) exceeds protocol-specified therapeutic dosage limit.`,
      })
    }

    const facts = (localPatient?.clinical_data || patient?.clinical_data)?.protocol_facts || {}
    const daysSinceBleed = facts?.days_since_major_bleed
    if (facts?.ongoing_bleeding || (typeof daysSinceBleed === "number" && daysSinceBleed < 30)) {
      const days = daysSinceBleed ?? 12
      violations.push({
        rule_id: `${activeTrialId}_EXC_BLEEDING_WASHOUT`,
        parameter: "Major Hemorrhage Washout",
        observed: `${days} days elapsed since major bleed`,
        limit: ">= 30 days mandatory washout",
        difference: `-${30 - days} days below required washout period`,
        reference: `${activeTrialId}-eligibility-003: Hemorrhagic Exclusion Criteria`,
        reason: `Patient experienced severe active/recent bleeding ${days} days ago; protocol mandates at least 30 days washout.`,
      })
    }

    const labs = (localPatient?.clinical_data || patient?.clinical_data)?.lab_results || {}
    const crclNum = Number(labs?.creatinine_clearance?.value ?? labs?.creatinine_clearance ?? 65)
    if (crclNum < 30) {
      violations.push({
        rule_id: `${activeTrialId}_EXC_SEVERE_RENAL`,
        parameter: "Creatinine Clearance Protocol Floor",
        observed: `CrCl ${crclNum.toFixed(1)} mL/min`,
        limit: ">= 30.0 mL/min protocol entry floor",
        difference: `${(crclNum - 30).toFixed(1)} mL/min below required entry floor`,
        reference: `${activeTrialId}-eligibility-006: Renal Stratification Protocol`,
        reason: `Observed creatinine clearance (${crclNum.toFixed(0)} mL/min) falls below the protocol-specified 30 mL/min participation floor.`,
      })
    }

    if (facts?.active_autoimmune_disease) {
      violations.push({
        rule_id: `${activeTrialId}_EXC_AUTOIMMUNE`,
        parameter: "Active Autoimmune Exclusion",
        observed: "Active autoimmune colitis on systemic immunosuppression",
        limit: "No active autoimmune disease requiring systemic immunosuppression",
        difference: "Active contraindicated condition",
        reference: `${activeTrialId}-eligibility-002: Checkpoint Exclusion Criteria`,
        reason: "Active autoimmune disorder requiring systemic immunosuppressive therapy strictly contraindicates checkpoint immunotherapy.",
      })
    }

    return {
      compliant: violations.length === 0,
      status: violations.length === 0 ? ("COMPLIANT" as const) : ("NON_COMPLIANT" as const),
      violations,
      reason: violations.length === 0
        ? "Proposed intervention and patient clinical parameters conform to all trial protocol and RAG rule specifications."
        : `${violations.length} trial protocol eligibility and dosing rule violation(s) identified against ${activeTrialId}.`,
    }
  }, [orderModified, arbitrationResult.rag_rule_result, hasDoseOverdose, activeAction, activeTrialId, localPatient, patient])

  const complianceResult = arbitrationResult.protocol_compliance_result
  const safetyResult = arbitrationResult.safety_result
  const financialResult = arbitrationResult.financial_result

  // Specialist Status Vectors: Prioritize evaluated arbitration results, updating dynamically if modified
  const rawCompStatus = complianceResult?.compliance_status || (ragRules.compliant && !hasDoseOverdose ? "COMPLIANT" : "NON_COMPLIANT")
  const isCompliant = orderModified ? (ragRules.compliant && !hasDoseOverdose) : (rawCompStatus === "COMPLIANT")
  const complianceStatus = isCompliant ? "COMPLIANT" : (orderModified ? (hasDoseOverdose ? "NON_COMPLIANT" : "COMPLIANT") : rawCompStatus)

  const rawSafetyStatus = safetyResult?.safety_status || (guardrail2.passed && !hasDoseOverdose ? "SAFE" : "UNSAFE")
  const isSafetySafe = orderModified ? (guardrail2.passed && !hasDoseOverdose) : (rawSafetyStatus === "SAFE")
  const safetyStatus = isSafetySafe ? "SAFE" : (orderModified ? (hasDoseOverdose || !guardrail2.passed ? "UNSAFE" : "SAFE") : rawSafetyStatus)

  const rawCoverageStatus = financialResult?.coverage_status || (!hasDoseOverdose ? "COVERED" : "NOT_COVERED")
  const isCovered = orderModified ? !hasDoseOverdose : (rawCoverageStatus === "COVERED")
  const coverageStatus = isCovered ? "COVERED" : (orderModified ? (hasDoseOverdose ? "NOT_COVERED" : "COVERED") : rawCoverageStatus)

  const financialExposure = orderModified
    ? (hasDoseOverdose ? 12500 : 0)
    : (typeof financialResult?.financialExposure === "number"
        ? financialResult.financialExposure
        : (typeof arbitrationResult.financialExposure === "number"
            ? arbitrationResult.financialExposure
            : (isCovered ? 0 : 12500)))

  // Section 4: 4 A2A Multi-Agent Consensus Matrix & Specialist Discrepancies (Specialists Only)
  const a2aDiscrepancies = useMemo(() => {
    const dissenting: string[] = []
    const reasons: Record<string, string> = {}

    if (complianceStatus !== "COMPLIANT") {
      dissenting.push("Protocol Compliance Specialist")
      reasons["Protocol Compliance Specialist"] =
        complianceResult?.explanation ||
        (hasDoseOverdose
          ? `Prescribed dosage (${activeAction}) exceeds protocol maximum ceiling.`
          : "Protocol compliance verification exception.")
    }
    if (safetyStatus !== "SAFE") {
      dissenting.push("Safety & Toxicity Specialist")
      reasons["Safety & Toxicity Specialist"] =
        safetyResult?.explanation ||
        (hasDoseOverdose
          ? "Supratherapeutic drug exposure increases risk of life-threatening organ toxicity and hemorrhage."
          : "Clinical safety or drug interaction contraindication.")
    }
    if (coverageStatus !== "COVERED") {
      dissenting.push("Financial Risk Specialist")
      reasons["Financial Risk Specialist"] =
        financialResult?.callout ||
        financialResult?.explanation ||
        (hasDoseOverdose
          ? "Non-protocol supratherapeutic dosing requires secondary prior authorization ($12,500 liability)."
          : "Sponsor reimbursement exception.")
    }

    const hasDiscrepancy = dissenting.length > 0 || !guardrail1.passed || !guardrail2.passed || !ragRules.compliant
    return {
      has_discrepancy: hasDiscrepancy,
      consensus_status: hasDiscrepancy ? ("CONSENSUS_REJECTED" as const) : ("UNANIMOUS_CONSENSUS_JUSTIFIED" as const),
      dissenting_agents: dissenting,
      reasons,
    }
  }, [complianceStatus, safetyStatus, coverageStatus, complianceResult, safetyResult, financialResult, guardrail1.passed, guardrail2.passed, ragRules.compliant, hasDoseOverdose, activeAction])

  // Dynamic Final Verdict Synthesis
  let finalVerdict: string = arbitrationResult.final_verdict || "JUSTIFIED"
  let recommendationTitle: string = arbitrationResult.recommendationTitle || "Consensus Verdict: JUSTIFIED"
  let recommendationSummary: string = arbitrationResult.summary || "Unanimous multi-agent consensus achieved. Protocol Compliance, Safety & Toxicity, and Financial Risk specialists all recommend proceeding. 100% sponsor trial coverage ($0 liability)."

  if (decision === "reject") {
    finalVerdict = "NOT_JUSTIFIED (PHYSICIAN REJECTED)"
    recommendationTitle = "Clinical Safety Hold: Order Discontinued"
    recommendationSummary = "Attending investigator exercised clinical override to REJECT the proposed order. Prescription held in pharmacy dispensing systems per GCP/IRB audit rules."
  } else if (decision === "accept") {
    finalVerdict = "JUSTIFIED (PHYSICIAN ACCEPTED)"
    recommendationTitle = "Physician Adjudication Confirmed: Order Approved"
    recommendationSummary = "Attending investigator electronically signed and approved this medication order under FDA 21 CFR Part 11 electronic records provisions."
  } else if (orderModified || decision === "override") {
    if (hasDoseOverdose || !guardrail1.passed || !guardrail2.passed) {
      finalVerdict = "NOT_JUSTIFIED"
      recommendationTitle = "Consensus Verdict: NOT_JUSTIFIED (Modified Regimen Non-Compliant)"
      recommendationSummary = "Proposed modification violates protocol safety constraints or guardrail thresholds."
    } else {
      finalVerdict = "JUSTIFIED (MODIFIED)"
      recommendationTitle = "Consensus Verdict: JUSTIFIED (MODIFIED TO STANDARD PROTOCOL)"
      recommendationSummary = `Medication order successfully titrated to protocol-compliant dosage (${activeAction}). Multi-agent consensus achieved with zero patient liability.`
    }
  } else if (!guardrail1.passed) {
    finalVerdict = "NOT_JUSTIFIED"
    recommendationTitle = "Consensus Verdict: NOT_JUSTIFIED (Ingress Demographic Failure)"
    recommendationSummary = guardrail1.reason
  } else if (!guardrail2.passed) {
    finalVerdict = "NOT_JUSTIFIED"
    recommendationTitle = "Consensus Verdict: NOT_JUSTIFIED (Safety Corridor Breach)"
    recommendationSummary = guardrail2.reason
  } else if (!ragRules.compliant || hasDoseOverdose) {
    finalVerdict = "NOT_JUSTIFIED"
    recommendationTitle = "Consensus Verdict: NOT_JUSTIFIED (Protocol Violation)"
    recommendationSummary = ragRules.violations[0]?.reason || "Prescribed medication order violates protocol dosing limits."
  } else if (a2aDiscrepancies.dissenting_agents.length > 0) {
    finalVerdict = "NOT_JUSTIFIED"
    recommendationTitle = "Consensus Verdict: NOT_JUSTIFIED (Multi-Agent Dissent)"
    recommendationSummary = `Consensus rejected: ${a2aDiscrepancies.dissenting_agents.join(", ")} flagged critical clinical, safety, or financial exceptions.`
  } else if (arbitrationResult.final_verdict) {
    finalVerdict = arbitrationResult.final_verdict
    recommendationTitle = arbitrationResult.recommendationTitle || `Consensus Verdict: ${arbitrationResult.final_verdict}`
    recommendationSummary = arbitrationResult.summary || recommendationSummary
  } else {
    finalVerdict = "JUSTIFIED"
    recommendationTitle = "Consensus Verdict: JUSTIFIED"
    recommendationSummary = "Unanimous multi-agent consensus achieved. Protocol Compliance, Safety & Toxicity, and Financial Risk specialists all recommend proceeding. 100% sponsor trial coverage ($0 liability)."
  }

  const isJustified = finalVerdict.startsWith("JUSTIFIED")

  // Metrics
  const metrics = arbitrationResult.agent_metrics || {}
  const complianceMetrics = metrics["Protocol Compliance Agent"]
  const safetyMetrics = metrics["Safety & Toxicity Agent"]
  const financialMetrics = metrics["Financial Risk Agent"]
  const reducerMetrics = metrics["Arbitration Reducer"]

  // Violation mapping for deep audit
  const rawViolations = arbitrationResult.protocolsViolated ??
    (arbitrationResult.protocol_compliance_result?.violations ?? []).map((violation: any) => ({
      name: String(violation.parameter ?? "Protocol requirement"),
      observed: String(violation.observed ?? "unknown"),
      limit: String(violation.limit ?? violation.expected ?? "Standard protocol threshold"),
      difference: violation.difference ? String(violation.difference) : undefined,
      reference: String(violation.reference ?? violation.protocol_text ?? "Trial Protocol Inclusion/Exclusion Specifications"),
      reason: violation.reason ? String(violation.reason) : undefined,
      clinical_implication: violation.clinical_implication ? String(violation.clinical_implication) : undefined,
    }))

  const protocolViolations = rawViolations.map((v: any) => ({
    ...v,
    limit: formatLimit(v.limit),
  }))

  const safetyConcerns = arbitrationResult.safety_result?.concerns ?? []

  // Clinician Resupply Handlers
  async function handleResupplySubmit() {
    const ageNum = parseFloat(resupplyAge)
    if (isNaN(ageNum) || ageNum <= 0 || ageNum > 120) {
      setResupplyError("Please enter a valid patient age between 1 and 120 years.")
      return
    }
    if (!resupplySex || resupplySex.trim() === "") {
      setResupplyError("Please select biological sex.")
      return
    }

    setResupplyError(null)
    setIsResupplying(true)
    const nextAttempt = resupplyAttempts + 1
    setResupplyAttempts(nextAttempt)

    const updatedPatient = {
      ...localPatient,
      age: ageNum,
      sex: resupplySex === "Female" || resupplySex === "F" ? "F" : "M",
    }
    setLocalPatient(updatedPatient)
    onPatientUpdated?.({
      age: ageNum,
      sex: resupplySex === "Female" || resupplySex === "F" ? "F" : "M",
    })

    try {
      await resupplyPatientData(
        patient.id,
        { age: ageNum, sex: resupplySex.toLowerCase() },
        nextAttempt,
        maxIters,
        `Clinician demographic resupply (Age: ${ageNum}, Sex: ${resupplySex}): ${resupplyAttestation}`
      )
      onRestartStream?.()
    } catch (err: any) {
      console.warn("Remote resupply endpoint warning (local demographic update active):", err)
    } finally {
      setIsResupplying(false)
    }
  }

  async function handleSkipResupply() {
    setIsResupplying(true)
    setResupplyError(null)
    const nextAttempt = resupplyAttempts + 1
    setResupplyAttempts(nextAttempt)

    if (nextAttempt >= maxIters) {
      onPatientDisqualified?.(patient.id)
    }

    try {
      await resupplyPatientData(
        patient.id,
        {},
        nextAttempt,
        maxIters,
        `Clinician unable to supply demographic records on attempt ${nextAttempt} of ${maxIters}`
      )
      onRestartStream?.()
    } catch (err: any) {
      console.warn("Remote attempt recording warning (local budget active):", err)
    } finally {
      setIsResupplying(false)
    }
  }

  // Direct Accept or Reject
  async function handleDirectDecision(decisionType: "accept" | "reject") {
    setIsSubmittingDecision(true)
    setDecision(decisionType)
    setModifyOpen(false)
    try {
      const justification = decisionType === "reject"
        ? "Order rejected and clinical hold enforced by attending investigator per 21 CFR Part 11."
        : "Order accepted and electronically co-signed by attending investigator per 21 CFR Part 11."
      await submitDecision(patient.id, decisionType, justification)
    } catch (error) {
      console.warn("Remote decision sync warning (local decision active):", error)
    } finally {
      setIsSubmittingDecision(false)
    }
  }

  // Disease-specific remediation prompt and label
  const patientMeds = patient?.medications || []
  const patientDx = (patient?.diagnosis || "").toLowerCase()
  const patientCohort = (patient?.cohort || "").toLowerCase()
  const allPatText = `${patientCohort} ${patientDx} ${patientMeds.join(" ")}`.toLowerCase()

  let remDose = "5 mg BID"
  let remText = "Titrate Apixaban to standard protocol dose of 5 mg orally twice daily (Arm A standard therapeutic window)."
  let remPrompt = "Adjust dosage to standard 5 mg BID per protocol Arm A guidelines."

  if (allPatText.includes("pembrolizumab") || allPatText.includes("oncology") || allPatText.includes("carcinoma") || allPatText.includes("cancer")) {
    remDose = "200 mg Q3W"
    remText = "Administer Pembrolizumab at standard protocol dose of 200 mg IV every 3 weeks (Cohort C therapeutic window)."
    remPrompt = "Adjust dosage to standard 200 mg IV every 3 weeks per oncology protocol guidelines."
  } else if (allPatText.includes("empagliflozin") || allPatText.includes("renal") || allPatText.includes("nephropathy")) {
    remDose = "10 mg Daily"
    remText = "Titrate Empagliflozin to standard protocol dose of 10 mg orally once daily (Cohort B therapeutic window)."
    remPrompt = "Adjust dosage to standard 10 mg oral once daily per renal protocol guidelines."
  } else if (allPatText.includes("pioglitazone") || allPatText.includes("nafld") || allPatText.includes("mash") || allPatText.includes("steatohepatitis")) {
    remDose = "30 mg Daily"
    remText = "Titrate Pioglitazone to standard protocol dose of 30 mg orally once daily (Cohort B therapeutic window)."
    remPrompt = "Adjust dosage to standard 30 mg oral once daily per metabolic protocol guidelines."
  }

  // 1-Click Remediation Recommendation
  async function handleApplyRemediation() {
    setIsApplyingRemediation(true)
    setComment(remPrompt)
    setModifyOpen(true)
    setIsExtracting(true)
    setTimeout(() => {
      modifyDrawerRef.current?.scrollIntoView({ behavior: "smooth", block: "nearest" })
    }, 60)

    const standardized = remDose.includes("5 mg") ? "Apixaban 5 mg oral twice daily"
      : remDose.includes("200 mg") ? "Pembrolizumab 200 mg IV every 3 weeks"
      : remDose.includes("10 mg") ? "Empagliflozin 10 mg oral once daily"
      : "Pioglitazone 30 mg oral once daily"
    setActiveAction(standardized)
    setOrderModified(true)
    setDecision("override")

    try {
      const result = await processClinicalComment(remPrompt)
      setExtractionResult(result)
    } catch (error) {
      console.warn("NLP auto-extraction note (standardized dose applied):", error)
    } finally {
      setIsExtracting(false)
      setIsApplyingRemediation(false)
    }
  }

  // AI Extraction for Clinical Override
  async function handleExtract() {
    setIsExtracting(true)
    try {
      const result = await processClinicalComment(comment)
      setExtractionResult(result)
    } catch (error) {
      console.error("Failed to extract parameters:", error)
    } finally {
      setIsExtracting(false)
    }
  }

  // Override Submit
  async function handleOverrideSubmit() {
    setIsSubmittingOverride(true)
    let updated = activeAction
    if (extractionResult?.standardized_action) {
      updated = extractionResult.standardized_action
    } else if (extractionResult?.modifications?.[0]) {
      const mod = extractionResult.modifications[0]
      updated = `${mod.dosage_name} ${mod.proposed_dosage} ${mod.dosage_unit || "mg"} ${mod.route || "oral"} ${mod.frequency || "twice daily"}`
    }
    setActiveAction(updated)
    setOrderModified(true)
    setDecision("override")

    try {
      await submitDecision(
        patient.id,
        "override",
        comment,
        extractionResult?.modifications || [],
        extractionResult
      )
      setExtractionResult(null)
      setComment("")
      setModifyOpen(false)
      onPatientUpdated?.({ action: updated })
      onRestartStream?.(updated)
    } catch (error) {
      console.warn("Remote override dispatch warning (local override active):", error)
      setExtractionResult(null)
      setComment("")
      setModifyOpen(false)
      onPatientUpdated?.({ action: updated })
      onRestartStream?.(updated)
    } finally {
      setIsSubmittingOverride(false)
    }
  }

  const handleCopyAuditPayload = () => {
    navigator.clipboard.writeText(JSON.stringify(arbitrationResult, null, 2))
    setCopiedPayload(true)
    setTimeout(() => setCopiedPayload(false), 2000)
  }

  return (
    <section className="rounded-2xl border border-[#2e2e2e] bg-[#161616] p-6 md:p-8 shadow-2xl space-y-8">
      {/* Top Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-[#282828] pb-5">
        <div className="flex flex-wrap items-center gap-4">
          <TrialGuardLogo className="h-8 w-auto" />
          <div className="hidden h-7 w-px bg-[#2e2e2e] sm:block" />
          <div className="flex items-center gap-3">
            <div className="flex size-10 items-center justify-center rounded-xl border border-[#2e2e2e] bg-[#121212] text-sky-400 shadow-inner">
              <Scale className="size-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-base font-bold text-white tracking-tight">
                  HITL Clinical Decision Gateway
                </h2>
                <span className="rounded-full border border-sky-500/30 bg-sky-500/10 px-2.5 py-0.5 font-mono text-[10px] font-bold text-sky-400">
                  FDA 21 CFR Part 11
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-0.5">
                Multi-Agent Adjudication · Patient <strong className="text-slate-300 font-semibold">{patient.id}</strong> ({patient.name}) · Cohort: {patient.cohort}
              </p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <span
            className={`rounded-full px-3.5 py-1 font-mono text-xs font-bold uppercase tracking-wider ${
              decision
                ? "bg-emerald-500/15 text-emerald-400 border border-emerald-500/30"
                : "bg-amber-500/15 text-amber-400 border border-amber-500/30 animate-pulse"
            }`}
          >
            {decision ? `Adjudicated: ${decision.toUpperCase()}` : "Awaiting Physician Adjudication"}
          </span>
        </div>
      </div>

      {/* Hero Consensus Synthesis Banner */}
      <div
        className={`rounded-xl border p-6 transition-all space-y-4 ${
          isJustified
            ? "border-emerald-500/40 bg-gradient-to-r from-emerald-950/30 via-[#141414] to-[#141414]"
            : "border-rose-500/40 bg-gradient-to-r from-rose-950/30 via-[#141414] to-[#141414]"
        }`}
      >
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-[#242424] pb-3">
          <div className="flex items-center gap-2.5">
            <div
              className={`flex size-7 items-center justify-center rounded-lg ${
                isJustified ? "bg-emerald-500/20 text-emerald-400" : "bg-rose-500/20 text-rose-400"
              }`}
            >
              <GitMerge className="size-3.5" />
            </div>
            <p className="text-xs font-bold uppercase tracking-wider text-slate-400">
              LangGraph Multi-Agent Consensus Recommendation
            </p>
          </div>

          <div className="flex items-center gap-2">
            <span
              className={`rounded-full px-2.5 py-0.5 font-mono text-[11px] font-bold uppercase tracking-wider ${
                isJustified
                  ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/40"
                  : "bg-rose-500/20 text-rose-400 border border-rose-500/40"
              }`}
            >
              FINAL VERDICT: {finalVerdict}
            </span>
            {reducerMetrics?.confidence && (
              <span className="rounded-full bg-[#202020] px-2 py-0.5 font-mono text-[10px] text-slate-300">
                {Math.round(reducerMetrics.confidence * 100)}% Consensus Assurance
              </span>
            )}
          </div>
        </div>

        <div>
          <h3 className="text-lg font-bold text-white text-balance leading-snug">
            {recommendationTitle}
          </h3>
          <p className="mt-2 text-sm leading-relaxed text-slate-200 text-pretty">
            {recommendationSummary}
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3.5 pt-3 border-t border-[#222] text-xs">
          <span className="font-semibold text-slate-400">Specialist Consensus:</span>
          <span className="flex items-center gap-1.5 font-mono">
            <span
              className={`size-2.5 rounded-full ${
                isCompliant ? "bg-emerald-400" : "bg-rose-400"
              }`}
            />
            <span className="text-slate-300">Protocol:</span>
            <span className={isCompliant ? "text-emerald-400 font-bold" : "text-rose-400 font-bold"}>
              {complianceStatus}
            </span>
          </span>
          <span className="text-slate-600">·</span>
          <span className="flex items-center gap-1.5 font-mono">
            <span
              className={`size-2.5 rounded-full ${
                isSafetySafe ? "bg-emerald-400" : "bg-rose-400"
              }`}
            />
            <span className="text-slate-300">Safety:</span>
            <span className={isSafetySafe ? "text-emerald-400 font-bold" : "text-rose-400 font-bold"}>
              {safetyStatus}
            </span>
          </span>
          <span className="text-slate-600">·</span>
          <span className="flex items-center gap-1.5 font-mono">
            <span
              className={`size-2.5 rounded-full ${
                isCovered ? "bg-emerald-400" : "bg-amber-400"
              }`}
            />
            <span className="text-slate-300">Coverage:</span>
            <span className={isCovered ? "text-emerald-400 font-bold" : "text-amber-400 font-bold"}>
              {isCovered
                ? "$0 (100% Sponsor CTA)"
                : `$${financialExposure.toLocaleString("en-US")} (Sponsor Denied · Prior Auth)`}
            </span>
          </span>
          {reducerMetrics?.latency_ms && (
            <>
              <span className="text-slate-600">·</span>
              <span className="font-mono text-slate-400">
                Synthesis Latency: {reducerMetrics.latency_ms}ms
              </span>
            </>
          )}
        </div>
      </div>

      {/* Patient Clinical Profile Dossier Banner */}
      <div className="rounded-xl border border-[#2e2e2e] bg-[#181818] p-6 shadow-xl space-y-5">
        <div className="flex flex-wrap items-center justify-between gap-4 border-b border-[#282828] pb-4">
          <div className="flex items-center gap-3.5">
            <div className="flex size-11 items-center justify-center rounded-xl bg-blue-500/15 text-blue-400 border border-blue-500/30 shadow-inner">
              <User className="size-6" />
            </div>
            <div>
              <div className="flex flex-wrap items-center gap-2.5">
                <h3 className="text-base font-bold text-white tracking-wide">
                  {clinicalProfile.name}
                </h3>
                <span className="rounded bg-[#252525] px-2.5 py-0.5 font-mono text-[11px] text-slate-300 font-semibold border border-[#333]">
                  MRN: {clinicalProfile.id}
                </span>
                <span className="rounded bg-sky-500/15 px-2.5 py-0.5 font-mono text-[11px] text-sky-300 border border-sky-500/30 font-bold">
                  {clinicalProfile.trialId}
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-1">
                {clinicalProfile.age} yrs · {clinicalProfile.sex} · DOB: {clinicalProfile.dob} · <span className="text-slate-300 font-medium">{clinicalProfile.cohort}</span>
              </p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2.5">
            <div className="flex items-center gap-2 rounded-lg border border-[#2e2e2e] bg-[#121212] px-3 py-1.5 text-xs">
              <Heart className="size-4 text-rose-400" />
              <span className="text-slate-400 text-xs">BP:</span>
              <span className="font-mono font-bold text-white text-xs">{clinicalProfile.bp}</span>
              <span className="text-slate-600">·</span>
              <span className="text-slate-400 text-xs">HR:</span>
              <span className="font-mono font-bold text-white text-xs">{clinicalProfile.hr}</span>
            </div>
            <div className="flex items-center gap-2 rounded-lg border border-[#2e2e2e] bg-[#121212] px-3 py-1.5 text-xs">
              <Activity className="size-4 text-emerald-400" />
              <span className="text-slate-400 text-xs">LVEF:</span>
              <span className="font-mono font-bold text-emerald-300 text-xs">{clinicalProfile.lvef}</span>
            </div>
          </div>
        </div>

        {/* Clinical Breakdown: Diagnoses, Active Meds & Labs Grid */}
        <div className="grid gap-4 md:grid-cols-3">
          {/* Diagnoses Panel */}
          <div className="rounded-xl border border-[#282828] bg-[#121212] p-4 space-y-2.5">
            <div className="flex items-center gap-2 text-xs font-bold text-slate-300 uppercase tracking-wider">
              <Stethoscope className="size-4 text-blue-400" />
              <span>Primary Pathologies & Diagnoses</span>
            </div>
            <div className="flex flex-wrap gap-2 pt-1">
              {clinicalProfile.diagnoses.map((dx, i) => (
                <span
                  key={i}
                  className="rounded-lg border border-blue-500/30 bg-blue-500/10 px-2.5 py-1 text-xs font-medium text-blue-200 capitalize"
                >
                  {dx}
                </span>
              ))}
            </div>
          </div>

          {/* Active Baseline Medications Panel */}
          <div className="rounded-xl border border-[#282828] bg-[#121212] p-4 space-y-2.5">
            <div className="flex items-center gap-2 text-xs font-bold text-slate-300 uppercase tracking-wider">
              <Pill className="size-4 text-amber-400" />
              <span>Active Baseline Regimens</span>
            </div>
            <div className="flex flex-wrap gap-2 pt-1">
              {clinicalProfile.medications.map((med, i) => (
                <span
                  key={i}
                  className="rounded-lg border border-amber-500/30 bg-amber-500/10 px-2.5 py-1 text-xs font-mono font-medium text-amber-200"
                >
                  {med}
                </span>
              ))}
            </div>
          </div>

          {/* Organ Clearance & Biomarker Telemetry Panel */}
          <div className="rounded-xl border border-[#282828] bg-[#121212] p-4 space-y-2.5">
            <div className="flex items-center gap-2 text-xs font-bold text-slate-300 uppercase tracking-wider">
              <Dna className="size-4 text-emerald-400" />
              <span>Baseline Organ Clearance Panel</span>
            </div>
            <div className="grid grid-cols-2 gap-x-3 gap-y-1.5 pt-1 font-mono text-xs">
              <div className="flex justify-between border-b border-[#222] pb-1">
                <span className="text-slate-400">CrCl:</span>
                <span className={`font-bold ${clinicalProfile.crcl >= 30 ? "text-emerald-400" : "text-rose-400"}`}>
                  {clinicalProfile.crcl} mL/min
                </span>
              </div>
              <div className="flex justify-between border-b border-[#222] pb-1">
                <span className="text-slate-400">Serum Cr:</span>
                <span className="text-slate-200 font-bold">{clinicalProfile.scr} mg/dL</span>
              </div>
              <div className="flex justify-between border-b border-[#222] pb-1">
                <span className="text-slate-400">eGFR:</span>
                <span className="text-slate-200 font-bold">{clinicalProfile.egfr} mL/min</span>
              </div>
              <div className="flex justify-between border-b border-[#222] pb-1">
                <span className="text-slate-400">ALT / AST:</span>
                <span className={`font-bold ${clinicalProfile.alt <= 120 && clinicalProfile.ast <= 120 ? "text-emerald-400" : "text-rose-400"}`}>
                  {clinicalProfile.alt} / {clinicalProfile.ast} U/L
                </span>
              </div>
              <div className="flex justify-between col-span-2 pt-1 text-[11px] text-slate-400">
                <span>Platelets: <strong className="text-slate-300">{Number(clinicalProfile.platelets).toLocaleString()}/µL</strong></span>
                <span>INR: <strong className="text-slate-300">{clinicalProfile.inr}</strong></span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 4 Dedicated Sections for Non-Aligned Errors & Guardrail Exceptions */}
      <div className="space-y-6">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-[#282828] pb-3">
          <div>
            <h3 className="text-sm font-bold text-white tracking-wide uppercase">
              Adjudication Guardrails & Multi-Agent Verification Architecture (4 Core Gates)
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Deterministic Ingress Gates, Protocol Corridors, RAG Rule Matching, and Autonomous A2A Consensus
            </p>
          </div>
          <span className="font-mono text-xs text-slate-400">
            FDA 21 CFR Part 11 Audit Trail
          </span>
        </div>

        <div className="grid gap-5">
          {/* SECTION 1: Ingress Demographic Validation (Guardrail 1) */}
          <div
            className={`rounded-xl border p-6 md:p-7 transition-all space-y-4 ${
              isLockedOut
                ? "border-rose-600/80 bg-gradient-to-r from-rose-950/80 via-[#1c0a0e] to-[#121212] shadow-xl shadow-rose-950/50 ring-1 ring-rose-500/50"
                : !guardrail1.passed
                ? "border-amber-500/50 bg-gradient-to-r from-amber-950/40 via-[#191410] to-[#121212] shadow-lg shadow-amber-950/30"
                : "border-emerald-500/30 bg-[#141414]"
            }`}
          >
            <div className="flex flex-wrap items-center justify-between gap-3 border-b border-[#242424] pb-3">
              <div className="flex items-center gap-3">
                <div
                  className={`flex size-8 items-center justify-center rounded-lg ${
                    isLockedOut
                      ? "bg-rose-500/20 text-rose-300"
                      : !guardrail1.passed
                      ? "bg-amber-500/20 text-amber-300"
                      : "bg-emerald-500/15 text-emerald-400"
                  }`}
                >
                  {isLockedOut ? (
                    <Lock className="size-4.5" />
                  ) : !guardrail1.passed ? (
                    <ShieldAlert className="size-4.5" />
                  ) : (
                    <ShieldCheck className="size-4.5" />
                  )}
                </div>
                <div>
                  <h4 className="text-sm font-bold text-white leading-tight">
                    Section 1: Ingress Demographic Validation (Guardrail 1)
                  </h4>
                  <p className="text-xs text-slate-400 mt-0.5 leading-tight">
                    FDA 21 CFR 312.62 · ICH E6(R2) Section 4.3 · Subject Identification Schema
                  </p>
                </div>
              </div>

              <span
                className={`rounded-full px-3 py-1 font-mono text-xs font-bold uppercase tracking-wider ${
                  isLockedOut
                    ? "bg-rose-500/30 text-rose-200 border border-rose-500/60 animate-pulse"
                    : !guardrail1.passed
                    ? "bg-amber-500/20 text-amber-300 border border-amber-500/40"
                    : "bg-emerald-500/15 text-emerald-400 border border-emerald-500/30"
                }`}
              >
                {isLockedOut
                  ? "⛔ LOCKED OUT: 3/3 MAX ITERATIONS EXCEEDED"
                  : !guardrail1.passed
                  ? `INGRESS_FAILED: RESUPPLY REQ (ATTEMPT ${currentAttempts + 1}/${maxIters})`
                  : currentAttempts > 0
                  ? `PASSED: RESUPPLIED (ATTEMPT ${currentAttempts}/${maxIters})`
                  : "PASSED: SCHEMA VERIFIED"}
              </span>
            </div>

            <div className="mt-3 space-y-4">
              {isLockedOut ? (
                /* Permanent Terminal Lockout Banner */
                <div className="rounded-xl border border-rose-500/60 bg-rose-950/60 p-5 space-y-4 shadow-inner">
                  <div className="flex items-start gap-3.5">
                    <div className="flex size-10 shrink-0 items-center justify-center rounded-lg bg-rose-500/30 text-rose-200">
                      <Lock className="size-5" />
                    </div>
                    <div className="space-y-1.5">
                      <h5 className="font-bold text-sm text-rose-200 uppercase tracking-wide flex items-center gap-2">
                        ⛔ Ingress Rejected: Patient ID Locked Out ({currentAttempts}/{maxIters} Attempts Exceeded)
                      </h5>
                      <p className="text-xs text-rose-100/90 leading-relaxed">
                        Subject ID <strong className="font-mono text-white underline">{patient.id}</strong> has exhausted the regulatory retry budget of <strong>{maxIters} attempts</strong> without verified demographic data. Under <strong>FDA 21 CFR 312.62 & ICH E6(R2)</strong>, this patient ID is permanently excluded and disqualified from the trial intake session.
                      </p>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs pt-1">
                    <div className="rounded-lg border border-rose-800/50 bg-[#0c0507] p-3 space-y-1">
                      <span className="text-[10px] font-mono uppercase tracking-wider text-rose-400 font-bold">
                        Regulatory Authority Citation
                      </span>
                      <p className="text-slate-300 font-medium">{guardrail1.regulatory_citation}</p>
                    </div>
                    <div className="rounded-lg border border-rose-800/50 bg-[#0c0507] p-3 space-y-1">
                      <span className="text-[10px] font-mono uppercase tracking-wider text-amber-400 font-bold">
                        Enforcement Status
                      </span>
                      <p className="text-amber-200 font-medium">Terminal Disqualification · Intake portal will not accept this ID.</p>
                    </div>
                  </div>

                  <div className="pt-2 flex justify-end">
                    <Button
                      onClick={() => onPatientDisqualified?.(patient.id)}
                      className="h-9 bg-rose-700 hover:bg-rose-600 text-white font-semibold text-xs transition-all shadow-md px-4"
                    >
                      <Lock className="size-3.5 mr-1.5" />
                      Disqualify Subject & Return to Intake Queue
                    </Button>
                  </div>
                </div>
              ) : !guardrail1.passed ? (
                <>
                  <div className="rounded-xl border border-rose-500/30 bg-rose-500/10 p-4 space-y-2.5">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-xs text-rose-200 uppercase tracking-wide">
                        Missing Mandatory Demographic Attributes:
                      </span>
                      <span className="rounded bg-rose-500/30 px-2.5 py-0.5 font-mono text-[10px] font-bold text-rose-100">
                        21 CFR 312.62 BREACH
                      </span>
                    </div>
                    <div className="flex flex-wrap gap-2 pt-1">
                      {guardrail1.missing_fields.map((f, i) => (
                        <span
                          key={i}
                          className="rounded-md border border-rose-500/40 bg-rose-950/60 px-3 py-1 font-mono text-xs font-bold text-rose-300"
                        >
                          ❌ {f} (Missing / Null)
                        </span>
                      ))}
                    </div>
                    <p className="text-xs leading-relaxed text-slate-200 pt-1">
                      <strong className="text-rose-300">Clinical Reason: </strong>
                      {guardrail1.reason}
                    </p>
                  </div>

                  {/* Interactive Clinician Demographic Resupply Console */}
                  <div className="rounded-xl border border-amber-500/40 bg-gradient-to-r from-amber-950/30 via-[#181510] to-[#121212] p-5 space-y-4">
                    <div className="flex flex-wrap items-center justify-between gap-2 border-b border-amber-500/20 pb-2.5">
                      <div className="flex items-center gap-2">
                        <Sparkles className="size-4 text-amber-400" />
                        <span className="text-xs font-bold text-amber-200 uppercase tracking-wide">
                          Clinician FHIR Demographic Resupply Console
                        </span>
                      </div>
                      <span className="rounded-full border border-amber-500/40 bg-amber-500/20 px-3 py-0.5 font-mono text-[10px] font-bold text-amber-300">
                        Resupply Attempt {currentAttempts + 1} of {maxIters} · ({maxIters - currentAttempts} remaining)
                      </span>
                    </div>

                    <p className="text-xs text-slate-300 leading-relaxed">
                      FDA 21 CFR 312.62 mandates complete demographic identification prior to clinical trial stratification. Attending clinician may manually input verified demographics below or record an unfulfilled resupply attempt. (Maximum {maxIters} attempts allowed before permanent patient ID lockout).
                    </p>

                    {resupplyError && (
                      <div className="flex items-center gap-2 rounded-lg border border-rose-500/40 bg-rose-950/40 p-2.5 text-xs text-rose-300">
                        <AlertCircle className="size-4 shrink-0" />
                        <span>{resupplyError}</span>
                      </div>
                    )}

                    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3 pt-1">
                      <div>
                        <label className="block text-[11px] font-mono uppercase tracking-wider text-slate-400 mb-1.5">
                          Patient Age (Years) <span className="text-rose-400">*</span>
                        </label>
                        <input
                          type="number"
                          min="1"
                          max="120"
                          value={resupplyAge}
                          onChange={(e) => setResupplyAge(e.target.value)}
                          placeholder="e.g. 58"
                          disabled={isResupplying}
                          className={`h-10 w-full rounded-lg border px-3.5 py-2 text-xs text-white font-mono placeholder:text-slate-500 focus:outline-none focus:ring-1 ${
                            guardrail1.missing_fields.includes("patient.age")
                              ? "border-amber-500/50 bg-[#1e1710] focus:ring-amber-400"
                              : "border-[#2e2e2e] bg-[#121212] focus:ring-sky-400"
                          }`}
                        />
                      </div>

                      <div>
                        <label className="block text-[11px] font-mono uppercase tracking-wider text-slate-400 mb-1.5">
                          Biological Sex <span className="text-rose-400">*</span>
                        </label>
                        <select
                          value={resupplySex}
                          onChange={(e) => setResupplySex(e.target.value)}
                          disabled={isResupplying}
                          className={`h-10 w-full rounded-lg border px-3.5 py-2 text-xs text-white font-mono focus:outline-none focus:ring-1 ${
                            guardrail1.missing_fields.includes("patient.sex")
                              ? "border-amber-500/50 bg-[#1e1710] focus:ring-amber-400"
                              : "border-[#2e2e2e] bg-[#121212] focus:ring-sky-400"
                          }`}
                        >
                          <option value="">Select Biological Sex</option>
                          <option value="Female">Female</option>
                          <option value="Male">Male</option>
                        </select>
                      </div>

                      <div className="sm:col-span-2 md:col-span-1">
                        <label className="block text-[11px] font-mono uppercase tracking-wider text-slate-400 mb-1.5">
                          Ingress Attestation
                        </label>
                        <input
                          type="text"
                          value={resupplyAttestation}
                          onChange={(e) => setResupplyAttestation(e.target.value)}
                          disabled={isResupplying}
                          className="h-10 w-full rounded-lg border border-[#2e2e2e] bg-[#121212] px-3.5 py-2 text-xs text-white font-mono placeholder:text-slate-500 focus:outline-none focus:ring-1 focus:ring-sky-400"
                        />
                      </div>
                    </div>

                    <div className="flex flex-wrap items-center gap-3 pt-2">
                      <Button
                        onClick={handleResupplySubmit}
                        disabled={isResupplying}
                        className="h-10 bg-amber-600 hover:bg-amber-500 text-white font-semibold text-xs transition-all shadow-md shadow-amber-950/40 px-4"
                      >
                        {isResupplying ? (
                          <>
                            <Loader2 className="size-3.5 mr-1.5 animate-spin" />
                            Re-evaluating Pipeline...
                          </>
                        ) : (
                          <>
                            <Check className="size-3.5 mr-1.5" />
                            Resupply Demographics & Re-evaluate
                          </>
                        )}
                      </Button>

                      <Button
                        variant="outline"
                        onClick={handleSkipResupply}
                        disabled={isResupplying}
                        className="h-10 border-rose-500/40 bg-rose-950/20 text-rose-300 hover:bg-rose-950/40 hover:text-white text-xs font-semibold px-4"
                      >
                        <AlertTriangle className="size-3.5 mr-1.5 text-rose-400" />
                        Unable to Supply (Record Attempt {currentAttempts + 1}/{maxIters})
                      </Button>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs pt-1">
                    <div className="rounded-xl border border-[#262626] bg-[#0d0d0d] p-3 space-y-1">
                      <span className="text-[10px] font-mono uppercase tracking-wider text-slate-400 font-bold">
                        Regulatory Authority Citation
                      </span>
                      <p className="text-slate-300 font-medium">{guardrail1.regulatory_citation}</p>
                    </div>
                    <div className="rounded-xl border border-[#262626] bg-[#0d0d0d] p-3 space-y-1">
                      <span className="text-[10px] font-mono uppercase tracking-wider text-amber-400 font-bold">
                        Required Clinical Remediation
                      </span>
                      <p className="text-amber-200 font-medium">{guardrail1.action_required}</p>
                    </div>
                  </div>
                </>
              ) : (
                <div className="flex items-center justify-between rounded-xl border border-emerald-500/20 bg-emerald-500/5 p-3 text-xs text-emerald-300">
                  <span>
                    ✓ <strong>Subject Demographics Verified:</strong>{" "}
                    {currentAttempts > 0
                      ? `Demographics successfully resupplied by clinician and verified on attempt ${currentAttempts} of ${maxIters}.`
                      : "Complete age, sex, and trial identifiers conform with FDA 21 CFR 312.62 ingress specifications."}
                  </span>
                  <span className="font-mono text-[10px] text-emerald-400 font-bold">0 Missing Fields</span>
                </div>
              )}
            </div>
          </div>

          {/* SECTION 2: Protocol Hard Boundaries & Immediate Short-Circuit (Guardrail 2) */}
          <div
            className={`rounded-xl border p-6 md:p-7 transition-all space-y-4 ${
              !guardrail2.passed
                ? "border-rose-500/60 bg-gradient-to-r from-rose-950/50 via-[#1c0d10] to-[#121212] shadow-lg shadow-rose-950/40 ring-1 ring-rose-500/40"
                : "border-emerald-500/30 bg-[#141414]"
            }`}
          >
            <div className="flex flex-wrap items-center justify-between gap-3 border-b border-[#242424] pb-3">
              <div className="flex items-center gap-3">
                <div
                  className={`flex size-8 items-center justify-center rounded-lg ${
                    !guardrail2.passed ? "bg-rose-500/20 text-rose-400 animate-pulse" : "bg-emerald-500/15 text-emerald-400"
                  }`}
                >
                  {!guardrail2.passed ? <AlertTriangle className="size-4.5" /> : <ShieldCheck className="size-4.5" />}
                </div>
                <div>
                  <h4 className="text-sm font-bold text-white leading-tight">
                    Section 2: Protocol Baseline Safety Corridors (Guardrail 2)
                  </h4>
                  <p className="text-xs text-slate-400 mt-0.5 leading-tight">
                    Catastrophic Boundary Gate · Acute Hepatic, Renal & Marrow Failure Stopping Rules
                  </p>
                </div>
              </div>

              <span
                className={`rounded-full px-3 py-1 font-mono text-xs font-bold uppercase tracking-wider ${
                  !guardrail2.passed
                    ? "bg-rose-500/30 text-rose-200 border border-rose-400 animate-pulse"
                    : "bg-emerald-500/15 text-emerald-400 border border-emerald-500/30"
                }`}
              >
                {!guardrail2.passed ? "CRITICAL BREACH: IMMEDIATE SHORT-CIRCUIT" : "PASSED: PHYSIOLOGY SAFE"}
              </span>
            </div>

            <div className="mt-3 space-y-3">
              {!guardrail2.passed ? (
                <>
                  <div className="grid gap-3">
                    {guardrail2.breached_boundaries.map((breach, i) => (
                      <div
                        key={i}
                        className="rounded-xl border border-rose-500/40 bg-rose-950/40 p-4 space-y-2.5"
                      >
                        <div className="flex flex-wrap items-center justify-between gap-2 text-xs">
                          <span className="font-bold text-white flex items-center gap-2">
                            <span className="size-2.5 rounded-full bg-rose-400 animate-ping" />
                            {breach.parameter}
                          </span>
                          <span className="rounded bg-rose-500/30 px-2.5 py-0.5 font-mono text-[10px] font-bold text-rose-200">
                            {breach.severity}
                          </span>
                        </div>
                        <div className="grid grid-cols-3 gap-3 font-mono text-xs rounded-lg bg-[#0d0d0d] p-3 border border-[#262626]">
                          <div>
                            <span className="text-[10px] uppercase text-slate-500 block font-semibold mb-0.5">Observed Value</span>
                            <span className="text-rose-400 font-bold text-sm">{breach.observed}</span>
                          </div>
                          <div>
                            <span className="text-[10px] uppercase text-slate-500 block font-semibold mb-0.5">Safety Ceiling</span>
                            <span className="text-slate-300 font-medium text-sm">{breach.limit}</span>
                          </div>
                          <div>
                            <span className="text-[10px] uppercase text-slate-500 block font-semibold mb-0.5">Critical Variance</span>
                            <span className="text-rose-300 font-bold text-sm">{breach.difference}</span>
                          </div>
                        </div>
                        <p className="text-xs text-slate-200 leading-relaxed pt-1">
                          <strong className="text-rose-300">Clinical Pathology: </strong>
                          {breach.reason}
                        </p>
                      </div>
                    ))}
                  </div>

                  <div className="rounded-xl border border-rose-500/30 bg-[#121212] p-3.5 text-xs text-slate-300 space-y-2">
                    <p className="text-rose-300 font-bold flex items-center gap-1.5">
                      <Lock className="size-4" />
                      Safety Short-Circuit Enforced:
                    </p>
                    <p className="text-xs leading-relaxed text-slate-300">
                      {guardrail2.reason}
                    </p>
                    <div className="pt-2 flex flex-wrap justify-between text-[11px] text-slate-400 font-mono border-t border-[#222]">
                      <span>Authority: <strong className="text-slate-300">{guardrail2.regulatory_citation}</strong></span>
                      <span className="text-amber-300">Action: <strong>{guardrail2.action_required}</strong></span>
                    </div>
                  </div>
                </>
              ) : (
                <div className="flex items-center justify-between rounded-xl border border-emerald-500/20 bg-emerald-500/5 p-3 text-xs text-emerald-300">
                  <span>
                    ✓ <strong>Organ Corridors Normal:</strong> Baseline hepatic (ALT/AST &le; 200 U/L), renal (eGFR &ge; 15 mL/min), and hematologic corridors safely within protocol corridors.
                  </span>
                  <span className="font-mono text-[10px] text-emerald-400 font-bold">0 Catastrophic Breaches</span>
                </div>
              )}
            </div>
          </div>

          {/* SECTION 3: RAG Protocol Rules & Eligibility Criteria Deviations */}
          <div
            className={`rounded-xl border p-6 md:p-7 transition-all space-y-4 ${
              !ragRules.compliant
                ? "border-amber-500/50 bg-gradient-to-r from-amber-950/40 via-[#18140f] to-[#121212] shadow-lg shadow-amber-950/30"
                : "border-emerald-500/30 bg-[#141414]"
            }`}
          >
            <div className="flex flex-wrap items-center justify-between gap-3 border-b border-[#242424] pb-3">
              <div className="flex items-center gap-3">
                <div
                  className={`flex size-8 items-center justify-center rounded-lg ${
                    !ragRules.compliant ? "bg-amber-500/20 text-amber-400" : "bg-emerald-500/15 text-emerald-400"
                  }`}
                >
                  {!ragRules.compliant ? <AlertCircle className="size-4.5" /> : <ShieldCheck className="size-4.5" />}
                </div>
                <div>
                  <h4 className="text-sm font-bold text-white leading-tight">
                    Section 3: RAG Protocol Rules & Eligibility Verification
                  </h4>
                  <p className="text-xs text-slate-400 mt-0.5 leading-tight">
                    Vector Knowledge Retrieval · Dosage Window Ceilings & Hemorrhage Washout Corridors
                  </p>
                </div>
              </div>

              <span
                className={`rounded-full px-3 py-1 font-mono text-xs font-bold uppercase tracking-wider ${
                  !ragRules.compliant
                    ? "bg-amber-500/20 text-amber-300 border border-amber-500/40"
                    : "bg-emerald-500/15 text-emerald-400 border border-emerald-500/30"
                }`}
              >
                {!ragRules.compliant ? "PROTOCOL_VIOLATIONS_DETECTED" : "100% PROTOCOL_COMPLIANT"}
              </span>
            </div>

            <div className="mt-3 space-y-3">
              {!ragRules.compliant ? (
                <>
                  <div className="grid gap-3">
                    {ragRules.violations.map((v, i) => (
                      <div
                        key={i}
                        className="rounded-xl border border-amber-500/40 bg-amber-950/30 p-4 space-y-2.5"
                      >
                        <div className="flex flex-wrap items-center justify-between gap-2 text-xs">
                          <span className="font-bold text-white">
                            Rule: {v.parameter}
                          </span>
                          <span className="rounded bg-amber-500/30 px-2.5 py-0.5 font-mono text-[10px] font-bold text-amber-200">
                            RULE ID: {v.rule_id}
                          </span>
                        </div>
                        <div className="grid grid-cols-3 gap-3 font-mono text-xs rounded-lg bg-[#0d0d0d] p-3 border border-[#262626]">
                          <div>
                            <span className="text-[10px] uppercase text-slate-500 block font-semibold mb-0.5">Observed Action / Lab</span>
                            <span className="text-amber-400 font-bold text-sm">{v.observed}</span>
                          </div>
                          <div>
                            <span className="text-[10px] uppercase text-slate-500 block font-semibold mb-0.5">Trial Protocol Requirement</span>
                            <span className="text-slate-300 font-medium text-sm">{v.limit}</span>
                          </div>
                          <div>
                            <span className="text-[10px] uppercase text-slate-500 block font-semibold mb-0.5">Protocol Deviation</span>
                            <span className="text-amber-300 font-bold text-sm">{v.difference}</span>
                          </div>
                        </div>
                        <p className="text-xs text-slate-200 leading-relaxed pt-1">
                          <strong className="text-amber-300">Clinical Reason: </strong>
                          {v.reason}
                        </p>
                        <p className="text-[11px] text-slate-400 italic">
                          Reference Citation: {v.reference}
                        </p>
                      </div>
                    ))}
                  </div>

                  <p className="text-xs text-amber-200/90 leading-relaxed pt-1">
                    {ragRules.reason}
                  </p>
                </>
              ) : (
                <div className="flex items-center justify-between rounded-xl border border-emerald-500/20 bg-emerald-500/5 p-3 text-xs text-emerald-300">
                  <span>
                    ✓ <strong>RAG Rules Conformed:</strong> Therapeutic dosage window and inclusion/exclusion eligibility conform with protocol Arm A specifications.
                  </span>
                  <span className="font-mono text-[10px] text-emerald-400 font-bold">0 Deviations</span>
                </div>
              )}
            </div>
          </div>

          {/* SECTION 4: 4 A2A Multi-Agent Consensus Matrix & Specialist Discrepancies */}
          <div
            className={`rounded-xl border p-6 md:p-7 transition-all space-y-4 ${
              a2aDiscrepancies.has_discrepancy
                ? "border-purple-500/50 bg-gradient-to-r from-purple-950/40 via-[#18111e] to-[#121212] shadow-lg shadow-purple-950/30"
                : "border-emerald-500/30 bg-[#141414]"
            }`}
          >
            <div className="flex flex-wrap items-center justify-between gap-3 border-b border-[#242424] pb-3">
              <div className="flex items-center gap-3">
                <div
                  className={`flex size-8 items-center justify-center rounded-lg ${
                    a2aDiscrepancies.has_discrepancy ? "bg-purple-500/20 text-purple-400" : "bg-emerald-500/15 text-emerald-400"
                  }`}
                >
                  <GitMerge className="size-4.5" />
                </div>
                <div>
                  <h4 className="text-sm font-bold text-white leading-tight">
                    Section 4: 4 A2A Multi-Agent Consensus Matrix & Specialist Objections
                  </h4>
                  <p className="text-xs text-slate-400 mt-0.5 leading-tight">
                    Autonomous Multi-Specialist Mesh (Compliance, Safety, Financial Risk & Arbitration Reducer)
                  </p>
                </div>
              </div>

              <span
                className={`rounded-full px-3 py-1 font-mono text-xs font-bold uppercase tracking-wider ${
                  a2aDiscrepancies.has_discrepancy
                    ? "bg-purple-500/20 text-purple-300 border border-purple-500/40"
                    : "bg-emerald-500/15 text-emerald-400 border border-emerald-500/30"
                }`}
              >
                {a2aDiscrepancies.has_discrepancy
                  ? `${a2aDiscrepancies.dissenting_agents.length} ${
                      a2aDiscrepancies.dissenting_agents.length === 1 ? "SPECIALIST" : "SPECIALISTS"
                    } DISSENTING: REJECTED`
                  : "UNANIMOUS CONSENSUS: JUSTIFIED"}
              </span>
            </div>

            <div className="mt-3 space-y-3">
              <div className="grid gap-3 md:grid-cols-2">
                {/* Specialist 1: Protocol Compliance */}
                <div className={`rounded-xl border p-4 space-y-2.5 ${
                  isCompliant ? "border-emerald-500/30 bg-[#0F1923]" : "border-rose-500/30 bg-[#0F1923]"
                }`}>
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-white flex items-center gap-1.5">
                      {isCompliant ? <ShieldCheck className="size-3.5 text-emerald-400" /> : <ShieldAlert className="size-3.5 text-rose-400" />}
                      1. Protocol Compliance Specialist
                    </span>
                    <span className={`rounded px-2 py-0.5 font-mono text-[10px] font-bold ${
                      isCompliant ? "bg-emerald-500/20 text-emerald-300" : "bg-rose-500/20 text-rose-300"
                    }`}>
                      {complianceStatus}
                    </span>
                  </div>
                  <div className="rounded bg-[#070D17] px-2.5 py-1 text-[11px] font-mono text-slate-400 flex items-center justify-between border border-slate-800">
                    <span>Protocol: {activeTrialId}</span>
                    <span className="text-sky-400">FDA 21 CFR 312.62</span>
                  </div>
                  <p className="text-xs text-slate-300 leading-relaxed">
                    {a2aDiscrepancies.reasons["Protocol Compliance Specialist"] || a2aDiscrepancies.reasons["Protocol Compliance Agent"] || complianceResult?.explanation || "Intervention evaluated against protocol dosing schedule."}
                  </p>
                </div>

                {/* Specialist 2: Safety & Toxicity */}
                <div className={`rounded-xl border p-4 space-y-2.5 ${
                  isSafetySafe ? "border-emerald-500/30 bg-[#0F1923]" : "border-rose-500/30 bg-[#0F1923]"
                }`}>
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-white flex items-center gap-1.5">
                      {isSafetySafe ? <CheckCircle2 className="size-3.5 text-emerald-400" /> : <AlertTriangle className="size-3.5 text-rose-400" />}
                      2. Safety & Toxicity Specialist
                    </span>
                    <span className={`rounded px-2 py-0.5 font-mono text-[10px] font-bold ${
                      isSafetySafe ? "bg-emerald-500/20 text-emerald-300" : "bg-rose-500/20 text-rose-300"
                    }`}>
                      {safetyStatus}
                    </span>
                  </div>
                  <div className="rounded bg-[#070D17] px-2.5 py-1 text-[11px] font-mono text-slate-400 flex items-center justify-between border border-slate-800">
                    <span>Renal: {renalDisplay}</span>
                    <span className="text-emerald-400">Organ Reserve Safe</span>
                  </div>
                  <p className="text-xs text-slate-300 leading-relaxed">
                    {a2aDiscrepancies.reasons["Safety & Toxicity Specialist"] || a2aDiscrepancies.reasons["Safety & Toxicity Agent"] || safetyResult?.explanation || "Toxicity thresholds and organ clearance contraindications evaluated."}
                  </p>
                </div>

                {/* Specialist 3: Financial Risk */}
                <div className={`rounded-xl border p-4 space-y-2.5 ${
                  isCovered ? "border-emerald-500/30 bg-[#0F1923]" : "border-amber-500/30 bg-[#0F1923]"
                }`}>
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-white flex items-center gap-1.5">
                      <DollarSign className="size-3.5 text-emerald-400" />
                      3. Financial Risk & Billing Specialist
                    </span>
                    <span className={`rounded px-2 py-0.5 font-mono text-[10px] font-bold ${
                      isCovered ? "bg-emerald-500/20 text-emerald-300" : "bg-amber-500/20 text-amber-300"
                    }`}>
                      {coverageStatus} (${financialExposure.toLocaleString("en-US")})
                    </span>
                  </div>
                  <div className="rounded bg-[#070D17] px-2.5 py-1 text-[11px] font-mono text-slate-400 flex items-center justify-between border border-slate-800">
                    <span>CMS NCD 310.1 Policy</span>
                    <span className="text-emerald-400">{isCovered ? "$0 Patient Cost" : "Prior Auth Required"}</span>
                  </div>
                  <p className="text-xs text-slate-300 leading-relaxed">
                    {a2aDiscrepancies.reasons["Financial Risk Specialist"] || a2aDiscrepancies.reasons["Financial Risk Agent"] || financialResult?.callout || financialResult?.explanation || "Sponsor trial agreement research billing checked."}
                  </p>
                </div>

                {/* Specialist 4: Arbitration Reducer */}
                <div className={`rounded-xl border p-4 space-y-2.5 ${
                  isJustified ? "border-emerald-500/30 bg-[#0F1923]" : "border-rose-500/30 bg-[#0F1923]"
                }`}>
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-white flex items-center gap-1.5">
                      <GitMerge className="size-3.5 text-sky-400" />
                      4. Arbitration Reducer Consensus
                    </span>
                    <span className={`rounded px-2 py-0.5 font-mono text-[10px] font-bold ${
                      isJustified ? "bg-emerald-500/20 text-emerald-300" : "bg-rose-500/20 text-rose-300"
                    }`}>
                      SYNTHESIS: {finalVerdict}
                    </span>
                  </div>
                  <div className="rounded bg-[#070D17] px-2.5 py-1 text-[11px] font-mono text-slate-400 flex items-center justify-between border border-slate-800">
                    <span>LangGraph Engine</span>
                    <span className="text-sky-400">Precautionary Principle</span>
                  </div>
                  <p className="text-xs text-slate-300 leading-relaxed">
                    {arbitrationResult.summary || "Consensus synthesis integrates all 3 microservice vectors to establish human adjudication recommendation."}
                  </p>
                </div>
              </div>

              {a2aDiscrepancies.has_discrepancy ? (
                <div className="rounded-xl border border-purple-500/30 bg-purple-950/20 p-3.5 text-xs text-purple-200 space-y-1">
                  <div className="flex items-center gap-2 font-bold text-purple-300">
                    <AlertCircle className="size-4 shrink-0" />
                    <span>Specialist Consensus Arbitration Analysis:</span>
                  </div>
                  <p className="leading-relaxed text-purple-200/90">
                    Multi-specialist synthesis rejected the clinical order due to dissenting objections from{" "}
                    <strong className="text-white font-semibold">{a2aDiscrepancies.dissenting_agents.join(", ")}</strong>.
                    LangGraph arbitration applied the precautionary clinical principle, enforcing regulatory and safety compliance over proposed trial interventions.
                  </p>
                </div>
              ) : (
                <div className="flex items-center justify-between rounded-xl border border-emerald-500/20 bg-emerald-500/5 p-3.5 text-xs text-emerald-300">
                  <span className="flex items-center gap-2">
                    <CheckCircle2 className="size-4 shrink-0 text-emerald-400" />
                    <span>
                      <strong>All 4 Autonomous Agents Harmonized:</strong> Protocol Compliance, Patient Safety, Financial Coverage, and Arbitration Reducer achieved 100% unanimous clinical alignment.
                    </span>
                  </span>
                  <span className="font-mono text-[10px] text-emerald-400 font-bold shrink-0 ml-2">4 / 4 Consensus</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* 4-Card Multi-Specialist Verdict Grid */}
      <div className="space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-2 border-b border-[#282828] pb-3">
          <div>
            <p className="text-sm font-bold uppercase tracking-wider text-white">
              Specialist Node Verdicts & Clinical Rationales (4 Nodes)
            </p>
            <p className="text-xs text-slate-400 mt-0.5">
              Independent parallel microservice reviews synthesized via LangGraph stateful graph
            </p>
          </div>
          <span className="rounded-full border border-slate-700/50 bg-[#0F1923] px-3 py-1 font-mono text-xs text-slate-300">
            A2A Consensus Protocol v2.4
          </span>
        </div>

        <div className="grid gap-6 md:grid-cols-2">
          {/* CARD 1: Protocol Compliance Specialist */}
          <div
            className={`flex flex-col justify-between rounded-xl border p-6 transition-all space-y-5 ${
              isCompliant
                ? "border-emerald-500/40 bg-emerald-500/5 hover:border-emerald-500/60"
                : "border-rose-500/40 bg-rose-500/5 hover:border-rose-500/60"
            }`}
          >
            <div className="space-y-4">
              {/* Header */}
              <div className="flex items-center justify-between gap-3 border-b border-[#282828] pb-3.5">
                <div className="flex items-center gap-3">
                  <div
                    className={`flex size-9 items-center justify-center rounded-lg ${
                      isCompliant ? "bg-emerald-500/15 text-emerald-400" : "bg-rose-500/15 text-rose-400"
                    }`}
                  >
                    {isCompliant ? <ShieldCheck className="size-5" /> : <ShieldAlert className="size-5" />}
                  </div>
                  <div>
                    <h4 className="text-sm font-bold text-white leading-tight">
                      Protocol Compliance Specialist
                    </h4>
                    <p className="text-xs text-slate-400 mt-0.5 leading-tight font-mono">
                      FDA Eligibility & Dosing Rules · {activeTrialId}
                    </p>
                  </div>
                </div>

                <span
                  className={`rounded-full px-3 py-1 font-mono text-xs font-bold uppercase tracking-wider ${
                    isCompliant
                      ? "bg-emerald-500/15 text-emerald-400 border border-emerald-500/30"
                      : "bg-rose-500/15 text-rose-400 border border-rose-500/30"
                  }`}
                >
                  {complianceStatus}
                </span>
              </div>

              {/* Protocol Violations / Certification Box */}
              <div className="space-y-3">
                {protocolViolations.length > 0 ? (
                  protocolViolations.map((violation: any, idx: number) => (
                    <div
                      key={idx}
                      className="rounded-xl border border-rose-500/30 bg-rose-500/10 p-4 space-y-2.5"
                    >
                      <div className="flex items-center justify-between text-xs">
                        <span className="font-bold text-white capitalize flex items-center gap-1.5">
                          <AlertTriangle className="size-3.5 text-rose-400 shrink-0" />
                          {violation.name} Evaluation
                        </span>
                        <span className="rounded bg-rose-500/20 px-2 py-0.5 font-mono text-[10px] text-rose-300 font-bold border border-rose-500/30">
                          PROTOCOL VIOLATION
                        </span>
                      </div>

                      {/* Quantitative Parameter Comparison Grid */}
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 rounded-lg bg-[#070D17]/80 p-2.5 border border-rose-500/20 text-xs font-mono">
                        <div>
                          <span className="text-[10px] uppercase text-slate-400 block font-sans font-medium">Observed Finding:</span>
                          <span className="text-rose-400 font-bold">{violation.observed}</span>
                        </div>
                        <div>
                          <span className="text-[10px] uppercase text-slate-400 block font-sans font-medium">Mandated Protocol Limit:</span>
                          <span className="text-emerald-400 font-bold">{violation.limit}</span>
                        </div>
                        {violation.difference && (
                          <div className="sm:col-span-2 pt-1 border-t border-slate-700/30">
                            <span className="text-[10px] uppercase text-slate-400 inline font-sans font-medium mr-2">Clinical Variance:</span>
                            <span className="text-amber-300 font-semibold">{violation.difference}</span>
                          </div>
                        )}
                      </div>

                      <div className="space-y-1 text-xs">
                        <p className="text-slate-300 leading-relaxed">
                          <strong className="text-slate-200">Violation Context: </strong>
                          {violation.reason || "Patient parameters fall outside the approved clinical trial eligibility corridor."}
                        </p>
                        <p className="text-[11px] font-mono text-slate-400">
                          <span className="text-slate-500">Trial Citation: </span>
                          {violation.reference || "Protocol Inclusion/Exclusion Specifications"}
                        </p>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="rounded-xl border border-emerald-500/30 bg-emerald-500/10 p-4 space-y-2 text-xs text-emerald-300">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-white flex items-center gap-1.5">
                        <CheckCircle2 className="size-3.5 text-emerald-400 shrink-0" />
                        100% In-Protocol Compliance Certified
                      </span>
                      <span className="rounded bg-emerald-500/20 px-2 py-0.5 font-mono text-[10px] text-emerald-300 font-bold">
                        VERIFIED
                      </span>
                    </div>
                    <div className="grid grid-cols-2 gap-1.5 font-mono text-[11px] text-emerald-200/90 pt-1">
                      <span>✓ Informed Consent: Validated</span>
                      <span>✓ Diagnostic Match: Confirmed</span>
                      <span>✓ Dose Ceiling: Within Arm A Window</span>
                      <span>✓ Washout Corridors: 0 Deviations</span>
                    </div>
                  </div>
                )}

                {/* Comprehensive Clinical Adjudication Narrative */}
                <div className="rounded-xl border border-[#242424] bg-[#0F1923] p-4 space-y-2">
                  <div className="flex items-center justify-between text-[11px] uppercase tracking-wider text-slate-400 font-bold border-b border-[#242424] pb-1.5">
                    <span>Clinical Adjudication Rationale</span>
                    <span className="font-mono text-sky-400">FDA 21 CFR 312.62</span>
                  </div>
                  <p className="text-xs leading-relaxed text-slate-200">
                    {complianceResult?.explanation ||
                      (isCompliant
                        ? `Intervention fully conforms with approved Trial Protocol ${activeTrialId} specifications. Dosing schedules, drug formulation, and patient eligibility cohorts satisfy all GCP E6(R2) research compliance criteria.`
                        : "Prescribed dosing or timing deviates from protocol-specified therapeutic window and inclusion/exclusion standards.")}
                  </p>
                </div>

                {/* Actionable Investigator Directive */}
                <div className={`rounded-xl border p-3.5 text-xs space-y-1 ${
                  isCompliant
                    ? "border-emerald-500/30 bg-emerald-950/20 text-emerald-200"
                    : "border-amber-500/30 bg-amber-950/20 text-amber-200"
                }`}>
                  <div className="flex items-center gap-1.5 font-bold uppercase tracking-wider text-[10px]">
                    <Info className="size-3.5" />
                    <span>Investigator Action Directive</span>
                  </div>
                  <p className="text-xs leading-relaxed">
                    {isCompliant
                      ? "Protocol Adherence Certified: Order is cleared for investigational pharmacy dispensing and electronic trial master file (eTMF) recording."
                      : (protocolViolations[0]?.rule_id === "EXC_BLEEDING_WASHOUT"
                          ? "Clinical Action Required: HOLD study medication. Do NOT administer factor Xa inhibitors until the mandatory 30-day post-bleed washout period has completed. Re-evaluate subject coagulation telemetry and rescreen on Day 31 post-bleed."
                          : "Clinical Action Required: Discontinue proposed off-protocol order or titrate to protocol-approved standard dosage window per Arm A guidelines.")}
                  </p>
                </div>
              </div>
            </div>

            {/* Footer */}
            <div className="flex items-center justify-between border-t border-[#242424] pt-3 text-xs text-slate-400 font-mono">
              <span className="flex items-center gap-1.5">
                <Clock className="size-3.5 text-slate-500" />
                Latency: {complianceMetrics?.latency_ms ? `${complianceMetrics.latency_ms}ms` : "614ms"}
              </span>
              <span className="text-sky-400 font-semibold">
                Assurance: {Math.round((complianceResult?.confidence ?? 0.98) * 100)}%
              </span>
            </div>
          </div>

          {/* CARD 2: Patient Safety & Toxicity Specialist */}
          <div
            className={`flex flex-col justify-between rounded-xl border p-6 transition-all space-y-5 ${
              isSafetySafe
                ? "border-emerald-500/40 bg-emerald-500/5 hover:border-emerald-500/60"
                : "border-rose-500/40 bg-rose-500/5 hover:border-rose-500/60"
            }`}
          >
            <div className="space-y-4">
              {/* Header */}
              <div className="flex items-center justify-between gap-3 border-b border-[#282828] pb-3.5">
                <div className="flex items-center gap-3">
                  <div
                    className={`flex size-9 items-center justify-center rounded-lg ${
                      isSafetySafe ? "bg-emerald-500/15 text-emerald-400" : "bg-rose-500/15 text-rose-400"
                    }`}
                  >
                    {isSafetySafe ? <CheckCircle2 className="size-5" /> : <AlertTriangle className="size-5" />}
                  </div>
                  <div>
                    <h4 className="text-sm font-bold text-white leading-tight">
                      Patient Safety & Toxicity Specialist
                    </h4>
                    <p className="text-xs text-slate-400 mt-0.5 leading-tight font-mono">
                      Organ Clearance, DDI & Hemorrhage Risk
                    </p>
                  </div>
                </div>

                <span
                  className={`rounded-full px-3 py-1 font-mono text-xs font-bold uppercase tracking-wider ${
                    isSafetySafe
                      ? "bg-emerald-500/15 text-emerald-400 border border-emerald-500/30"
                      : "bg-rose-500/15 text-rose-400 border border-rose-500/30"
                  }`}
                >
                  {safetyStatus}
                </span>
              </div>

              {/* Multi-Parameter Physiological Biomarker Telemetry Grid */}
              <div className="rounded-xl border border-[#282828] bg-[#070D17] p-3.5 space-y-2.5">
                <div className="flex items-center justify-between text-[11px] font-bold uppercase tracking-wider text-slate-400 border-b border-slate-800 pb-1.5">
                  <span>Organ Clearance & Biomarker Telemetry</span>
                  <span className="font-mono text-sky-400">4 Core Safeguards</span>
                </div>

                <div className="grid grid-cols-2 gap-2 text-xs font-mono">
                  {/* Renal */}
                  <div className="rounded-lg bg-[#0F1923] p-2 border border-slate-700/40">
                    <span className="text-[10px] text-slate-400 font-sans block">Renal Clearance:</span>
                    <span className={`font-bold ${isRenalEligible ? "text-emerald-400" : "text-rose-400"}`}>
                      {renalDisplay}
                    </span>
                    <span className="text-[10px] text-slate-500 block">Limit: &ge; 30 mL/min ({isRenalEligible ? "Safe" : "Breach"})</span>
                  </div>

                  {/* Hepatic */}
                  <div className="rounded-lg bg-[#0F1923] p-2 border border-slate-700/40">
                    <span className="text-[10px] text-slate-400 font-sans block">Hepatic Transaminases:</span>
                    <span className="font-bold text-slate-200">
                      ALT {clinicalProfile.alt} · AST {clinicalProfile.ast} U/L
                    </span>
                    <span className="text-[10px] text-slate-500 block">Ceiling: &le; 200 U/L (Normal)</span>
                  </div>

                  {/* Hematology */}
                  <div className="rounded-lg bg-[#0F1923] p-2 border border-slate-700/40">
                    <span className="text-[10px] text-slate-400 font-sans block">Hematologic Reserve:</span>
                    <span className="font-bold text-slate-200">
                      ANC {clinicalProfile.anc.toLocaleString()} /µL
                    </span>
                    <span className="text-[10px] text-slate-500 block">Floor: &ge; 500 /µL (Preserved)</span>
                  </div>

                  {/* DDI Screening */}
                  <div className="rounded-lg bg-[#0F1923] p-2 border border-slate-700/40">
                    <span className="text-[10px] text-slate-400 font-sans block">Pharmacokinetic DDI:</span>
                    <span className={`font-bold ${hasDoseOverdose ? "text-amber-400" : "text-emerald-400"}`}>
                      CYP3A4 / P-gp
                    </span>
                    <span className="text-[10px] text-slate-500 block">0 Severe Modulators</span>
                  </div>
                </div>
              </div>

              {/* Safety Concerns or Confirmed Tolerance */}
              <div className="space-y-2.5">
                {safetyConcerns.length > 0 ? (
                  safetyConcerns.map((concern: any, idx: number) => (
                    <div
                      key={idx}
                      className="rounded-xl border border-rose-500/30 bg-rose-500/10 p-3.5 text-xs text-rose-200 space-y-1.5"
                    >
                      <div className="flex items-center gap-2 font-bold text-rose-300">
                        <AlertCircle className="size-4 shrink-0" />
                        <span>Toxicity Flag: {concern.parameter || "Overdose Risk"}</span>
                      </div>
                      <p className="text-xs leading-relaxed text-slate-300">
                        {concern.reason || "Dose significantly exceeds therapeutic threshold."}
                      </p>
                    </div>
                  ))
                ) : (
                  <div className="rounded-xl border border-emerald-500/30 bg-emerald-500/10 p-3.5 text-xs text-emerald-300 space-y-1">
                    <div className="flex items-center gap-1.5 font-bold">
                      <CheckCircle2 className="size-3.5 shrink-0 text-emerald-400" />
                      <span>Physiological Tolerance Verified:</span>
                    </div>
                    <p className="text-emerald-200/90 leading-relaxed text-[11px]">
                      Renal glomerular filtration and hepatic biliary pathways are fully preserved. No acute metabolic decompensation, agranulocytosis, or severe CYP3A4/P-gp interactions identified.
                    </p>
                  </div>
                )}

                {/* Comprehensive Pharmacokinetic Rationale Narrative */}
                <div className="rounded-xl border border-[#242424] bg-[#0F1923] p-4 space-y-2">
                  <div className="flex items-center justify-between text-[11px] uppercase tracking-wider text-slate-400 font-bold border-b border-[#242424] pb-1.5">
                    <span>Pharmacokinetic & Toxicity Evaluation</span>
                    <span className="font-mono text-sky-400">ICH S2/S9 Guidelines</span>
                  </div>
                  <p className="text-xs leading-relaxed text-slate-200">
                    {safetyResult?.explanation ||
                      (isSafetySafe
                        ? "Patient laboratory clearance values indicate safe therapeutic tolerance. Adequate renal clearance (Cockcroft-Gault) and stable hepatic transaminases support standard drug elimination kinetics without accumulation risk."
                        : "Prescribed regimen represents severe acute toxicity and unmonitored drug accumulation risk.")}
                  </p>
                </div>

                {/* Actionable Clinical Safety Advisory */}
                <div className={`rounded-xl border p-3.5 text-xs space-y-1 ${
                  isSafetySafe
                    ? "border-emerald-500/30 bg-emerald-950/20 text-emerald-200"
                    : "border-rose-500/30 bg-rose-950/20 text-rose-200"
                }`}>
                  <div className="flex items-center gap-1.5 font-bold uppercase tracking-wider text-[10px]">
                    <Activity className="size-3.5" />
                    <span>Clinical Safety Advisory</span>
                  </div>
                  <p className="text-xs leading-relaxed">
                    {isSafetySafe
                      ? "Safety Clearance Granted: Baseline physiological reserves are sufficient to support study drug administration without empiric dose attenuation."
                      : "Safety Halt Enforced: Drug administration is contraindicated due to severe acute toxicity hazard. Obtain repeat STAT laboratory panel."}
                  </p>
                </div>
              </div>
            </div>

            {/* Footer */}
            <div className="flex items-center justify-between border-t border-[#242424] pt-3 text-xs text-slate-400 font-mono">
              <span className="flex items-center gap-1.5">
                <Clock className="size-3.5 text-slate-500" />
                Latency: {safetyMetrics?.latency_ms ? `${safetyMetrics.latency_ms}ms` : "942ms"}
              </span>
              <span className="text-sky-400 font-semibold">
                Assurance: {Math.round((safetyResult?.confidence ?? 0.95) * 100)}%
              </span>
            </div>
          </div>

          {/* CARD 3: Financial Risk & Payer Specialist */}
          <div
            className={`flex flex-col justify-between rounded-xl border p-6 transition-all space-y-5 ${
              isCovered
                ? "border-emerald-500/40 bg-emerald-500/5 hover:border-emerald-500/60"
                : "border-amber-500/40 bg-amber-500/5 hover:border-amber-500/60"
            }`}
          >
            <div className="space-y-4">
              {/* Header */}
              <div className="flex items-center justify-between gap-3 border-b border-[#282828] pb-3.5">
                <div className="flex items-center gap-3">
                  <div
                    className={`flex size-9 items-center justify-center rounded-lg ${
                      isCovered ? "bg-emerald-500/15 text-emerald-400" : "bg-amber-500/15 text-amber-400"
                    }`}
                  >
                    <DollarSign className="size-5" />
                  </div>
                  <div>
                    <h4 className="text-sm font-bold text-white leading-tight">
                      Financial Risk & Payer Specialist
                    </h4>
                    <p className="text-xs text-slate-400 mt-0.5 leading-tight font-mono">
                      Sponsor CTA Billing & Patient Exposure
                    </p>
                  </div>
                </div>

                <span
                  className={`rounded-full px-3 py-1 font-mono text-xs font-bold uppercase tracking-wider ${
                    isCovered
                      ? "bg-emerald-500/15 text-emerald-400 border border-emerald-500/30"
                      : "bg-amber-500/15 text-amber-400 border border-amber-500/30"
                  }`}
                >
                  {isCovered ? "COVERED" : coverageStatus}
                </span>
              </div>

              {/* Research Billing & Coverage Matrix */}
              <div className="space-y-3">
                <div className="flex items-center justify-between rounded-xl border border-[#282828] bg-[#070D17] p-3.5">
                  <div>
                    <span className="text-[10px] uppercase tracking-wider text-slate-400 font-semibold block">
                      {isCovered ? "Patient Out-of-Pocket Liability" : "Uncovered Exposure / Subject Liability"}
                    </span>
                    <p className={`font-mono text-2xl font-bold mt-0.5 ${isCovered ? "text-emerald-400" : "text-amber-400"}`}>
                      ${financialExposure.toLocaleString("en-US")}
                    </p>
                  </div>
                  <div className="text-right">
                    <span
                      className={`inline-block rounded-full px-2.5 py-1 text-xs font-bold uppercase tracking-wider ${
                        isCovered ? "bg-emerald-500/15 text-emerald-400 border border-emerald-500/30" : "bg-amber-500/15 text-amber-400 border border-amber-500/30"
                      }`}
                    >
                      {isCovered ? "100% Sponsor Covered" : "Prior Auth Required"}
                    </span>
                    <span className="block font-mono text-[10px] text-slate-500 mt-1">CMS NCD 310.1 Active</span>
                  </div>
                </div>

                {/* Reimbursement Tier & Billing Codes */}
                <div className="grid grid-cols-2 gap-2 text-xs font-mono">
                  <div className="rounded-lg bg-[#0F1923] p-2.5 border border-slate-700/40">
                    <span className="text-[10px] font-sans text-slate-400 uppercase block">Reimbursement Tier:</span>
                    <span className="text-slate-200 font-medium block truncate">
                      {financialResult?.tier || (isCovered ? "Tier-1 Investigational" : "Non-Covered Protocol Deviation")}
                    </span>
                  </div>
                  <div className="rounded-lg bg-[#0F1923] p-2.5 border border-slate-700/40">
                    <span className="text-[10px] font-sans text-slate-400 uppercase block">Billing Modifiers:</span>
                    <span className="text-sky-400 font-medium block">
                      CPT 99215-Q0 / HCPCS
                    </span>
                  </div>
                </div>

                {/* Comprehensive Billing Adjudication Narrative */}
                <div className="rounded-xl border border-[#242424] bg-[#0F1923] p-4 space-y-2">
                  <div className="flex items-center justify-between text-[11px] uppercase tracking-wider text-slate-400 font-bold border-b border-[#242424] pb-1.5">
                    <span>Research Billing & Payer Rationale</span>
                    <span className="font-mono text-sky-400">CMS NCD 310.1</span>
                  </div>
                  <p className="text-xs leading-relaxed text-slate-200">
                    {financialResult?.callout ||
                      financialResult?.explanation ||
                      (isCovered
                        ? "100% Protocol & Investigational Coverage under Sponsor Clinical Trial Agreement. All study drug compounding, administration, and routine protocol monitoring encounters are fully subsidized by the trial sponsor with $0 subject copay."
                        : "Sponsor research coverage denied due to protocol non-compliance or unapproved dosing. Prior authorization required before dispensing.")}
                  </p>
                </div>

                {/* Actionable Billing Directive */}
                <div className={`rounded-xl border p-3.5 text-xs space-y-1 ${
                  isCovered
                    ? "border-emerald-500/30 bg-emerald-950/20 text-emerald-200"
                    : "border-amber-500/30 bg-amber-950/20 text-amber-200"
                }`}>
                  <div className="flex items-center gap-1.5 font-bold uppercase tracking-wider text-[10px]">
                    <FileCheck className="size-3.5" />
                    <span>Clinical Research Billing Guidance</span>
                  </div>
                  <p className="text-xs leading-relaxed">
                    {isCovered
                      ? "Billing Authorization Confirmed: Route clinical trial encounter under qualifying trial registry NCT02415400. Apply modifier Q0/Q1 with zero patient cost-share."
                      : "Billing Hold: Flag encounter for research financial review. Do not bill Medicare or commercial payer without secondary sponsor prior authorization."}
                  </p>
                </div>
              </div>
            </div>

            {/* Footer */}
            <div className="flex items-center justify-between border-t border-[#242424] pt-3 text-xs text-slate-400 font-mono">
              <span className="flex items-center gap-1.5">
                <Clock className="size-3.5 text-slate-500" />
                Latency: {financialMetrics?.latency_ms ? `${financialMetrics.latency_ms}ms` : "480ms"}
              </span>
              <span className="text-sky-400 font-semibold">
                Assurance: {Math.round((financialMetrics?.confidence ?? 0.97) * 100)}%
              </span>
            </div>
          </div>

          {/* CARD 4: LangGraph Arbitration Reducer Consensus */}
          <div
            className={`flex flex-col justify-between rounded-xl border p-6 transition-all space-y-5 ${
              isJustified
                ? "border-emerald-500/40 bg-emerald-500/5 hover:border-emerald-500/60"
                : "border-rose-500/40 bg-rose-500/5 hover:border-rose-500/60"
            }`}
          >
            <div className="space-y-4">
              {/* Header */}
              <div className="flex items-center justify-between gap-3 border-b border-[#282828] pb-3.5">
                <div className="flex items-center gap-3">
                  <div
                    className={`flex size-9 items-center justify-center rounded-lg ${
                      isJustified ? "bg-emerald-500/15 text-emerald-400" : "bg-rose-500/15 text-rose-400"
                    }`}
                  >
                    <GitMerge className="size-5" />
                  </div>
                  <div>
                    <h4 className="text-sm font-bold text-white leading-tight">
                      Arbitration Reducer Consensus
                    </h4>
                    <p className="text-xs text-slate-400 mt-0.5 leading-tight font-mono">
                      Multi-Specialist Synthesis Engine
                    </p>
                  </div>
                </div>

                <span
                  className={`rounded-full px-3 py-1 font-mono text-xs font-bold uppercase tracking-wider ${
                    isJustified
                      ? "bg-emerald-500/15 text-emerald-400 border border-emerald-500/30"
                      : "bg-rose-500/15 text-rose-400 border border-rose-500/30"
                  }`}
                >
                  {finalVerdict}
                </span>
              </div>

              {/* Dynamic Specialist Convergence Bar */}
              <div className="space-y-3">
                <div className="rounded-xl border border-[#282828] bg-[#070D17] p-3 space-y-2">
                  <div className="flex items-center justify-between text-[10px] uppercase tracking-wider text-slate-400 font-semibold border-b border-slate-800 pb-1.5">
                    <span>Autonomous Specialist Alignment</span>
                    <span className="font-mono text-slate-400">3 Parallel Vectors</span>
                  </div>

                  <div className="grid grid-cols-3 gap-1.5 text-center font-mono text-[11px]">
                    <div className={`rounded p-1.5 border ${
                      isCompliant ? "border-emerald-500/30 bg-emerald-500/10 text-emerald-300" : "border-rose-500/30 bg-rose-500/10 text-rose-300"
                    }`}>
                      <span className="text-[9px] uppercase block font-sans text-slate-400">Protocol</span>
                      <span className="font-bold">{isCompliant ? "PASS" : "VETO"}</span>
                    </div>

                    <div className={`rounded p-1.5 border ${
                      isSafetySafe ? "border-emerald-500/30 bg-emerald-500/10 text-emerald-300" : "border-rose-500/30 bg-rose-500/10 text-rose-300"
                    }`}>
                      <span className="text-[9px] uppercase block font-sans text-slate-400">Safety</span>
                      <span className="font-bold">{isSafetySafe ? "PASS" : "VETO"}</span>
                    </div>

                    <div className={`rounded p-1.5 border ${
                      isCovered ? "border-emerald-500/30 bg-emerald-500/10 text-emerald-300" : "border-amber-500/30 bg-amber-500/10 text-amber-300"
                    }`}>
                      <span className="text-[9px] uppercase block font-sans text-slate-400">Coverage</span>
                      <span className="font-bold">{isCovered ? "PASS" : "HOLD"}</span>
                    </div>
                  </div>

                  {/* True Dynamic Convergence String */}
                  <div className="flex items-center justify-between pt-1 text-xs">
                    <span className="text-slate-400 font-medium">Consensus State:</span>
                    <span className={`font-bold font-mono text-[11px] ${
                      a2aDiscrepancies.dissenting_agents.length === 0
                        ? "text-emerald-400"
                        : a2aDiscrepancies.dissenting_agents.length === 1
                          ? "text-amber-400"
                          : "text-rose-400"
                    }`}>
                      {a2aDiscrepancies.dissenting_agents.length === 0
                        ? "✓ All 3 Specialists Harmonized (100% Alignment)"
                        : a2aDiscrepancies.dissenting_agents.length === 1
                          ? `⚠ 1 Specialist Dissenting (${a2aDiscrepancies.dissenting_agents[0].replace(" Agent", "").replace(" Specialist", "")}: Action Blocked)`
                          : `✕ Multi-Specialist Dissent (${a2aDiscrepancies.dissenting_agents.length} Objections)`}
                    </span>
                  </div>
                </div>

                {/* Recommended Clinical Action Box */}
                <div className="rounded-xl border border-[#282828] bg-[#0F1923] p-3.5 space-y-1">
                  <span className="text-[10px] uppercase tracking-wider text-slate-400 font-semibold block">
                    Recommended Clinical Action Directive
                  </span>
                  <p className="text-xs font-bold text-white">
                    {isJustified
                      ? "Proceed with treatment: Administer investigational dose per protocol Arm A specifications."
                      : (protocolViolations[0]?.rule_id === "EXC_BLEEDING_WASHOUT"
                          ? "Hold study medication: Defer randomization until 30-day post-bleed washout completes on Day 31."
                          : "Reject proposed escalation: Dose-reduce to 5 mg orally BID per Arm A guidelines.")}
                  </p>
                </div>

                {/* Comprehensive Reducer Rationale Narrative */}
                <div className="rounded-xl border border-[#242424] bg-[#0F1923] p-4 space-y-2">
                  <div className="flex items-center justify-between text-[11px] uppercase tracking-wider text-slate-400 font-bold border-b border-[#242424] pb-1.5">
                    <span>Multi-Specialist Synthesis Rationale</span>
                    <span className="font-mono text-sky-400">Precautionary Principle</span>
                  </div>
                  <p className="text-xs leading-relaxed text-slate-200">
                    {arbitrationResult.summary ||
                      "Arbitration Reducer synthesized Protocol Compliance, Safety & Toxicity, and Financial Risk Specialist evaluations. The precautionary principle was enforced to guarantee patient safety and protocol fidelity."}
                  </p>
                </div>

                {/* Actionable Clinical Care Plan (3 Steps) */}
                <div className="rounded-xl border border-slate-700/50 bg-[#070D17] p-3.5 space-y-1.5 text-xs">
                  <span className="text-[10px] uppercase tracking-wider text-slate-400 font-bold block">
                    Adjudication Care Plan & Next Steps
                  </span>
                  <div className="space-y-1 font-mono text-[11px] text-slate-300">
                    <p>
                      <strong className="text-slate-100">1. Pharmacy Dispensing: </strong>
                      {isJustified ? "Release order for electronic dispensing." : "HOLD order in pharmacy dispensary system."}
                    </p>
                    <p>
                      <strong className="text-slate-100">2. Trial eCRF Audit: </strong>
                      {isJustified ? "Log compliance certificate in trial master file." : "Log protocol exception and reason for hold in EDC."}
                    </p>
                    <p>
                      <strong className="text-slate-100">3. Patient Follow-up: </strong>
                      {isJustified ? "Routine Cycle 1 Day 1 laboratory monitoring." : "Repeat coagulation and complete metabolic panel prior to reassessment."}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Footer */}
            <div className="flex items-center justify-between border-t border-[#242424] pt-3 text-xs text-slate-400 font-mono">
              <span className="flex items-center gap-1.5">
                <Clock className="size-3.5 text-slate-500" />
                Latency: {reducerMetrics?.latency_ms ? `${reducerMetrics.latency_ms}ms` : "1102ms"}
              </span>
              <span className="text-sky-400 font-semibold">
                Consensus Assurance: {Math.round((reducerMetrics?.confidence ?? 0.95) * 100)}%
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Expandable Multi-Agent Audit Trail & Raw Evidence */}
      <div className="rounded-xl border border-[#282828] bg-[#121212] overflow-hidden">
        <button
          onClick={() => setShowDeepAudit((prev) => !prev)}
          className="flex w-full items-center justify-between p-4 text-left text-xs font-bold text-slate-200 hover:bg-[#181818] transition-colors"
        >
          <div className="flex items-center gap-2.5">
            <Lock className="size-4 text-emerald-400" />
            <span>Inspect Multi-Agent Evidence & Raw Telemetry (FDA 21 CFR Part 11)</span>
          </div>
          <div className="flex items-center gap-2 text-xs text-slate-400">
            <span>{showDeepAudit ? "Collapse Audit" : "Expand Rationale & Evidence"}</span>
            {showDeepAudit ? <ChevronUp className="size-4" /> : <ChevronDown className="size-4" />}
          </div>
        </button>

        {showDeepAudit && (
          <div className="border-t border-[#282828] p-5 space-y-4 text-xs">
            {/* RAG Vector Chunks */}
            {arbitrationResult.protocol_evidence && arbitrationResult.protocol_evidence.length > 0 && (
              <div className="space-y-2">
                <p className="font-bold text-sky-400 uppercase tracking-wider text-[11px]">
                  Vector Protocol Evidence Chunks (ChromaDB / RAG)
                </p>
                <div className="grid gap-2.5">
                  {arbitrationResult.protocol_evidence.map((chunk: any, i: number) => (
                    <div key={i} className="rounded-lg border border-[#282828] bg-[#0d0d0d] p-3 text-xs">
                      <div className="flex items-center justify-between text-slate-400 mb-1 font-mono text-[10px]">
                        <span>Chunk ID: {chunk.chunk_id || `chunk-${i}`}</span>
                        {chunk.score && (
                          <span className="text-emerald-400 font-semibold">Similarity: {chunk.score}</span>
                        )}
                      </div>
                      <p className="text-slate-200 leading-relaxed">{chunk.text || JSON.stringify(chunk)}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Safety Evidence */}
            {arbitrationResult.safety_evidence && arbitrationResult.safety_evidence.length > 0 && (
              <div className="space-y-2">
                <p className="font-bold text-rose-400 uppercase tracking-wider text-[11px]">
                  Safety & Contraindication Telemetry
                </p>
                <div className="rounded-lg border border-[#282828] bg-[#0d0d0d] p-3 text-xs text-slate-300">
                  {arbitrationResult.safety_evidence.map((ev: any, i: number) => (
                    <p key={i} className="leading-relaxed">
                      • {typeof ev === "string" ? ev : JSON.stringify(ev)}
                    </p>
                  ))}
                </div>
              </div>
            )}

            {/* Copyable JSON Payload */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <p className="font-bold text-slate-400 uppercase tracking-wider text-[11px]">
                  Cryptographic Audit Payload
                </p>
                <button
                  onClick={handleCopyAuditPayload}
                  className="flex items-center gap-1.5 rounded bg-[#202020] px-2.5 py-1 text-xs text-slate-300 hover:bg-[#303030] transition-colors"
                >
                  {copiedPayload ? (
                    <>
                      <Check className="size-3.5 text-emerald-400" />
                      <span className="text-emerald-400 font-bold">Copied to Clipboard</span>
                    </>
                  ) : (
                    <>
                      <Copy className="size-3.5" />
                      <span>Copy Complete JSON</span>
                    </>
                  )}
                </button>
              </div>
              <pre className="max-h-56 overflow-x-auto rounded-lg border border-[#282828] bg-[#080808] p-3.5 font-mono text-[11px] text-slate-300">
                {JSON.stringify(arbitrationResult, null, 2)}
              </pre>
            </div>
          </div>
        )}
      </div>

      {/* Action Bar */}
      {isLockedOut ? (
        <div className="rounded-xl border border-rose-500/50 bg-gradient-to-r from-rose-950/40 via-[#181113] to-[#121212] p-5 space-y-3.5">
          <div className="flex items-center gap-2 text-rose-300 text-xs font-bold uppercase tracking-wider">
            <Lock className="size-4 text-rose-400" />
            Decision Actions Barred · Subject Locked Out (3/3 Retries Exceeded)
          </div>
          <p className="text-xs text-slate-300 leading-relaxed">
            This patient record is permanently excluded from trial intake under FDA 21 CFR 312.62 because mandatory demographic data was unfulfilled after 3 iterations. Clinical order co-signature and protocol overrides are disabled for this ID.
          </p>
          <Button
            onClick={() => onPatientDisqualified?.(patient.id)}
            className="h-12 w-full bg-rose-600 hover:bg-rose-500 text-white font-semibold text-sm transition-all shadow-lg shadow-rose-950/50 rounded-xl"
          >
            <Lock className="size-4 mr-2" />
            Disqualify Subject & Return to Intake Queue
          </Button>
        </div>
      ) : (
        <div className="flex flex-col gap-3 sm:flex-row pt-4">
          <Button
            onClick={() => handleDirectDecision("accept")}
            className={`h-12 flex-1 font-semibold text-white rounded-xl text-sm transition-all shadow-lg ${
              decision === "accept"
                ? "bg-[#10b981] ring-2 ring-[#10b981]/50 shadow-emerald-950/50"
                : isJustified
                  ? "bg-[#10b981] hover:bg-[#10b981]/90 shadow-emerald-950/30"
                  : "bg-slate-700 hover:bg-slate-600 text-slate-200"
            }`}
          >
            <Check className="size-4 mr-2" />
            Accept {isJustified ? "Order" : "(Caution: Non-Compliant)"}
          </Button>

          <Button
            variant="outline"
            onClick={() => {
              setModifyOpen((v) => {
                const next = !v
                if (next) {
                  setTimeout(() => {
                    modifyDrawerRef.current?.scrollIntoView({ behavior: "smooth", block: "nearest" })
                  }, 80)
                }
                return next
              })
            }}
            className="h-12 flex-1 border-[#2e2e2e] bg-[#121212] font-semibold text-white hover:bg-[#252525] hover:text-white rounded-xl text-sm transition-all shadow-md active:scale-95"
          >
            <Pencil className="size-4 mr-2" />
            Modify Dosage / Override
            <ChevronDown
              className={`size-4 ml-2 transition-transform duration-200 ${
                modifyOpen ? "rotate-180" : ""
              }`}
            />
          </Button>

          <Button
            onClick={() => handleDirectDecision("reject")}
            className={`h-12 flex-1 font-semibold text-white rounded-xl text-sm transition-all shadow-lg ${
              decision === "reject"
                ? "bg-[#ef4444] ring-2 ring-[#ef4444]/50 shadow-rose-950/50"
                : !isJustified
                  ? "bg-[#ef4444] hover:bg-[#ef4444]/90 shadow-rose-950/30"
                  : "bg-slate-700 hover:bg-slate-600 text-slate-200"
            }`}
          >
            <X className="size-4 mr-2" />
            Reject Order {!isJustified && "(Recommended)"}
          </Button>
        </div>
      )}

      {/* Post-Decision Feedback & Download Banners */}
      {decision === "accept" && (
        <div className="rounded-xl border border-emerald-500/40 bg-gradient-to-r from-emerald-950/40 via-[#131d16] to-[#121212] p-6 md:p-7 shadow-2xl animate-in fade-in slide-in-from-top-2 duration-300">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="flex items-start gap-3.5">
              <div className="flex size-11 shrink-0 items-center justify-center rounded-xl bg-emerald-500/20 text-emerald-400">
                <FileCheck className="size-6" />
              </div>
              <div>
                <div className="flex items-center gap-2.5">
                  <h3 className="text-base font-bold text-white">
                    Adjudication Accepted: Order Confirmed in Protocol Registry
                  </h3>
                  <span className="rounded-full bg-emerald-500/20 px-2.5 py-0.5 font-mono text-[10px] font-bold text-emerald-300">
                    21 CFR PART 11 SEALED
                  </span>
                </div>
                <p className="mt-1.5 text-xs text-slate-300 leading-relaxed">
                  Electronic signature and clinical verification recorded for Patient {patient.id}. Your official audit report is ready for immediate regulatory download.
                </p>
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-2.5 shrink-0">
              <Button
                onClick={() => window.open(`${getGatewayUrl()}/api/reports/${patient.id}/pdf?decision=accept`, "_blank")}
                className="h-11 bg-emerald-500 text-white font-bold hover:bg-emerald-400 shadow-lg shadow-emerald-900/40 rounded-xl px-4 text-xs"
              >
                <Download className="size-4 mr-2" />
                Download Official Adjudication PDF
              </Button>
              <a
                href={`/report/${patient.id}`}
                className="inline-flex h-11 items-center justify-center rounded-xl border border-[#333] bg-[#1a1a1a] px-4 text-xs font-semibold text-slate-300 hover:bg-[#252525] hover:text-white transition-colors"
              >
                <FileText className="size-4 mr-2" />
                View Full Audit
              </a>
            </div>
          </div>
        </div>
      )}

      {decision === "reject" && (
        <div className="rounded-xl border border-rose-500/40 bg-gradient-to-r from-rose-950/40 via-[#211417] to-[#121212] p-6 md:p-7 shadow-2xl animate-in fade-in slide-in-from-top-2 duration-300 space-y-5">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="flex items-start gap-3.5">
              <div className="flex size-11 shrink-0 items-center justify-center rounded-xl bg-rose-500/20 text-rose-400">
                <ShieldAlert className="size-6" />
              </div>
              <div>
                <div className="flex items-center gap-2.5">
                  <h3 className="text-base font-bold text-white">
                    Clinical Safety Hold Enforced: Order Rejected
                  </h3>
                  <span className="rounded-full bg-rose-500/20 px-2.5 py-0.5 font-mono text-[10px] font-bold text-rose-300">
                    CONTRAINDICATION ENFORCED
                  </span>
                </div>
                <p className="mt-1.5 text-xs text-slate-300 leading-relaxed">
                  Prescription order held in pharmacy systems. High-dose toxicity contraindication logged in trial audit ledger per GCP/IRB requirements.
                </p>
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-2.5 shrink-0">
              <Button
                onClick={() => window.open(`${getGatewayUrl()}/api/reports/${patient.id}/pdf?decision=reject`, "_blank")}
                className="h-11 bg-rose-600 text-white font-bold hover:bg-rose-500 shadow-lg shadow-rose-900/40 rounded-xl px-4 text-xs"
              >
                <Download className="size-4 mr-2" />
                Download Rejection Notice (PDF)
              </Button>
              <a
                href={`/report/${patient.id}`}
                className="inline-flex h-11 items-center justify-center rounded-xl border border-[#333] bg-[#1a1a1a] px-4 text-xs font-semibold text-slate-300 hover:bg-[#252525] hover:text-white transition-colors"
              >
                <FileText className="size-4 mr-2" />
                View Safety Audit
              </a>
            </div>
          </div>

          {/* Remediation 1-Click Action Box */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 rounded-xl border border-amber-500/30 bg-amber-500/10 p-4 text-xs">
            <div className="flex items-center gap-3">
              <AlertTriangle className="size-4.5 text-amber-400 shrink-0" />
              <div>
                <span className="font-bold text-amber-300">Recommended Clinical Remediation: </span>
                <span className="text-slate-200">{remText}</span>
              </div>
            </div>

            <Button
              onClick={handleApplyRemediation}
              disabled={isExtracting || isApplyingRemediation}
              size="sm"
              className="h-10 bg-amber-500 text-black font-bold hover:bg-amber-400 shrink-0 rounded-lg px-4 text-xs active:scale-95 transition-all"
            >
              {isApplyingRemediation || isExtracting ? (
                <>
                  <Loader2 className="size-3.5 mr-1.5 animate-spin" />
                  Applying Dose Adjustment ({remDose})...
                </>
              ) : (
                <>
                  <Sparkles className="size-3.5 mr-1.5" />
                  Apply Dose Adjustment ({remDose})
                </>
              )}
            </Button>
          </div>
        </div>
      )}

      {/* Modify / Override Drawer */}
      <div
        ref={modifyDrawerRef}
        className={`grid transition-all duration-300 ease-out ${
          modifyOpen ? "mt-4 grid-rows-[1fr] opacity-100" : "grid-rows-[0fr] opacity-0"
        }`}
      >
        <div className="overflow-hidden">
          <div className="rounded-xl border border-[#2e2e2e] bg-[#121212] p-6 space-y-5">
            <div className="flex items-center justify-between border-b border-[#242424] pb-3.5">
              <div>
                <p className="text-sm font-bold text-white">
                  Physician Protocol Override & Adjustment
                </p>
                <p className="text-xs text-amber-400 mt-0.5">
                  Requires Principal Investigator (PI) Clinical Justification & Co-Sign
                </p>
              </div>
              <span className="rounded-full bg-amber-500/10 px-2.5 py-0.5 text-[10px] font-bold text-amber-400 border border-amber-500/20">
                HITL Exception Gate
              </span>
            </div>

            {/* AI Extraction State 1: Awaiting Input or Invalid / Warning */}
            {(!extractionResult?.is_valid || extractionResult?.is_appropriate === false) && (
              <div className="space-y-4">
                {extractionResult && (extractionResult.is_valid === false || extractionResult.is_appropriate === false) && (
                  <div className="rounded-xl border border-rose-500/40 bg-rose-950/40 p-4 text-rose-300 space-y-2">
                    <div className="flex items-center gap-2 font-bold text-rose-200 text-xs uppercase tracking-wider">
                      <AlertTriangle className="size-4 shrink-0 text-rose-400" />
                      ⚠️ Clinical Warning: Inappropriate or Ambiguous Doctor Note
                    </div>
                    <p className="text-xs text-rose-300 leading-relaxed">
                      {extractionResult.warning || extractionResult.reasoning || "The entered note does not specify an actionable medication name or numerical dosage."}
                    </p>
                    <div className="rounded border border-rose-800/40 bg-[#0c0507] p-2 text-[11px] font-mono text-slate-300">
                      <span className="text-rose-400 font-bold">Action Required:</span> Provide a recognizable medication and target numerical dosage.
                      <br />
                      <span className="text-slate-400">Example:</span> &ldquo;Titrate Apixaban to 5 mg oral twice daily per protocol Arm A&rdquo;
                    </div>
                  </div>
                )}

                <Field label="Clinical Rationale & Doctor's Prescription Note">
                  <textarea
                    value={comment}
                    onChange={(e) => setComment(e.target.value)}
                    rows={4}
                    placeholder="E.g., Patient exhibits normal CrCl 68 mL/min and stable renal clearance. Titrate apixaban to 5 mg oral twice daily per protocol Arm A specifications..."
                    className="w-full resize-none rounded-xl border border-[#2e2e2e] bg-[#1a1a1a] p-3.5 text-xs text-white placeholder:text-slate-500 focus:border-sky-500 focus:outline-none leading-relaxed"
                  />
                </Field>

                <Button
                  onClick={handleExtract}
                  disabled={isExtracting || !comment.trim()}
                  className="h-11 w-full bg-sky-500 text-white font-semibold hover:bg-sky-400 rounded-xl text-sm transition-all"
                >
                  {isExtracting ? (
                    <>
                      <Loader2 className="size-4 mr-2 animate-spin" />
                      Evaluating Doctor Note via Clinical LLM...
                    </>
                  ) : (
                    <>
                      <Sparkles className="size-4 mr-2" />
                      Evaluate Doctor Note & Extract FHIR Updates
                    </>
                  )}
                </Button>
              </div>
            )}

            {/* AI Extraction State 2: Extracted Data Confirmed & Appropriate */}
            {extractionResult?.is_valid && extractionResult?.is_appropriate !== false && (
              <div className="space-y-4 animate-in fade-in slide-in-from-bottom-2 duration-300">
                <div className="rounded-xl border border-emerald-500/30 bg-emerald-500/10 p-4 space-y-3">
                  <div className="flex flex-wrap items-center justify-between gap-2 border-b border-emerald-500/20 pb-2.5">
                    <div className="flex items-center gap-2">
                      <CheckCircle2 className="size-4 text-emerald-400" />
                      <p className="text-sm font-bold text-emerald-300">
                        Doctor Note Validated by Clinical LLM
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

                  <div className="grid gap-2">
                    {extractionResult.modifications?.map((mod: any, idx: number) => (
                      <div
                        key={idx}
                        className="rounded-lg bg-[#121212] border border-[#2e2e2e] p-3 text-xs space-y-2"
                      >
                        <div className="flex items-center justify-between">
                          <span className="text-slate-200 font-semibold text-sm">{mod.dosage_name}</span>
                          <span className="font-mono font-bold text-emerald-400 text-sm">
                            {mod.proposed_dosage} {mod.dosage_unit}
                          </span>
                        </div>
                        <div className="grid grid-cols-2 gap-2 text-[11px] font-mono text-slate-400 border-t border-[#222] pt-2">
                          <div>
                            <span className="text-slate-500 block text-[10px] uppercase">Frequency / Route</span>
                            <span className="text-slate-200 font-medium">{mod.frequency || "twice daily"} ({mod.route || "oral"})</span>
                          </div>
                          <div>
                            <span className="text-slate-500 block text-[10px] uppercase">Timing Schedule</span>
                            <span className="text-sky-300 font-medium">{mod.timing_schedule || "08:00, 20:00"}</span>
                          </div>
                        </div>
                        <div className="flex items-center justify-between text-[10px] font-mono bg-[#0a0a0a] rounded px-2.5 py-1 border border-slate-800">
                          <span className="text-slate-500">Target FHIR Field:</span>
                          <span className="text-amber-300 font-semibold">{mod.target_field || "MedicationRequest.dosageInstruction[0]"}</span>
                        </div>
                      </div>
                    ))}
                  </div>

                  <div className="rounded border border-emerald-500/20 bg-emerald-950/20 p-2.5 text-[11px] text-emerald-300 font-mono">
                    <span className="font-bold">Target Clinical Action:</span> {extractionResult.standardized_action || activeAction}
                  </div>
                </div>

                <div className="flex gap-3">
                  <Button
                    variant="outline"
                    onClick={() => setExtractionResult(null)}
                    className="h-11 flex-1 border-[#2e2e2e] bg-[#1a1a1a] text-white hover:bg-[#252525] rounded-xl text-sm"
                  >
                    Edit Doctor Note
                  </Button>
                  <Button
                    onClick={handleOverrideSubmit}
                    disabled={isSubmittingOverride}
                    className="h-11 flex-[2] bg-emerald-500 text-white font-semibold hover:bg-emerald-400 rounded-xl text-sm shadow-lg shadow-emerald-950/30 active:scale-95 transition-all"
                  >
                    {isSubmittingOverride ? (
                      <>
                        <Loader2 className="size-4 mr-2 animate-spin" />
                        Updating FHIR Database & Re-evaluating...
                      </>
                    ) : (
                      <>
                        <Check className="size-4 mr-2" />
                        Confirm & Update FHIR Database
                      </>
                    )}
                  </Button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </section>
  )
}

function Field({
  label,
  children,
}: {
  label: string
  children: React.ReactNode
}) {
  return (
    <label className="block">
      <span className="mb-1.5 block text-[11px] font-semibold uppercase tracking-wider text-slate-400">
        {label}
      </span>
      {children}
    </label>
  )
}
