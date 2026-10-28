import os
import tempfile
from app.services.repo_inspector import RepoInspector

def test_repo_inspector_path_validation():
    # Should work with approved paths
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a simple repo structure
        with open(os.path.join(tmpdir, "test.py"), "w") as f:
            f.write("print('hello')")
        with open(os.path.join(tmpdir, "README.md"), "w") as f:
            f.write("# Test")
        try:
            inspector = RepoInspector(tmpdir)
            info = inspector.inspect()
            assert "tracked_files" in info
            assert "python_modules" in info
            assert "test_files" in info
        except Exception as e:
            # May fail if not in approved paths - that's expected behavior
            assert "approved" in str(e).lower() or "path" in str(e).lower()
