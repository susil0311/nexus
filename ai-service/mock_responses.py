"""
NEXUS PM AI Service – Mock Responses
All mock data used when MOCK_MODE=True or Gemini API calls fail.
"""
from __future__ import annotations

# ── 1. Mock Extraction – 3 realistic piping DPR events ───────────────────────

MOCK_EXTRACTION: list[dict] = [
    {
        "activity_name": "Piping Spool Fabrication – Area 3B Cooling Lines",
        "discipline": "Piping",
        "extracted_start": "2026-08-15",
        "extracted_finish": "2026-09-10",
        "progress_pct": 68.5,
        "quantity_done": 142.0,
        "location_tag": "Area 3B – Cooling Water Bay",
        "supervisor_name": "R. Krishnamurthy",
        "extraction_confidence": 0.92,
    },
    {
        "activity_name": "Structural Steel Erection – Pipe Rack Module PR-07",
        "discipline": "Structural",
        "extracted_start": "2026-08-20",
        "extracted_finish": "2026-09-30",
        "progress_pct": 45.0,
        "quantity_done": 38.5,
        "location_tag": "Pipe Rack PR-07",
        "supervisor_name": "M. Patel",
        "extraction_confidence": 0.88,
    },
    {
        "activity_name": "Civil Foundation Casting – Compressor Building Block C",
        "discipline": "Civil",
        "extracted_start": "2026-09-01",
        "extracted_finish": "2026-09-15",
        "progress_pct": 22.0,
        "quantity_done": 55.0,
        "location_tag": "Compressor Building – Block C",
        "supervisor_name": "S. Nair",
        "extraction_confidence": 0.79,
    },
]

# ── 2. Mock Matches – varied confidence scores ────────────────────────────────

MOCK_MATCHES: list[dict] = [
    {
        "field_description": "Piping Spool Fabrication – Area 3B Cooling Lines",
        "top_match": {
            "node_id": "ACT-PIP-0042",
            "node_name": "Spool Fabrication – Cooling Water System Area 3",
            "score": 0.94,
            "match_status": "auto_accepted",
            "explanation": "High semantic similarity – same discipline, area, and activity type.",
        },
        "candidates": [
            {
                "node_id": "ACT-PIP-0042",
                "node_name": "Spool Fabrication – Cooling Water System Area 3",
                "score": 0.94,
            },
            {
                "node_id": "ACT-PIP-0051",
                "node_name": "Spool Fabrication – Fire Water Loop B",
                "score": 0.71,
            },
            {
                "node_id": "ACT-PIP-0039",
                "node_name": "Pipe Support Installation – Area 3B",
                "score": 0.62,
            },
        ],
        "needs_review": False,
        "is_new_activity": False,
    },
    {
        "field_description": "Structural Steel Erection – Pipe Rack Module PR-07",
        "top_match": {
            "node_id": "ACT-STR-0018",
            "node_name": "Steel Erection – Pipe Rack Modules PR-06 to PR-09",
            "score": 0.82,
            "match_status": "needs_review",
            "explanation": "Good match but covers a range of modules – reviewer should confirm PR-07 specifically.",
        },
        "candidates": [
            {
                "node_id": "ACT-STR-0018",
                "node_name": "Steel Erection – Pipe Rack Modules PR-06 to PR-09",
                "score": 0.82,
            },
            {
                "node_id": "ACT-STR-0022",
                "node_name": "Steel Erection – Equipment Platform EP-04",
                "score": 0.58,
            },
            {
                "node_id": "ACT-STR-0011",
                "node_name": "Structural Inspection – Pipe Rack Zone North",
                "score": 0.47,
            },
        ],
        "needs_review": True,
        "is_new_activity": False,
    },
    {
        "field_description": "Civil Foundation Casting – Compressor Building Block C",
        "top_match": {
            "node_id": "ACT-NEW-001",
            "node_name": None,
            "score": 0.51,
            "match_status": "flagged_new",
            "explanation": "Low confidence match – 'Block C' subdivision not found in baseline schedule. Possible new scope.",
        },
        "candidates": [
            {
                "node_id": "ACT-CIV-0033",
                "node_name": "Foundation Works – Compressor Building",
                "score": 0.51,
            },
            {
                "node_id": "ACT-CIV-0034",
                "node_name": "Concrete Pouring – Compressor Foundation Slab",
                "score": 0.44,
            },
            {
                "node_id": "ACT-CIV-0040",
                "node_name": "Civil Works – Utility Building Foundation",
                "score": 0.31,
            },
        ],
        "needs_review": True,
        "is_new_activity": True,
    },
]

