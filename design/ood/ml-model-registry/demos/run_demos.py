#!/usr/bin/env python3
"""
Demo Runner Script - ML Model Registry
======================================

This script provides a convenient way to run all demo scripts with proper
setup, verification, and cleanup. It also provides options to run individual
demos or all demos in sequence.

Usage:
  python demos/run_demos.py --all                    # Run all demos
  python demos/run_demos.py --demo 1                 # Run specific demo
  python demos/run_demos.py --demo 1,3,5            # Run multiple demos
  python demos/run_demos.py --list                   # List available demos
  python demos/run_demos.py --check                  # Check prerequisites only
  python demos/run_demos.py --clean                  # Clean up demo data

Features:
- Automatic prerequisite checking
- Progress tracking and reporting
- Error handling and recovery
- Demo data cleanup
- Comprehensive verification
"""

import argparse
import subprocess
import sys
import time
import requests
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime


# Configuration
BASE_URL = "http://localhost:8000/api/v1"
HEALTH_URL = "http://localhost:8000/health"
DEMOS_DIR = Path(__file__).parent
PROJECT_ROOT = DEMOS_DIR.parent

# Demo configurations
DEMOS = {
    1: {
        "name": "Basic Model Registration",
        "script": "01_basic_model_registration.py",
        "description": "Demonstrates core model and version creation functionality",
        "duration_estimate": "2-3 minutes",
        "prerequisites": ["API running"],
        "use_cases": ["Model registration", "Version management", "Basic search"]
    },
    2: {
        "name": "Model Lifecycle Management",
        "script": "02_model_lifecycle_management.py", 
        "description": "Shows model status transitions and promotion workflows",
        "duration_estimate": "3-4 minutes",
        "prerequisites": ["API running"],
        "use_cases": ["Status management", "Model promotion", "Production deployment"]
    },
    3: {
        "name": "Evaluation and Metrics",
        "script": "03_evaluation_and_metrics.py",
        "description": "Demonstrates evaluation tracking and model comparison features",
        "duration_estimate": "4-5 minutes", 
        "prerequisites": ["API running"],
        "use_cases": ["Performance tracking", "Model comparison", "Metrics visualization"]
    },
    4: {
        "name": "Artifact Operations",
        "script": "04_artifact_operations.py",
        "description": "Shows artifact upload, download, and format support",
        "duration_estimate": "3-4 minutes",
        "prerequisites": ["API running", "sklearn package"],
        "use_cases": ["Artifact storage", "Multi-format support", "File management"]
    },
    5: {
        "name": "End-to-End Workflow",
        "script": "05_end_to_end_workflow.py",
        "description": "Complete MLOps workflow from experimentation to production",
        "duration_estimate": "8-10 minutes",
        "prerequisites": ["API running", "sklearn package", "numpy package"],
        "use_cases": ["Complete MLOps", "Experimentation", "Model governance"]
    }
}


