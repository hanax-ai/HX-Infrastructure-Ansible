
#!/usr/bin/env python3
"""
Security Quality Gate Script
Sprint 2 - Advanced Capabilities Implementation

This script evaluates security scan results against defined thresholds
and determines if the security quality gate should pass or fail.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, Tuple
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SecurityGate:
    """Security quality gate evaluator."""
    
    def __init__(self):
        # Load thresholds from environment variables
        self.thresholds = {
            'max_critical_vulnerabilities': int(os.getenv('MAX_CRITICAL_VULNERABILITIES', '0')),
            'max_high_vulnerabilities': int(os.getenv('MAX_HIGH_VULNERABILITIES', '5')),
            'max_medium_vulnerabilities': int(os.getenv('MAX_MEDIUM_VULNERABILITIES', '20')),
            'min_scan_coverage': float(os.getenv('MIN_SCAN_COVERAGE', '80.0')),
            'required_tools': os.getenv('REQUIRED_SECURITY_TOOLS', 'trivy,kics').split(',')
        }
        
        self.gate_result = {
            'status': 'UNKNOWN',
            'timestamp': None,
            'vulnerabilities': {
                'critical': 0,
                'high': 0,
                'medium': 0,
                'low': 0,
                'total': 0
            },
            'scan_coverage': {
                'executed_tools': [],
                'coverage_percentage': 0.0,
                'missing_tools': []
            },
            'violations': [],
            'recommendations': [],
            'details': {}
        }
        
        logger.info(f"Security gate thresholds: {self.thresholds}")

    def load_security_report(self, report_file: str = 'security-report.json') -> Dict[str, Any]:
        """Load security report data."""
        try:
            if not os.path.exists(report_file):
                raise FileNotFoundError(f"Security report not found: {report_file}")
            
            with open(report_file, 'r') as f:
                report_data = json.load(f)
            
            logger.info(f"Loaded security report from {report_file}")
            return report_data
            
        except Exception as e:
            logger.error(f"Error loading security report: {e}")
            raise

    def evaluate_vulnerability_thresholds(self, report_data: Dict[str, Any]) -> Tuple[bool, list]:
        """Evaluate vulnerability counts against thresholds."""
        logger.info("Evaluating vulnerability thresholds...")
        
        summary = report_data.get('summary', {})
        violations = []
        
        # Extract vulnerability counts
        self.gate_result['vulnerabilities'] = {
            'critical': summary.get('critical_count', 0),
            'high': summary.get('high_count', 0),
            'medium': summary.get('medium_count', 0),
            'low': summary.get('low_count', 0),
            'total': summary.get('total_vulnerabilities', 0)
        }
        
        # Check critical vulnerabilities
        critical_count = self.gate_result['vulnerabilities']['critical']
        if critical_count > self.thresholds['max_critical_vulnerabilities']:
            violation = {
                'type': 'critical_vulnerabilities',
                'severity': 'critical',
                'message': f"Critical vulnerabilities ({critical_count}) exceed threshold ({self.thresholds['max_critical_vulnerabilities']})",
                'current_value': critical_count,
                'threshold': self.thresholds['max_critical_vulnerabilities'],
                'blocking': True
            }
            violations.append(violation)
            logger.error(violation['message'])
        
        # Check high vulnerabilities
        high_count = self.gate_result['vulnerabilities']['high']
        if high_count > self.thresholds['max_high_vulnerabilities']:
            violation = {
                'type': 'high_vulnerabilities',
                'severity': 'high',
                'message': f"High vulnerabilities ({high_count}) exceed threshold ({self.thresholds['max_high_vulnerabilities']})",
                'current_value': high_count,
                'threshold': self.thresholds['max_high_vulnerabilities'],
                'blocking': True
            }
            violations.append(violation)
            logger.warning(violation['message'])
        
        # Check medium vulnerabilities
        medium_count = self.gate_result['vulnerabilities']['medium']
        if medium_count > self.thresholds['max_medium_vulnerabilities']:
            violation = {
                'type': 'medium_vulnerabilities',
                'severity': 'medium',
                'message': f"Medium vulnerabilities ({medium_count}) exceed threshold ({self.thresholds['max_medium_vulnerabilities']})",
                'current_value': medium_count,
                'threshold': self.thresholds['max_medium_vulnerabilities'],
                'blocking': False  # Medium violations are warnings, not blocking
            }
            violations.append(violation)
            logger.warning(violation['message'])
        
        # Determine if vulnerabilities block the gate
        blocking_violations = [v for v in violations if v.get('blocking', False)]
        passed = len(blocking_violations) == 0
        
        return passed, violations

    def evaluate_scan_coverage(self, report_data: Dict[str, Any]) -> Tuple[bool, list]:
        """Evaluate security scan coverage."""
        logger.info("Evaluating scan coverage...")
        
        summary = report_data.get('summary', {})
        scan_coverage = summary.get('scan_coverage', {})
        violations = []
        
        # Extract coverage information
        self.gate_result['scan_coverage'] = {
            'executed_tools': summary.get('tools_executed', []),
            'coverage_percentage': scan_coverage.get('coverage_percentage', 0.0),
            'missing_tools': []
        }
        
        # Check overall coverage percentage
        coverage_percentage = self.gate_result['scan_coverage']['coverage_percentage']
        if coverage_percentage < self.thresholds['min_scan_coverage']:
            violation = {
                'type': 'scan_coverage',
                'severity': 'medium',
                'message': f"Scan coverage ({coverage_percentage:.1f}%) below threshold ({self.thresholds['min_scan_coverage']}%)",
                'current_value': coverage_percentage,
                'threshold': self.thresholds['min_scan_coverage'],
                'blocking': False
            }
            violations.append(violation)
            logger.warning(violation['message'])
        
        # Check required tools
        executed_tools = [tool.lower() for tool in self.gate_result['scan_coverage']['executed_tools']]
        missing_tools = []
        
        for required_tool in self.thresholds['required_tools']:
            required_tool = required_tool.strip().lower()
            if required_tool not in executed_tools:
                missing_tools.append(required_tool)
        
        self.gate_result['scan_coverage']['missing_tools'] = missing_tools
        
        if missing_tools:
            violation = {
                'type': 'missing_required_tools',
                'severity': 'high',
                'message': f"Required security tools not executed: {', '.join(missing_tools)}",
                'current_value': missing_tools,
                'threshold': self.thresholds['required_tools'],
                'blocking': True
            }
            violations.append(violation)
            logger.error(violation['message'])
        
        # Determine if coverage issues block the gate
        blocking_violations = [v for v in violations if v.get('blocking', False)]
        passed = len(blocking_violations) == 0
        
        return passed, violations

    def evaluate_tool_execution(self, report_data: Dict[str, Any]) -> Tuple[bool, list]:
        """Evaluate security tool execution status."""
        logger.info("Evaluating tool execution status...")
        
        tool_results = report_data.get('tool_results', {})
        violations = []
        
        # Check for tool execution errors
        for tool_id, tool_data in tool_results.items():
            if tool_data.get('errors'):
                violation = {
                    'type': 'tool_execution_error',
                    'severity': 'medium',
                    'message': f"Tool {tool_data.get('name', tool_id)} had execution errors: {'; '.join(tool_data['errors'])}",
                    'current_value': tool_data['errors'],
                    'threshold': 'no_errors',
                    'blocking': False
                }
                violations.append(violation)
                logger.warning(violation['message'])
        
        # Tool execution errors are warnings, not blocking
        return True, violations

    def generate_recommendations(self):
        """Generate security gate recommendations."""
        logger.info("Generating security gate recommendations...")
        
        recommendations = []
        
        # Vulnerability-based recommendations
        if self.gate_result['vulnerabilities']['critical'] > 0:
            recommendations.append({
                'priority': 'critical',
                'category': 'vulnerability_management',
                'title': 'Fix Critical Vulnerabilities',
                'description': f"Address {self.gate_result['vulnerabilities']['critical']} critical vulnerabilities immediately",
                'action': 'Review security report and implement fixes for all critical vulnerabilities'
            })
        
        if self.gate_result['vulnerabilities']['high'] > self.thresholds['max_high_vulnerabilities']:
            recommendations.append({
                'priority': 'high',
                'category': 'vulnerability_management',
                'title': 'Reduce High Vulnerability Count',
                'description': f"High vulnerability count ({self.gate_result['vulnerabilities']['high']}) exceeds threshold",
                'action': 'Prioritize fixing high-severity vulnerabilities in next development cycle'
            })
        
        # Coverage-based recommendations
        if self.gate_result['scan_coverage']['missing_tools']:
            recommendations.append({
                'priority': 'high',
                'category': 'tooling',
                'title': 'Enable Missing Security Tools',
                'description': f"Required tools not executed: {', '.join(self.gate_result['scan_coverage']['missing_tools'])}",
                'action': 'Configure and enable all required security scanning tools'
            })
        
        if self.gate_result['scan_coverage']['coverage_percentage'] < self.thresholds['min_scan_coverage']:
            recommendations.append({
                'priority': 'medium',
                'category': 'tooling',
                'title': 'Improve Scan Coverage',
                'description': f"Scan coverage ({self.gate_result['scan_coverage']['coverage_percentage']:.1f}%) below target",
                'action': 'Investigate and fix security tool configuration issues'
            })
        
        # Success recommendations
        if self.gate_result['status'] == 'PASS':
            recommendations.append({
                'priority': 'info',
                'category': 'security_posture',
                'title': 'Security Gate Passed',
                'description': 'All security quality gates passed successfully',
                'action': 'Continue following security best practices and regular scanning'
            })
        
        self.gate_result['recommendations'] = recommendations

    def evaluate_security_gate(self, report_file: str = 'security-report.json') -> Dict[str, Any]:
        """Evaluate the complete security gate."""
        logger.info("Starting security gate evaluation...")
        
        try:
            # Load security report
            report_data = self.load_security_report(report_file)
            
            # Initialize gate result
            self.gate_result['timestamp'] = report_data.get('metadata', {}).get('generated_at')
            
            # Evaluate different aspects
            vuln_passed, vuln_violations = self.evaluate_vulnerability_thresholds(report_data)
            coverage_passed, coverage_violations = self.evaluate_scan_coverage(report_data)
            tool_passed, tool_violations = self.evaluate_tool_execution(report_data)
            
            # Aggregate violations
            all_violations = vuln_violations + coverage_violations + tool_violations
            self.gate_result['violations'] = all_violations
            
            # Determine overall status
            blocking_violations = [v for v in all_violations if v.get('blocking', False)]
            overall_passed = len(blocking_violations) == 0
            
            self.gate_result['status'] = 'PASS' if overall_passed else 'FAIL'
            
            # Store detailed results
            self.gate_result['details'] = {
                'vulnerability_evaluation': {
                    'passed': vuln_passed,
                    'violations': vuln_violations
                },
                'coverage_evaluation': {
                    'passed': coverage_passed,
                    'violations': coverage_violations
                },
                'tool_evaluation': {
                    'passed': tool_passed,
                    'violations': tool_violations
                }
            }
            
            # Generate recommendations
            self.generate_recommendations()
            
            logger.info(f"Security gate evaluation completed: {self.gate_result['status']}")
            
            return self.gate_result
            
        except Exception as e:
            logger.error(f"Security gate evaluation failed: {e}")
            self.gate_result['status'] = 'ERROR'
            self.gate_result['violations'].append({
                'type': 'evaluation_error',
                'severity': 'critical',
                'message': f"Security gate evaluation failed: {str(e)}",
                'blocking': True
            })
            return self.gate_result

    def save_gate_result(self, output_file: str = 'security-gate-result.json'):
        """Save security gate result to file."""
        try:
            with open(output_file, 'w') as f:
                json.dump(self.gate_result, f, indent=2, default=str)
            logger.info(f"Security gate result saved to {output_file}")
        except Exception as e:
            logger.error(f"Error saving gate result: {e}")

    def create_status_files(self):
        """Create status files for CI/CD pipeline."""
        if self.gate_result['status'] == 'PASS':
            Path('security-gate-passed').touch()
            logger.info("Created security-gate-passed file")
        else:
            Path('security-gate-failed').touch()
            logger.info("Created security-gate-failed file")

    def print_gate_summary(self):
        """Print security gate summary to console."""
        print("\n" + "="*60)
        print("SECURITY QUALITY GATE SUMMARY")
        print("="*60)
        print(f"Status: {self.gate_result['status']}")
        print(f"Timestamp: {self.gate_result['timestamp']}")
        
        print(f"\nVulnerabilities:")
        print(f"  Critical: {self.gate_result['vulnerabilities']['critical']} (max: {self.thresholds['max_critical_vulnerabilities']})")
        print(f"  High: {self.gate_result['vulnerabilities']['high']} (max: {self.thresholds['max_high_vulnerabilities']})")
        print(f"  Medium: {self.gate_result['vulnerabilities']['medium']} (max: {self.thresholds['max_medium_vulnerabilities']})")
        print(f"  Total: {self.gate_result['vulnerabilities']['total']}")
        
        print(f"\nScan Coverage:")
        print(f"  Coverage: {self.gate_result['scan_coverage']['coverage_percentage']:.1f}% (min: {self.thresholds['min_scan_coverage']}%)")
        print(f"  Executed Tools: {', '.join(self.gate_result['scan_coverage']['executed_tools'])}")
        if self.gate_result['scan_coverage']['missing_tools']:
            print(f"  Missing Tools: {', '.join(self.gate_result['scan_coverage']['missing_tools'])}")
        
        if self.gate_result['violations']:
            print(f"\nViolations:")
            for violation in self.gate_result['violations']:
                blocking_text = " (BLOCKING)" if violation.get('blocking') else ""
                print(f"  - {violation['severity'].upper()}: {violation['message']}{blocking_text}")
        
        if self.gate_result['recommendations']:
            print(f"\nTop Recommendations:")
            for rec in self.gate_result['recommendations'][:3]:
                print(f"  - {rec['priority'].upper()}: {rec['title']}")
        
        print("="*60)

def main():
    """Main execution function."""
    logger.info("Starting Security Quality Gate Evaluation")
    
    try:
        gate = SecurityGate()
        
        # Evaluate security gate
        result = gate.evaluate_security_gate()
        
        # Save results
        gate.save_gate_result()
        
        # Create status files
        gate.create_status_files()
        
        # Print summary
        gate.print_gate_summary()
        
        # Exit with appropriate code
        exit_code = 0 if result['status'] == 'PASS' else 1
        logger.info(f"Security gate evaluation completed with exit code: {exit_code}")
        sys.exit(exit_code)
        
    except Exception as e:
        logger.error(f"Security gate evaluation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

