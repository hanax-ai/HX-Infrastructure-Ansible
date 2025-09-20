
#!/usr/bin/env python3
"""
Phase 2 Day 2 Completion Validation Script
Validates all Phase 2 Day 2 requirements are met
"""

import os
import sys
import yaml
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Any

class Phase2Validator:
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.validation_results = {
            'timestamp': datetime.now().isoformat(),
            'phase': 'Phase 2 Day 2',
            'target_rating': '8.5/10',
            'requirements': {},
            'overall_status': 'PENDING',
            'score': 0.0,
            'issues': [],
            'recommendations': []
        }
        
    def validate_operational_safety(self) -> Tuple[bool, float, List[str]]:
        """Validate operational safety enhancement requirements"""
        issues = []
        score = 0.0
        max_score = 25.0
        
        # Check operational safety role exists
        safety_role_path = self.base_path / 'roles' / 'operational_safety'
        if safety_role_path.exists():
            score += 5.0
            
            # Check main tasks file
            main_tasks = safety_role_path / 'tasks' / 'main.yml'
            if main_tasks.exists():
                score += 5.0
                try:
                    with open(main_tasks) as f:
                        content = f.read()
                        
                    # Check for key safety features
                    safety_features = [
                        'safety_confirmation_required',
                        'dangerous_command_protection',
                        'backup_verification',
                        'maintenance_window_check',
                        'rollback_script'
                    ]
                    
                    for feature in safety_features:
                        if feature in content:
                            score += 2.0
                        else:
                            issues.append(f"Missing safety feature: {feature}")
                            
                except Exception as e:
                    issues.append(f"Error reading operational safety tasks: {e}")
            else:
                issues.append("Operational safety main tasks file missing")
        else:
            issues.append("Operational safety role missing")
            
        # Check for safety procedures documentation
        safety_docs = self.base_path / 'docs' / 'OPERATIONAL_SAFETY_PROCEDURES.md'
        if safety_docs.exists():
            score += 5.0
        else:
            issues.append("Operational safety procedures documentation missing")
            
        return score >= max_score * 0.8, score, issues
        
    def validate_production_inventory(self) -> Tuple[bool, float, List[str]]:
        """Validate production inventory completion"""
        issues = []
        score = 0.0
        max_score = 25.0
        
        # Check production inventory exists
        prod_inventory = self.base_path / 'inventories' / 'production' / 'hosts.yml'
        if prod_inventory.exists():
            score += 5.0
            
            try:
                with open(prod_inventory) as f:
                    inventory_data = yaml.safe_load(f)
                    
                # Check for production hosts
                if 'all' in inventory_data and 'children' in inventory_data['all']:
                    children = inventory_data['all']['children']
                    
                    # Check for different server types
                    server_types = ['production_web_servers', 'production_database_servers', 
                                  'production_app_servers', 'production_monitoring']
                    
                    for server_type in server_types:
                        if server_type in children:
                            score += 2.0
                        else:
                            issues.append(f"Missing server group: {server_type}")
                            
                    # Check for SSH configuration
                    if 'vars' in inventory_data['all']:
                        vars_section = inventory_data['all']['vars']
                        ssh_configs = [
                            'ansible_ssh_private_key_file',
                            'ansible_ssh_common_args',
                            'ansible_connection_timeout'
                        ]
                        
                        for config in ssh_configs:
                            if config in vars_section:
                                score += 2.0
                            else:
                                issues.append(f"Missing SSH config: {config}")
                                
                else:
                    issues.append("Invalid inventory structure")
                    
            except Exception as e:
                issues.append(f"Error reading production inventory: {e}")
        else:
            issues.append("Production inventory file missing")
            
        # Check production group vars
        prod_group_vars = self.base_path / 'group_vars' / 'production.yml'
        if prod_group_vars.exists():
            score += 5.0
        else:
            issues.append("Production group variables missing")
            
        # Check SSH key management
        ssh_role = self.base_path / 'roles' / 'ssh_key_management'
        if ssh_role.exists():
            score += 5.0
        else:
            issues.append("SSH key management role missing")
            
        return score >= max_score * 0.8, score, issues
        
    def validate_security_validation(self) -> Tuple[bool, float, List[str]]:
        """Validate comprehensive security validation"""
        issues = []
        score = 0.0
        max_score = 30.0
        
        # Check security scanner exists
        security_scanner = self.base_path / 'security' / 'validation' / 'security_scan.py'
        if security_scanner.exists():
            score += 10.0
            
            # Try to run security scan
            try:
                result = subprocess.run([
                    'python3', str(security_scanner), str(self.base_path), 
                    '--output', '/tmp/security_scan_results.json'
                ], capture_output=True, text=True, timeout=300)
                
                if result.returncode in [0, 2]:  # 0 = no issues, 2 = medium issues
                    score += 10.0
                elif result.returncode == 1:  # Critical issues
                    issues.append("Critical security issues found")
                    score += 5.0
                else:
                    issues.append("Security scan failed")
                    
            except subprocess.TimeoutExpired:
                issues.append("Security scan timed out")
            except Exception as e:
                issues.append(f"Error running security scan: {e}")
        else:
            issues.append("Security scanner missing")
            
        # Check for ansible-lint compliance
        try:
            result = subprocess.run(['ansible-lint', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                score += 5.0
                
                # Run ansible-lint
                lint_result = subprocess.run(['ansible-lint', str(self.base_path)],
                                           capture_output=True, text=True)
                if lint_result.returncode == 0:
                    score += 5.0
                else:
                    issues.append("ansible-lint issues found")
            else:
                issues.append("ansible-lint not available")
        except FileNotFoundError:
            issues.append("ansible-lint not installed")
            
        return score >= max_score * 0.8, score, issues
        
    def validate_documentation(self) -> Tuple[bool, float, List[str]]:
        """Validate documentation and process updates"""
        issues = []
        score = 0.0
        max_score = 20.0
        
        # Check for key documentation files
        doc_files = [
            'docs/OPERATIONAL_SAFETY_PROCEDURES.md',
            'README.md',
            'docs/SECURITY.md'
        ]
        
        for doc_file in doc_files:
            doc_path = self.base_path / doc_file
            if doc_path.exists():
                score += 5.0
            else:
                issues.append(f"Missing documentation: {doc_file}")
                
        # Check maintenance playbook
        maintenance_playbook = self.base_path / 'playbooks' / 'maintenance' / 'production_maintenance.yml'
        if maintenance_playbook.exists():
            score += 5.0
        else:
            issues.append("Production maintenance playbook missing")
            
        return score >= max_score * 0.8, score, issues
        
    def run_validation(self) -> Dict[str, Any]:
        """Run complete Phase 2 Day 2 validation"""
        print("Starting Phase 2 Day 2 validation...")
        
        # Validate each requirement
        requirements = {
            'operational_safety': self.validate_operational_safety(),
            'production_inventory': self.validate_production_inventory(),
            'security_validation': self.validate_security_validation(),
            'documentation': self.validate_documentation()
        }
        
        total_score = 0.0
        total_max_score = 100.0
        all_passed = True
        all_issues = []
        
        for req_name, (passed, score, issues) in requirements.items():
            self.validation_results['requirements'][req_name] = {
                'passed': passed,
                'score': score,
                'issues': issues
            }
            
            total_score += score
            all_issues.extend(issues)
            
            if not passed:
                all_passed = False
                
        # Calculate overall results
        self.validation_results['score'] = (total_score / total_max_score) * 10.0
        self.validation_results['issues'] = all_issues
        
        # Determine overall status
        if all_passed and self.validation_results['score'] >= 8.5:
            self.validation_results['overall_status'] = 'PASSED'
        elif self.validation_results['score'] >= 8.0:
            self.validation_results['overall_status'] = 'PARTIAL'
        else:
            self.validation_results['overall_status'] = 'FAILED'
            
        # Generate recommendations
        self._generate_recommendations()
        
        return self.validation_results
        
    def _generate_recommendations(self):
        """Generate recommendations based on validation results"""
        recommendations = []
        
        if self.validation_results['overall_status'] == 'FAILED':
            recommendations.append("CRITICAL: Address all failed requirements before requesting Phase 3 authorization")
            
        if self.validation_results['score'] < 8.5:
            recommendations.append(f"Current score {self.validation_results['score']:.1f}/10 - Target 8.5/10 required")
            
        # Specific recommendations based on failed requirements
        for req_name, req_data in self.validation_results['requirements'].items():
            if not req_data['passed']:
                if req_name == 'operational_safety':
                    recommendations.append("Complete operational safety framework implementation")
                elif req_name == 'production_inventory':
                    recommendations.append("Finalize production inventory and SSH key management")
                elif req_name == 'security_validation':
                    recommendations.append("Resolve security validation issues")
                elif req_name == 'documentation':
                    recommendations.append("Complete documentation and process updates")
                    
        if not recommendations:
            recommendations.append("All requirements met - Ready for Phase 3 authorization")
            
        self.validation_results['recommendations'] = recommendations
        
    def print_results(self):
        """Print validation results"""
        print(f"\n{'='*80}")
        print("PHASE 2 DAY 2 VALIDATION RESULTS")
        print(f"{'='*80}")
        print(f"Overall Status: {self.validation_results['overall_status']}")
        print(f"Score: {self.validation_results['score']:.1f}/10.0 (Target: 8.5/10)")
        print(f"Timestamp: {self.validation_results['timestamp']}")
        
        print(f"\nRequirement Results:")
        for req_name, req_data in self.validation_results['requirements'].items():
            status = "✅ PASS" if req_data['passed'] else "❌ FAIL"
            print(f"  {req_name.replace('_', ' ').title()}: {status} ({req_data['score']:.1f} points)")
            
        if self.validation_results['issues']:
            print(f"\nIssues Found ({len(self.validation_results['issues'])}):")
            for issue in self.validation_results['issues']:
                print(f"  • {issue}")
                
        print(f"\nRecommendations:")
        for rec in self.validation_results['recommendations']:
            print(f"  • {rec}")
            
        print(f"\n{'='*80}")
        
        if self.validation_results['overall_status'] == 'PASSED':
            print("🎉 PHASE 2 DAY 2 COMPLETE - READY FOR PHASE 3 AUTHORIZATION")
        elif self.validation_results['overall_status'] == 'PARTIAL':
            print("⚠️  PHASE 2 DAY 2 PARTIALLY COMPLETE - MINOR ISSUES TO RESOLVE")
        else:
            print("❌ PHASE 2 DAY 2 INCOMPLETE - MAJOR ISSUES TO RESOLVE")
            
        print(f"{'='*80}")
        
def main():
    if len(sys.argv) != 2:
        print("Usage: python3 validate_phase2_completion.py <ansible_project_path>")
        sys.exit(1)
        
    project_path = sys.argv[1]
    validator = Phase2Validator(project_path)
    
    results = validator.run_validation()
    validator.print_results()
    
    # Save results to file
    results_file = Path(project_path) / 'PHASE2_DAY2_VALIDATION_RESULTS.json'
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
        
    print(f"\nDetailed results saved to: {results_file}")
    
    # Exit with appropriate code
    if results['overall_status'] == 'PASSED':
        sys.exit(0)
    elif results['overall_status'] == 'PARTIAL':
        sys.exit(1)
    else:
        sys.exit(2)
        
if __name__ == '__main__':
    main()
