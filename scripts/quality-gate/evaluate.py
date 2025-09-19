
#!/usr/bin/env python3
"""
Quality Gate Evaluation Script
Sprint 2 - Advanced Capabilities Implementation

This script evaluates the quality gate based on test results, security scans,
and performance benchmarks to determine if the build should pass or fail.
"""

import json
import os
import sys
import glob
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Any, Tuple
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class QualityGateEvaluator:
    """Evaluates quality gates based on various metrics and thresholds."""
    
    def __init__(self):
        self.results = {
            'timestamp': None,
            'overall_status': 'UNKNOWN',
            'gates': {},
            'metrics': {},
            'recommendations': []
        }
        
        # Quality gate thresholds (configurable via environment variables)
        self.thresholds = {
            'max_critical_vulnerabilities': int(os.getenv('MAX_CRITICAL_VULNERABILITIES', '0')),
            'max_high_vulnerabilities': int(os.getenv('MAX_HIGH_VULNERABILITIES', '5')),
            'max_medium_vulnerabilities': int(os.getenv('MAX_MEDIUM_VULNERABILITIES', '20')),
            'min_test_coverage': float(os.getenv('MIN_TEST_COVERAGE', '80.0')),
            'max_test_failures': int(os.getenv('MAX_TEST_FAILURES', '0')),
            'max_lint_errors': int(os.getenv('MAX_LINT_ERRORS', '0')),
            'max_performance_degradation': float(os.getenv('MAX_PERFORMANCE_DEGRADATION', '20.0')),
            'min_performance_score': float(os.getenv('MIN_PERFORMANCE_SCORE', '70.0'))
        }
        
        logger.info(f"Quality gate thresholds: {self.thresholds}")

    def evaluate_security_gate(self) -> Tuple[bool, Dict[str, Any]]:
        """Evaluate security-related quality gates."""
        logger.info("Evaluating security quality gate...")
        
        gate_result = {
            'status': 'PASS',
            'vulnerabilities': {
                'critical': 0,
                'high': 0,
                'medium': 0,
                'low': 0
            },
            'issues': [],
            'tools_run': []
        }
        
        # Check for security scan results
        security_files = [
            'trivy-results.sarif',
            'kics-results/results.sarif',
            'snyk.sarif',
            'checkov-results.sarif',
            'security-report.json'
        ]
        
        for file_path in security_files:
            if os.path.exists(file_path):
                tool_name = file_path.split('-')[0].split('/')[0]
                gate_result['tools_run'].append(tool_name)
                
                try:
                    if file_path.endswith('.sarif'):
                        vulnerabilities = self._parse_sarif_file(file_path)
                    elif file_path.endswith('.json'):
                        vulnerabilities = self._parse_security_json(file_path)
                    else:
                        continue
                    
                    # Aggregate vulnerabilities
                    for severity, count in vulnerabilities.items():
                        if severity in gate_result['vulnerabilities']:
                            gate_result['vulnerabilities'][severity] += count
                            
                except Exception as e:
                    logger.error(f"Error parsing {file_path}: {e}")
                    gate_result['issues'].append(f"Failed to parse {file_path}: {e}")
        
        # Evaluate against thresholds
        critical_count = gate_result['vulnerabilities']['critical']
        high_count = gate_result['vulnerabilities']['high']
        medium_count = gate_result['vulnerabilities']['medium']
        
        if critical_count > self.thresholds['max_critical_vulnerabilities']:
            gate_result['status'] = 'FAIL'
            gate_result['issues'].append(
                f"Critical vulnerabilities ({critical_count}) exceed threshold ({self.thresholds['max_critical_vulnerabilities']})"
            )
        
        if high_count > self.thresholds['max_high_vulnerabilities']:
            gate_result['status'] = 'FAIL'
            gate_result['issues'].append(
                f"High vulnerabilities ({high_count}) exceed threshold ({self.thresholds['max_high_vulnerabilities']})"
            )
        
        if medium_count > self.thresholds['max_medium_vulnerabilities']:
            gate_result['status'] = 'FAIL'
            gate_result['issues'].append(
                f"Medium vulnerabilities ({medium_count}) exceed threshold ({self.thresholds['max_medium_vulnerabilities']})"
            )
        
        return gate_result['status'] == 'PASS', gate_result

    def evaluate_testing_gate(self) -> Tuple[bool, Dict[str, Any]]:
        """Evaluate testing-related quality gates."""
        logger.info("Evaluating testing quality gate...")
        
        gate_result = {
            'status': 'PASS',
            'test_results': {
                'total_tests': 0,
                'passed_tests': 0,
                'failed_tests': 0,
                'skipped_tests': 0
            },
            'coverage': 0.0,
            'issues': [],
            'test_suites': []
        }
        
        # Check for test result files
        test_files = glob.glob('**/test-results.xml', recursive=True) + \
                    glob.glob('**/integration-test-results.xml', recursive=True) + \
                    glob.glob('**/molecule-test-results-*', recursive=True)
        
        for test_file in test_files:
            try:
                if test_file.endswith('.xml'):
                    test_data = self._parse_junit_xml(test_file)
                    gate_result['test_suites'].append(test_data)
                    
                    # Aggregate results
                    gate_result['test_results']['total_tests'] += test_data.get('total', 0)
                    gate_result['test_results']['passed_tests'] += test_data.get('passed', 0)
                    gate_result['test_results']['failed_tests'] += test_data.get('failed', 0)
                    gate_result['test_results']['skipped_tests'] += test_data.get('skipped', 0)
                    
            except Exception as e:
                logger.error(f"Error parsing test file {test_file}: {e}")
                gate_result['issues'].append(f"Failed to parse {test_file}: {e}")
        
        # Calculate coverage if available
        coverage_files = glob.glob('**/coverage.json', recursive=True)
        if coverage_files:
            try:
                with open(coverage_files[0], 'r') as f:
                    coverage_data = json.load(f)
                    gate_result['coverage'] = coverage_data.get('totals', {}).get('percent_covered', 0.0)
            except Exception as e:
                logger.error(f"Error parsing coverage file: {e}")
        
        # Evaluate against thresholds
        failed_tests = gate_result['test_results']['failed_tests']
        coverage = gate_result['coverage']
        
        if failed_tests > self.thresholds['max_test_failures']:
            gate_result['status'] = 'FAIL'
            gate_result['issues'].append(
                f"Test failures ({failed_tests}) exceed threshold ({self.thresholds['max_test_failures']})"
            )
        
        if coverage < self.thresholds['min_test_coverage']:
            gate_result['status'] = 'FAIL'
            gate_result['issues'].append(
                f"Test coverage ({coverage}%) below threshold ({self.thresholds['min_test_coverage']}%)"
            )
        
        return gate_result['status'] == 'PASS', gate_result

    def evaluate_code_quality_gate(self) -> Tuple[bool, Dict[str, Any]]:
        """Evaluate code quality-related gates."""
        logger.info("Evaluating code quality gate...")
        
        gate_result = {
            'status': 'PASS',
            'lint_results': {
                'ansible_lint_errors': 0,
                'yaml_lint_errors': 0,
                'python_lint_errors': 0
            },
            'issues': [],
            'tools_run': []
        }
        
        # Check for lint result files
        lint_patterns = {
            'ansible-lint': ['ansible-lint-results.json', 'ansible-lint.log'],
            'yamllint': ['yamllint-results.json', 'yamllint.log'],
            'flake8': ['flake8-results.json', 'flake8.log']
        }
        
        total_lint_errors = 0
        
        for tool, patterns in lint_patterns.items():
            for pattern in patterns:
                if os.path.exists(pattern):
                    gate_result['tools_run'].append(tool)
                    try:
                        errors = self._parse_lint_results(pattern, tool)
                        gate_result['lint_results'][f"{tool.replace('-', '_')}_errors"] = errors
                        total_lint_errors += errors
                    except Exception as e:
                        logger.error(f"Error parsing {pattern}: {e}")
                        gate_result['issues'].append(f"Failed to parse {pattern}: {e}")
                    break
        
        # Evaluate against thresholds
        if total_lint_errors > self.thresholds['max_lint_errors']:
            gate_result['status'] = 'FAIL'
            gate_result['issues'].append(
                f"Lint errors ({total_lint_errors}) exceed threshold ({self.thresholds['max_lint_errors']})"
            )
        
        return gate_result['status'] == 'PASS', gate_result

    def evaluate_performance_gate(self) -> Tuple[bool, Dict[str, Any]]:
        """Evaluate performance-related gates."""
        logger.info("Evaluating performance quality gate...")
        
        gate_result = {
            'status': 'PASS',
            'performance_score': 0.0,
            'benchmark_results': {},
            'issues': []
        }
        
        # Check for performance results
        performance_files = ['performance-results.json', 'performance-report.json']
        
        for perf_file in performance_files:
            if os.path.exists(perf_file):
                try:
                    with open(perf_file, 'r') as f:
                        perf_data = json.load(f)
                    
                    # Extract performance score
                    if 'benchmarks' in perf_data and 'overall_metrics' in perf_data['benchmarks']:
                        gate_result['performance_score'] = perf_data['benchmarks']['overall_metrics'].get('performance_score', 0.0)
                        gate_result['benchmark_results'] = perf_data['benchmarks']
                    
                    break
                    
                except Exception as e:
                    logger.error(f"Error parsing {perf_file}: {e}")
                    gate_result['issues'].append(f"Failed to parse {perf_file}: {e}")
        
        # Evaluate against thresholds
        performance_score = gate_result['performance_score']
        
        if performance_score < self.thresholds['min_performance_score']:
            gate_result['status'] = 'FAIL'
            gate_result['issues'].append(
                f"Performance score ({performance_score}) below threshold ({self.thresholds['min_performance_score']})"
            )
        
        return gate_result['status'] == 'PASS', gate_result

    def _parse_sarif_file(self, file_path: str) -> Dict[str, int]:
        """Parse SARIF file and extract vulnerability counts."""
        vulnerabilities = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        
        try:
            with open(file_path, 'r') as f:
                sarif_data = json.load(f)
            
            for run in sarif_data.get('runs', []):
                for result in run.get('results', []):
                    level = result.get('level', 'info').lower()
                    if level in ['error', 'critical']:
                        vulnerabilities['critical'] += 1
                    elif level in ['warning', 'high']:
                        vulnerabilities['high'] += 1
                    elif level in ['info', 'medium']:
                        vulnerabilities['medium'] += 1
                    else:
                        vulnerabilities['low'] += 1
                        
        except Exception as e:
            logger.error(f"Error parsing SARIF file {file_path}: {e}")
        
        return vulnerabilities

    def _parse_security_json(self, file_path: str) -> Dict[str, int]:
        """Parse security JSON file and extract vulnerability counts."""
        vulnerabilities = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        
        try:
            with open(file_path, 'r') as f:
                security_data = json.load(f)
            
            # Handle different JSON structures
            if 'vulnerabilities' in security_data:
                for vuln in security_data['vulnerabilities']:
                    severity = vuln.get('severity', 'low').lower()
                    if severity in vulnerabilities:
                        vulnerabilities[severity] += 1
                        
        except Exception as e:
            logger.error(f"Error parsing security JSON file {file_path}: {e}")
        
        return vulnerabilities

    def _parse_junit_xml(self, file_path: str) -> Dict[str, Any]:
        """Parse JUnit XML file and extract test results."""
        test_data = {
            'file': file_path,
            'total': 0,
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'errors': 0
        }
        
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Handle different XML structures
            if root.tag == 'testsuite':
                test_data['total'] = int(root.get('tests', 0))
                test_data['failed'] = int(root.get('failures', 0))
                test_data['errors'] = int(root.get('errors', 0))
                test_data['skipped'] = int(root.get('skipped', 0))
                test_data['passed'] = test_data['total'] - test_data['failed'] - test_data['errors'] - test_data['skipped']
            
            elif root.tag == 'testsuites':
                for testsuite in root.findall('testsuite'):
                    test_data['total'] += int(testsuite.get('tests', 0))
                    test_data['failed'] += int(testsuite.get('failures', 0))
                    test_data['errors'] += int(testsuite.get('errors', 0))
                    test_data['skipped'] += int(testsuite.get('skipped', 0))
                
                test_data['passed'] = test_data['total'] - test_data['failed'] - test_data['errors'] - test_data['skipped']
                
        except Exception as e:
            logger.error(f"Error parsing JUnit XML file {file_path}: {e}")
        
        return test_data

    def _parse_lint_results(self, file_path: str, tool: str) -> int:
        """Parse lint results and return error count."""
        error_count = 0
        
        try:
            if file_path.endswith('.json'):
                with open(file_path, 'r') as f:
                    lint_data = json.load(f)
                
                if tool == 'ansible-lint':
                    error_count = len(lint_data) if isinstance(lint_data, list) else 0
                elif tool == 'yamllint':
                    error_count = len(lint_data.get('files', {}))
                elif tool == 'flake8':
                    error_count = lint_data.get('error_count', 0)
            
            else:  # Log file
                with open(file_path, 'r') as f:
                    lines = f.readlines()
                
                # Count error lines (simple heuristic)
                error_count = len([line for line in lines if 'error' in line.lower() or 'fail' in line.lower()])
                
        except Exception as e:
            logger.error(f"Error parsing lint file {file_path}: {e}")
        
        return error_count

    def generate_recommendations(self) -> List[str]:
        """Generate recommendations based on quality gate results."""
        recommendations = []
        
        # Security recommendations
        if not self.results['gates']['security']['passed']:
            recommendations.append("🔒 Address critical and high severity vulnerabilities before deployment")
            recommendations.append("🔍 Review security scan results and implement fixes")
        
        # Testing recommendations
        if not self.results['gates']['testing']['passed']:
            recommendations.append("🧪 Fix failing tests and improve test coverage")
            recommendations.append("📊 Add more comprehensive test cases")
        
        # Code quality recommendations
        if not self.results['gates']['code_quality']['passed']:
            recommendations.append("🔧 Fix linting errors and improve code quality")
            recommendations.append("📝 Follow coding standards and best practices")
        
        # Performance recommendations
        if not self.results['gates']['performance']['passed']:
            recommendations.append("⚡ Optimize performance bottlenecks")
            recommendations.append("📈 Review and improve slow-running tasks")
        
        # General recommendations
        if self.results['overall_status'] == 'FAIL':
            recommendations.append("🚫 Deployment blocked - resolve quality gate failures")
            recommendations.append("🔄 Re-run quality gates after fixes")
        else:
            recommendations.append("✅ All quality gates passed - ready for deployment")
        
        return recommendations

    def evaluate_all_gates(self) -> Dict[str, Any]:
        """Evaluate all quality gates and return comprehensive results."""
        logger.info("Starting comprehensive quality gate evaluation...")
        
        # Initialize results
        self.results['timestamp'] = os.getenv('GITHUB_RUN_ID', 'local-run')
        
        # Evaluate each gate
        gates = {
            'security': self.evaluate_security_gate,
            'testing': self.evaluate_testing_gate,
            'code_quality': self.evaluate_code_quality_gate,
            'performance': self.evaluate_performance_gate
        }
        
        all_passed = True
        
        for gate_name, gate_func in gates.items():
            logger.info(f"Evaluating {gate_name} gate...")
            try:
                passed, gate_result = gate_func()
                self.results['gates'][gate_name] = {
                    'passed': passed,
                    'result': gate_result
                }
                
                if not passed:
                    all_passed = False
                    logger.warning(f"{gate_name} gate FAILED")
                else:
                    logger.info(f"{gate_name} gate PASSED")
                    
            except Exception as e:
                logger.error(f"Error evaluating {gate_name} gate: {e}")
                self.results['gates'][gate_name] = {
                    'passed': False,
                    'result': {'status': 'ERROR', 'error': str(e)}
                }
                all_passed = False
        
        # Set overall status
        self.results['overall_status'] = 'PASS' if all_passed else 'FAIL'
        
        # Generate recommendations
        self.results['recommendations'] = self.generate_recommendations()
        
        logger.info(f"Quality gate evaluation completed: {self.results['overall_status']}")
        
        return self.results

    def save_results(self, output_file: str = 'quality-gate-results.json'):
        """Save quality gate results to file."""
        try:
            with open(output_file, 'w') as f:
                json.dump(self.results, f, indent=2)
            logger.info(f"Quality gate results saved to {output_file}")
        except Exception as e:
            logger.error(f"Error saving results to {output_file}: {e}")

    def create_status_files(self):
        """Create status files for CI/CD pipeline."""
        if self.results['overall_status'] == 'PASS':
            Path('quality-gate-passed').touch()
            logger.info("Created quality-gate-passed file")
        else:
            Path('quality-gate-failed').touch()
            logger.info("Created quality-gate-failed file")

def main():
    """Main execution function."""
    logger.info("Starting Quality Gate Evaluation")
    
    evaluator = QualityGateEvaluator()
    
    try:
        # Evaluate all gates
        results = evaluator.evaluate_all_gates()
        
        # Save results
        evaluator.save_results()
        
        # Create status files
        evaluator.create_status_files()
        
        # Print summary
        print("\n" + "="*60)
        print("QUALITY GATE EVALUATION SUMMARY")
        print("="*60)
        print(f"Overall Status: {results['overall_status']}")
        print(f"Timestamp: {results['timestamp']}")
        print("\nGate Results:")
        
        for gate_name, gate_data in results['gates'].items():
            status = "✅ PASS" if gate_data['passed'] else "❌ FAIL"
            print(f"  {gate_name.title()}: {status}")
        
        print("\nRecommendations:")
        for rec in results['recommendations']:
            print(f"  {rec}")
        
        print("="*60)
        
        # Exit with appropriate code
        sys.exit(0 if results['overall_status'] == 'PASS' else 1)
        
    except Exception as e:
        logger.error(f"Quality gate evaluation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

