import json
from typing import Dict, Any, List
from app.core.config import settings
from app.core.logging import logger

class AgentWorkflow:
    def __init__(self):
        self.deterministic = settings.deterministic_mode
    
    def plan(self, repo_info: Dict[str, Any], task_description: str) -> Dict[str, Any]:
        if self.deterministic:
            return {
                "steps": [
                    "Inspect relevant files based on task",
                    "Identify files that need modification",
                    "Propose minimal changes",
                    "Review for safety and correctness",
                    "Prepare tests to run"
                ],
                "files_to_inspect": repo_info.get("python_modules", [])[:5],
                "approach": "Deterministic planning - analyze task keywords and suggest targeted changes"
            }
        # Would integrate with LLM here
        return self.plan(repo_info, task_description)
    
    def develop(self, plan: Dict[str, Any], repo_info: Dict[str, Any], task_description: str) -> Dict[str, Any]:
        if self.deterministic:
            # Create a simple deterministic patch
            diff = f"""diff --git a/README.md b/README.md
index 1234567..89abcdef 100644
--- a/README.md
+++ b/README.md
@@ -1 +1,3 @@
 # Repository
+
+<!-- Task: {task_description[:50]} -->"""
            return {
                "diff": diff,
                "files_changed": ["README.md"],
                "patch_summary": "Added task annotation (deterministic mode)",
                "changes": []
            }
        return self.develop(plan, repo_info, task_description)
    
    def review(self, diff_info: Dict[str, Any]) -> Dict[str, Any]:
        if self.deterministic:
            risks = []
            if len(diff_info.get("files_changed", [])) > 10:
                risks.append("Large number of files changed")
            return {
                "approved_for_testing": True,
                "risks": risks,
                "comments": "Deterministic review - basic safety checks passed"
            }
        return self.review(diff_info)
    
    def prepare_tests(self, repo_info: Dict[str, Any]) -> List[str]:
        return repo_info.get("test_files", [])[:3]

workflow = AgentWorkflow()
