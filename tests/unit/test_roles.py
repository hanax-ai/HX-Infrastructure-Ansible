
"""
Unit tests for Ansible roles
Tests role functionality, variable validation, and task logic
"""

import pytest
import yaml
import os
from pathlib import Path
from unittest.mock import Mock, patch
import tempfile
import json


class TestRoleStructure:
    """Test that roles follow proper structure and conventions"""
    
    @pytest.fixture
    def roles_dir(self):
        return Path(__file__).parent.parent.parent / 'roles'
    
    def test_roles_directory_exists(self, roles_dir):
        """Test that roles directory exists"""
        assert roles_dir.exists(), "Roles directory should exist"
        assert roles_dir.is_dir(), "Roles path should be a directory"
    
    def test_role_structure(self, roles_dir):
        """Test that each role has proper directory structure"""
        required_dirs = ['tasks', 'defaults']
        optional_dirs = ['handlers', 'templates', 'vars', 'meta', 'files']
        
        for role_dir in roles_dir.iterdir():
            if role_dir.is_dir() and not role_dir.name.startswith('.'):
                # Check required directories
                for req_dir in required_dirs:
                    dir_path = role_dir / req_dir
                    if not dir_path.exists():
                        # Allow empty roles with .keep files
                        keep_file = role_dir / '.keep'
                        assert keep_file.exists(), f"Role {role_dir.name} missing {req_dir} directory or .keep file"
    
    def test_role_metadata(self, roles_dir):
        """Test that roles have proper metadata"""
        for role_dir in roles_dir.iterdir():
            if role_dir.is_dir() and not role_dir.name.startswith('.'):
                meta_file = role_dir / 'meta' / 'main.yml'
                if meta_file.exists():
                    with open(meta_file, 'r') as f:
                        meta_data = yaml.safe_load(f)
                        assert 'galaxy_info' in meta_data, f"Role {role_dir.name} missing galaxy_info"
                        
                        galaxy_info = meta_data['galaxy_info']
                        assert 'author' in galaxy_info, f"Role {role_dir.name} missing author"
                        assert 'description' in galaxy_info, f"Role {role_dir.name} missing description"


class TestRoleVariables:
    """Test role variable definitions and validation"""
    
    @pytest.fixture
    def roles_dir(self):
        return Path(__file__).parent.parent.parent / 'roles'
    
    def test_defaults_syntax(self, roles_dir):
        """Test that defaults/main.yml files have valid YAML syntax"""
        for role_dir in roles_dir.iterdir():
            if role_dir.is_dir() and not role_dir.name.startswith('.'):
                defaults_file = role_dir / 'defaults' / 'main.yml'
                if defaults_file.exists():
                    with open(defaults_file, 'r') as f:
                        try:
                            yaml.safe_load(f)
                        except yaml.YAMLError as e:
                            pytest.fail(f"Invalid YAML in {defaults_file}: {e}")
    
    def test_vars_syntax(self, roles_dir):
        """Test that vars/main.yml files have valid YAML syntax"""
        for role_dir in roles_dir.iterdir():
            if role_dir.is_dir() and not role_dir.name.startswith('.'):
                vars_file = role_dir / 'vars' / 'main.yml'
                if vars_file.exists():
                    with open(vars_file, 'r') as f:
                        try:
                            yaml.safe_load(f)
                        except yaml.YAMLError as e:
                            pytest.fail(f"Invalid YAML in {vars_file}: {e}")
    
    def test_variable_naming(self, roles_dir):
        """Test that variables follow naming conventions"""
        for role_dir in roles_dir.iterdir():
            if role_dir.is_dir() and not role_dir.name.startswith('.'):
                defaults_file = role_dir / 'defaults' / 'main.yml'
                if defaults_file.exists():
                    with open(defaults_file, 'r') as f:
                        defaults_data = yaml.safe_load(f) or {}
                        for var_name in defaults_data.keys():
                            # Variables should use snake_case
                            assert '_' in var_name or var_name.islower(), \
                                f"Variable {var_name} in {role_dir.name} should use snake_case"


