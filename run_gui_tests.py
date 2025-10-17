#!/usr/bin/env python3
"""
REDLINE GUI Test Runner
Run all GUI tests with different options.
"""

import sys
import os
import argparse
import subprocess
import time

def run_quick_tests():
    """Run quick GUI tests."""
    print("Running Quick GUI Tests...")
    print("=" * 50)
    
    try:
        result = subprocess.run([sys.executable, "test_gui_quick.py"], 
                              capture_output=True, text=True, timeout=60)
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("❌ Quick tests timed out")
        return False
    except Exception as e:
        print(f"❌ Error running quick tests: {str(e)}")
        return False

def run_performance_tests():
    """Run GUI performance tests."""
    print("Running GUI Performance Tests...")
    print("=" * 50)
    
    try:
        result = subprocess.run([sys.executable, "test_gui_performance.py"], 
                              capture_output=True, text=True, timeout=300)
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("❌ Performance tests timed out")
        return False
    except Exception as e:
        print(f"❌ Error running performance tests: {str(e)}")
        return False

def run_integration_tests():
    """Run full GUI integration tests."""
    print("Running Full GUI Integration Tests...")
    print("=" * 50)
    
    try:
        result = subprocess.run([sys.executable, "test_gui_integration.py"], 
                              capture_output=True, text=True, timeout=600)
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("❌ Integration tests timed out")
        return False
    except Exception as e:
        print(f"❌ Error running integration tests: {str(e)}")
        return False

def run_all_tests():
    """Run all GUI tests."""
    print("Running All GUI Tests...")
    print("=" * 50)
    
    tests = [
        ("Quick Tests", run_quick_tests),
        ("Performance Tests", run_performance_tests),
        ("Integration Tests", run_integration_tests)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{test_name}")
        print("-" * 30)
        
        start_time = time.time()
        success = test_func()
        end_time = time.time()
        
        results[test_name] = {
            'success': success,
            'time': end_time - start_time
        }
        
        if success:
            print(f"✅ {test_name} passed in {end_time - start_time:.1f}s")
        else:
            print(f"❌ {test_name} failed in {end_time - start_time:.1f}s")
    
    # Print summary
    print("\n" + "=" * 50)
    print("Test Summary:")
    print("-" * 30)
    
    total_passed = 0
    total_time = 0
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result['success'] else "❌ FAILED"
        print(f"{test_name:20} {status:10} ({result['time']:.1f}s)")
        
        if result['success']:
            total_passed += 1
        total_time += result['time']
    
    print(f"\nOverall: {total_passed}/{len(tests)} tests passed in {total_time:.1f}s")
    
    return total_passed == len(tests)

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Run REDLINE GUI tests")
    parser.add_argument("--quick", action="store_true", help="Run quick tests only")
    parser.add_argument("--performance", action="store_true", help="Run performance tests only")
    parser.add_argument("--integration", action="store_true", help="Run integration tests only")
    parser.add_argument("--all", action="store_true", help="Run all tests (default)")
    
    args = parser.parse_args()
    
    # If no specific test is requested, run all
    if not any([args.quick, args.performance, args.integration]):
        args.all = True
    
    print("REDLINE GUI Test Runner")
    print("=" * 50)
    
    success = True
    
    if args.quick:
        success = run_quick_tests()
    elif args.performance:
        success = run_performance_tests()
    elif args.integration:
        success = run_integration_tests()
    elif args.all:
        success = run_all_tests()
    
    if success:
        print("\n✅ All requested tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
