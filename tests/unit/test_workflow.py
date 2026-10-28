import pytest
from app.agents.workflow import AgentWorkflow
from app.core.config import settings

def test_workflow_plan_deterministic():
    workflow = AgentWorkflow()
    repo_info = {"python_modules": ["app/main.py"], "test_files": ["tests/test_main.py"]}
    plan = workflow.plan(repo_info, "Add feature")
    assert "steps" in plan
    assert isinstance(plan["steps"], list)
    assert len(plan["steps"]) > 0

def test_workflow_develop_deterministic():
    workflow = AgentWorkflow()
    plan = {"steps": []}
    repo_info = {"python_modules": []}
    result = workflow.develop(plan, repo_info, "Test task")
    assert "diff" in result
    assert "files_changed" in result
    assert isinstance(result["files_changed"], list)
