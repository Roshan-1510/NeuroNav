#!/usr/bin/env python3
"""
NeuroNav Test Runner
Runs all tests and provides a summary report
"""

import subprocess
import sys
import os

def run_tests():
    """Run all tests and return results"""
    print("🧪 Running NeuroNav API Tests...")
    print("=" * 50)
    
    # Change to the correct directory
    test_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(test_dir)
    
    try:
        # Run pytest with verbose output
        result = subprocess.run([
            sys.executable, '-m', 'pytest', 
            os.path.join(parent_dir, 'tests'),
            '-v',
            '--tb=short',
            '--color=yes'
        ], capture_output=True, text=True, cwd=parent_dir)
        
        print("📊 Test Output:")
        print("-" * 30)
        print(result.stdout)
        
        if result.stderr:
            print("⚠️  Warnings/Errors:")
            print("-" * 30)
            print(result.stderr)
        
        print("=" * 50)
        
        if result.returncode == 0:
            print("✅ All tests passed!")
            return True
        else:
            print("❌ Some tests failed!")
            print(f"Exit code: {result.returncode}")
            return False
            
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False

def main():
    """Main test runner function"""
    print("🚀 NeuroNav Test Suite")
    print("Testing admin APIs for quiz questions and resources")
    print()
    
    success = run_tests()
    
    if success:
        print("\n🎉 Test suite completed successfully!")
        print("All admin APIs are working correctly.")
    else:
        print("\n💥 Test suite failed!")
        print("Please check the output above for details.")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)