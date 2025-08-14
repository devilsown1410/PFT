import pytest
import sys
import os

def run_all_tests():
    print("Running Tests for Personal Finance Tracker...")
    print("=" * 55)
    test_files = [
        "app.py",
        "test_models.py",
    ]
    
    total_passed = 0
    total_failed = 0
    
    for test_file in test_files:
        if os.path.exists(test_file):
            print(f"\n Running {test_file}...")
            print("-" * 40)
            result = pytest.main([test_file, "-v", "--tb=short"])
            if result == 0:
                print(f" {test_file} - All tests passed!")
                total_passed += 1
            else:
                print(f" {test_file} - Some tests failed!")
                total_failed += 1
        else:
            print(f" {test_file} not found, skipping...")
    
    print("\n" + "=" * 55)
    print(f"SUMMARY: {total_passed} files passed, {total_failed} files had failures")
    print("Test run completed!")

def run_specific_test(test_name):
    if os.path.exists(test_name):
        print(f"Running {test_name}...")
        pytest.main([test_name, "-v"])
    else:
        print(f" Test file {test_name} not found!")

def list_available_tests():
    test_files = [f for f in os.listdir('.') if f.startswith('test_') or f == 'app.py']
    print("Available test files:")
    for i, test_file in enumerate(test_files, 1):
        print(f"  {i}. {test_file}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]
        run_specific_test(command)
    else:
        run_all_tests()