class DemoRunner:
    """Main demo runner class with progress tracking and verification."""
    
    def __init__(self):
        self.results = {}
        self.start_time = None
        self.api_available = False
    
    def check_prerequisites(self) -> bool:
        """Check all prerequisites for running demos."""
        print("Checking prerequisites...")
        
        # Check API health
        try:
            response = requests.get(HEALTH_URL, timeout=5)
            self.api_available = response.status_code == 200 and response.json().get("status") == "healthy"
            if self.api_available:
                print("✓ API is healthy and accessible")
            else:
                print("✗ API is not healthy")
                print("  Please start the application first:")
                print("    poetry run python -m app.main")
                return False
        except Exception as e:
            print("✗ Cannot connect to API")
            print(f"  Error: {e}")
            print("  Please ensure the application is running on localhost:8000")
            return False
        
        # Check Python packages
        required_packages = ["requests", "sklearn", "numpy", "joblib"]
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package)
                print(f"✓ {package} is available")
            except ImportError:
                missing_packages.append(package)
                print(f"✗ {package} is missing")
        
        if missing_packages:
            print(f"\nMissing packages: {', '.join(missing_packages)}")
            print("Install with: pip install " + " ".join(missing_packages))
            return False
        
        # Check demo files exist
        missing_scripts = []
        for demo_id, demo_info in DEMOS.items():
            script_path = DEMOS_DIR / demo_info["script"]
            if script_path.exists():
                print(f"✓ Demo {demo_id} script found")
            else:
                missing_scripts.append(demo_info["script"])
                print(f"✗ Demo {demo_id} script missing: {script_path}")
        
        if missing_scripts:
            print(f"\nMissing demo scripts: {', '.join(missing_scripts)}")
            return False
        
        print("✓ All prerequisites satisfied")
        return True
    
    def list_demos(self):
        """List all available demos with descriptions."""
        print("Available ML Model Registry Demos")
        print("=" * 50)
        
        for demo_id, demo_info in DEMOS.items():
            print(f"\nDemo {demo_id}: {demo_info['name']}")
            print(f"  Script: {demo_info['script']}")
            print(f"  Description: {demo_info['description']}")
            print(f"  Duration: {demo_info['duration_estimate']}")
            print(f"  Use Cases: {', '.join(demo_info['use_cases'])}")
    
    def run_demo(self, demo_id: int) -> Dict[str, Any]:
        """Run a specific demo and return results."""
        if demo_id not in DEMOS:
            return {"success": False, "error": f"Demo {demo_id} not found"}
        
        demo_info = DEMOS[demo_id]
        script_path = DEMOS_DIR / demo_info["script"]
        
        print(f"\n{'=' * 60}")
        print(f"Running Demo {demo_id}: {demo_info['name']}")
        print(f"{'=' * 60}")
        print(f"Script: {demo_info['script']}")
        print(f"Expected duration: {demo_info['duration_estimate']}")
        
        start_time = time.time()
        
        try:
            # Run the demo script
            result = subprocess.run(
                [sys.executable, str(script_path)],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )
            
            duration = time.time() - start_time
            
            # Parse output for success/failure indication
            output_lines = result.stdout.split('\n')
            demo_result = "UNKNOWN"
            
            for line in output_lines:
                if "Demo Result: SUCCESS" in line:
                    demo_result = "SUCCESS"
                    break
                elif "Demo Result: FAILED" in line:
                    demo_result = "FAILED"
                    break
            
            return {
                "success": result.returncode == 0 and demo_result == "SUCCESS",
                "duration": duration,
                "demo_result": demo_result,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "output_lines": len(output_lines)
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Demo timed out after 10 minutes",
                "duration": time.time() - start_time
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "duration": time.time() - start_time
            }
    
    def run_multiple_demos(self, demo_ids: List[int]) -> Dict[int, Dict[str, Any]]:
        """Run multiple demos in sequence."""
        self.start_time = time.time()
        results = {}
        
        print(f"Running {len(demo_ids)} demos in sequence...")
        print(f"Demo IDs: {', '.join(map(str, demo_ids))}")
        
        for i, demo_id in enumerate(demo_ids, 1):
            print(f"\n[{i}/{len(demo_ids)}] Starting Demo {demo_id}...")
            
            result = self.run_demo(demo_id)
            results[demo_id] = result
            
            if result["success"]:
                print(f"✓ Demo {demo_id} completed successfully ({result.get('duration', 0):.1f}s)")
            else:
                print(f"✗ Demo {demo_id} failed")
                if "error" in result:
                    print(f"  Error: {result['error']}")
                
                # Ask if user wants to continue
                if len(demo_ids) > 1 and i < len(demo_ids):
                    response = input("\nDemo failed. Continue with remaining demos? (y/n): ")
                    if response.lower() != 'y':
                        print("Stopping demo execution.")
                        break
        
        return results
    
    def print_summary(self, results: Dict[int, Dict[str, Any]]):
        """Print a comprehensive summary of demo results."""
        total_duration = time.time() - self.start_time if self.start_time else 0
        
        print(f"\n{'=' * 70}")
        print("DEMO EXECUTION SUMMARY")
        print(f"{'=' * 70}")
        
        print(f"Execution started: {datetime.fromtimestamp(self.start_time).strftime('%Y-%m-%d %H:%M:%S') if self.start_time else 'N/A'}")
        print(f"Total duration: {total_duration:.1f} seconds")
        print(f"Demos executed: {len(results)}")
        
        # Summary table
        print(f"\nDetailed Results:")
        print("-" * 70)
        print(f"{'Demo':<6} {'Name':<25} {'Status':<10} {'Duration':<10} {'Output':<10}")
        print("-" * 70)
        
        successful = 0
        failed = 0
        
        for demo_id, result in results.items():
            demo_name = DEMOS[demo_id]["name"][:23]  # Truncate if too long
            status = "SUCCESS" if result["success"] else "FAILED"
            duration = f"{result.get('duration', 0):.1f}s"
            output_lines = result.get("output_lines", 0)
            
            print(f"{demo_id:<6} {demo_name:<25} {status:<10} {duration:<10} {output_lines:<10}")
            
            if result["success"]:
                successful += 1
            else:
                failed += 1
        
        print("-" * 70)
        print(f"Successful: {successful}, Failed: {failed}")
        
        # Show failures in detail
        if failed > 0:
            print(f"\nFailure Details:")
            for demo_id, result in results.items():
                if not result["success"]:
                    demo_name = DEMOS[demo_id]["name"]
                    print(f"\nDemo {demo_id} ({demo_name}):")
                    if "error" in result:
                        print(f"  Error: {result['error']}")
                    if result.get("return_code") != 0:
                        print(f"  Return code: {result['return_code']}")
                    if result.get("stderr"):
                        print(f"  stderr: {result['stderr'][:200]}...")
        
        # Overall result
        overall_success = failed == 0
        print(f"\nOverall Result: {'SUCCESS' if overall_success else 'PARTIAL SUCCESS' if successful > 0 else 'FAILED'}")
        
        if overall_success:
            print("🎉 All demos completed successfully!")
            print("\nYou can now:")
            print("- Explore the API at http://localhost:8000/docs")
            print("- View the created models and data in the application")
            print("- Try the sample training scripts in the examples/ directory")
        else:
            print("\n⚠️  Some demos failed. Check the error details above.")
            print("Common issues:")
            print("- API not running (poetry run python -m app.main)")
            print("- Missing dependencies (poetry install)")
            print("- Port conflicts or network issues")
    
    def cleanup_demo_data(self) -> bool:
        """Clean up demo data by deleting test models."""
        if not self.api_available:
            print("✗ API not available for cleanup")
            return False
        
        print("Cleaning up demo data...")
        
        try:
            # Get all models
            response = requests.get(f"{BASE_URL}/models/")
            if response.status_code != 200:
                print("✗ Failed to retrieve models for cleanup")
                return False
            
            models = response.json()
            demo_models = []
            
            # Identify demo models by name patterns
            demo_patterns = [
                "demo-classification-model",
                "lifecycle-demo-model", 
                "evaluation-demo-model",
                "artifact-demo-model",
                "customer-churn-prediction"
            ]
            
            for model in models:
                model_name = model.get("name", "").lower()
                if any(pattern in model_name for pattern in demo_patterns):
                    demo_models.append(model)
            
            if not demo_models:
                print("✓ No demo models found to clean up")
                return True
            
            print(f"Found {len(demo_models)} demo models to delete:")
            for model in demo_models:
                print(f"  - {model['name']} (ID: {model['id'][:8]}...)")
            
            # Confirm deletion
            response = input("\nDelete these demo models? (y/N): ")
            if response.lower() != 'y':
                print("Cleanup cancelled")
                return True
            
            # Delete models
            deleted = 0
            for model in demo_models:
                delete_response = requests.delete(f"{BASE_URL}/models/{model['id']}")
                if delete_response.status_code == 204:
                    print(f"✓ Deleted {model['name']}")
                    deleted += 1
                else:
                    print(f"✗ Failed to delete {model['name']}")
            
            print(f"\n✓ Cleanup completed: {deleted}/{len(demo_models)} models deleted")
            return True
            
        except Exception as e:
            print(f"✗ Cleanup failed: {e}")
            return False


