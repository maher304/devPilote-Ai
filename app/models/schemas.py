from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class TaskStatus(str, Enum):
    PENDING = "pending"
    PLANNING = "planning"
    DEVELOPING = "developing"
    REVIEWING = "reviewing"
    TESTING = "testing"
    AWAITING_APPROVAL = "awaiting_approval"
    APPROVED = "approved"
    RUNNING_TESTS = "running_tests"
    COMPLETED = "completed"
    FAILED = "failed"

class RepositoryRegister(BaseModel):
    path: str
    name: Optional[str] = None

class TaskCreate(BaseModel):
    repo_id: int
    description: str

class DiffView(BaseModel):
    diff: str
    files_changed: List[str]

class TestResult(BaseModel):
    test_name: str
    status: str
    output: str
    duration: float

class TaskReport(BaseModel):
    task_id: int
    description: str
    files_inspected: List[str]
    files_changed: List[str]
    patch_summary: str
    tests_executed: List[str]
    test_results: List[TestResult]
    errors: List[str]
    limitations: List[str]
    created_at: datetime
