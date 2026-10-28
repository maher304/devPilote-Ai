import os
import git
from pathlib import Path
from typing import List, Dict, Any
from app.core.config import settings

class RepoInspector:
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path).resolve()
        self._validate_path()
    
    def _validate_path(self):
        approved = settings.get_approved_paths()
        is_approved = False
        for ap in approved:
            try:
                if str(self.repo_path).startswith(str(Path(ap).resolve())) or str(self.repo_path) == str(Path(ap).resolve()):
                    is_approved = True
                    break
            except:
                continue
        if not is_approved and approved:
            raise ValueError(f"Path {self.repo_path} not in approved paths")
    
    def inspect(self) -> Dict[str, Any]:
        try:
            repo = git.Repo(self.repo_path)
            tracked_files = [item.path for item in repo.tree().traverse() if item.type == 'blob']
        except:
            tracked_files = []
            for root, dirs, files in os.walk(self.repo_path):
                if '.git' in dirs:
                    dirs.remove('.git')
                for f in files:
                    rel = os.path.relpath(os.path.join(root, f), self.repo_path)
                    tracked_files.append(rel)
        
        py_files = [f for f in tracked_files if f.endswith('.py')]
        test_files = [f for f in tracked_files if 'test' in f.lower()]
        
        structure = self._get_structure()
        
        return {
            "tracked_files": tracked_files,
            "python_modules": py_files,
            "test_files": test_files,
            "structure": structure,
            "summary": f"Repository with {len(tracked_files)} files, {len(py_files)} Python modules, {len(test_files)} test files"
        }
    
    def _get_structure(self) -> str:
        lines = []
        for root, dirs, files in os.walk(self.repo_path):
            if '.git' in dirs:
                dirs.remove('.git')
            level = root.replace(str(self.repo_path), '').count(os.sep)
            indent = ' ' * 4 * level
            lines.append(f'{indent}{os.path.basename(root)}/')
            subindent = ' ' * 4 * (level + 1)
            for f in files:
                lines.append(f'{subindent}{f}')
        return '\n'.join(lines[:100])  # Limit
    
    def read_file(self, file_path: str) -> str:
        full_path = (self.repo_path / file_path).resolve()
        if not str(full_path).startswith(str(self.repo_path)):
            raise ValueError("Path traversal detected")
        with open(full_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def get_diff(self) -> str:
        try:
            repo = git.Repo(self.repo_path)
            if repo.is_dirty():
                return repo.git.diff()
            return ""
        except:
            return ""
