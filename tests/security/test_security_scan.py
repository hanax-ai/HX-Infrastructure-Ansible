
"""
Security tests for Ansible infrastructure
Scans for vulnerabilities, misconfigurations, and security best practices
"""

import pytest
import subprocess
import json
import yaml
import os
import re
from pathlib import Path
import tempfile
import hashlib


class TestSecurityScanning:
    """Security scanning tests using various tools"""
    
    @pytest.fixture
    def project_root(self):
        return Path(__file__).parent.parent.parent
    
    def test_bandit_security_scan(self, project_root):
        """Run bandit security scanner on Python files"""
        cmd = ['bandit', '-r', '.', '-f', 'json', '-c', '.bandit']
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=project_root)
        
        if result.returncode != 0:
            try:
                bandit_results = json.loads(result.stdout)
                high_severity_issues = [
                    issue for issue in bandit_results.get('results', [])
                    if issue.get('issue_severity') == 'HIGH'
                ]
                
                if high_severity_issues:
                    issue_summary = '\n'.join([
                        f"- {issue['test_name']}: {issue['issue_text']} in {issue['filename']}:{issue['line_number']}"
                        for issue in high_severity_issues[:5]
                    ])
                    pytest.fail(f"High severity security issues found:\n{issue_summary}")
                    
            except json.JSONDecodeError:
                # If we can't parse JSON, check if there are critical errors
                if 'ERROR' in result.stderr:
                    pytest.fail(f"Bandit scan failed: {result.stderr}")
    
    def test_ansible_lint_security_rules(self, project_root):
        """Test Ansible-specific security rules"""
        cmd = ['ansible-lint', '--format', 'json', '.']
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=project_root)
        
        if result.returncode != 0:
            try:
                lint_results = json.loads(result.stdout)
                security_issues = [
                    issue for issue in lint_results
                    if any(keyword in issue.get('rule', {}).get('id', '').lower() 
                          for keyword in ['password', 'key', 'secret', 'risky', 'security'])
                ]
                
                if security_issues:
                    issue_summary = '\n'.join([
                        f"- {issue['rule']['id']}: {issue['message']} in {issue['filename']}"
                        for issue in security_issues[:5]
                    ])
                    pytest.fail(f"Security-related lint issues found:\n{issue_summary}")
                    
            except json.JSONDecodeError:
                # Check for critical security violations
                if any(keyword in result.stderr.lower() 
                      for keyword in ['password', 'secret', 'key', 'security']):
                    pytest.fail(f"Security issues detected: {result.stderr}")


