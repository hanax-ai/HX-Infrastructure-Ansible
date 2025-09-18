
#!/usr/bin/env python3
"""
Quality Gate Assessment Script for HX Infrastructure Ansible
Evaluates overall project quality and enforces standards for Phase 4
"""

import json
import sys
import os
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Tuple, Any
import yaml


class QualityAssessment:
    """Comprehensive quality assessment for Ansible infrastructure"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.reports_dir = self.project_root / "reports"
        self.reports_dir.mkdir(exist_ok=True)
        
        self.quality_metrics = {
            'documentation': 0,
            'testing': 0,
            'security': 0,
            'performance': 0,
            'compliance': 0,
            'maintainability': 0
        }
        
        self.target_score = 9.5  # Phase 4 target
        self.minimum_score = 9.0  # Minimum acceptable
        
    def assess_documentation_quality(self) -> float:
        """Assess documentation completeness and quality"""
        print("📚 Assessing documentation quality...")
        
        score = 0.0
        max_score = 100.0
        
        # Check for key documentation files
        key_docs = [
            'README.md',
            'docs/SECURITY.md',
            'docs/development_guidelines.md',
            'docs_site/docs/index.md'
        ]
        
        existing_docs = 0
        for doc in key_docs:
            if (self.project_root / doc).exists():
                existing_docs += 1
        
        score += (existing_docs / len(key_docs)) * 30
        
        # Check role documentation
        roles_dir = self.project_root / 'roles'
        if roles_dir.exists():
            roles_with_docs = 0
            total_roles = 0
            
            for role_dir in roles_dir.iterdir():
                if role_dir.is_dir() and not role_dir.name.startswith('.'):
                    total_roles += 1
                    readme_file = role_dir / 'README.md'
                    if readme_file.exists():
                        roles_with_docs += 1
            
            if total_roles > 0:
                score += (roles_with_docs / total_roles) * 25
        
        # Check for generated documentation
        docs_site = self.project_root / 'docs_site'
        if docs_site.exists():
            score += 20
            
            # Check if documentation builds successfully
            try:
                result = subprocess.run(
                    ['mkdocs', 'build', '--strict'],
                    cwd=docs_site,
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    score += 15
            except FileNotFoundError:
                pass
        
        # Check documentation style compliance
        try:
            result = subprocess.run(
                ['markdownlint-cli2', '**/*.md'],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                score += 10
        except FileNotFoundError:
            pass
        
        self.quality_metrics['documentation'] = min(score, max_score)
        return self.quality_metrics['documentation']
    
    def assess_testing_coverage(self) -> float:
        """Assess testing framework and coverage"""
        print("🧪 Assessing testing coverage...")
        
        score = 0.0
        max_score = 100.0
        
        # Check for test directories and files
        test_types = ['unit', 'integration', 'performance', 'security', 'chaos']
        existing_tests = 0
        
        for test_type in test_types:
            test_dir = self.project_root / 'tests' / test_type
            if test_dir.exists() and list(test_dir.glob('test_*.py')):
                existing_tests += 1
        
        score += (existing_tests / len(test_types)) * 40
        
        # Check for Molecule tests
        molecule_tests = 0
        roles_dir = self.project_root / 'roles'
        if roles_dir.exists():
            for role_dir in roles_dir.iterdir():
                if role_dir.is_dir() and (role_dir / 'molecule').exists():
                    molecule_tests += 1
        
        if molecule_tests > 0:
            score += 20
        
        # Run actual tests and check results
        try:
            # Run unit tests
            result = subprocess.run(
                ['python', '-m', 'pytest', 'tests/unit/', '--tb=short'],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                score += 20
            elif 'passed' in result.stdout:
                score += 10
        except Exception:
            pass
        
        # Check for test configuration
        test_configs = ['.pytest.ini', 'pytest.ini', 'pyproject.toml']
        for config in test_configs:
            if (self.project_root / config).exists():
                score += 5
                break
        
        # Check syntax validation
        try:
            result = subprocess.run(
                ['ansible-playbook', '--syntax-check', 'site.yml'],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                score += 15
        except Exception:
            pass
        
        self.quality_metrics['testing'] = min(score, max_score)
        return self.quality_metrics['testing']
    
    def assess_security_compliance(self) -> float:
        """Assess security practices and compliance"""
        print("🔒 Assessing security compliance...")
        
        score = 0.0
        max_score = 100.0
        
        # Check for security configuration files
        security_configs = ['.bandit', 'security/']
        for config in security_configs:
            if (self.project_root / config).exists():
                score += 10
        
        # Run security scans
        try:
            result = subprocess.run(
                ['bandit', '-r', '.', '-f', 'json'],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                score += 25
                # Parse results for severity
                try:
                    bandit_data = json.loads(result.stdout)
                    high_issues = len([
                        issue for issue in bandit_data.get('results', [])
                        if issue.get('issue_severity') == 'HIGH'
                    ])
                    if high_issues == 0:
                        score += 15
                except json.JSONDecodeError:
                    pass
        except Exception:
            pass
        
        # Check for vault usage
        vault_files = list(self.project_root.rglob('*vault*'))
        if vault_files:
            score += 10
        
        # Check for proper file permissions in SSH keys
        ssh_keys_dir = self.project_root / 'files' / 'ssh_keys'
        if ssh_keys_dir.exists():
            secure_keys = 0
            total_keys = 0
            for key_file in ssh_keys_dir.iterdir():
                if key_file.is_file() and not key_file.name.endswith('.pub'):
                    total_keys += 1
                    stat_info = key_file.stat()
                    permissions = oct(stat_info.st_mode)[-3:]
                    if permissions in ['600', '400']:
                        secure_keys += 1
            
            if total_keys > 0:
                score += (secure_keys / total_keys) * 15
        
        # Check for security documentation
        security_docs = list(self.project_root.rglob('*security*'))
        if security_docs:
            score += 10
        
        # Run security tests
        try:
            result = subprocess.run(
                ['python', '-m', 'pytest', 'tests/security/', '--tb=short'],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                score += 15
        except Exception:
            pass
        
        self.quality_metrics['security'] = min(score, max_score)
        return self.quality_metrics['security']
    
    def assess_performance_standards(self) -> float:
        """Assess performance and efficiency"""
        print("⚡ Assessing performance standards...")
        
        score = 0.0
        max_score = 100.0
        
        # Check for performance tests
        perf_tests = self.project_root / 'tests' / 'performance'
        if perf_tests.exists() and list(perf_tests.glob('test_*.py')):
            score += 30
        
        # Run performance benchmarks
        try:
            result = subprocess.run(
                ['python', '-m', 'pytest', 'tests/performance/', '--tb=short'],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                score += 25
        except Exception:
            pass
        
        # Check ansible-lint performance
        try:
            start_time = time.time()
            result = subprocess.run(
                ['ansible-lint', '.'],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            duration = time.time() - start_time
            
            # Score based on linting speed (under 60 seconds is good)
            if duration < 30:
                score += 20
            elif duration < 60:
                score += 15
            elif duration < 120:
                score += 10
        except Exception:
            pass
        
        # Check for optimization configurations
        optimization_files = ['.ansible-lint', '.yamllint', 'ansible.cfg']
        for opt_file in optimization_files:
            if (self.project_root / opt_file).exists():
                score += 5
        
        # Check role efficiency (fewer files, better organization)
        roles_dir = self.project_root / 'roles'
        if roles_dir.exists():
            efficient_roles = 0
            total_roles = 0
            
            for role_dir in roles_dir.iterdir():
                if role_dir.is_dir() and not role_dir.name.startswith('.'):
                    total_roles += 1
                    # Check for proper role structure
                    required_dirs = ['tasks', 'defaults']
                    has_structure = all(
                        (role_dir / req_dir).exists() or (role_dir / '.keep').exists()
                        for req_dir in required_dirs
                    )
                    if has_structure:
                        efficient_roles += 1
            
            if total_roles > 0:
                score += (efficient_roles / total_roles) * 10
        
        self.quality_metrics['performance'] = min(score, max_score)
        return self.quality_metrics['performance']
    
    def assess_compliance_standards(self) -> float:
        """Assess compliance with Ansible and industry standards"""
        print("📋 Assessing compliance standards...")
        
        score = 0.0
        max_score = 100.0
        
        # Run ansible-lint for compliance
        try:
            result = subprocess.run(
                ['ansible-lint', '--format', 'json', '.'],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                score += 40
            else:
                try:
                    lint_data = json.loads(result.stdout)
                    error_count = len([
                        issue for issue in lint_data
                        if issue.get('level') == 'error'
                    ])
                    # Partial score based on error count
                    if error_count == 0:
                        score += 40
                    elif error_count < 5:
                        score += 30
                    elif error_count < 10:
                        score += 20
                    else:
                        score += 10
                except json.JSONDecodeError:
                    score += 10
        except Exception:
            pass
        
        # Run yamllint for YAML compliance
        try:
            result = subprocess.run(
                ['yamllint', '.'],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                score += 25
            elif 'error' not in result.stdout.lower():
                score += 15
        except Exception:
            pass
        
        # Check for compliance documentation
        compliance_docs = [
            'docs/compliance/',
            'docs/SECURITY.md',
            'CHANGELOG.md'
        ]
        
        existing_compliance = 0
        for doc in compliance_docs:
            if (self.project_root / doc).exists():
                existing_compliance += 1
        
        score += (existing_compliance / len(compliance_docs)) * 15
        
        # Check for proper metadata in roles
        roles_dir = self.project_root / 'roles'
        if roles_dir.exists():
            compliant_roles = 0
            total_roles = 0
            
            for role_dir in roles_dir.iterdir():
                if role_dir.is_dir() and not role_dir.name.startswith('.'):
                    total_roles += 1
                    meta_file = role_dir / 'meta' / 'main.yml'
                    if meta_file.exists():
                        try:
                            with open(meta_file, 'r') as f:
                                meta_data = yaml.safe_load(f)
                                if 'galaxy_info' in meta_data:
                                    compliant_roles += 1
                        except Exception:
                            pass
            
            if total_roles > 0:
                score += (compliant_roles / total_roles) * 20
        
        self.quality_metrics['compliance'] = min(score, max_score)
        return self.quality_metrics['compliance']
    
    def assess_maintainability(self) -> float:
        """Assess code maintainability and organization"""
        print("🔧 Assessing maintainability...")
        
        score = 0.0
        max_score = 100.0
        
        # Check for proper project structure
        required_dirs = [
            'roles', 'playbooks', 'inventories', 'group_vars',
            'docs', 'tests', 'scripts'
        ]
        
        existing_dirs = 0
        for req_dir in required_dirs:
            if (self.project_root / req_dir).exists():
                existing_dirs += 1
        
        score += (existing_dirs / len(required_dirs)) * 25
        
        # Check for configuration files
        config_files = [
            'ansible.cfg', 'requirements.yml', '.gitignore',
            '.pre-commit-config.yaml'
        ]
        
        existing_configs = 0
        for config in config_files:
            if (self.project_root / config).exists():
                existing_configs += 1
        
        score += (existing_configs / len(config_files)) * 20
        
        # Check for automation
        automation_files = [
            '.github/workflows/',
            'scripts/quality/',
            '.pre-commit-config.yaml'
        ]
        
        existing_automation = 0
        for auto_file in automation_files:
            if (self.project_root / auto_file).exists():
                existing_automation += 1
        
        score += (existing_automation / len(automation_files)) * 25
        
        # Check for version control best practices
        gitignore = self.project_root / '.gitignore'
        if gitignore.exists():
            score += 10
            try:
                with open(gitignore, 'r') as f:
                    content = f.read()
                    if 'venv' in content and '*.pyc' in content:
                        score += 5
            except Exception:
                pass
        
        # Check for dependency management
        requirements = self.project_root / 'requirements.yml'
        if requirements.exists():
            score += 10
            try:
                with open(requirements, 'r') as f:
                    req_data = yaml.safe_load(f)
                    if isinstance(req_data, list) and len(req_data) > 0:
                        score += 5
            except Exception:
                pass
        
        self.quality_metrics['maintainability'] = min(score, max_score)
        return self.quality_metrics['maintainability']
    
    def calculate_overall_score(self) -> float:
        """Calculate overall quality score"""
        weights = {
            'documentation': 0.20,
            'testing': 0.25,
            'security': 0.20,
            'performance': 0.15,
            'compliance': 0.15,
            'maintainability': 0.05
        }
        
        weighted_score = sum(
            self.quality_metrics[metric] * weight
            for metric, weight in weights.items()
        )
        
        # Convert to 10-point scale
        return weighted_score / 10.0
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive quality report"""
        print("\n🎯 Running comprehensive quality assessment...")
        
        # Run all assessments
        self.assess_documentation_quality()
        self.assess_testing_coverage()
        self.assess_security_compliance()
        self.assess_performance_standards()
        self.assess_compliance_standards()
        self.assess_maintainability()
        
        overall_score = self.calculate_overall_score()
        
        report = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'overall_score': round(overall_score, 2),
            'target_score': self.target_score,
            'minimum_score': self.minimum_score,
            'quality_metrics': {
                metric: round(score, 2)
                for metric, score in self.quality_metrics.items()
            },
            'assessment': self.get_quality_assessment(overall_score),
            'recommendations': self.get_recommendations(),
            'phase_status': self.get_phase_status(overall_score)
        }
        
        return report
    
    def get_quality_assessment(self, score: float) -> str:
        """Get quality assessment based on score"""
        if score >= 9.5:
            return "EXEMPLARY - Phase 4 Target Achieved"
        elif score >= 9.0:
            return "EXCELLENT - High Quality Infrastructure"
        elif score >= 8.5:
            return "GOOD - Above Average Quality"
        elif score >= 8.0:
            return "ACCEPTABLE - Meets Basic Standards"
        else:
            return "NEEDS IMPROVEMENT - Below Standards"
    
    def get_recommendations(self) -> List[str]:
        """Generate recommendations based on assessment"""
        recommendations = []
        
        for metric, score in self.quality_metrics.items():
            if score < 80:
                if metric == 'documentation':
                    recommendations.append(
                        "Improve documentation coverage - add README files to all roles"
                    )
                elif metric == 'testing':
                    recommendations.append(
                        "Enhance testing framework - add more unit and integration tests"
                    )
                elif metric == 'security':
                    recommendations.append(
                        "Strengthen security practices - review vault usage and permissions"
                    )
                elif metric == 'performance':
                    recommendations.append(
                        "Optimize performance - review role efficiency and linting speed"
                    )
                elif metric == 'compliance':
                    recommendations.append(
                        "Improve compliance - fix ansible-lint and yamllint issues"
                    )
                elif metric == 'maintainability':
                    recommendations.append(
                        "Enhance maintainability - improve project structure and automation"
                    )
        
        return recommendations
    
    def get_phase_status(self, score: float) -> str:
        """Determine phase completion status"""
        if score >= self.target_score:
            return "PHASE 4 COMPLETE - Exemplary Infrastructure Automation Achieved"
        elif score >= self.minimum_score:
            return "PHASE 3 COMPLETE - Ready for Phase 4 Optimization"
        else:
            return "IN PROGRESS - Continue Quality Improvements"
    
    def save_report(self, report: Dict[str, Any]) -> None:
        """Save quality report to file"""
        report_file = self.reports_dir / 'quality_assessment.json'
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📊 Quality report saved to: {report_file}")
    
    def print_summary(self, report: Dict[str, Any]) -> None:
        """Print quality assessment summary"""
        print("\n" + "="*60)
        print("🎯 HX INFRASTRUCTURE ANSIBLE - QUALITY ASSESSMENT")
        print("="*60)
        print(f"Overall Score: {report['overall_score']}/10.0")
        print(f"Assessment: {report['assessment']}")
        print(f"Phase Status: {report['phase_status']}")
        print("\n📊 Quality Metrics:")
        
        for metric, score in report['quality_metrics'].items():
            status = "✅" if score >= 80 else "⚠️" if score >= 60 else "❌"
            print(f"  {status} {metric.title()}: {score}/100")
        
        if report['recommendations']:
            print("\n💡 Recommendations:")
            for i, rec in enumerate(report['recommendations'], 1):
                print(f"  {i}. {rec}")
        
        print("\n" + "="*60)


def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Quality Gate Assessment for HX Infrastructure Ansible'
    )
    parser.add_argument(
        '--enforce',
        action='store_true',
        help='Enforce quality gate (exit with error if below minimum)'
    )
    parser.add_argument(
        '--target',
        type=float,
        default=9.5,
        help='Target quality score (default: 9.5)'
    )
    parser.add_argument(
        '--minimum',
        type=float,
        default=9.0,
        help='Minimum acceptable score (default: 9.0)'
    )
    
    args = parser.parse_args()
    
    # Initialize quality assessment
    qa = QualityAssessment()
    qa.target_score = args.target
    qa.minimum_score = args.minimum
    
    # Generate report
    report = qa.generate_report()
    
    # Save and display results
    qa.save_report(report)
    qa.print_summary(report)
    
    # Enforce quality gate if requested
    if args.enforce:
        if report['overall_score'] < args.minimum:
            print(f"\n❌ Quality gate failed: {report['overall_score']} < {args.minimum}")
            sys.exit(1)
        else:
            print(f"\n✅ Quality gate passed: {report['overall_score']} >= {args.minimum}")
    
    return report['overall_score']


if __name__ == '__main__':
    main()
