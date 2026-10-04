import { TrialGuardLogo } from "@/components/trialguard-logo"
import { getGatewayUrl } from "@/lib/api-config"

type Report = {
    report_id?: string
    saved_at?: string
    patient_id: string
    trial_id?: string
    final_decision?: string
    decision_timestamp?: string
    final_verdict?: string
    summary?: string
    original_prescribed_action?: string
    final_prescribed_action?: string
    clinician_justification?: string | null
    protocol_compliance_result?: Record<string, unknown>
    safety_result?: Record<string, unknown>
    financial_result?: Record<string, unknown>
    protocol_evidence?: Array<Record<string, unknown>>
    safety_evidence?: Array<Record<string, unknown>>
    report_history?: Array<Record<string, unknown>>
    agent_metrics?: Record<string, Record<string, unknown>>
    iteration_count?: number
}

export default async function ReportPage({ params }: { params: Promise<{ patientId: string }> }) {
    const { patientId } = await params
    const baseUrl = getGatewayUrl()
    let report: Report | undefined = undefined

    try {
        const controller = new AbortController()
        const timeoutId = setTimeout(() => controller.abort(), 3500)
        const response = await fetch(`${baseUrl}/api/reports/${encodeURIComponent(patientId)}`, {
            cache: "no-store",
            signal: controller.signal,
        }).catch(() => null)
        clearTimeout(timeoutId)

        if (response && response.ok) {
            const payload = await response.json()
            report = (payload.reports ?? []).at(-1) as Report | undefined
        }
    } catch (err) {
        console.warn(`Report fetch failed at ${baseUrl}:`, err)
    }

    return (
        <main className="min-h-screen bg-[#121212] px-4 py-8 text-white md:px-8">
            <div className="mx-auto max-w-6xl space-y-6">
                <header className="rounded-2xl border border-[#2e2e2e] bg-[#181818] p-6 md:p-8 space-y-6 shadow-2xl">
                    <div className="flex flex-wrap items-center justify-between gap-4 border-b border-[#282828] pb-4">
                        <TrialGuardLogo className="h-8 w-auto" showSubtitle />
                        <a href="/" className="inline-flex items-center gap-1.5 rounded-lg border border-[#333] bg-[#121212] px-3.5 py-1.5 text-xs text-slate-300 hover:bg-[#222] hover:text-white transition-colors">
                            &larr; Back to Adjudication Console
                        </a>
                    </div>
                    <div className="flex flex-wrap items-end justify-between gap-4">
                        <div>
                            <span className="text-[11px] font-semibold uppercase tracking-wider text-sky-400 font-mono">
                                21 CFR Part 11 Audit Trail
                            </span>
                            <h1 className="text-3xl font-bold text-white tracking-tight mt-1">Official Clinical Adjudication Report</h1>
                            <p className="mt-1 font-mono text-sm text-slate-400">Patient {patientId} · Trial Protocol {report?.trial_id ?? "NCT02415400"}</p>
                        </div>
                        <div className="flex flex-wrap items-center gap-3">
                            <StatusBadge value={report?.final_verdict ?? "REPORT_UNAVAILABLE"} />
                            <a
                                href={`/api/reports/${encodeURIComponent(patientId)}/pdf`}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="inline-flex items-center gap-2 rounded-xl bg-emerald-600 px-4 py-2.5 text-xs font-bold text-white hover:bg-emerald-500 shadow-lg shadow-emerald-950/40 transition-all"
                            >
                                <svg className="size-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                </svg>
                                Download Official PDF (21 CFR Part 11)
                            </a>
                        </div>
                    </div>
                </header>

                {!report ? (
                    <section className="rounded-xl border border-[#f59e0b]/30 bg-[#1e1e1e] p-6 text-sm text-slate-300">
                        No finalized report is available. An Accept or Reject decision must be recorded first.
                    </section>
                ) : (
                    <>
                        <section className="grid gap-5 lg:grid-cols-[1.4fr_0.6fr]">
                            <ReportSection title="Arbitration Summary">
                                <p className="text-base leading-7 text-slate-200">{report.summary ?? "No summary was returned."}</p>
                            </ReportSection>
                            <ReportSection title="Decision Record">
                                <Detail label="Decision" value={report.final_decision} />
                                <Detail label="Timestamp" value={report.decision_timestamp} />
                                <Detail label="Iteration" value={String(report.iteration_count ?? 0)} />
                            </ReportSection>
                        </section>

                        <section className="grid gap-5 md:grid-cols-2">
                            <ReportSection title="Prescribed Action">
                                <Detail label="Original" value={report.original_prescribed_action} />
                                <Detail label="Final" value={report.final_prescribed_action} />
                                <Detail label="Clinician justification" value={report.clinician_justification ?? "None provided"} />
                            </ReportSection>
                            <ReportSection title="Financial Risk Agent">
                                <JsonList data={report.financial_result} />
                            </ReportSection>
                        </section>

                        <section className="grid gap-5 md:grid-cols-2">
                            <AgentReport title="Protocol Compliance Agent" data={report.protocol_compliance_result} />
                            <AgentReport title="Safety & Toxicity Agent" data={report.safety_result} />
                        </section>

                        <section className="grid gap-5 md:grid-cols-2">
                            <ReportSection title="Protocol Evidence"><JsonList data={report.protocol_evidence} /></ReportSection>
                            <ReportSection title="Safety Evidence"><JsonList data={report.safety_evidence} /></ReportSection>
                        </section>

                        <ReportSection title="Agent Metrics"><JsonList data={report.agent_metrics} /></ReportSection>
                        <ReportSection title="Refinement History"><JsonList data={report.report_history} /></ReportSection>
                    </>
                )}
            </div>
        </main>
    )
}

