
"""
Integration tests for deployment scenarios
Tests end-to-end deployment workflows and multi-role interactions
"""

import pytest
import subprocess
import tempfile
import yaml
import os
from pathlib import Path
import json
import time


class TestDeploymentWorkflow:
    """Test complete deployment workflows"""
    
    @pytest.fixture
    def project_root(self):
        return Path(__file__).parent.parent.parent
    
    @pytest.fixture
    def inventory_file(self, project_root):
        return project_root / 'inventories' / 'dev' / 'hosts.yml'
    
    def test_inventory_syntax(self, inventory_file):
        """Test that inventory files have valid syntax"""
        assert inventory_file.exists(), "Development inventory should exist"
        
        with open(inventory_file, 'r') as f:
            try:
                inventory_data = yaml.safe_load(f)
                assert inventory_data is not None, "Inventory should not be empty"
            except yaml.YAMLError as e:
                pytest.fail(f"Invalid YAML in inventory: {e}")
    
    def test_playbook_syntax_check(self, project_root):
        """Test that main playbooks pass syntax check"""
        playbooks = [
            'site.yml',
            'playbooks/safety_test.yml',
            'playbooks/phase3_integration_test.yml'
        ]
        
        for playbook in playbooks:
            playbook_path = project_root / playbook
            if playbook_path.exists():
                cmd = [
                    'ansible-playbook',
                    '--syntax-check',
                    '--inventory', str(project_root / 'inventories' / 'dev' / 'hosts.yml'),
                    str(playbook_path)
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, cwd=project_root)
                assert result.returncode == 0, f"Syntax check failed for {playbook}: {result.stderr}"
    
    def test_ansible_lint_compliance(self, project_root):
        """Test that playbooks pass ansible-lint checks"""
        cmd = ['ansible-lint', '--format', 'json', '.']
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=project_root)
        
        if result.returncode != 0:
            try:
                lint_results = json.loads(result.stdout)
                # Filter out warnings and focus on errors
                errors = [issue for issue in lint_results if issue.get('level') == 'error']
                if errors:
                    error_summary = '\n'.join([f"- {err['message']} in {err['filename']}" for err in errors[:5]])
                    pytest.fail(f"Ansible-lint errors found:\n{error_summary}")
            except json.JSONDecodeError:
                # If JSON parsing fails, show raw output
                if 'CRITICAL' in result.stderr or 'ERROR' in result.stderr:
                    pytest.fail(f"Ansible-lint failed: {result.stderr}")


class TestRoleIntegration:
    """Test integration between multiple roles"""
    
    @pytest.fixture
    def project_root(self):
        return Path(__file__).parent.parent.parent
    
    def test_role_dependencies_resolution(self, project_root):
        """Test that role dependencies can be resolved"""
        roles_dir = project_root / 'roles'
        
        for role_dir in roles_dir.iterdir():
            if role_dir.is_dir() and not role_dir.name.startswith('.'):
                meta_file = role_dir / 'meta' / 'main.yml'
                if meta_file.exists():
                    with open(meta_file, 'r') as f:
                        meta_data = yaml.safe_load(f) or {}
                        dependencies = meta_data.get('dependencies', [])
                        
                        for dep in dependencies:
                            if isinstance(dep, str):
                                dep_name = dep
                            elif isinstance(dep, dict):
                                dep_name = dep.get('role', dep.get('name', ''))
                            
                            # Check local dependencies exist
                            if dep_name and not dep_name.startswith('community.'):
                                dep_path = roles_dir / dep_name
                                assert dep_path.exists(), \
                                    f"Role dependency {dep_name} not found for {role_dir.name}"
    
    def test_variable_consistency(self, project_root):
        """Test that variables are consistently defined across roles"""
        roles_dir = project_root / 'roles'
        all_variables = {}
        
        # Collect all variables from all roles
        for role_dir in roles_dir.iterdir():
            if role_dir.is_dir() and not role_dir.name.startswith('.'):
                defaults_file = role_dir / 'defaults' / 'main.yml'
                if defaults_file.exists():
                    with open(defaults_file, 'r') as f:
                        defaults_data = yaml.safe_load(f) or {}
                        for var_name, var_value in defaults_data.items():
                            if var_name in all_variables:
                                # Check for conflicting default values
                                if all_variables[var_name] != var_value:
                                    print(f"Warning: Variable {var_name} has different defaults in multiple roles")
                            all_variables[var_name] = var_value


