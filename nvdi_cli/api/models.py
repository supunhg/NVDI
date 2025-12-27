from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class CVSSv3(BaseModel):
    baseScore: Optional[float] = None
    baseSeverity: Optional[str] = None
    vectorString: Optional[str] = None
    exploitabilityScore: Optional[float] = None
    impactScore: Optional[float] = None


class CVSSv2(BaseModel):
    baseScore: Optional[float] = None
    vectorString: Optional[str] = None
    severity: Optional[str] = None


class Reference(BaseModel):
    url: str
    source: Optional[str] = None
    tags: List[str] = []


class Weakness(BaseModel):
    source: Optional[str] = None
    type: Optional[str] = None
    description: List[str] = []


class CPE(BaseModel):
    criteria: Optional[str] = None
    matchCriteriaId: Optional[str] = None
    vulnerable: Optional[bool] = None


class CVEModel(BaseModel):
    id: str
    sourceIdentifier: Optional[str] = None
    description: Optional[str] = None
    publishedDate: Optional[str] = None
    lastModifiedDate: Optional[str] = None
    vulnStatus: Optional[str] = None
    cvssv3: Optional[CVSSv3] = None
    cvssv2: Optional[CVSSv2] = None
    references: List[Reference] = []
    weaknesses: List[Weakness] = []
    configurations: List[CPE] = []
    raw_data: Optional[Dict[str, Any]] = None
