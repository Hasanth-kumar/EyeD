#!/usr/bin/env python3
"""
Phase 5 Test Runner - Comprehensive Testing Suite
Runs all Phase 5 tests and provides detailed reporting
"""

import unittest
import sys
import os
import time
from datetime import datetime

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

def run_test_suite(test_class, suite_name):
    """Run a specific test suite and return results"""
    print(f"\n{'='*60}")
    print(f"Running {suite_name}")
    print(f"{'='*60}")
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
    
    # Run tests
    start_time = time.time()
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)
    end_time = time.time()
    
    # Calculate statistics
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    skipped = len(result.skipped) if hasattr(result, 'skipped') else 0
    duration = end_time - start_time
    
    # Print summary
    print(f"\n{suite_name} Results:")
    print(f"  Total Tests: {total_tests}")
    print(f"  Failures: {failures}")
    print(f"  Errors: {errors}")
    print(f"  Skipped: {skipped}")
    print(f"  Duration: {duration:.2f} seconds")
    
    return {
        'suite': suite_name,
        'total': total_tests,
        'failures': failures,
        'errors': errors,
        'skipped': skipped,
        'duration': duration,
        'success': failures == 0 and errors == 0
    }

def run_all_tests():
    """Run all Phase 5 test suites"""
    print("🚀 Phase 5 Comprehensive Testing Suite")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Import test classes
    try:
        from test_services import (
            TestServiceFactory, 
            TestAttendanceService, 
            TestAttendanceServiceIntegration
        )
        from test_repositories import (
            TestAttendanceRepository, 
            TestAttendanceRepositoryEdgeCases
        )
        from test_dashboard_components import (
            TestDashboardOverviewComponent,
            TestDashboardAttendanceTableComponent,
            TestDashboardAnalyticsComponent,
            TestDashboardRegistrationComponent,
            TestDashboardComponentIntegration,
            TestDashboardComponentMocking
        )
        from test_integration import (
            TestCompleteSystemIntegration,
            TestSystemWorkflowIntegration
        )
    except ImportError as e:
        print(f"❌ Error importing test modules: {e}")
        print("Make sure all test files are in the tests directory")
        return
    
    # Define test suites
    test_suites = [
        (TestServiceFactory, "Service Factory Tests"),
        (TestAttendanceService, "Attendance Service Tests"),
        (TestAttendanceServiceIntegration, "Attendance Service Integration Tests"),
        (TestAttendanceRepository, "Attendance Repository Tests"),
        (TestAttendanceRepositoryEdgeCases, "Attendance Repository Edge Cases"),
        (TestDashboardOverviewComponent, "Dashboard Overview Component Tests"),
        (TestDashboardAttendanceTableComponent, "Dashboard Attendance Table Component Tests"),
        (TestDashboardAnalyticsComponent, "Dashboard Analytics Component Tests"),
        (TestDashboardRegistrationComponent, "Dashboard Registration Component Tests"),
        (TestDashboardComponentIntegration, "Dashboard Component Integration Tests"),
        (TestDashboardComponentMocking, "Dashboard Component Mocking Tests"),
        (TestCompleteSystemIntegration, "Complete System Integration Tests"),
        (TestSystemWorkflowIntegration, "System Workflow Integration Tests")
    ]
    
    # Run all test suites
    results = []
    total_start_time = time.time()
    
    for test_class, suite_name in test_suites:
        try:
            result = run_test_suite(test_class, suite_name)
            results.append(result)
        except Exception as e:
            print(f"❌ Error running {suite_name}: {e}")
            results.append({
                'suite': suite_name,
                'total': 0,
                'failures': 0,
                'errors': 1,
                'skipped': 0,
                'duration': 0,
                'success': False
            })
    
    total_end_time = time.time()
    total_duration = total_end_time - total_start_time
    
    # Print comprehensive summary
    print(f"\n{'='*60}")
    print("PHASE 5 TESTING COMPLETE")
    print(f"{'='*60}")
    print(f"Total Duration: {total_duration:.2f} seconds")
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Calculate overall statistics
    total_tests = sum(r['total'] for r in results)
    total_failures = sum(r['failures'] for r in results)
    total_errors = sum(r['errors'] for r in results)
    total_skipped = sum(r['skipped'] for r in results)
    successful_suites = sum(1 for r in results if r['success'])
    total_suites = len(results)
    
    print(f"\nOverall Results:")
    print(f"  Test Suites: {total_suites}")
    print(f"  Successful Suites: {successful_suites}")
    print(f"  Failed Suites: {total_suites - successful_suites}")
    print(f"  Total Tests: {total_tests}")
    print(f"  Total Failures: {total_failures}")
    print(f"  Total Errors: {total_errors}")
    print(f"  Total Skipped: {total_skipped}")
    
    # Print suite-by-suite results
    print(f"\nSuite-by-Suite Results:")
    print(f"{'Suite Name':<40} {'Status':<10} {'Tests':<8} {'Fail':<6} {'Error':<6} {'Duration':<10}")
    print("-" * 80)
    
    for result in results:
        status = "✅ PASS" if result['success'] else "❌ FAIL"
        print(f"{result['suite']:<40} {status:<10} {result['total']:<8} {result['failures']:<6} {result['errors']:<6} {result['duration']:<10.2f}s")
    
    # Print detailed failure information
    if total_failures > 0 or total_errors > 0:
        print(f"\n❌ Test Failures and Errors Detected:")
        print("Review the output above for detailed failure information.")
        print("Common issues:")
        print("  - Missing dependencies or imports")
        print("  - File path issues")
        print("  - Mock configuration problems")
        print("  - Service initialization errors")
    
    # Print success message if all tests passed
    if total_failures == 0 and total_errors == 0:
        print(f"\n🎉 ALL TESTS PASSED!")
        print("Phase 5 implementation is working correctly.")
        print("The system demonstrates:")
        print("  ✅ Clean architecture with service layer")
        print("  ✅ Proper dependency injection")
        print("  ✅ Comprehensive error handling")
        print("  ✅ Robust data persistence")
        print("  ✅ UI component integration")
        print("  ✅ Complete workflow testing")
    
    return {
        'total_tests': total_tests,
        'total_failures': total_failures,
        'total_errors': total_errors,
        'total_skipped': total_skipped,
        'successful_suites': successful_suites,
        'total_suites': total_suites,
        'total_duration': total_duration,
        'all_passed': total_failures == 0 and total_errors == 0
    }