class TestRoleTasks:
    """Test role task definitions and logic"""
    
    @pytest.fixture
    def roles_dir(self):
        return Path(__file__).parent.parent.parent / 'roles'
    
    def test_tasks_syntax(self, roles_dir):
        """Test that task files have valid YAML syntax"""
        for role_dir in roles_dir.iterdir():
            if role_dir.is_dir() and not role_dir.name.startswith('.'):
                tasks_dir = role_dir / 'tasks'
                if tasks_dir.exists():
                    for task_file in tasks_dir.glob('*.yml'):
                        with open(task_file, 'r') as f:
                            try:
                                yaml.safe_load(f)
                            except yaml.YAMLError as e:
                                pytest.fail(f"Invalid YAML in {task_file}: {e}")
    
    def test_task_naming(self, roles_dir):
        """Test that tasks have descriptive names"""
        for role_dir in roles_dir.iterdir():
            if role_dir.is_dir() and not role_dir.name.startswith('.'):
                tasks_dir = role_dir / 'tasks'
                if tasks_dir.exists():
                    for task_file in tasks_dir.glob('*.yml'):
                        with open(task_file, 'r') as f:
                            tasks_data = yaml.safe_load(f) or []
                            if isinstance(tasks_data, list):
                                for task in tasks_data:
                                    if isinstance(task, dict) and 'name' in task:
                                        name = task['name']
                                        assert len(name) > 5, \
                                            f"Task name '{name}' in {task_file} should be descriptive"
                                        assert not name.startswith('Task'), \
                                            f"Task name '{name}' in {task_file} should not start with 'Task'"


class TestRoleHandlers:
    """Test role handler definitions"""
    
    @pytest.fixture
    def roles_dir(self):
        return Path(__file__).parent.parent.parent / 'roles'
    
    def test_handlers_syntax(self, roles_dir):
        """Test that handler files have valid YAML syntax"""
        for role_dir in roles_dir.iterdir():
            if role_dir.is_dir() and not role_dir.name.startswith('.'):
                handlers_dir = role_dir / 'handlers'
                if handlers_dir.exists():
                    for handler_file in handlers_dir.glob('*.yml'):
                        with open(handler_file, 'r') as f:
                            try:
                                yaml.safe_load(f)
                            except yaml.YAMLError as e:
                                pytest.fail(f"Invalid YAML in {handler_file}: {e}")


class TestRoleTemplates:
    """Test role template files"""
    
    @pytest.fixture
    def roles_dir(self):
        return Path(__file__).parent.parent.parent / 'roles'
    
    def test_template_syntax(self, roles_dir):
        """Test that Jinja2 templates have basic syntax validation"""
        from jinja2 import Environment, meta, exceptions
        
        env = Environment()
        
        for role_dir in roles_dir.iterdir():
            if role_dir.is_dir() and not role_dir.name.startswith('.'):
                templates_dir = role_dir / 'templates'
                if templates_dir.exists():
                    for template_file in templates_dir.glob('*'):
                        if template_file.is_file() and not template_file.name.startswith('.'):
                            try:
                                with open(template_file, 'r') as f:
                                    content = f.read()
                                    # Basic Jinja2 syntax validation
                                    env.parse(content)
                            except exceptions.TemplateSyntaxError as e:
                                pytest.fail(f"Template syntax error in {template_file}: {e}")
                            except UnicodeDecodeError:
                                # Skip binary files
                                pass


class TestRoleIntegration:
    """Integration tests for role functionality"""
    
    def test_role_dependencies(self):
        """Test that role dependencies are properly defined"""
        roles_dir = Path(__file__).parent.parent.parent / 'roles'
        
        for role_dir in roles_dir.iterdir():
            if role_dir.is_dir() and not role_dir.name.startswith('.'):
                meta_file = role_dir / 'meta' / 'main.yml'
                if meta_file.exists():
                    with open(meta_file, 'r') as f:
                        meta_data = yaml.safe_load(f) or {}
                        dependencies = meta_data.get('dependencies', [])
                        
                        # Check that dependencies exist
                        for dep in dependencies:
                            if isinstance(dep, str):
                                dep_name = dep
                            elif isinstance(dep, dict):
                                dep_name = dep.get('role', dep.get('name', ''))
                            
                            if dep_name and not dep_name.startswith('community.'):
                                dep_path = roles_dir / dep_name
                                assert dep_path.exists(), \
                                    f"Dependency {dep_name} for role {role_dir.name} does not exist"


class TestRoleDocumentation:
    """Test role documentation completeness"""
    
    @pytest.fixture
    def roles_dir(self):
        return Path(__file__).parent.parent.parent / 'roles'
    
    def test_readme_exists(self, roles_dir):
        """Test that important roles have README files"""
        important_roles = [
            'hx_ca_trust_standardized',
            'hx_domain_join_standardized',
            'hx_pg_auth_standardized'
        ]
        
        for role_name in important_roles:
            role_dir = roles_dir / role_name
            if role_dir.exists():
                readme_file = role_dir / 'README.md'
                assert readme_file.exists(), f"Role {role_name} should have README.md"


if __name__ == '__main__':
    pytest.main([__file__])
