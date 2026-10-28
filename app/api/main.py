from fastapi import FastAPI, HTTPException, Depends
from typing import List
from app.models.schemas import RepositoryRegister, TaskCreate, TaskReport, TaskStatus
from app.core.database import db
from app.services.repo_inspector import RepoInspector
from app.agents.workflow import workflow
from app.services.test_executor import executor
from app.core.logging import logger
import json
from datetime import datetime

app = FastAPI(
    title="DevPilot AI",
    description="AI-powered software engineering assistant",
    version="1.0.0"
)

@app.post("/repositories")
def register_repository(repo: RepositoryRegister):
    try:
        repo_id = db.register_repo(repo.path, repo.name)
        return {"repo_id": repo_id, "message": "Repository registered"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/repositories/{repo_id}/inspect")
def inspect_repository(repo_id: int):
    repo = db.get_repo(repo_id)
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
    try:
        inspector = RepoInspector(repo['path'])
        info = inspector.inspect()
        return info
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/tasks")
def create_task(task: TaskCreate):
    repo = db.get_repo(task.repo_id)
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
    task_id = db.create_task(task.repo_id, task.description)
    db.update_task(task_id, status=TaskStatus.PLANNING)
    
    # Run workflow
    try:
        inspector = RepoInspector(repo['path'])
        repo_info = inspector.inspect()
        plan = workflow.plan(repo_info, task.description)
        db.update_task(task_id, status=TaskStatus.DEVELOPING, plan=json.dumps(plan))
        
        dev_result = workflow.develop(plan, repo_info, task.description)
        db.update_task(task_id, status=TaskStatus.REVIEWING, diff=dev_result['diff'], 
                       files_changed=json.dumps(dev_result['files_changed']),
                       patch_summary=dev_result['patch_summary'])
        
        review = workflow.review(dev_result)
        if review['approved_for_testing']:
            db.update_task(task_id, status=TaskStatus.AWAITING_APPROVAL)
        else:
            db.update_task(task_id, status=TaskStatus.FAILED)
        
        return {"task_id": task_id, "status": db.get_task(task_id)['status']}
    except Exception as e:
        db.update_task(task_id, status=TaskStatus.FAILED)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    task = db.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.get("/tasks/{task_id}/diff")
def get_diff(task_id: int):
    task = db.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"diff": task.get('diff', ''), "files_changed": task.get('files_changed', [])}

@app.post("/tasks/{task_id}/approve")
def approve_task(task_id: int):
    task = db.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.update_task(task_id, status=TaskStatus.APPROVED, approved=1, approved_at=datetime.now())
    return {"message": "Task approved"}

@app.post("/tasks/{task_id}/test")
def run_tests(task_id: int):
    task = db.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if not task.get('approved'):
        raise HTTPException(status_code=400, detail="Task not approved")
    
    repo = db.get_repo(task['repo_id'])
    inspector = RepoInspector(repo['path'])
    repo_info = inspector.inspect()
    test_files = workflow.prepare_tests(repo_info)
    
    db.update_task(task_id, status=TaskStatus.RUNNING_TESTS)
    result = executor.execute_tests(repo['path'], test_files)
    
    for tr in result['test_results']:
        db.add_test_result(task_id, tr['test_name'], tr['status'], tr['output'], tr['duration'])
    
    db.update_task(task_id, status=TaskStatus.COMPLETED)
    return result

@app.get("/tasks/{task_id}/report")
def get_report(task_id: int):
    task = db.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    test_results = db.get_test_results(task_id)
    
    report = {
        "task_id": task_id,
        "description": task['description'],
        "files_inspected": task.get('files_inspected', []),
        "files_changed": task.get('files_changed', []),
        "patch_summary": task.get('patch_summary', ''),
        "tests_executed": [tr['test_name'] for tr in test_results],
        "test_results": test_results,
        "errors": [],
        "limitations": ["Running in deterministic mode", "Docker sandbox configured"],
        "created_at": task['created_at']
    }
    return report

@app.get("/health")
def health():
    return {"status": "healthy", "docker_available": executor.docker_available, "deterministic_mode": True}