def run_specific_suite(suite_name):
    """Run a specific test suite by name"""
    print(f"🎯 Running specific test suite: {suite_name}")
    
    # Map suite names to test classes
    suite_map = {
        'services': 'TestServiceFactory, TestAttendanceService, TestAttendanceServiceIntegration',
        'repositories': 'TestAttendanceRepository, TestAttendanceRepositoryEdgeCases',
        'dashboard': 'TestDashboardOverviewComponent, TestDashboardAttendanceTableComponent, TestDashboardAnalyticsComponent, TestDashboardRegistrationComponent, TestDashboardComponentIntegration, TestDashboardComponentMocking',
        'integration': 'TestCompleteSystemIntegration, TestSystemWorkflowIntegration',
        'all': 'all'
    }
    
    if suite_name not in suite_map:
        print(f"❌ Unknown test suite: {suite_name}")
        print(f"Available suites: {', '.join(suite_map.keys())}")
        return
    
    if suite_name == 'all':
        return run_all_tests()
    
    # Run specific suite
    suite_names = suite_map[suite_name].split(', ')
    print(f"Running suites: {', '.join(suite_names)}")
    
    # Import and run specific suites
    results = []
    for suite_name_clean in suite_names:
        try:
            # Map suite names to test classes
            if suite_name_clean == 'TestServiceFactory':
                from test_services import TestServiceFactory
                result = run_test_suite(TestServiceFactory, "Service Factory Tests")
            elif suite_name_clean == 'TestAttendanceService':
                from test_services import TestAttendanceService
                result = run_test_suite(TestAttendanceService, "Attendance Service Tests")
            elif suite_name_clean == 'TestAttendanceServiceIntegration':
                from test_services import TestAttendanceServiceIntegration
                result = run_test_suite(TestAttendanceServiceIntegration, "Attendance Service Integration Tests")
            elif suite_name_clean == 'TestAttendanceRepository':
                from test_repositories import TestAttendanceRepository
                result = run_test_suite(TestAttendanceRepository, "Attendance Repository Tests")
            elif suite_name_clean == 'TestAttendanceRepositoryEdgeCases':
                from test_repositories import TestAttendanceRepositoryEdgeCases
                result = run_test_suite(TestAttendanceRepositoryEdgeCases, "Attendance Repository Edge Cases")
            elif suite_name_clean == 'TestDashboardOverviewComponent':
                from test_dashboard_components import TestDashboardOverviewComponent
                result = run_test_suite(TestDashboardOverviewComponent, "Dashboard Overview Component Tests")
            elif suite_name_clean == 'TestDashboardAttendanceTableComponent':
                from test_dashboard_components import TestDashboardAttendanceTableComponent
                result = run_test_suite(TestDashboardAttendanceTableComponent, "Dashboard Attendance Table Component Tests")
            elif suite_name_clean == 'TestDashboardAnalyticsComponent':
                from test_dashboard_components import TestDashboardAnalyticsComponent
                result = run_test_suite(TestDashboardAnalyticsComponent, "Dashboard Analytics Component Tests")
            elif suite_name_clean == 'TestDashboardRegistrationComponent':
                from test_dashboard_components import TestDashboardRegistrationComponent
                result = run_test_suite(TestDashboardRegistrationComponent, "Dashboard Registration Component Tests")
            elif suite_name_clean == 'TestDashboardComponentIntegration':
                from test_dashboard_components import TestDashboardComponentIntegration
                result = run_test_suite(TestDashboardComponentIntegration, "Dashboard Component Integration Tests")
            elif suite_name_clean == 'TestDashboardComponentMocking':
                from test_dashboard_components import TestDashboardComponentMocking
                result = run_test_suite(TestDashboardComponentMocking, "Dashboard Component Mocking Tests")
            elif suite_name_clean == 'TestCompleteSystemIntegration':
                from test_integration import TestCompleteSystemIntegration
                result = run_test_suite(TestCompleteSystemIntegration, "Complete System Integration Tests")
            elif suite_name_clean == 'TestSystemWorkflowIntegration':
                from test_integration import TestSystemWorkflowIntegration
                result = run_test_suite(TestSystemWorkflowIntegration, "System Workflow Integration Tests")
            
            results.append(result)
        except Exception as e:
            print(f"❌ Error running {suite_name_clean}: {e}")
            results.append({
                'suite': suite_name_clean,
                'total': 0,
                'failures': 0,
                'errors': 1,
                'skipped': 0,
                'duration': 0,
                'success': False
            })
    
    return results


if __name__ == '__main__':
    # Check command line arguments
    if len(sys.argv) > 1:
        suite_name = sys.argv[1].lower()
        run_specific_suite(suite_name)
    else:
        # Run all tests by default
        run_all_tests()

