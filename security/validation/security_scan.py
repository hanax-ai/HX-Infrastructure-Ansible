
#!/usr/bin/env python3
"""
Comprehensive Security Validation Scanner - Phase 2 Day 2
Performs security scanning of Ansible configurations and playbooks
"""

import os
import sys
import yaml
import json
import re
import subprocess
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple

class SecurityScanner:
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.findings = []
        self.stats = {
            'files_scanned': 0,
            'critical_issues': 0,
            'high_issues': 0,
            'medium_issues': 0,
            'low_issues': 0,
            'info_issues': 0
        }
        
    def add_finding(self, severity: str, category: str, message: str, 
                   file_path: str = None, line_number: int = None, 
                   recommendation: str = None):
        """Add a security finding"""
        finding = {
            'timestamp': datetime.now().isoformat(),
            'severity': severity.upper(),
            'category': category,
            'message': message,
            'file_path': str(file_path) if file_path else None,
            'line_number': line_number,
            'recommendation': recommendation
        }
        self.findings.append(finding)
        self.stats[f'{severity.lower()}_issues'] += 1
        
    def scan_yaml_files(self):
        """Scan YAML files for security issues"""
        yaml_files = list(self.base_path.rglob('*.yml')) + list(self.base_path.rglob('*.yaml'))
        
        for yaml_file in yaml_files:
            if self._should_skip_file(yaml_file):
                continue
                
            self.stats['files_scanned'] += 1
            self._scan_yaml_file(yaml_file)
            
    def _should_skip_file(self, file_path: Path) -> bool:
        """Check if file should be skipped"""
        skip_patterns = [
            '.git/',
            '__pycache__/',
            '.pytest_cache/',
            'node_modules/',
            '.venv/',
            'venv/',
        ]
        
        file_str = str(file_path)
        return any(pattern in file_str for pattern in skip_patterns)
        
    def _scan_yaml_file(self, file_path: Path):
        """Scan individual YAML file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Parse YAML
            try:
                yaml_data = yaml.safe_load(content)
            except yaml.YAMLError as e:
                self.add_finding('medium', 'syntax', f'YAML syntax error: {e}', 
                               file_path, recommendation='Fix YAML syntax errors')
                return
                
            # Security checks
            self._check_hardcoded_secrets(content, file_path)
            self._check_dangerous_commands(content, file_path)
            self._check_file_permissions(yaml_data, file_path)
            self._check_vault_usage(yaml_data, file_path)
            self._check_ssh_security(yaml_data, file_path)
            self._check_sudo_usage(yaml_data, file_path)
            self._check_network_security(yaml_data, file_path)
            
        except Exception as e:
            self.add_finding('low', 'scan_error', f'Error scanning file: {e}', 
                           file_path, recommendation='Review file manually')
            
    def _check_hardcoded_secrets(self, content: str, file_path: Path):
        """Check for hardcoded secrets"""
        secret_patterns = [
            (r'password\s*[:=]\s*["\']?[^"\'\s]{8,}', 'Potential hardcoded password'),
            (r'api[_-]?key\s*[:=]\s*["\']?[A-Za-z0-9]{20,}', 'Potential hardcoded API key'),
            (r'secret[_-]?key\s*[:=]\s*["\']?[A-Za-z0-9]{20,}', 'Potential hardcoded secret key'),
            (r'token\s*[:=]\s*["\']?[A-Za-z0-9]{20,}', 'Potential hardcoded token'),
            (r'-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----', 'Hardcoded private key'),
            (r'mysql://[^:]+:[^@]+@', 'Database connection string with credentials'),
            (r'postgresql://[^:]+:[^@]+@', 'Database connection string with credentials'),
        ]
        
        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            for pattern, description in secret_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    # Skip if it's a vault reference or template variable
                    if '{{' in line or 'vault' in line.lower() or 'lookup(' in line:
                        continue
                        
                    self.add_finding('critical', 'secrets', 
                                   f'{description} found in line {line_num}',
                                   file_path, line_num,
                                   'Use Ansible Vault or environment variables for secrets')
                    
    def _check_dangerous_commands(self, content: str, file_path: Path):
        """Check for dangerous commands"""
        dangerous_patterns = [
            (r'\brm\s+-rf\s+/', 'Dangerous recursive delete command'),
            (r'\bdd\s+if=', 'Dangerous disk operation'),
            (r'\bmkfs\b', 'Filesystem creation command'),
            (r'\bfdisk\b', 'Disk partitioning command'),
            (r'\bshred\b', 'Secure file deletion command'),
            (r'\bwipefs\b', 'Filesystem signature removal'),
            (r'>\s*/dev/sd[a-z]', 'Direct disk write operation'),
            (r'\bchmod\s+777', 'Overly permissive file permissions'),
            (r'sudo\s+su\s+-', 'Privilege escalation to root'),
        ]
        
        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            for pattern, description in dangerous_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    self.add_finding('high', 'dangerous_commands',
                                   f'{description} found in line {line_num}',
                                   file_path, line_num,
                                   'Use safer alternatives or add safety checks')
                    
    def _check_file_permissions(self, yaml_data: Any, file_path: Path):
        """Check file permissions in YAML data"""
        if not isinstance(yaml_data, (dict, list)):
            return
            
        def check_permissions_recursive(data, path=""):
            if isinstance(data, dict):
                for key, value in data.items():
                    if key == 'mode' and isinstance(value, (str, int)):
                        mode_str = str(value)
                        if mode_str.endswith('777') or mode_str.endswith('666'):
                            self.add_finding('medium', 'permissions',
                                           f'Overly permissive file mode: {mode_str}',
                                           file_path,
                                           recommendation='Use more restrictive permissions')
                    check_permissions_recursive(value, f"{path}.{key}")
            elif isinstance(data, list):
                for i, item in enumerate(data):
                    check_permissions_recursive(item, f"{path}[{i}]")
                    
        check_permissions_recursive(yaml_data)
        
    def _check_vault_usage(self, yaml_data: Any, file_path: Path):
        """Check for proper vault usage"""
        content_str = str(yaml_data)
        
        # Check for unencrypted sensitive variables
        sensitive_vars = ['password', 'secret', 'key', 'token', 'credential']
        
        if isinstance(yaml_data, dict):
            for key, value in yaml_data.items():
                if any(sensitive in key.lower() for sensitive in sensitive_vars):
                    if isinstance(value, str) and not value.startswith('$ANSIBLE_VAULT'):
                        if not ('{{' in value or 'lookup(' in value):
                            self.add_finding('high', 'vault',
                                           f'Sensitive variable "{key}" not encrypted',
                                           file_path,
                                           recommendation='Encrypt sensitive variables with ansible-vault')
                                           
    def _check_ssh_security(self, yaml_data: Any, file_path: Path):
        """Check SSH security configurations"""
        content_str = str(yaml_data).lower()
        
        # Check for weak SSH settings
        if 'passwordauthentication' in content_str and 'yes' in content_str:
            self.add_finding('high', 'ssh_security',
                           'SSH password authentication enabled',
                           file_path,
                           recommendation='Disable password authentication, use key-based auth')
                           
        if 'permitrootlogin' in content_str and 'yes' in content_str:
            self.add_finding('high', 'ssh_security',
                           'SSH root login permitted',
                           file_path,
                           recommendation='Disable root login via SSH')
                           
        if 'stricthostkeychecking' in content_str and 'no' in content_str:
            self.add_finding('medium', 'ssh_security',
                           'SSH strict host key checking disabled',
                           file_path,
                           recommendation='Enable strict host key checking')
                           
    def _check_sudo_usage(self, yaml_data: Any, file_path: Path):
        """Check sudo usage patterns"""
        content_str = str(yaml_data)
        
        # Check for passwordless sudo
        if 'NOPASSWD' in content_str:
            self.add_finding('medium', 'sudo',
                           'Passwordless sudo configuration found',
                           file_path,
                           recommendation='Limit passwordless sudo to specific commands')
                           
        # Check for overly broad sudo permissions
        if 'ALL=(ALL) ALL' in content_str:
            self.add_finding('high', 'sudo',
                           'Overly broad sudo permissions',
                           file_path,
                           recommendation='Use principle of least privilege for sudo')
                           
    def _check_network_security(self, yaml_data: Any, file_path: Path):
        """Check network security configurations"""
        content_str = str(yaml_data).lower()
        
        # Check for insecure protocols
        insecure_protocols = ['http://', 'ftp://', 'telnet://', 'rsh://']
        for protocol in insecure_protocols:
            if protocol in content_str:
                self.add_finding('medium', 'network_security',
                               f'Insecure protocol {protocol} found',
                               file_path,
                               recommendation='Use secure alternatives (HTTPS, SFTP, SSH)')
                               
        # Check for open firewall rules
        if 'ufw allow' in content_str and '0.0.0.0/0' in content_str:
            self.add_finding('medium', 'network_security',
                           'Firewall rule allows access from anywhere',
                           file_path,
                           recommendation='Restrict firewall rules to specific IP ranges')
                           
    def run_ansible_lint(self):
        """Run ansible-lint for additional checks"""
        try:
            result = subprocess.run(['ansible-lint', '--parseable', str(self.base_path)],
                                  capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                self.add_finding('info', 'ansible_lint', 'ansible-lint passed successfully')
            else:
                lines = result.stdout.split('\n')
                for line in lines:
                    if line.strip():
                        parts = line.split(':')
                        if len(parts) >= 4:
                            file_path = parts[0]
                            line_num = parts[1] if parts[1].isdigit() else None
                            message = ':'.join(parts[3:]).strip()
                            
                            self.add_finding('medium', 'ansible_lint',
                                           f'ansible-lint: {message}',
                                           file_path, line_num,
                                           'Fix ansible-lint issues')
                                           
        except subprocess.TimeoutExpired:
            self.add_finding('low', 'ansible_lint', 'ansible-lint timed out')
        except FileNotFoundError:
            self.add_finding('info', 'ansible_lint', 'ansible-lint not available')
        except Exception as e:
            self.add_finding('low', 'ansible_lint', f'ansible-lint error: {e}')
            
    def run_yamllint(self):
        """Run yamllint for YAML syntax checking"""
        try:
            result = subprocess.run(['yamllint', '-f', 'parsable', str(self.base_path)],
                                  capture_output=True, text=True, timeout=300)
            
            lines = result.stdout.split('\n')
            for line in lines:
                if line.strip():
                    # Parse yamllint output: file:line:col: [level] message
                    match = re.match(r'([^:]+):(\d+):(\d+):\s*\[(\w+)\]\s*(.+)', line)
                    if match:
                        file_path, line_num, col, level, message = match.groups()
                        severity = 'low' if level == 'warning' else 'medium'
                        
                        self.add_finding(severity, 'yaml_lint',
                                       f'YAML: {message}',
                                       file_path, int(line_num),
                                       'Fix YAML formatting issues')
                                       
        except subprocess.TimeoutExpired:
            self.add_finding('low', 'yaml_lint', 'yamllint timed out')
        except FileNotFoundError:
            self.add_finding('info', 'yaml_lint', 'yamllint not available')
        except Exception as e:
            self.add_finding('low', 'yaml_lint', f'yamllint error: {e}')
            
    def generate_report(self, output_file: str = None):
        """Generate security scan report"""
        report = {
            'scan_info': {
                'timestamp': datetime.now().isoformat(),
                'base_path': str(self.base_path),
                'scanner_version': '1.0.0',
                'total_findings': len(self.findings)
            },
            'statistics': self.stats,
            'findings': self.findings,
            'summary': {
                'risk_level': self._calculate_risk_level(),
                'recommendations': self._generate_recommendations()
            }
        }
        
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)
        
        return report
        
    def _calculate_risk_level(self) -> str:
        """Calculate overall risk level"""
        if self.stats['critical_issues'] > 0:
            return 'CRITICAL'
        elif self.stats['high_issues'] > 5:
            return 'HIGH'
        elif self.stats['high_issues'] > 0 or self.stats['medium_issues'] > 10:
            return 'MEDIUM'
        elif self.stats['medium_issues'] > 0:
            return 'LOW'
        else:
            return 'MINIMAL'
            
    def _generate_recommendations(self) -> List[str]:
        """Generate top recommendations"""
        recommendations = []
        
        if self.stats['critical_issues'] > 0:
            recommendations.append('URGENT: Address all critical security issues immediately')
            
        if self.stats['high_issues'] > 0:
            recommendations.append('Address high-severity security issues within 24 hours')
            
        # Count categories
        categories = {}
        for finding in self.findings:
            cat = finding['category']
            categories[cat] = categories.get(cat, 0) + 1
            
        # Top categories
        top_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)[:3]
        for category, count in top_categories:
            recommendations.append(f'Focus on {category} issues ({count} findings)')
            
        return recommendations
        
    def print_summary(self):
        """Print scan summary"""
        print(f"\n{'='*60}")
        print("SECURITY SCAN SUMMARY")
        print(f"{'='*60}")
        print(f"Files Scanned: {self.stats['files_scanned']}")
        print(f"Total Findings: {len(self.findings)}")
        print(f"Risk Level: {self._calculate_risk_level()}")
        print(f"\nFindings by Severity:")
        print(f"  Critical: {self.stats['critical_issues']}")
        print(f"  High:     {self.stats['high_issues']}")
        print(f"  Medium:   {self.stats['medium_issues']}")
        print(f"  Low:      {self.stats['low_issues']}")
        print(f"  Info:     {self.stats['info_issues']}")
        
        if self.findings:
            print(f"\nTop Issues:")
            for finding in sorted(self.findings, 
                                key=lambda x: {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3, 'INFO': 4}[x['severity']])[:5]:
                print(f"  [{finding['severity']}] {finding['message']}")
                if finding['file_path']:
                    print(f"    File: {finding['file_path']}")
                    
def main():
    parser = argparse.ArgumentParser(description='Ansible Security Scanner')
    parser.add_argument('path', help='Path to scan')
    parser.add_argument('--output', '-o', help='Output file for JSON report')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    scanner = SecurityScanner(args.path)
    
    print("Starting security scan...")
    scanner.scan_yaml_files()
    scanner.run_ansible_lint()
    scanner.run_yamllint()
    
    report = scanner.generate_report(args.output)
    scanner.print_summary()
    
    if args.output:
        print(f"\nDetailed report saved to: {args.output}")
        
    # Exit with error code if critical issues found
    if scanner.stats['critical_issues'] > 0:
        sys.exit(1)
    elif scanner.stats['high_issues'] > 0:
        sys.exit(2)
    else:
        sys.exit(0)
        
if __name__ == '__main__':
    main()