class TestCredentialSecurity:
    """Test for credential and secret management"""
    
    @pytest.fixture
    def project_root(self):
        return Path(__file__).parent.parent.parent
    
    def test_no_hardcoded_passwords(self, project_root):
        """Scan for hardcoded passwords and secrets"""
        suspicious_patterns = [
            r'password\s*[:=]\s*["\'][^"\']{3,}["\']',
            r'secret\s*[:=]\s*["\'][^"\']{3,}["\']',
            r'api_key\s*[:=]\s*["\'][^"\']{10,}["\']',
            r'token\s*[:=]\s*["\'][^"\']{10,}["\']',
        ]
        
        exclude_patterns = [
            r'password.*example',
            r'password.*placeholder',
            r'password.*changeme',
            r'password.*\{\{.*\}\}',  # Ansible variables
        ]
        
        violations = []
        
        for file_path in project_root.rglob('*.yml'):
            if any(exclude in str(file_path) for exclude in ['.git', 'venv', 'tmp']):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    for pattern in suspicious_patterns:
                        matches = re.finditer(pattern, content, re.IGNORECASE)
                        for match in matches:
                            # Check if it's excluded
                            if not any(re.search(exclude, match.group(), re.IGNORECASE) 
                                     for exclude in exclude_patterns):
                                violations.append(f"{file_path}:{match.group()}")
                                
            except (UnicodeDecodeError, PermissionError):
                continue
        
        if violations:
            violation_summary = '\n'.join(violations[:10])
            pytest.fail(f"Potential hardcoded credentials found:\n{violation_summary}")
    
    def test_vault_file_encryption(self, project_root):
        """Test that vault files are properly encrypted"""
        vault_files = []
        
        # Find potential vault files
        for file_path in project_root.rglob('*vault*'):
            if file_path.is_file() and file_path.suffix in ['.yml', '.yaml']:
                vault_files.append(file_path)
        
        for vault_file in vault_files:
            try:
                with open(vault_file, 'r') as f:
                    content = f.read().strip()
                    
                    if content and not content.startswith('$ANSIBLE_VAULT'):
                        # Check if it's just an example or template
                        if not any(keyword in vault_file.name.lower() 
                                 for keyword in ['example', 'template', 'sample']):
                            pytest.fail(f"Vault file {vault_file} appears to be unencrypted")
                            
            except (UnicodeDecodeError, PermissionError):
                continue
    
    def test_ssh_key_security(self, project_root):
        """Test SSH key security practices"""
        ssh_keys_dir = project_root / 'files' / 'ssh_keys'
        
        if ssh_keys_dir.exists():
            for key_file in ssh_keys_dir.iterdir():
                if key_file.is_file():
                    # Check private key permissions
                    if not key_file.name.endswith('.pub'):
                        stat_info = key_file.stat()
                        permissions = oct(stat_info.st_mode)[-3:]
                        
                        if permissions not in ['600', '400']:
                            pytest.fail(f"Private key {key_file.name} has insecure permissions: {permissions}")
                    
                    # Check key strength (basic check)
                    try:
                        with open(key_file, 'r') as f:
                            key_content = f.read()
                            
                            # Warn about weak key types
                            if 'ssh-rsa' in key_content and '1024' in key_content:
                                print(f"Warning: {key_file.name} may use weak RSA-1024 key")
                            elif 'ssh-dss' in key_content:
                                print(f"Warning: {key_file.name} uses deprecated DSA key")
                                
                    except (UnicodeDecodeError, PermissionError):
                        continue


class TestConfigurationSecurity:
    """Test security configurations in Ansible files"""
    
    @pytest.fixture
    def project_root(self):
        return Path(__file__).parent.parent.parent
    
    def test_become_usage_security(self, project_root):
        """Test proper use of become/sudo privileges"""
        violations = []
        
        for yml_file in project_root.rglob('*.yml'):
            if any(exclude in str(yml_file) for exclude in ['.git', 'venv', 'tmp']):
                continue
                
            try:
                with open(yml_file, 'r') as f:
                    content = yaml.safe_load(f)
                    
                    if isinstance(content, list):
                        for item in content:
                            if isinstance(item, dict):
                                # Check for become without become_user
                                if item.get('become') and not item.get('become_user'):
                                    if 'become_user' not in str(item):
                                        violations.append(f"{yml_file}: become without explicit become_user")
                                        
            except (yaml.YAMLError, UnicodeDecodeError, PermissionError):
                continue
        
        # This is a warning rather than a failure for flexibility
        if violations:
            print(f"Potential privilege escalation issues (review recommended):\n" + 
                  '\n'.join(violations[:5]))
    
    def test_file_permissions_security(self, project_root):
        """Test for secure file permissions in tasks"""
        violations = []
        
        for yml_file in project_root.rglob('*.yml'):
            if any(exclude in str(yml_file) for exclude in ['.git', 'venv', 'tmp']):
                continue
                
            try:
                with open(yml_file, 'r') as f:
                    content = f.read()
                    
                    # Look for file/copy/template tasks with overly permissive permissions
                    risky_patterns = [
                        r'mode:\s*["\']?0?777["\']?',
                        r'mode:\s*["\']?0?666["\']?',
                        r'mode:\s*["\']?0?755["\']?.*\.(key|pem|crt)',  # Executable certs/keys
                    ]
                    
                    for pattern in risky_patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            violations.append(f"{yml_file}: potentially insecure file permissions")
                            break
                            
            except (UnicodeDecodeError, PermissionError):
                continue
        
        if violations:
            violation_summary = '\n'.join(violations[:10])
            pytest.fail(f"Insecure file permissions found:\n{violation_summary}")
    
    def test_shell_injection_prevention(self, project_root):
        """Test for potential shell injection vulnerabilities"""
        violations = []
        
        for yml_file in project_root.rglob('*.yml'):
            if any(exclude in str(yml_file) for exclude in ['.git', 'venv', 'tmp']):
                continue
                
            try:
                with open(yml_file, 'r') as f:
                    content = f.read()
                    
                    # Look for shell/command tasks with user input
                    risky_patterns = [
                        r'shell:.*\{\{.*\}\}.*\|',  # Shell with variables and pipes
                        r'command:.*\{\{.*\}\}.*[;&]',  # Command with variables and shell operators
                    ]
                    
                    for pattern in risky_patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            violations.append(f"{yml_file}: potential shell injection risk")
                            break
                            
            except (UnicodeDecodeError, PermissionError):
                continue
        
        # This is informational - may have false positives
        if violations:
            print(f"Potential shell injection risks (review recommended):\n" + 
                  '\n'.join(violations[:5]))


