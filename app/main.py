from fastapi import FastAPI, HTTPException, status

from app.models import (
    DefectInspection,
    DefectSeverity,
    InspectionCreate,
    InspectionResult,
    Part,
    PartCreate,
    QualitySummary,
)


def create_app() -> FastAPI:
    app = FastAPI(
        title="I'm a rebel",
        version="0.1.0",
        description=(
            "A small part-traceability and visual quality backend, built for fun and as a slightly rebellious job application."
        ),
    )

    parts: dict[str, Part] = {}
    inspections: list[DefectInspection] = []

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/parts", status_code=status.HTTP_201_CREATED)
    def create_part(part_create: PartCreate) -> Part:
        part = Part(
            part_number=part_create.part_number,
            batch_id=part_create.batch_id,
        )

        parts[part.part_uid] = part

        return part

    @app.get("/parts/{part_uid}")
    def get_part(part_uid: str) -> Part:
        part = parts.get(part_uid)

        if part is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Part not found",
            )

        return part

    @app.post("/parts/{part_uid}/inspections", status_code=status.HTTP_201_CREATED)
    def create_inspection(part_uid: str, inspection_create: InspectionCreate) -> DefectInspection:
        if part_uid not in parts:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Part not found",
            )

        inspection = DefectInspection(
            part_uid=part_uid,
            station_id=inspection_create.station_id,
            result=inspection_create.result,
            confidence=inspection_create.confidence,
            severity=inspection_create.severity,
            defect_type=inspection_create.defect_type,
            evidence_uri=inspection_create.evidence_uri,
        )

        inspections.append(inspection)

        return inspection

    @app.get("/parts/{part_uid}/inspections")
    def list_part_inspections(part_uid: str) -> list[DefectInspection]:
        if part_uid not in parts:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Part not found",
            )

        return [inspection for inspection in inspections if inspection.part_uid == part_uid]

    @app.get("/quality/summary")
    def quality_summary() -> QualitySummary:
        inspected_part_uids = {inspection.part_uid for inspection in inspections}

        defects = [
            inspection
            for inspection in inspections
            if inspection.result == InspectionResult.DEFECT_DETECTED
        ]

        severity_breakdown = {severity.value: 0 for severity in DefectSeverity}

        for inspection in defects:
            if inspection.severity is not None:
                severity_breakdown[inspection.severity.value] += 1

        parts_inspected = len(inspected_part_uids)
        defects_detected = len(defects)

        defect_rate = defects_detected / len(inspections) if inspections else 0.0

        return QualitySummary(
            parts_registered=len(parts),
            parts_inspected=parts_inspected,
            total_inspections=len(inspections),
            defects_detected=defects_detected,
            defect_rate=defect_rate,
            severity_breakdown=severity_breakdown,
        )

    @app.get("/")
    def root() -> dict:
        return {
            "message": "Backend Engineer application, but with fewer PDFs.",
            "demo": "/docs",
            "health": "/health",
        }

    @app.get("/candidate")
    def candidate() -> dict:
        return {
            "name": "Panagiotis Zaparas",
            "applying_for": "Backend Engineer",
            "location": "Manchester, UK",
            "experience": "5+ years",
            "languages": ["Python", "C++", "C#", "SQL"],
            "interests": [
                "automation",
                "computer vision",
                "production systems",
                "physical-world engineering",
                "making painful manual processes disappear",
            ],
            "status": "hoping_for_201_created",
        }

    @app.get("/candidate/evidence")
    def candidate_evidence() -> dict:
        return {
            "production_automation": {
                "typical_workload": "4,000-5,000 high-resolution images",
                "peak_workload": "~120,000 images",
                "impact": "Reduced workflows from weeks to hours",
            },
            "visual_quality_control": {
                "tools": ["Python", "OpenCV", "scikit-learn"],
                "work": "Automated ghosting and failed-render detection",
                "impact": "Saved hundreds of manual review hours",
            },
            "backend": {
                "tools": ["FastAPI", "Pydantic", "pytest", "Docker"],
                "focus": [
                    "validation",
                    "workflow APIs",
                    "failure handling",
                    "testing",
                ],
            },
            "physical_systems": [
                "ROS",
                "Intel RealSense",
                "robotics",
                "computer vision",
            ],
        }

    @app.get("/tea", status_code=status.HTTP_418_IM_A_TEAPOT)
    def tea() -> dict:
        return {
            "status": "qualified",
            "coffee": True,
            "biscuits": "strongly_preferred",
            "cake": "production_dependency",
        }

    return app


app = create_app()
