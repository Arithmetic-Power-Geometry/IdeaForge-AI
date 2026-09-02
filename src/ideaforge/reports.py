from __future__ import annotations

from io import BytesIO
import json
import math
from xml.sax.saxutils import escape


def portfolio_json(records):
    if hasattr(records, "to_dict"):
        try:
            records = records.to_dict(orient="records")
        except TypeError:
            records = records.to_dict()
    return json.dumps(records, indent=2, ensure_ascii=False, default=str).encode("utf-8")


def _fmt(value, digits=3, suffix=""):
    try:
        value = float(value)
        if not math.isfinite(value):
            return "N/A"
        return f"{value:.{digits}f}{suffix}"
    except Exception:
        return str(value) if value is not None else "N/A"


def assessment_pdf(row, readiness=None):
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet

        buf = BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=42, leftMargin=42, topMargin=42, bottomMargin=42)
        styles = getSampleStyleSheet()
        story = [Paragraph("IdeaForge AI - Auditable Assessment Report", styles["Title"]), Spacer(1, 10)]
        story += [Paragraph(f"<b>Question:</b> {escape(str(row['question']))}", styles["BodyText"]), Spacer(1, 8)]
        data = [
            ["Metric", "Value"],
            ["Question ID", str(row["question_id"])],
            ["Domain", str(row.get("domain", "General"))],
            ["Origin / mode", f"{row.get('origin', '')} / {row.get('scoring_mode', '')}"],
            ["Raw DC (declared procedure infimum)", _fmt(row.get("dc_raw"))],
            ["Normalized DC", _fmt(row.get("dc"))],
            ["Signed representational change", _fmt(row.get("delta_l"))],
            ["Raw QC", _fmt(row.get("qc_raw"))],
            ["Normalized QC", _fmt(row.get("qc"))],
            ["Discovery-Plane eligible", "Yes" if bool(row.get("discovery_plane_eligible")) else "No"],
            ["Region", str(row.get("region", "N/A"))],
            ["Frontier", "Yes" if bool(row.get("frontier")) else "No"],
            ["Utility", _fmt(row.get("utility"))],
            ["Venture screen", _fmt(row.get("venture_readiness"), 1, "/100")],
            ["Confidence", str(row.get("confidence", ""))],
        ]
        t = Table(data, colWidths=[170, 300])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#6C4CF1")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), .3, colors.lightgrey),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("PADDING", (0, 0), (-1, -1), 6),
        ]))
        story += [t, Spacer(1, 12)]
        story += [
            Paragraph("Recommendation", styles["Heading2"]),
            Paragraph(escape(str(row.get("recommendation", ""))), styles["BodyText"]),
            Spacer(1, 6),
            Paragraph("Next action", styles["Heading2"]),
            Paragraph(escape(str(row.get("next_action", ""))), styles["BodyText"]),
        ]
        if readiness:
            story += [Spacer(1, 10), Paragraph("Startup readiness evidence status", styles["Heading2"])]
            rt = Table([["Dimension", "Status"]] + [[str(k), str(v)] for k, v in readiness.items()], colWidths=[150, 320])
            rt.setStyle(TableStyle([
                ("GRID", (0, 0), (-1, -1), .3, colors.lightgrey),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EEF0FF")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("PADDING", (0, 0), (-1, -1), 5),
            ]))
            story.append(rt)
        story += [
            Spacer(1, 14),
            Paragraph("Important boundary", styles["Heading2"]),
            Paragraph(
                "IdeaForge is an early-stage decision-support system. DPT coordinates are relative to declared conventions. "
                "Questions with representational expansion or no admissible declared procedure are retained for audit but excluded "
                "from the nonnegative Discovery Plane. AI suggestions are preliminary; frontier membership and venture-screen values "
                "do not establish truth, novelty, patentability, product-market fit, fundability, safety, or startup success.",
                styles["BodyText"],
            ),
        ]
        doc.build(story)
        return buf.getvalue()
    except Exception:
        return b""