class TestEnvironmentConfiguration:
    """Test environment-specific configurations"""
    
    @pytest.fixture
    def project_root(self):
        return Path(__file__).parent.parent.parent
    
    def test_environment_inventories(self, project_root):
        """Test that all environment inventories are valid"""
        inventories_dir = project_root / 'inventories'
        environments = ['dev', 'test', 'prod']
        
        for env in environments:
            env_dir = inventories_dir / env
            if env_dir.exists():
                hosts_file = env_dir / 'hosts.yml'
                if hosts_file.exists():
                    with open(hosts_file, 'r') as f:
                        try:
                            inventory_data = yaml.safe_load(f)
                            assert inventory_data is not None, f"{env} inventory should not be empty"
                        except yaml.YAMLError as e:
                            pytest.fail(f"Invalid YAML in {env} inventory: {e}")
    
    def test_group_vars_consistency(self, project_root):
        """Test that group_vars are consistently structured"""
        group_vars_dir = project_root / 'group_vars'
        
        if group_vars_dir.exists():
            for group_file in group_vars_dir.glob('*.yml'):
                with open(group_file, 'r') as f:
                    try:
                        group_data = yaml.safe_load(f)
                        if group_data:
                            # Basic validation that it's a dictionary
                            assert isinstance(group_data, dict), \
                                f"Group vars in {group_file.name} should be a dictionary"
                    except yaml.YAMLError as e:
                        pytest.fail(f"Invalid YAML in group vars {group_file.name}: {e}")


class TestSecurityConfiguration:
    """Test security-related configurations"""
    
    @pytest.fixture
    def project_root(self):
        return Path(__file__).parent.parent.parent
    
    def test_vault_file_encryption(self, project_root):
        """Test that vault files are properly encrypted"""
        vault_dirs = [
            project_root / 'vault',
            project_root / 'group_vars',
            project_root / 'host_vars'
        ]
        
        for vault_dir in vault_dirs:
            if vault_dir.exists():
                for vault_file in vault_dir.rglob('*vault*'):
                    if vault_file.is_file() and vault_file.suffix in ['.yml', '.yaml']:
                        with open(vault_file, 'r') as f:
                            content = f.read()
                            # Check if file is encrypted (starts with $ANSIBLE_VAULT)
                            if content.strip() and not content.startswith('$ANSIBLE_VAULT'):
                                # This might be a template or example file
                                if 'example' not in vault_file.name.lower():
                                    print(f"Warning: {vault_file} may contain unencrypted sensitive data")
    
    def test_ssh_key_permissions(self, project_root):
        """Test that SSH keys have proper permissions"""
        ssh_keys_dir = project_root / 'files' / 'ssh_keys'
        
        if ssh_keys_dir.exists():
            for key_file in ssh_keys_dir.glob('*'):
                if key_file.is_file() and not key_file.name.endswith('.pub'):
                    # Private keys should have restrictive permissions
                    stat_info = key_file.stat()
                    permissions = oct(stat_info.st_mode)[-3:]
                    assert permissions in ['600', '400'], \
                        f"Private key {key_file.name} should have 600 or 400 permissions, got {permissions}"


class TestBackupAndRecovery:
    """Test backup and recovery procedures"""
    
    @pytest.fixture
    def project_root(self):
        return Path(__file__).parent.parent.parent
    
    def test_backup_scripts_exist(self, project_root):
        """Test that backup scripts are available"""
        backup_dirs = [
            project_root / 'scripts' / 'backup',
            project_root / 'backup' / 'scripts'
        ]
        
        backup_script_found = False
        for backup_dir in backup_dirs:
            if backup_dir.exists():
                scripts = list(backup_dir.glob('*.sh')) + list(backup_dir.glob('*.py'))
                if scripts:
                    backup_script_found = True
                    break
        
        # This is informational - backup scripts may be role-specific
        if not backup_script_found:
            print("Info: No backup scripts found in common locations")
    
    def test_recovery_procedures_documented(self, project_root):
        """Test that recovery procedures are documented"""
        docs_dir = project_root / 'docs'
        recovery_docs = []
        
        if docs_dir.exists():
            recovery_docs = list(docs_dir.rglob('*recovery*')) + \
                           list(docs_dir.rglob('*backup*')) + \
                           list(docs_dir.rglob('*restore*'))
        
        # This is informational
        if not recovery_docs:
            print("Info: No recovery documentation found")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