function ReportSection({ title, children }: { title: string; children: React.ReactNode }) {
    return (
        <section className="rounded-xl border border-[#282828] bg-[#181818] p-6 space-y-4 shadow-md">
            <h2 className="text-xs font-bold uppercase tracking-wider text-slate-400 border-b border-[#242424] pb-2.5">
                {title}
            </h2>
            <div className="space-y-3 pt-1">{children}</div>
        </section>
    )
}

function AgentReport({ title, data }: { title: string; data?: Record<string, unknown> }) {
    return (
        <ReportSection title={title}>
            <div className="flex items-center justify-between gap-2 mb-2">
                <StatusBadge value={String(data?.compliance_status ?? data?.safety_status ?? "UNKNOWN")} />
            </div>
            <Detail label="Clinical Explanation" value={String(data?.explanation ?? "No explanation was returned.")} />
            <JsonList data={data?.violations ?? data?.concerns ?? data?.evidence} />
        </ReportSection>
    )
}

function Detail({ label, value }: { label: string; value?: string }) {
    return (
        <div className="space-y-1">
            <p className="text-[11px] font-mono uppercase tracking-wider text-slate-400 font-semibold">{label}</p>
            <p className="break-words text-sm leading-relaxed text-slate-200">{value ?? "Not available"}</p>
        </div>
    )
}

function StatusBadge({ value }: { value: string }) {
    const isPass = value.includes("PASSED") || value.includes("COMPLIANT") || value.includes("SAFE") || value.includes("JUSTIFIED")
    return (
        <span className={`inline-flex rounded-full px-3 py-1 font-mono text-xs font-bold uppercase tracking-wider border ${
            isPass
                ? "border-emerald-500/30 bg-emerald-500/10 text-emerald-400"
                : "border-rose-500/30 bg-rose-500/10 text-rose-400"
        }`}>
            {value.replaceAll("_", " ")}
        </span>
    )
}

function JsonList({ data }: { data: unknown }) {
    if (!data || (Array.isArray(data) && data.length === 0)) return <p className="text-xs text-slate-500 italic">None reported.</p>
    return (
        <pre className="max-h-96 overflow-auto rounded-xl border border-[#282828] bg-[#0d0d0d] p-3.5 font-mono text-xs leading-relaxed text-slate-300">
            {JSON.stringify(data, null, 2)}
        </pre>
    )
}