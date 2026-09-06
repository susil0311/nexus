"""
Seed demo data for NEXUS PM.

Run from the backend directory:
    python -m scripts.seed_demo_data

Or:
    python scripts/seed_demo_data.py

Requires DATABASE_URL to be set (reads .env automatically via pydantic-settings).
"""
from __future__ import annotations

import sys
import os

# Ensure the backend root is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import uuid
from datetime import date, datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import AsyncSessionLocal, create_tables
from app.core.security import hash_password
from app.models.models import (
    ActivityMatch,
    ActualProgress,
    AnomalyFlag,
    AnomalyStatus,
    ExtractedEvent,
    FieldSubmission,
    InstitutionalMemory,
    MatchStatus,
    PerformanceMetric,
    ProcessingStatus,
    Project,
    ProjectStatus,
    ScheduleNode,
    Severity,
    SubmissionType,
    User,
    UserRole,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def d(s: str) -> date:
    return date.fromisoformat(s)


def dt(s: str) -> datetime:
    return datetime.fromisoformat(s).replace(tzinfo=timezone.utc)


# ---------------------------------------------------------------------------
# Seed data definitions
# ---------------------------------------------------------------------------

USERS = [
    {
        "email": "supervisor1@demo.com",
        "name": "Rajan Borah",
        "role": UserRole.supervisor,
        "discipline": "piping",
        "password": "demo123",
    },
    {
        "email": "planner1@demo.com",
        "name": "Priya Sharma",
        "role": UserRole.planner,
        "discipline": None,
        "password": "demo123",
    },
    {
        "email": "pm1@demo.com",
        "name": "Arun Gogoi",
        "role": UserRole.pm,
        "discipline": None,
        "password": "demo123",
    },
]

PROJECTS = [
    {
        "name": "Kaziranga Pipeline Extension",
        "code": "KPE-2024",
        "client": "Oil India Limited",
        "location": "Kaziranga, Assam",
        "latitude": 26.5775,
        "longitude": 93.1700,
        "baseline_start": d("2025-01-15"),
        "baseline_end": d("2026-06-30"),
        "status": ProjectStatus.active,
    },
    {
        "name": "Duliajan Compressor Station",
        "code": "DCS-2025",
        "client": "ONGC Assam",
        "location": "Duliajan, Assam",
        "latitude": 27.3598,
        "longitude": 95.3214,
        "baseline_start": d("2025-04-01"),
        "baseline_end": d("2026-12-31"),
        "status": ProjectStatus.active,
    },
]

# 30 nodes per project, structured as L1→L2→L3→L4→L5
# Structure: 1 L1, 3 L2, 9 L3, 17 L4/L5 leaf nodes
SCHEDULE_TEMPLATES = [
    # (activity_id_suffix, parent_suffix, level, discipline, name, baseline_start, baseline_finish, duration, quantity, unit)
    ("A", None,  1, None,             "Project Execution",                    "2025-01-15", "2026-06-30", 531, None,    None),
    ("A1", "A",  2, "civil",          "Civil Works",                          "2025-01-15", "2025-09-30", 258, None,    None),
    ("A2", "A",  2, "piping",         "Piping Works",                         "2025-03-01", "2026-03-31", 395, None,    None),
    ("A3", "A",  2, "electrical",     "Electrical & Instrumentation",         "2025-06-01", "2026-06-30", 394, None,    None),
    ("A1a", "A1", 3, "civil",         "Site Preparation & Grading",           "2025-01-15", "2025-03-31",  75, 4500.0,  "m2"),
    ("A1b", "A1", 3, "civil",         "Excavation for Pipeline Trench",       "2025-02-01", "2025-05-15", 103, 1800.0,  "m3"),
    ("A1c", "A1", 3, "civil",         "Pump Foundation Concrete Works",       "2025-04-01", "2025-07-31", 120,  250.0,  "m3"),
    ("A2a", "A2", 3, "piping",        "Pipe Laying Section A-B",              "2025-03-01", "2025-07-31", 152, 1200.0,  "m"),
    ("A2b", "A2", 3, "piping",        "Pipe Laying Section B-C",              "2025-06-01", "2025-10-31", 152, 1100.0,  "m"),
    ("A2c", "A2", 3, "piping",        "Welding & Joint Inspection",           "2025-04-01", "2026-02-28", 333,  450.0,  "joints"),
    ("A3a", "A3", 3, "electrical",    "MCC Panel Installation",               "2025-06-01", "2025-09-30", 121,    3.0,  "units"),
    ("A3b", "A3", 3, "electrical",    "Cable Laying MCC to Field",            "2025-08-01", "2025-12-31", 152, 5400.0,  "m"),
    ("A3c", "A3", 3, "instrumentation","Instrument Loop Testing",             "2025-10-01", "2026-04-30", 211,  180.0,  "loops"),
    # L4 under A1a
    ("A1a1","A1a", 4, "civil",        "Topsoil Stripping",                    "2025-01-15", "2025-02-15",  31, 1500.0,  "m2"),
    ("A1a2","A1a", 4, "civil",        "Levelling & Compaction",               "2025-02-01", "2025-03-31",  58, 3000.0,  "m2"),
    # L4 under A1b
    ("A1b1","A1b", 4, "civil",        "Machine Excavation Pipeline Route",    "2025-02-01", "2025-04-15",  73,  900.0,  "m3"),
    ("A1b2","A1b", 4, "civil",        "Manual Trench Shaping",                "2025-04-01", "2025-05-15",  44,  900.0,  "m3"),
    # L4 under A1c
    ("A1c1","A1c", 4, "civil",        "Grouting Pump Foundation Pads",        "2025-04-01", "2025-06-15",  75,   80.0,  "m3"),
    ("A1c2","A1c", 4, "civil",        "Structural Steel Column Erection",     "2025-06-01", "2025-07-31",  60,   12.0,  "MT"),
    # L4 under A2a
    ("A2a1","A2a", 4, "piping",       "Pipe Stringing Section A-A2",         "2025-03-01", "2025-05-15",  75,  600.0,  "m"),
    ("A2a2","A2a", 4, "piping",       "Pipe Stringing Section A2-B",         "2025-05-01", "2025-07-31",  91,  600.0,  "m"),
    # L4 under A2b
    ("A2b1","A2b", 4, "piping",       "Holiday Testing Section B-B2",        "2025-06-01", "2025-08-15",  75,  550.0,  "m"),
    ("A2b2","A2b", 4, "piping",       "Pipe Laying Section B2-C",            "2025-08-01", "2025-10-31",  91,  550.0,  "m"),
    # L4 under A2c
    ("A2c1","A2c", 4, "piping",       "Root Pass Welding All Joints",        "2025-04-01", "2025-10-31", 213,  225.0,  "joints"),
    ("A2c2","A2c", 4, "piping",       "Final NDT & Radiography",             "2025-09-01", "2026-02-28", 181,  225.0,  "joints"),
    # L4 under A3a
    ("A3a1","A3a", 4, "electrical",   "MCC Foundation & Cable Trench",       "2025-06-01", "2025-07-15",  44,    6.0,  "units"),
    ("A3a2","A3a", 4, "electrical",   "MCC Panel Termination & Energisation","2025-07-16", "2025-09-30",  76,    3.0,  "units"),
    # L4 under A3b
    ("A3b1","A3b", 4, "electrical",   "Cable Drum Laying HT Side",           "2025-08-01", "2025-10-31",  91, 2700.0,  "m"),
    ("A3b2","A3b", 4, "electrical",   "Cable Laying LT & Control Cables",    "2025-10-01", "2025-12-31",  91, 2700.0,  "m"),
    # L4 under A3c
    ("A3c1","A3c", 4, "instrumentation","Instrument Calibration",            "2025-10-01", "2026-01-31", 122,   90.0,  "loops"),
    ("A3c2","A3c", 4, "instrumentation","Loop Testing & PSSR",               "2026-01-01", "2026-04-30", 119,   90.0,  "loops"),
]

FIELD_SUBMISSIONS = [
    {
        "discipline": "piping",
        "submission_date": d("2025-09-15"),
        "content": "Pipe laying section A-B completed 60%. Root pass welding on 45 joints done. Material at site ready for next week.",
        "type": SubmissionType.text,
    },
    {
        "discipline": "civil",
        "submission_date": d("2025-08-30"),
        "content": "Excavation for pipeline trench 80% done. Machine breakdown caused 2-day delay. Resuming tomorrow with hired equipment.",
        "type": SubmissionType.text,
    },
    {
        "discipline": "electrical",
        "submission_date": d("2025-10-10"),
        "content": "MCC panel installation completed. Cable laying started from MCC to field junction box 1. 300m laid today.",
        "type": SubmissionType.dpr,
    },
    {
        "discipline": "civil",
        "submission_date": d("2025-07-20"),
        "content": "Grouting pump foundation pads. 3 out of 4 pads completed. Concrete poured 45 m3 today. Curing ongoing for pad 2.",
        "type": SubmissionType.text,
    },
    {
        "discipline": "piping",
        "submission_date": d("2025-11-05"),
        "content": "NDT inspection on 30 joints done. 2 joints failed, reweld ordered. Holiday testing section B-B2 ongoing – 70% complete.",
        "type": SubmissionType.voice,
    },
]

EXTRACTED_EVENTS_DATA = [
    # Matches A2a – Pipe Laying Section A-B
    {"raw_description": "Pipe laying section A-B completed 60%", "discipline": "piping",
     "extracted_start": d("2025-09-01"), "extracted_finish": None, "progress_pct": 60.0,
     "quantity_done": 720.0, "location_tag": "Section A-B", "supervisor_name": "Rajan Borah",
     "extraction_confidence": 0.91, "activity_suffix": "A2a"},
    # Matches A1b – Excavation
    {"raw_description": "Excavation for pipeline trench 80% done", "discipline": "civil",
     "extracted_start": d("2025-08-01"), "extracted_finish": None, "progress_pct": 80.0,
     "quantity_done": 1440.0, "location_tag": "Pipeline Route", "supervisor_name": "Rajan Borah",
     "extraction_confidence": 0.88, "activity_suffix": "A1b"},
    # Matches A3a – MCC Installation
    {"raw_description": "MCC panel installation completed", "discipline": "electrical",
     "extracted_start": d("2025-09-20"), "extracted_finish": d("2025-10-08"), "progress_pct": 100.0,
     "quantity_done": 3.0, "location_tag": "Substation Area", "supervisor_name": None,
     "extraction_confidence": 0.95, "activity_suffix": "A3a"},
    # Matches A1c1 – Grouting
    {"raw_description": "Grouting pump foundation pads. 3 out of 4 completed", "discipline": "civil",
     "extracted_start": d("2025-06-01"), "extracted_finish": None, "progress_pct": 75.0,
     "quantity_done": 60.0, "location_tag": "Pump Area", "supervisor_name": None,
     "extraction_confidence": 0.83, "activity_suffix": "A1c1"},
    # Matches A2c2 – NDT
    {"raw_description": "NDT inspection on 30 joints done. 2 joints failed.", "discipline": "piping",
     "extracted_start": d("2025-10-15"), "extracted_finish": None, "progress_pct": 13.0,
     "quantity_done": 30.0, "location_tag": "Section B-B2", "supervisor_name": "Rajan Borah",
     "extraction_confidence": 0.79, "activity_suffix": "A2c2"},
]

ACTUAL_PROGRESS_DATA = [
    # (activity_suffix, actual_start, actual_finish, progress_pct, is_complete)
    ("A1a1", d("2025-01-16"), d("2025-02-10"), 100.0, True),
    ("A1a2", d("2025-02-05"), d("2025-04-02"), 100.0, True),
    ("A1b1", d("2025-02-02"), None, 100.0, True),
    ("A1b2", d("2025-04-05"), None, 65.0, False),
    ("A1c1", d("2025-04-10"), None, 75.0, False),
    ("A2a1", d("2025-03-05"), d("2025-05-20"), 100.0, True),
    ("A2a2", d("2025-05-15"), None, 80.0, False),
    ("A2c1", d("2025-04-08"), None, 60.0, False),
    ("A3a1", d("2025-06-10"), d("2025-07-20"), 100.0, True),
    ("A3a2", d("2025-07-22"), d("2025-09-28"), 100.0, True),
]

INSTITUTIONAL_MEMORY = [
    {
        "project_code": "KPE-2019",
        "discipline": "piping",
        "activity_type": "pipe_laying",
        "planned_duration": 120,
        "actual_duration": 148,
        "delay_causes": ["monsoon", "labour_shortage"],
        "season": "monsoon",
        "notes": "Monsoon onset 3 weeks early in 2019 disrupted pipe stringing. Buffer of 20 days recommended for similar routes.",
    },
    {
        "project_code": "KPE-2021",
        "discipline": "civil",
        "activity_type": "excavation",
        "planned_duration": 75,
        "actual_duration": 95,
        "delay_causes": ["machine_breakdown", "hard_rock"],
        "season": "winter",
        "notes": "Unexpected hard rock layer at 2m depth near km marker 14. Required blasting permit – 3 week delay.",
    },
    {
        "project_code": "DCS-2022",
        "discipline": "piping",
        "activity_type": "welding_inspection",
        "planned_duration": 90,
        "actual_duration": 82,
        "delay_causes": [],
        "season": "post_monsoon",
        "notes": "Post-monsoon season proved optimal for welding quality. Radiography rejection rate only 1.2%.",
    },
    {
        "project_code": "DCS-2022",
        "discipline": "electrical",
        "activity_type": "cable_laying",
        "planned_duration": 60,
        "actual_duration": 70,
        "delay_causes": ["material_delay"],
        "season": "winter",
        "notes": "HT cable delivery delayed 12 days due to port congestion. Order early with 15-day buffer.",
    },
    {
        "project_code": "KPE-2021",
        "discipline": "instrumentation",
        "activity_type": "loop_testing",
        "planned_duration": 45,
        "actual_duration": 51,
        "delay_causes": ["software_issue", "vendor_support_delay"],
        "season": "summer",
        "notes": "DCS configuration required vendor site visit. Plan for remote support contract in advance.",
    },
]


# ---------------------------------------------------------------------------
# Main seeder
# ---------------------------------------------------------------------------

async def seed(db: AsyncSession) -> None:
    print("🌱 Starting NEXUS PM demo data seed...")

    # ── Users ──────────────────────────────────────────────────────────────
    user_objs: dict[str, User] = {}
    for u_data in USERS:
        existing = (await db.execute(select(User).where(User.email == u_data["email"]))).scalar_one_or_none()
        if existing:
            user_objs[u_data["email"]] = existing
            print(f"   ⏭  User {u_data['email']} already exists")
            continue
        user = User(
            email=u_data["email"],
            name=u_data["name"],
            role=u_data["role"],
            discipline=u_data["discipline"],
            password_hash=hash_password(u_data["password"]),
        )
        db.add(user)
        await db.flush()
        user_objs[u_data["email"]] = user
        print(f"   ✅ Created user: {u_data['email']} ({u_data['role'].value})")

    supervisor = user_objs["supervisor1@demo.com"]
    planner = user_objs["planner1@demo.com"]

    # ── Projects ────────────────────────────────────────────────────────────
    project_objs: dict[str, Project] = {}
    for p_data in PROJECTS:
        existing = (await db.execute(select(Project).where(Project.code == p_data["code"]))).scalar_one_or_none()
        if existing:
            project_objs[p_data["code"]] = existing
            print(f"   ⏭  Project {p_data['code']} already exists")
            continue
        proj = Project(**{k: v for k, v in p_data.items()})
        db.add(proj)
        await db.flush()
        project_objs[p_data["code"]] = proj
        print(f"   ✅ Created project: {p_data['name']} ({p_data['code']})")

    # ── Schedule Nodes (30 per project) ─────────────────────────────────────
    for code, proj in project_objs.items():
        # Check if already seeded
        count_res = await db.execute(
            select(ScheduleNode).where(ScheduleNode.project_id == proj.id).limit(1)
        )
        if count_res.scalar_one_or_none():
            print(f"   ⏭  Schedule nodes for {code} already exist")
            continue

        id_map: dict[str, uuid.UUID] = {}
        for tpl in SCHEDULE_TEMPLATES:
            (
                suffix, parent_suffix, level, discipline, name,
                bs_start, bs_finish, duration, quantity, unit
            ) = tpl

            node = ScheduleNode(
                project_id=proj.id,
                activity_id=f"{code}-{suffix}",
                parent_id=id_map.get(parent_suffix) if parent_suffix else None,
                level=level,
                discipline=discipline,
                name=name,
                baseline_start=d(bs_start),
                baseline_finish=d(bs_finish),
                planned_duration=duration,
                planned_quantity=quantity,
                unit=unit,
                is_milestone=False,
                float_days=max(0, 30 - duration % 30),
            )
            db.add(node)
            await db.flush()
            id_map[suffix] = node.id

        print(f"   ✅ Created {len(SCHEDULE_TEMPLATES)} schedule nodes for {code}")
        await db.commit()

        # ── Field Submissions + Extracted Events + Matches ──────────────────
        node_lookup: dict[str, ScheduleNode] = {}
        nodes_res = await db.execute(
            select(ScheduleNode).where(ScheduleNode.project_id == proj.id)
        )
        for n in nodes_res.scalars().all():
            # strip the "CODE-" prefix to get suffix back
            suffix_key = n.activity_id.replace(f"{code}-", "")
            node_lookup[suffix_key] = n

        for i, sub_data in enumerate(FIELD_SUBMISSIONS):
            sub = FieldSubmission(
                project_id=proj.id,
                submitted_by=supervisor.id,
                submission_type=sub_data["type"],
                raw_content=sub_data["content"] if sub_data["type"] != SubmissionType.voice else None,
                discipline=sub_data["discipline"],
                submission_date=sub_data["submission_date"],
                processing_status=ProcessingStatus.done,
            )
            db.add(sub)
            await db.flush()

            ev_data = EXTRACTED_EVENTS_DATA[i]
            event = ExtractedEvent(
                submission_id=sub.id,
                project_id=proj.id,
                raw_description=ev_data["raw_description"],
                discipline=ev_data["discipline"],
                extracted_start=ev_data["extracted_start"],
                extracted_finish=ev_data["extracted_finish"],
                progress_pct=ev_data["progress_pct"],
                quantity_done=ev_data["quantity_done"],
                location_tag=ev_data["location_tag"],
                supervisor_name=ev_data["supervisor_name"],
                extraction_confidence=ev_data["extraction_confidence"],
            )
            db.add(event)
            await db.flush()

            target_node = node_lookup.get(ev_data["activity_suffix"])
            auto = ev_data["extraction_confidence"] >= 0.85
            match = ActivityMatch(
                extracted_event_id=event.id,
                schedule_node_id=target_node.id if target_node else None,
                match_score=ev_data["extraction_confidence"],
                match_method="semantic_similarity",
                match_explanation=f"AI matched with {ev_data['extraction_confidence']:.0%} confidence to '{target_node.name if target_node else 'unknown'}'",
                status=MatchStatus.auto_accepted if auto else MatchStatus.needs_review,
                reviewed_by=planner.id if auto else None,
                reviewed_at=datetime.now(timezone.utc) if auto else None,
            )
            db.add(match)
            await db.flush()

        print(f"   ✅ Created {len(FIELD_SUBMISSIONS)} submissions + events + matches for {code}")
        await db.commit()

        # ── Actual Progress ──────────────────────────────────────────────────
        for suffix, act_start, act_finish, pct, is_done in ACTUAL_PROGRESS_DATA:
            node = node_lookup.get(suffix)
            if not node:
                continue
            ap = ActualProgress(
                project_id=proj.id,
                schedule_node_id=node.id,
                actual_start=act_start,
                actual_finish=act_finish,
                progress_pct=pct,
                is_complete=is_done,
                confidence_score=0.88,
                source_type="field_submission",
                audit_hash=None,
            )
            db.add(ap)

        await db.flush()
        print(f"   ✅ Created {len(ACTUAL_PROGRESS_DATA)} actual progress records for {code}")

        # ── Performance Metrics ─────────────────────────────────────────────
        for spi_val, cpi_val, risk, pred_fin, ts_offset_days in [
            (0.87, 0.91, 0.18, d("2026-08-15"), 30),
            (0.92, 0.94, 0.12, d("2026-07-20"), 0),
        ]:
            metric = PerformanceMetric(
                project_id=proj.id,
                schedule_node_id=None,
                computed_at=datetime.now(timezone.utc) - timedelta(days=ts_offset_days),
                spi=spi_val,
                cpi=cpi_val,
                float_consumed=int((1.0 - spi_val) * 60),
                predicted_finish=pred_fin,
                delay_risk_score=risk,
                forecast_explanation=(
                    f"SPI={spi_val}. At current velocity, project is tracking "
                    f"{round((1-spi_val)*100, 1)}% behind plan. Predicted finish: {pred_fin}."
                ),
            )
            db.add(metric)

        await db.flush()
        print(f"   ✅ Created 2 performance metrics for {code}")

        # ── Anomaly Flag ─────────────────────────────────────────────────────
        anomaly = AnomalyFlag(
            project_id=proj.id,
            anomaly_type="schedule_deviation",
            description=(
                "Pipe laying progress is 15% behind baseline for this period. "
                "Crew deployment insufficient for current scope velocity. "
                "Risk of spilling into monsoon season if not corrected within 2 weeks."
            ),
            severity=Severity.high,
            status=AnomalyStatus.open,
        )
        db.add(anomaly)
        await db.flush()
        print(f"   ✅ Created anomaly flag for {code}")

        await db.commit()

    # ── Institutional Memory (shared) ──────────────────────────────────────
    for im_data in INSTITUTIONAL_MEMORY:
        im = InstitutionalMemory(
            project_id=None,
            project_code=im_data["project_code"],
            discipline=im_data["discipline"],
            activity_type=im_data["activity_type"],
            planned_duration=im_data["planned_duration"],
            actual_duration=im_data["actual_duration"],
            delay_causes=im_data["delay_causes"],
            season=im_data["season"],
            notes=im_data["notes"],
        )
        db.add(im)

    await db.commit()
    print(f"   ✅ Created {len(INSTITUTIONAL_MEMORY)} institutional memory records")

    print("\n✨ Seed complete!")
    print("\n📋 Demo Accounts:")
    print("   supervisor1@demo.com  / demo123  (Supervisor – Piping)")
    print("   planner1@demo.com     / demo123  (Planner)")
    print("   pm1@demo.com          / demo123  (Project Manager)")
    print("\n📁 Projects:")
    for code, proj in project_objs.items():
        print(f"   {code}: {proj.name}")


async def main() -> None:
    await create_tables()
    async with AsyncSessionLocal() as db:
        await seed(db)


if __name__ == "__main__":
    asyncio.run(main())