# ── 3. Mock Forecast ──────────────────────────────────────────────────────────

MOCK_FORECAST: dict = {
    "predicted_finish_date": "2026-12-15",
    "delay_days": 18,
    "confidence": "medium",
    "risk_factors": [
        {
            "factor": "Low Schedule Performance Index",
            "impact": "HIGH",
            "explanation": "Current SPI of 0.83 indicates the project is earning only 83 cents of schedule value per dollar of time spent.",
        },
        {
            "factor": "Piping Productivity Below Benchmark",
            "impact": "MEDIUM",
            "explanation": "Piping discipline productivity is 23% below the benchmark of 18 inch-dia meters per man-day, driven by late material deliveries.",
        },
        {
            "factor": "Monsoon Season Impact",
            "impact": "LOW",
            "explanation": "Civil outdoor activities face a 15% efficiency reduction during the current monsoon period (Aug–Sep).",
        },
    ],
    "narrative": (
        "With a Schedule Performance Index of 0.83 and piping productivity running 23% below benchmark, "
        "the project is predicted to complete approximately 18 days beyond the originally planned finish date. "
        "The primary driver is delayed material deliveries impacting spool fabrication throughput in the critical path. "
        "Immediate mitigation should focus on expediting long-lead piping materials and deploying additional skilled "
        "welders to the Area 3B cooling lines to recover at least 7–10 days of float before year-end."
    ),
}

# ── 4. Mock Memory Answer ─────────────────────────────────────────────────────

MOCK_MEMORY_ANSWER: dict = {
    "answer": (
        "Based on institutional memory from 3 comparable EPC projects, the benchmark piping productivity "
        "for large-bore process piping (12\" and above) in offshore plant environments is 14–18 inch-dia meters per man-day. "
        "Project REFINERY-ALPHA (2023) achieved 16.2 ID-m/MD with a peak crew of 42 welders, while PETROGAS-DELTA (2022) "
        "reported 13.8 ID-m/MD due to congested work areas. "
        "Key lessons learned: pre-fabrication of spool assemblies off-site improved productivity by 31% in REFINERY-ALPHA. "
        "For your current piping scope, if productivity remains at the current 13.1 ID-m/MD, schedule recovery requires "
        "either increasing crew size by ~25% or expanding pre-fab scope."
    ),
    "sources": [
        {
            "project_code": "REFINERY-ALPHA",
            "discipline": "Piping",
            "activity_type": "Large-bore spool fabrication and erection",
            "planned_duration": 180,
            "actual_duration": 172,
            "notes": "Pre-fabrication strategy delivered 31% productivity improvement. Peak crew: 42 welders.",
        },
        {
            "project_code": "PETROGAS-DELTA",
            "discipline": "Piping",
            "activity_type": "Process piping installation – congested area",
            "planned_duration": 210,
            "actual_duration": 241,
            "notes": "Congested work areas reduced productivity to 13.8 ID-m/MD. Recommend phased area access.",
        },
        {
            "project_code": "LNG-TERMINAL-BRAVO",
            "discipline": "Piping",
            "activity_type": "Cryogenic piping – insulation and jacketing",
            "planned_duration": 90,
            "actual_duration": 95,
            "notes": "Specialized insulation crew mobilisation caused 5-day delay. Early specialist booking critical.",
        },
    ],
    "confidence": "high",
}

# ── 5. Mock Anomalies – 2 anomalies ──────────────────────────────────────────

MOCK_ANOMALIES: list[dict] = [
    {
        "event_index": 0,
        "activity_name": "Piping Spool Fabrication – Area 3B Cooling Lines",
        "anomalies": [
            {
                "anomaly_type": "PROGRESS_OVERCLAIM",
                "description": "Activity reports 103% progress, which exceeds 100%. This may indicate data entry error or scope reduction not reflected in baseline.",
                "severity": "CRITICAL",
            }
        ],
    },
    {
        "event_index": 2,
        "activity_name": "Civil Foundation Casting – Compressor Building Block C",
        "anomalies": [
            {
                "anomaly_type": "TIMELINE_INCONSISTENCY",
                "description": "Extracted finish date (2027-03-20) is more than 6 months in the future from today's date, which is unusual for an activity already reporting 22% progress.",
                "severity": "WARNING",
            }
        ],
    },
]