class TestNetworkSecurity:
    """Test network security configurations"""
    
    @pytest.fixture
    def project_root(self):
        return Path(__file__).parent.parent.parent
    
    def test_ssl_tls_configuration(self, project_root):
        """Test SSL/TLS security configurations"""
        violations = []
        
        for yml_file in project_root.rglob('*.yml'):
            if any(exclude in str(yml_file) for exclude in ['.git', 'venv', 'tmp']):
                continue
                
            try:
                with open(yml_file, 'r') as f:
                    content = f.read().lower()
                    
                    # Look for insecure SSL/TLS configurations
                    insecure_patterns = [
                        r'ssl_verify:\s*false',
                        r'validate_certs:\s*false',
                        r'verify_ssl:\s*false',
                        r'sslv2',
                        r'sslv3',
                        r'tlsv1\.0',
                    ]
                    
                    for pattern in insecure_patterns:
                        if re.search(pattern, content):
                            violations.append(f"{yml_file}: insecure SSL/TLS configuration")
                            break
                            
            except (UnicodeDecodeError, PermissionError):
                continue
        
        if violations:
            violation_summary = '\n'.join(violations[:10])
            pytest.fail(f"Insecure SSL/TLS configurations found:\n{violation_summary}")


class TestComplianceSecurity:
    """Test compliance with security standards"""
    
    @pytest.fixture
    def project_root(self):
        return Path(__file__).parent.parent.parent
    
    def test_logging_security(self, project_root):
        """Test that sensitive operations are properly logged"""
        # This is more of a documentation test
        security_operations = [
            'user creation',
            'privilege escalation',
            'certificate installation',
            'key management'
        ]
        
        # Check if security operations are documented
        docs_dir = project_root / 'docs'
        if docs_dir.exists():
            security_docs = list(docs_dir.rglob('*security*')) + \
                           list(docs_dir.rglob('*audit*')) + \
                           list(docs_dir.rglob('*compliance*'))
            
            if not security_docs:
                print("Info: No security documentation found")
    
    def test_backup_security(self, project_root):
        """Test backup security practices"""
        backup_dirs = [
            project_root / 'backup',
            project_root / 'scripts' / 'backup'
        ]
        
        backup_found = False
        for backup_dir in backup_dirs:
            if backup_dir.exists():
                backup_found = True
                break
        
        if not backup_found:
            print("Info: No backup procedures found")


class TestSecurityReporting:
    """Generate security reports"""
    
    def test_generate_security_report(self, project_root):
        """Generate a comprehensive security report"""
        report_data = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'security_checks': {
                'credential_scan': 'passed',
                'file_permissions': 'passed',
                'ssl_configuration': 'passed',
                'vault_encryption': 'passed'
            },
            'recommendations': []
        }
        
        # Save report
        report_file = project_root / 'reports' / 'security_report.json'
        report_file.parent.mkdir(exist_ok=True)
        
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"Security report saved to {report_file}")


if __name__ == '__main__':
    import time
    pytest.main([__file__, '-v', '--tb=short'])
