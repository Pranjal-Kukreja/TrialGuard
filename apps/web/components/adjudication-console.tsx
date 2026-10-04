"use client"

import { useEffect, useState } from "react"
import { ArrowLeft, Loader2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { DecisionGateway } from "@/components/decision-gateway"
import { ExecutionStream } from "@/components/execution-stream"
import { OrchestrationGraph } from "@/components/orchestration-graph"
import { TrialGuardLogo } from "@/components/trialguard-logo"
import { getGatewayUrl } from "@/lib/api-config"
import type { ArbitrationResult } from "@/app/actions"
import type { Patient } from "@/lib/clinical-data"

type Props = {
  patient: Patient
  protocol: string
  action: string
  onBack: () => void
  onDisqualifyPatient?: (patientId: string) => void
  onUpdatePatient?: (updatedPatient: Partial<Patient>) => void
}

export function AdjudicationConsole({
  patient,
  protocol,
  action,
  onBack,
  onDisqualifyPatient,
  onUpdatePatient,
}: Props) {
  const protocolId = protocol.split(" ")[0]

  const [currentAction, setCurrentAction] = useState(action)
  const [streamKey, setStreamKey] = useState(0)
  const [arbitrationResult, setArbitrationResult] = useState<ArbitrationResult | null>(null)
  const [runStarted, setRunStarted] = useState(false)

  useEffect(() => {
    setCurrentAction(action)
  }, [action])

  useEffect(() => {
    let cancelled = false
    setRunStarted(false)
    setArbitrationResult(null)

    const baseUrl = getGatewayUrl()
    fetch(`${baseUrl}/api/orchestrator/runs`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        patientId: patient.id,
        prescribed_action: currentAction,
        trial_id: protocolId,
        patient: {
          id: patient.id,
          patient_id: patient.id,
          name: patient.name,
          age: patient.age,
          sex: patient.sex,
          dob: patient.dob,
          cohort: patient.cohort,
          diagnosis: patient.diagnosis,
          creatinine: patient.creatinine,
          medications: patient.medications,
          clinical_data: patient.clinical_data,
        },
      }),
    })
      .then((response) => {
        if (!response.ok) throw new Error(`Failed to start orchestration run: ${response.status}`)
        if (!cancelled) setRunStarted(true)
      })
      .catch((error) => console.error("Failed to start orchestration run:", error))

    return () => {
      cancelled = true
    }
  }, [patient.id, currentAction, protocolId, streamKey])

  const handleRestartStream = (newAction?: string) => {
    if (newAction) {
      setCurrentAction(newAction)
      onUpdatePatient?.({ action: newAction })
    }
    setArbitrationResult(null)
    setRunStarted(true)
    setStreamKey(prev => prev + 1)
  }

  const handleArbitrationComplete = (result: ArbitrationResult) => {
    if (!result || (!result.final_verdict && !result.patientId && !result.patient_profile)) {
      return
    }
    if (result?.prescribed_action && result.prescribed_action !== currentAction) {
      setCurrentAction(result.prescribed_action)
      onUpdatePatient?.({ action: result.prescribed_action })
    }
    setArbitrationResult(result)
  }

  return (
    <div className="min-h-screen bg-[#121212] text-white">
      {/* Top context header */}
      <header className="border-b border-[#282828] bg-[#161616]/90 backdrop-blur-sm px-5 py-4 md:px-8">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <TrialGuardLogo className="h-8 w-auto" showSubtitle />
            <div className="hidden h-6 w-px bg-[#2e2e2e] md:block" />
            <Button
              variant="outline"
              size="sm"
              onClick={onBack}
              className="border-[#2e2e2e] bg-[#1e1e1e] text-slate-300 hover:bg-[#2a2a2a] hover:text-white text-xs"
            >
              <ArrowLeft className="size-3.5 mr-1.5" />
              Back to Patient Lookup
            </Button>
            <div className="hidden lg:block">
              <p className="text-xs font-semibold text-slate-300">
                Adjudication Console{" "}
                <span className="text-slate-500 font-normal">/ Multi-Agent Human-In-the-Loop Review</span>
              </p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2.5">
            <span className="rounded-full border border-[#2e2e2e] bg-[#1e1e1e] px-3 py-1 font-mono text-[11px] text-slate-300">
              PATIENT ID: <strong className="text-white font-bold">{patient.id}</strong>
            </span>
            <span className="rounded-full border border-[#2e2e2e] bg-[#1e1e1e] px-3 py-1 font-mono text-[11px] text-slate-300">
              PROTOCOL: <strong className="text-white font-bold">{protocolId}</strong>
            </span>
            <span className="hidden rounded-full border border-[#2e2e2e] bg-[#1e1e1e] px-3 py-1 text-[11px] text-slate-400 xl:inline">
              Site 04 · Massachusetts General
            </span>
            <div className="flex items-center gap-2 rounded-full border border-[#10b981]/30 bg-[#10b981]/10 px-3 py-1">
              <span className="relative flex size-2">
                <span className="absolute inline-flex size-full animate-ping rounded-full bg-[#10b981] opacity-75" />
                <span className="relative inline-flex size-2 rounded-full bg-[#10b981]" />
              </span>
              <span className="text-[11px] font-semibold text-[#10b981]">
                Live Telemetry
              </span>
            </div>
          </div>
        </div>

        <div className="mt-2.5 flex items-center justify-between border-t border-[#222] pt-2 text-xs text-slate-400">
          <p>
            Adjudication Queue: <span className="font-medium text-slate-300">{patient.cohort}</span> · 1 of 7 pending review
          </p>
          <span className="text-[11px] font-mono text-slate-500 hidden sm:inline">
            21 CFR Part 11 Active Session
          </span>
        </div>
      </header>

      <main className="mx-auto max-w-7xl space-y-8 p-6 md:p-8">
        {/* Full-width Expansive React Flow Block */}
        <OrchestrationGraph
          key={`orch-graph-${patient.id}`}
          patientId={patient.id}
          patient={{ ...patient, action: currentAction }}
          action={currentAction}
          arbitrationResult={arbitrationResult}
          restartSignal={streamKey}
          onArbitrationComplete={handleArbitrationComplete}
        />

        {!runStarted && !arbitrationResult && (
          <div className="flex items-center justify-center gap-2 rounded-xl border border-[#2e2e2e] bg-[#1e1e1e] p-6 text-sm text-slate-400">
            <Loader2 className="size-4 animate-spin text-[#3b82f6]" />
            Starting multi-agent clinical evaluation pipeline...
          </div>
        )}

        {arbitrationResult && (
          <DecisionGateway
            patient={{ ...patient, action: currentAction }}
            arbitrationResult={arbitrationResult}
            onRestartStream={handleRestartStream}
            onPatientUpdated={(updated) => {
              if (updated.action) {
                setCurrentAction(updated.action)
              }
              onUpdatePatient?.(updated)
            }}
            onPatientDisqualified={(id) => {
              onDisqualifyPatient?.(id)
              onBack()
            }}
          />
        )}

        {/* Detailed Chronological Execution Stream */}
        <ExecutionStream
          patientId={patient.id}
          action={currentAction}
          key={streamKey}
          onComplete={(result) => setArbitrationResult(result)}
        />
      </main>
    </div>
  )
}
