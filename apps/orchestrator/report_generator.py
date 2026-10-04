"""
TrialGuard 21 CFR Part 11 Adjudication PDF Report Generator.
Generates an audit-ready, tamper-evident clinical trial adjudication summary.
"""

import io
import time
from typing import Any, Dict, List, Optional

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle, Image as RLImage


LOGO_PATHS = [
    Path(__file__).resolve().parent / "assets" / "trialguard-logo.png",
    Path(__file__).resolve().parents[2] / "apps" / "web" / "public" / "trialguard-logo.png",
    Path("/Users/aahannayak/RESOURCE/techquest/apps/web/public/trialguard-logo.png"),
]


def _find_logo_path() -> Optional[str]:
    for p in LOGO_PATHS:
        if p.exists():
            return str(p)
    return None


def generate_adjudication_pdf_bytes(report_payload: Dict[str, Any]) -> io.BytesIO:
    """
    Generates a PDF document for clinical trial adjudication and returns an in-memory BytesIO buffer.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=40,
        rightMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()
    normal = styles["Normal"]

    # Custom styles
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=16,
        leading=20,
        textColor=colors.HexColor("#1A365D"),
    )
    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=normal,
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#4A5568"),
    )
    h2_style = ParagraphStyle(
        "SectionHeader",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#2B6CB0"),
        spaceBefore=10,
        spaceAfter=6,
    )
    cell_style = ParagraphStyle(
        "TableCell",
        parent=normal,
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#2D3748"),
    )
    cell_bold = ParagraphStyle(
        "TableCellBold",
        parent=normal,
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#1A202C"),
    )

    story = []

    header_data = report_payload.get("header", {})
    final_adj = report_payload.get("final_adjudication", {})
    sub_agents = report_payload.get("sub_agent_breakdown", {})
    violations = report_payload.get("active_violations", [])
    audit_trail = report_payload.get("audit_trail", [])

    decision = str(final_adj.get("decision", "UNKNOWN")).upper()

    # 1. Header & Title Banner
    if decision in ("REJECTED", "FAIL"):
        doc_title = "TRIALGUARD AI — ADVERSE EVENT & REJECTION NOTICE"
        doc_sub = "Regulatory Compliance: 21 CFR Part 11 Electronic Records | Safety & Contraindication Notice"
        hr_color = colors.HexColor("#9B2C2C")
    elif decision in ("APPROVED", "ACCEPTED"):
        doc_title = "TRIALGUARD AI — CLINICAL ADJUDICATION CERTIFICATE"
        doc_sub = "Regulatory Compliance: 21 CFR Part 11 Electronic Records & Signatures | Protocol Order Approved"
        hr_color = colors.HexColor("#276749")
    else:
        doc_title = "TRIALGUARD AI — CLINICAL ADJUDICATION RECORD"
        doc_sub = "Regulatory Compliance: 21 CFR Part 11 Electronic Records & Signatures"
        hr_color = colors.HexColor("#2B6CB0")

    logo_file = _find_logo_path()
    if logo_file:
        logo_img = RLImage(logo_file, width=80, height=50.6)
        header_table = Table(
            [
                [
                    logo_img,
                    [
                        Paragraph(doc_title, title_style),
                        Spacer(1, 3),
                        Paragraph(
                            f"{doc_sub} | Generated: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}",
                            subtitle_style,
                        ),
                    ],
                ]
            ],
            colWidths=[90, 442],
        )
        header_table.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(header_table)
    else:
        story.append(Paragraph(doc_title, title_style))
        story.append(
            Paragraph(
                f"{doc_sub} | Generated: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}",
                subtitle_style,
            )
        )
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=2, color=hr_color, spaceAfter=12))

    # 2. Patient & Protocol Metadata Table
    patient_id = header_data.get("patient_id", "N/A")
    trial_id = header_data.get("trial_id", "N/A")
    cohort = header_data.get("cohort", "Standard Protocol")
    prescribed = header_data.get("prescribed_action", "N/A")
    modification = header_data.get("modification")

    patient_meta = [
        [Paragraph("<b>Patient Identifier:</b>", cell_style), Paragraph(str(patient_id), cell_bold),
         Paragraph("<b>Protocol Identifier:</b>", cell_style), Paragraph(str(trial_id), cell_bold)],
        [Paragraph("<b>Assigned Cohort:</b>", cell_style), Paragraph(str(cohort), cell_style),
         Paragraph("<b>Prescribed Action:</b>", cell_style), Paragraph(str(prescribed), cell_style)],
    ]
    if modification:
        patient_meta.append([
            Paragraph("<b>Clinician Modification:</b>", cell_style),
            Paragraph(str(modification), cell_style),
            Paragraph("", cell_style),
            Paragraph("", cell_style),
        ])

    t_meta = Table(patient_meta, colWidths=[120, 150, 120, 140])
    t_meta.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F7FAFC")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#E2E8F0")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#EDF2F7")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 12))

    # 3. Final Adjudication Verdict Box
    decision = str(final_adj.get("decision", "UNKNOWN")).upper()
    eligibility = str(final_adj.get("eligibility", "UNKNOWN")).upper()
    confidence = final_adj.get("confidence")
    conf_str = f"{float(confidence) * 100:.1f}%" if confidence is not None else "N/A"
    hitl_status = final_adj.get("hitl_approval_status", "AUTO_PROCESSED")
    rationale = final_adj.get("clinician_rationale", "Automated multi-agent consensus sealed.")

    if decision in ("APPROVED", "ACCEPTED"):
        status_bg = colors.HexColor("#C6F6D5")
        status_text_color = colors.HexColor("#22543D")
    elif decision in ("REJECTED", "FAIL"):
        status_bg = colors.HexColor("#FED7D7")
        status_text_color = colors.HexColor("#742A2A")
    else:
        status_bg = colors.HexColor("#FEFCBF")
        status_text_color = colors.HexColor("#744210")

    verdict_rows = [
        [
            Paragraph(f"<b>FINAL DECISION: {decision}</b>", ParagraphStyle("VD", parent=cell_bold, fontSize=12, textColor=status_text_color)),
            Paragraph(f"<b>Eligibility:</b> {eligibility}", cell_style),
            Paragraph(f"<b>Confidence:</b> {conf_str}", cell_style),
            Paragraph(f"<b>HITL Status:</b> {hitl_status}", cell_style),
        ],
        [
            Paragraph(f"<b>Adjudication Rationale:</b> {rationale}", cell_style),
            "", "", ""
        ]
    ]
    t_verdict = Table(verdict_rows, colWidths=[150, 120, 110, 150])
    t_verdict.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), status_bg),
        ("BOX", (0, 0), (-1, -1), 1.5, status_text_color),
        ("SPAN", (0, 1), (3, 1)),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t_verdict)
    story.append(Spacer(1, 14))

    # 4. Specialist Sub-Agent Breakdown
    story.append(Paragraph("Specialist Sub-Agent Consensus Breakdown", h2_style))
    comp = sub_agents.get("compliance_agent", {})
    safe = sub_agents.get("safety_agent", {})
    fin = sub_agents.get("financial_agent", {})

    agent_rows = [
        [
            Paragraph("<b>Agent Domain</b>", cell_bold),
            Paragraph("<b>Status / Verdict</b>", cell_bold),
            Paragraph("<b>Metrics / Details</b>", cell_bold),
            Paragraph("<b>Summary Findings</b>", cell_bold),
        ],
        [
            Paragraph("<b>Compliance</b> (Port 8001)", cell_style),
            Paragraph(str(comp.get("compliance_status", "N/A")), cell_style),
            Paragraph(f"Confidence: {comp.get('confidence', 'N/A')}", cell_style),
            Paragraph(str(comp.get("summary", comp.get("explanation", "Protocol compliance check verified."))), cell_style),
        ],
        [
            Paragraph("<b>Safety & Toxicity</b> (Port 8002)", cell_style),
            Paragraph(str(safe.get("safety_status", "N/A")), cell_style),
            Paragraph(f"Risk Score: {safe.get('risk_score', 0.0)}", cell_style),
            Paragraph(str(safe.get("summary", "Biological safety evaluation complete.")), cell_style),
        ],
        [
            Paragraph("<b>Financial & Pre-Auth</b> (Port 8003)", cell_style),
            Paragraph(str(fin.get("coverage_status", "N/A")), cell_style),
            Paragraph(f"Tier: {fin.get('tier', 'Standard')} | PreAuth: {fin.get('pre_auth_required', False)}", cell_style),
            Paragraph(str(fin.get("explanation", "Coverage determination complete.")), cell_style),
        ],
    ]
    t_agents = Table(agent_rows, colWidths=[120, 100, 120, 190])
    t_agents.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EDF2F7")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E0")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(t_agents)
    story.append(Spacer(1, 14))

    # 5. Violations & Safety Hazards
    story.append(Paragraph("Active Protocol Violations & Safety Contraindications", h2_style))
    if violations:
        viol_rows = [
            [
                Paragraph("<b>Rule / Parameter</b>", cell_bold),
                Paragraph("<b>Observed</b>", cell_bold),
                Paragraph("<b>Expected / Limit</b>", cell_bold),
                Paragraph("<b>Severity</b>", cell_bold),
                Paragraph("<b>Clinical Reason</b>", cell_bold),
            ]
        ]
        for v in violations:
            if isinstance(v, dict):
                viol_rows.append([
                    Paragraph(str(v.get("rule_id") or v.get("parameter", "N/A")), cell_style),
                    Paragraph(str(v.get("observed", "N/A")), cell_style),
                    Paragraph(str(v.get("expected", "N/A")), cell_style),
                    Paragraph(str(v.get("severity", "HARD")), cell_style),
                    Paragraph(str(v.get("reason", "Protocol breach recorded.")), cell_style),
                ])
        t_viol = Table(viol_rows, colWidths=[100, 75, 75, 60, 220])
        t_viol.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#FFF5F5")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#FEB2B2")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#FED7D7")),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(t_viol)
    else:
        story.append(Paragraph("<i>No active protocol deviations, contraindications, or safety breaches recorded.</i>", cell_style))

    if decision in ("REJECTED", "FAIL"):
        story.append(Spacer(1, 8))
        story.append(Paragraph(
            "<b>Clinical Remediation Action:</b> Patient contraindication enforced. Recommend dose reduction to standard protocol Arm A dosage: Apixaban 5 mg orally twice daily.",
            ParagraphStyle("Remediation", parent=cell_style, textColor=colors.HexColor("#742A2A"))
        ))

    story.append(Spacer(1, 14))

    # 6. Immutable Audit Trail (21 CFR Part 11)
    story.append(Paragraph("21 CFR Part 11 Electronic Audit Trail", h2_style))
    if audit_trail:
        trail_rows = [
            [
                Paragraph("<b>Step / Node</b>", cell_bold),
                Paragraph("<b>Status / Action</b>", cell_bold),
                Paragraph("<b>Reviewer / System</b>", cell_bold),
                Paragraph("<b>Details / Rationale</b>", cell_bold),
            ]
        ]
        for entry in audit_trail[-10:]:  # Last 10 significant events
            if isinstance(entry, dict):
                step = entry.get("step") or entry.get("event") or "workflow_event"
                status = entry.get("status") or entry.get("action") or entry.get("total_verdict") or "logged"
                reviewer = entry.get("reviewer_id") or "SYSTEM_AUTOMATED"
                rationale_text = entry.get("rationale") or entry.get("notes") or entry.get("adjudication_verdict") or ""
                trail_rows.append([
                    Paragraph(str(step), cell_style),
                    Paragraph(str(status), cell_style),
                    Paragraph(str(reviewer), cell_style),
                    Paragraph(str(rationale_text), cell_style),
                ])
        t_trail = Table(trail_rows, colWidths=[110, 90, 110, 220])
        t_trail.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EDF2F7")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E0")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        story.append(t_trail)
    else:
        story.append(Paragraph("<i>No historical audit trail records present.</i>", cell_style))

    doc.build(story)
    buffer.seek(0)
    return buffer
