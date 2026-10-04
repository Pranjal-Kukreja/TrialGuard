import { NextResponse } from "next/server"

export const dynamic = "force-dynamic"

export async function POST(req: Request) {
  try {
    const payload = await req.json()
    const patientId = payload.patientId || payload.patient_id || "P034"
    return NextResponse.json({ status: "started", patientId })
  } catch (err: any) {
    return NextResponse.json({ error: err?.message || "Invalid payload" }, { status: 400 })
  }
}
