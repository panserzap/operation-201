from datetime import UTC, datetime
from enum import StrEnum
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator


class InspectionResult(StrEnum):
    NO_DEFECT = "no_defect"
    DEFECT_DETECTED = "defect_detected"


class DefectSeverity(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    UNCLASSIFIED = "unclassified"


class PartCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    part_number: str
    batch_id: str | None = None


class Part(BaseModel):
    part_uid: str = Field(default_factory=lambda: f"PART-{uuid4().hex[:12].upper()}")
    part_number: str
    batch_id: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class InspectionCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    station_id: str
    result: InspectionResult
    confidence: float = Field(ge=0, le=1)

    severity: DefectSeverity | None = None
    defect_type: str | None = None
    evidence_uri: str | None = None

    @model_validator(mode="after")
    def validate_defect_details(self):
        if self.result == InspectionResult.DEFECT_DETECTED and self.severity is None:
            raise ValueError("severity is required when a defect is detected")

        if self.result == InspectionResult.NO_DEFECT:
            if self.severity is not None:
                raise ValueError("severity cannot be provided when no defect is detected")

            if self.defect_type is not None:
                raise ValueError("defect_type cannot be provided when no defect is detected")

        return self


class DefectInspection(BaseModel):
    inspection_id: str = Field(default_factory=lambda: f"INS-{uuid4().hex[:12].upper()}")
    part_uid: str
    station_id: str
    captured_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    result: InspectionResult
    confidence: float = Field(ge=0, le=1)

    severity: DefectSeverity | None = None
    defect_type: str | None = None
    evidence_uri: str | None = None


class QualitySummary(BaseModel):
    parts_registered: int
    parts_inspected: int
    total_inspections: int
    defects_detected: int
    defect_rate: float
    severity_breakdown: dict[str, int]
