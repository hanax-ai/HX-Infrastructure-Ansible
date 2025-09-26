#!/usr/bin/env python3
"""
Phase 2A Consolidation Validation Script
Validates repository readiness for Phase 2B consolidation
"""

import subprocess
import json
import os
import sys
from datetime import datetime
from pathlib import Path

class ConsolidationValidator:
    def __init__(self):
        self.validation_results = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'UNKNOWN',
            'checks': {},
            'errors': [],
            'warnings': [],
            'recommendations': []
        }
        
        self.required_target_branches = [
            'phase-2-consolidated',
            'feature-consolidated-production', 
            'security-remediation-consolidated',
            'infrastructure-consolidated'
        ]

    def run_command(self, cmd, capture_output=True):
        """Run shell command and return result"""
        try:
            result = subprocess.run(cmd, shell=True, capture_output=capture_output, 
                                  text=True, check=True)
            return result.stdout.strip() if capture_output else True
        except subprocess.CalledProcessError as e:
            return None

    def validate_target_branches(self):
        """Validate all target branches exist"""
        print("🎯 Validating target branches...")
        
        missing_branches = []
        existing_branches = []
        
        for branch in self.required_target_branches:
            if self.run_command(f"git show-ref --verify --quiet refs/remotes/origin/{branch}"):
                existing_branches.append(branch)
                print(f"  ✅ {branch}")
            else:
                missing_branches.append(branch)
                print(f"  ❌ {branch}")
        
        self.validation_results['checks']['target_branches'] = {
            'status': 'PASS' if not missing_branches else 'FAIL',
            'existing': existing_branches,
            'missing': missing_branches,
            'total_required': len(self.required_target_branches),
            'total_existing': len(existing_branches)
        }
        
        if missing_branches:
            self.validation_results['errors'].append(
                f"Missing target branches: {', '.join(missing_branches)}"
            )
        
        return not missing_branches

    def validate_ansible_structure(self):
        """Validate Ansible directory structure"""
        print("📁 Validating Ansible structure...")
        
        required_dirs = ['roles', 'playbooks', 'inventory', 'group_vars']
        optional_dirs = ['host_vars', 'vars', 'templates', 'files']
        required_files = ['ansible.cfg', 'site.yml']
        
        missing_dirs = []
        missing_files = []
        existing_structure = {}
        
        # Check directories
        for dir_name in required_dirs + optional_dirs:
            if os.path.exists(dir_name):
                existing_structure[dir_name] = {
                    'exists': True,
                    'type': 'directory',
                    'required': dir_name in required_dirs
                }
                print(f"  ✅ {dir_name}/")
            else:
                existing_structure[dir_name] = {
                    'exists': False,
                    'type': 'directory', 
                    'required': dir_name in required_dirs
                }
                if dir_name in required_dirs:
                    missing_dirs.append(dir_name)
                    print(f"  ❌ {dir_name}/")
                else:
                    print(f"  ⚠️  {dir_name}/ (optional)")
        
        # Check files
        for file_name in required_files:
            if os.path.exists(file_name):
                existing_structure[file_name] = {
                    'exists': True,
                    'type': 'file',
                    'required': True
                }
                print(f"  ✅ {file_name}")
            else:
                existing_structure[file_name] = {
                    'exists': False,
                    'type': 'file',
                    'required': True
                }
                missing_files.append(file_name)
                print(f"  ❌ {file_name}")
        
        self.validation_results['checks']['ansible_structure'] = {
            'status': 'PASS' if not (missing_dirs or missing_files) else 'FAIL',
            'structure': existing_structure,
            'missing_dirs': missing_dirs,
            'missing_files': missing_files
        }
        
        if missing_dirs or missing_files:
            self.validation_results['errors'].append(
                f"Missing Ansible structure - Dirs: {missing_dirs}, Files: {missing_files}"
            )
        
        return not (missing_dirs or missing_files)

    def validate_consolidation_matrix(self):
        """Validate consolidation matrix exists and is valid"""
        print("📊 Validating consolidation matrix...")
        
        matrix_file = 'docs/phase-2A/consolidation_matrix.csv'
        matrix_md = 'docs/phase-2A/consolidation_matrix.md'
        
        matrix_exists = os.path.exists(matrix_file)
        matrix_md_exists = os.path.exists(matrix_md)
        
        consolidate_count = 0
        keep_count = 0
        
        if matrix_exists:
            try:
                with open(matrix_file, 'r') as f:
                    lines = f.readlines()
                    for line in lines[1:]:  # Skip header
                        if 'CONSOLIDATE' in line:
                            consolidate_count += 1
                        elif 'KEEP' in line:
                            keep_count += 1
                print(f"  ✅ Matrix file exists: {consolidate_count} CONSOLIDATE, {keep_count} KEEP")
            except Exception as e:
                print(f"  ❌ Error reading matrix file: {e}")
                matrix_exists = False
        else:
            print(f"  ❌ Matrix file missing: {matrix_file}")
        
        if matrix_md_exists:
            print(f"  ✅ Matrix documentation exists: {matrix_md}")
        else:
            print(f"  ❌ Matrix documentation missing: {matrix_md}")
        
        self.validation_results['checks']['consolidation_matrix'] = {
            'status': 'PASS' if (matrix_exists and matrix_md_exists) else 'FAIL',
            'csv_exists': matrix_exists,
            'md_exists': matrix_md_exists,
            'consolidate_branches': consolidate_count,
            'keep_branches': keep_count,
            'total_branches': consolidate_count + keep_count
        }
        
        if not (matrix_exists and matrix_md_exists):
            self.validation_results['errors'].append(
                "Consolidation matrix files missing or invalid"
            )
        
        return matrix_exists and matrix_md_exists

    def validate_git_status(self):
        """Validate git repository status"""
        print("🔧 Validating git status...")
        
        # Check for uncommitted changes
        status_output = self.run_command("git status --porcelain")
        has_uncommitted = bool(status_output)
        
        # Get current branch
        current_branch = self.run_command("git branch --show-current")
        
        # Check if we're on a safe branch for analysis
        safe_branches = ['main', 'phase-2A-analysis'] + self.required_target_branches
        on_safe_branch = current_branch in safe_branches
        
        # Get total branch count
        branch_count = len(self.run_command("git branch -r").split('\n')) if self.run_command("git branch -r") else 0
        
        self.validation_results['checks']['git_status'] = {
            'status': 'PASS' if (not has_uncommitted and on_safe_branch) else 'WARN',
            'current_branch': current_branch,
            'has_uncommitted_changes': has_uncommitted,
            'on_safe_branch': on_safe_branch,
            'total_branches': branch_count,
            'uncommitted_files': status_output.split('\n') if status_output else []
        }
        
        if has_uncommitted:
            self.validation_results['warnings'].append(
                f"Uncommitted changes detected on branch {current_branch}"
            )
        
        if not on_safe_branch:
            self.validation_results['warnings'].append(
                f"Currently on branch {current_branch}, recommend switching to safe branch"
            )
        
        return True  # Git status issues are warnings, not failures

    def validate_phase_2a_artifacts(self):
        """Validate Phase 2A artifacts are complete"""
        print("📋 Validating Phase 2A artifacts...")
        
        required_artifacts = [
            'docs/phase-2A/consolidation_matrix.csv',
            'docs/phase-2A/consolidation_matrix.md', 
            'docs/phase-2A/dependency_mapping.md',
            'docs/phase-2A/generate_consolidation_matrix.py',
            'docs/phase-2A/validate_consolidation.py',
            '.github/workflows/phase-2-consolidation-ci.yml'
        ]
        
        missing_artifacts = []
        existing_artifacts = []
        
        for artifact in required_artifacts:
            if os.path.exists(artifact):
                existing_artifacts.append(artifact)
                print(f"  ✅ {artifact}")
            else:
                missing_artifacts.append(artifact)
                print(f"  ❌ {artifact}")
        
        self.validation_results['checks']['phase_2a_artifacts'] = {
            'status': 'PASS' if not missing_artifacts else 'FAIL',
            'existing': existing_artifacts,
            'missing': missing_artifacts,
            'completion_percentage': (len(existing_artifacts) / len(required_artifacts)) * 100
        }
        
        if missing_artifacts:
            self.validation_results['errors'].append(
                f"Missing Phase 2A artifacts: {', '.join(missing_artifacts)}"
            )
        
        return not missing_artifacts

    def generate_recommendations(self):
        """Generate recommendations based on validation results"""
        print("💡 Generating recommendations...")
        
        # Check overall readiness
        failed_checks = [name for name, check in self.validation_results['checks'].items() 
                        if check['status'] == 'FAIL']
        
        if not failed_checks:
            self.validation_results['recommendations'].append(
                "✅ Repository is READY for Phase 2B consolidation execution"
            )
            self.validation_results['overall_status'] = 'READY'
        else:
            self.validation_results['recommendations'].append(
                f"❌ Repository is NOT READY - Failed checks: {', '.join(failed_checks)}"
            )
            self.validation_results['overall_status'] = 'NOT_READY'
        
        # Specific recommendations
        if 'target_branches' in failed_checks:
            self.validation_results['recommendations'].append(
                "Create missing target branches using: git checkout -b <branch-name> && git push -u origin <branch-name>"
            )
        
        if 'consolidation_matrix' in failed_checks:
            self.validation_results['recommendations'].append(
                "Run consolidation matrix generation: python3 docs/phase-2A/generate_consolidation_matrix.py"
            )
        
        if 'phase_2a_artifacts' in failed_checks:
            self.validation_results['recommendations'].append(
                "Complete Phase 2A artifact generation before proceeding to Phase 2B"
            )
        
        # Performance recommendations
        consolidate_count = self.validation_results['checks'].get('consolidation_matrix', {}).get('consolidate_branches', 0)
        if consolidate_count > 15:
            self.validation_results['recommendations'].append(
                f"⚠️  High branch count ({consolidate_count}) - consider batch consolidation approach"
            )

    def run_validation(self):
        """Run complete validation suite"""
        print("🚀 Starting Phase 2A Consolidation Validation")
        print("=" * 50)
        
        validation_functions = [
            self.validate_target_branches,
            self.validate_ansible_structure,
            self.validate_consolidation_matrix,
            self.validate_git_status,
            self.validate_phase_2a_artifacts
        ]
        
        all_passed = True
        for validation_func in validation_functions:
            try:
                result = validation_func()
                if not result:
                    all_passed = False
            except Exception as e:
                print(f"❌ Validation error in {validation_func.__name__}: {e}")
                self.validation_results['errors'].append(f"Validation error: {e}")
                all_passed = False
            print()
        
        self.generate_recommendations()
        
        # Save results
        results_file = 'docs/phase-2A/validation_results.json'
        os.makedirs(os.path.dirname(results_file), exist_ok=True)
        with open(results_file, 'w') as f:
            json.dump(self.validation_results, f, indent=2)
        
        print("📊 Validation Summary")
        print("=" * 50)
        print(f"Overall Status: {self.validation_results['overall_status']}")
        print(f"Errors: {len(self.validation_results['errors'])}")
        print(f"Warnings: {len(self.validation_results['warnings'])}")
        print(f"Results saved to: {results_file}")
        
        if self.validation_results['errors']:
            print("\n❌ Errors:")
            for error in self.validation_results['errors']:
                print(f"  - {error}")
        
        if self.validation_results['warnings']:
            print("\n⚠️  Warnings:")
            for warning in self.validation_results['warnings']:
                print(f"  - {warning}")
        
        print("\n💡 Recommendations:")
        for rec in self.validation_results['recommendations']:
            print(f"  - {rec}")
        
        return all_passed

def main():
    validator = ConsolidationValidator()
    success = validator.run_validation()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
