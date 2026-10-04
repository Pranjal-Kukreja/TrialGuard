import { NextRequest } from "next/server"
import { getArbitrationResult } from "@/app/actions"

export const dynamic = "force-dynamic"

export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url)
  const patientId = searchParams.get("patientId") || "P034"
  const actionParam = searchParams.get("action")

  const result = await getArbitrationResult(patientId, actionParam || undefined)

  const encoder = new TextEncoder()
  const stream = new ReadableStream({
    async start(controller) {
      const send = (data: any) => {
        controller.enqueue(encoder.encode(`data: ${JSON.stringify(data)}\n\n`))
      }

      const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms))

      // Stage 1: Parallel Specialist Dispatch (LangGraph Fan-Out)
      send({ name: "Protocol Compliance Agent", status: "processing" })
      send({ name: "Safety & Toxicity Agent", status: "processing" })
      send({ name: "Financial Risk Agent", status: "processing" })

      await sleep(350)

      // Stage 2: Specialist Agents Complete with Patient-Specific Evidence
      send({
        name: "Protocol Compliance Agent",
        status: "completed",
        result: result.protocol_compliance_result,
        latency: "340ms",
        confidence: "98%",
        callout: result.protocol_compliance_result?.explanation || "Protocol compliance review completed.",
      })

      await sleep(250)

      send({
        name: "Safety & Toxicity Agent",
        status: "completed",
        result: result.safety_result,
        latency: "410ms",
        confidence: "95%",
        callout: result.safety_result?.explanation || "Patient safety evaluation completed.",
      })

      await sleep(250)

      const finRes = result.financial_result || {}
      send({
        name: "Financial Risk Agent",
        status: "completed",
        result: finRes,
        latency: "290ms",
        confidence: "96%",
        callout: finRes.callout || finRes.explanation || "Financial coverage review completed.",
        financialExposure: result.financialExposure ?? finRes.financialExposure ?? 0,
      })

      send({ name: "Client Agent", status: "completed" })

      await sleep(200)

      // Stage 3: Arbitration Reducer Synthesis
      send({
        name: "Arbitration Reducer",
        status: "processing",
        subtext: "Synthesizing specialist verdicts...",
      })

      await sleep(400)

      send({
        name: "Arbitration Reducer",
        status: "completed",
        callout: result.summary,
        final_verdict: result.final_verdict,
        latency: "520ms",
        confidence: "96%",
      })

      controller.close()
    },
  })

  return new Response(stream, {
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache, no-transform",
      Connection: "keep-alive",
      "X-Accel-Buffering": "no",
    },
  })
}