def parse_demo_ids(demo_string: str) -> List[int]:
    """Parse demo IDs from comma-separated string."""
    try:
        demo_ids = [int(x.strip()) for x in demo_string.split(',')]
        invalid_ids = [x for x in demo_ids if x not in DEMOS]
        if invalid_ids:
            raise ValueError(f"Invalid demo IDs: {invalid_ids}")
        return demo_ids
    except ValueError as e:
        raise argparse.ArgumentTypeError(f"Invalid demo IDs: {e}")


def main():
    """Main entry point for the demo runner."""
    parser = argparse.ArgumentParser(
        description="Run ML Model Registry demo scripts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python demos/run_demos.py --all                    # Run all demos
  python demos/run_demos.py --demo 1                 # Run demo 1 only
  python demos/run_demos.py --demo 1,3,5            # Run demos 1, 3, and 5
  python demos/run_demos.py --list                   # List available demos
  python demos/run_demos.py --check                  # Check prerequisites
  python demos/run_demos.py --clean                  # Clean up demo data
        """
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--all", action="store_true", help="Run all demos")
    group.add_argument("--demo", type=parse_demo_ids, help="Run specific demo(s) (comma-separated IDs)")
    group.add_argument("--list", action="store_true", help="List available demos")
    group.add_argument("--check", action="store_true", help="Check prerequisites only")
    group.add_argument("--clean", action="store_true", help="Clean up demo data")
    
    args = parser.parse_args()
    
    runner = DemoRunner()
    
    if args.list:
        runner.list_demos()
        return
    
    if args.check:
        success = runner.check_prerequisites()
        sys.exit(0 if success else 1)
    
    if args.clean:
        runner.check_prerequisites()  # Need API for cleanup
        success = runner.cleanup_demo_data()
        sys.exit(0 if success else 1)
    
    # Check prerequisites before running demos
    if not runner.check_prerequisites():
        sys.exit(1)
    
    # Determine which demos to run
    if args.all:
        demo_ids = list(DEMOS.keys())
    else:
        demo_ids = args.demo
    
    print(f"\nPreparing to run {len(demo_ids)} demo(s)...")
    
    # Show what will be tested
    print("\nThis will test the following use cases:")
    use_cases = set()
    for demo_id in demo_ids:
        use_cases.update(DEMOS[demo_id]["use_cases"])
    
    for use_case in sorted(use_cases):
        print(f"  - {use_case}")
    
    estimated_time = sum(
        int(DEMOS[demo_id]["duration_estimate"].split('-')[1].split()[0]) 
        for demo_id in demo_ids
    )
    print(f"\nEstimated total time: ~{estimated_time} minutes")
    
    # Confirm execution
    response = input("\nProceed with demo execution? (y/N): ")
    if response.lower() != 'y':
        print("Demo execution cancelled")
        return
    
    # Run the demos
    results = runner.run_multiple_demos(demo_ids)
    
    # Print summary
    runner.print_summary(results)
    
    # Exit with appropriate code
    failed_count = sum(1 for result in results.values() if not result["success"])
    sys.exit(0 if failed_count == 0 else 1)


if __name__ == "__main__":
    main()