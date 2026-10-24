"""
pdf_report.py - Executive PDF Analytics Report Generator
=========================================================
Generates a multi-page, publication-quality PDF report using ReportLab:
- Channel Performance Score & Sub-scores
- Executive KPIs & Age-Fairness (Views/Day) Analysis
- Automated Plain-English Insights & Smart Content Recommendations
- Machine Learning Model Evaluation & Baseline Comparison
- Comment Sentiment Distribution & Data Quality Audit
- Embedded High-Resolution Visualizations
"""

import os
import io
from datetime import datetime
from typing import Dict, Any, List

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY


def generate_pdf_report(
    channel_info: Dict[str, Any],
    kpis: Dict[str, Any],
    channel_score: Dict[str, Any],
    insights: List[str],
    recommendations: List[Dict[str, str]],
    top_videos: List[Dict[str, Any]],
    ml_metrics: Dict[str, Any],
    sentiment: Dict[str, Any],
    data_quality: Dict[str, Any],
    charts_dir: str = None
) -> bytes:
    """Compiles complete channel analytics into a professional PDF document."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom Palette
    c_navy = colors.HexColor("#0b132b")
    c_blue = colors.HexColor("#2563eb")
    c_green = colors.HexColor("#10b981")
    c_dark = colors.HexColor("#0f172a")
    c_slate = colors.HexColor("#475569")
    c_light = colors.HexColor("#f8fafc")
    c_border = colors.HexColor("#cbd5e1")

    # Typography Styles
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=c_navy
    )
    subtitle_style = ParagraphStyle(
        "DocSubTitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=c_slate
    )
    h1_style = ParagraphStyle(
        "SectionH1",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=17,
        textColor=c_blue,
        spaceBefore=10,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=c_dark
    )
    bullet_style = ParagraphStyle(
        "Bullet",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=12,
        textColor=c_dark,
        leftIndent=12,
        spaceAfter=4
    )
    score_big_style = ParagraphStyle(
        "ScoreBig",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=26,
        leading=30,
        textColor=c_green,
        alignment=TA_CENTER
    )

    elements = []

    # 1. Title Header & Meta
    elements.append(Paragraph("YouTube Analytics & Trends Platform", title_style))
    elements.append(Paragraph("Executive Performance, Statistical Evaluation & Machine Learning Report", subtitle_style))
    elements.append(Spacer(1, 8))
    elements.append(HRFlowable(width="100%", thickness=2, color=c_blue, spaceBefore=2, spaceAfter=8))

    # Meta Info Row
    collected_date = channel_info.get("collected_at", datetime.now().strftime("%d %B %Y, %I:%M %p"))
    data_source_label = channel_info.get("data_source", "Demo Dataset")
    channel_title = channel_info.get("title", "Google Developers")

    meta_table_data = [
        [
            Paragraph(f"<b>Channel:</b> {channel_title}", body_style),
            Paragraph(f"<b>Data Source:</b> {data_source_label}", body_style),
            Paragraph(f"<b>Report Date:</b> {collected_date}", body_style)
        ]
    ]
    meta_table = Table(meta_table_data, colWidths=[200, 160, 180])
    meta_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), c_light),
        ("PADDING", (0, 0), (-1, -1), 6),
        ("BOX", (0, 0), (-1, -1), 0.5, c_border),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE")
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 10))

    # 2. Channel Performance Score Card (0 to 100)
    score_val = channel_score.get("overall_score", 84.5)
    tier_label = channel_score.get("tier", "Strong (Tier A)")
    sub = channel_score.get("subscores", {})

    score_card_data = [
        [
            Paragraph(f"<b>CHANNEL PERFORMANCE SCORE</b><br/><font size=7 color='#64748b'>Weighted Multi-Factor Benchmark</font>", body_style),
            Paragraph(f"{score_val} / 100", score_big_style),
            Paragraph(f"<b>Rating:</b> <font color='#10b981'>{tier_label}</font><br/><font size=7.5 color='#475569'>Reach: {sub.get('reach', 85)} | Eng: {sub.get('engagement', 80)}<br/>Cadence: {sub.get('cadence', 90)} | Sent: {sub.get('sentiment', 80)}</font>", body_style)
        ]
    ]
    score_table = Table(score_card_data, colWidths=[200, 140, 200])
    score_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f0fdf4")),
        ("BOX", (0, 0), (-1, -1), 1, c_green),
        ("PADDING", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE")
    ]))
    elements.append(score_table)
    elements.append(Spacer(1, 10))

    # 3. Key Performance Indicators
    elements.append(Paragraph("1. Executive Summary & Catalog KPIs", h1_style))
    kpi_data = [
        ["Total Uploads", "Catalog Views", "Total Likes", "Total Comments", "Avg Views / Video", "Avg Engagement"],
        [
            f"{kpis.get('total_videos', 0):,}",
            f"{kpis.get('total_views', 0):,}",
            f"{kpis.get('total_likes', 0):,}",
            f"{kpis.get('total_comments', 0):,}",
            f"{kpis.get('avg_views', 0):,}",
            f"{kpis.get('avg_engagement_rate', 0.0):.2f}%"
        ]
    ]
    kpi_table = Table(kpi_data, colWidths=[90, 90, 90, 90, 95, 85])
    kpi_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), c_navy),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 8),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("BACKGROUND", (0, 1), (-1, 1), c_light),
        ("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 1), (-1, 1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, c_border),
        ("PADDING", (0, 0), (-1, -1), 5)
    ]))
    elements.append(kpi_table)
    elements.append(Spacer(1, 10))

    # 4. Automated Plain-English Insights
    elements.append(Paragraph("2. Automated Plain-English Data Insights", h1_style))
    for ins in insights[:4]:
        elements.append(Paragraph(f"• {ins}", bullet_style))
    elements.append(Spacer(1, 8))

    # 5. Top 5 Videos & Age-Fairness (Views per Day)
    elements.append(Paragraph("3. Top Videos & Age-Adjusted Fairness (Views / Day)", h1_style))
    top_table_rows = [["Rank", "Video Title", "Views", "Likes", "Engagement", "Views / Day"]]
    for idx, v in enumerate(top_videos[:5], 1):
        vpd = v.get("views_per_day", 0)
        top_table_rows.append([
            str(idx),
            v.get("title", "Untitled")[:40] + ("..." if len(v.get("title", "")) > 40 else ""),
            f"{int(v.get('views', 0)):,}",
            f"{int(v.get('likes', 0)):,}",
            f"{float(v.get('engagement_rate', 0)):.2f}%",
            f"{int(float(vpd)):,}/day"
        ])

    top_tbl = Table(top_table_rows, colWidths=[35, 230, 75, 65, 65, 70])
    top_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), c_blue),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, c_border),
        ("PADDING", (0, 0), (-1, -1), 4),
        ("ALIGN", (0, 0), (0, -1), "CENTER"),
        ("ALIGN", (2, 0), (-1, -1), "RIGHT")
    ]))
    elements.append(top_tbl)
    elements.append(Spacer(1, 10))

    # 6. Machine Learning Model Evaluation vs Baseline
    elements.append(Paragraph("4. Pre-Publication Machine Learning Evaluation Benchmark", h1_style))
    elements.append(Paragraph(
        "<b>Pre-Publication Leakage Guard:</b> Inputs are restricted strictly to pre-publication metadata (title length, word count, description length, tag count, day of week, hour). Post-publication signals (likes/comments) are excluded.",
        body_style
    ))
    elements.append(Spacer(1, 4))

    rf_mae = ml_metrics.get("rf_mae", 138951)
    rf_rmse = ml_metrics.get("rf_rmse", 160565)
    rf_r2 = ml_metrics.get("rf_r2", -0.530)
    base_mae = ml_metrics.get("baseline_mae", 133768)
    base_rmse = ml_metrics.get("baseline_rmse", 153089)

    ml_table_data = [
        ["Model Architecture", "MAE (Mean Absolute Error)", "RMSE (Root Mean Sq)", "R² Score (Log Views)", "Validation Status"],
        ["Random Forest Regressor", f"{rf_mae:,} views", f"{rf_rmse:,} views", f"{rf_r2:.3f}", "Experimental"],
        ["Naive Median Baseline", f"{base_mae:,} views", f"{base_rmse:,} views", "0.000", "Reference Standard"]
    ]
    ml_tbl = Table(ml_table_data, colWidths=[150, 110, 110, 80, 90])
    ml_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), c_slate),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, c_border),
        ("PADDING", (0, 0), (-1, -1), 4),
        ("ALIGN", (1, 1), (-1, -1), "CENTER")
    ]))
    elements.append(ml_tbl)
    elements.append(Spacer(1, 10))

    # 7. Smart Evidence-Based Recommendations
    elements.append(Paragraph("5. Evidence-Based Content Recommendations", h1_style))
    for rec in recommendations[:3]:
        elements.append(Paragraph(f"• <b>[{rec.get('category', 'Strategy')}]:</b> {rec.get('recommendation', '')} <font color='#64748b'>({rec.get('evidence', '')})</font>", bullet_style))
    elements.append(Spacer(1, 8))

    # 8. Data-Quality Audit
    elements.append(Paragraph("6. Dataset Health & Data Quality Audit", h1_style))
    dq_data = [
        ["Total Rows / Cols", "Exact Duplicates", "Unique Video IDs", "Missing Views", "Negative Numbers", "Quality Score"],
        [
            f"{data_quality.get('total_records', 0)} × {data_quality.get('total_columns', 0)}",
            str(data_quality.get("duplicate_rows", 0)),
            str(data_quality.get("unique_video_ids", 0)),
            str(data_quality.get("missing_views", 0)),
            str(data_quality.get("invalid_numerical_values", 0)),
            f"{data_quality.get('quality_score', 100)}%"
        ]
    ]
    dq_tbl = Table(dq_data, colWidths=[90, 90, 90, 90, 90, 90])
    dq_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#334155")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, c_border),
        ("PADDING", (0, 0), (-1, -1), 4),
        ("ALIGN", (0, 0), (-1, -1), "CENTER")
    ]))
    elements.append(dq_tbl)
    elements.append(Spacer(1, 12))

    # 9. Embedded Visualization Highlights
    if charts_dir and os.path.exists(charts_dir):
        chart1 = os.path.join(charts_dir, "chart1_top_viewed_videos.png")
        chart2 = os.path.join(charts_dir, "chart2_best_time_to_publish.png")
        chart_elements = []
        if os.path.exists(chart1):
            chart_elements.append(Paragraph("<b>Top Viewed Videos Distribution:</b>", body_style))
            chart_elements.append(Spacer(1, 4))
            chart_elements.append(Image(chart1, width=6.8 * inch, height=3.0 * inch))
            chart_elements.append(Spacer(1, 8))
        if os.path.exists(chart2):
            chart_elements.append(Paragraph("<b>Publishing-Time Performance Analysis (Observed Patterns):</b>", body_style))
            chart_elements.append(Spacer(1, 4))
            chart_elements.append(Image(chart2, width=6.8 * inch, height=2.6 * inch))

        if chart_elements:
            elements.append(KeepTogether(chart_elements))

    # Footer Disclaimer
    elements.append(Spacer(1, 10))
    elements.append(HRFlowable(width="100%", thickness=1, color=c_border, spaceBefore=4, spaceAfter=6))
    elements.append(Paragraph(
        "<font size=7 color='#64748b'><b>Disclaimer:</b> This analytics document was compiled automatically by the YouTube Analytics & Trends Platform. Historical observed performance and machine learning estimates do not constitute guaranteed future reach.</font>",
        body_style
    ))

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()
