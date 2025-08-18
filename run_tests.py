#!/usr/bin/env python3

import sys
import os
import subprocess

def run_tests(test_module=None, verbose=True):
    
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)
    
    cmd = ["python", "-m", "pytest"]
    
    if verbose:
        cmd.append("-v")
    
    if test_module:
        cmd.append(f"testing/{test_module}")
    else:
        cmd.append("testing/")
    
    try:
        import pytest_cov
        cmd.extend(["--cov=controllers", "--cov=routes", "--cov-report=term-missing"])
    except ImportError:
        print("Note: pytest-cov not installed. Install for coverage reports.")
    
    print(f"Running: {' '.join(cmd)}")
    print("-" * 50)
    result = subprocess.run(cmd)
    return result.returncode

def main():
    print("Personal Finance Tracker API - Test Suite")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        test_module = sys.argv[1]
        print(f"Running tests for: {test_module}")
        return_code = run_tests(test_module)
    else:
        print("Running all tests...")
        return_code = run_tests()
    
    if return_code == 0:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed!")
    
    return return_code

if __name__ == "__main__":
    sys.exit(main())
