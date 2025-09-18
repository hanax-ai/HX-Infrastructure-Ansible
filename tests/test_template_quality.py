
#!/usr/bin/env python3
"""
Test Suite for Template Quality Enhancement Framework
"""

import os
import sys
import json
import pytest
import tempfile
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from template_validator import TemplateValidator
from template_docgen import TemplateDocGenerator

class TestTemplateValidator:
    
    def setup_method(self):
        """Setup test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.test_templates = []
        
        # Create test templates
        self.create_test_template("good_template.j2", """
{# Good template with proper structure #}
{% extends 'base.j2' %}

{% block configuration %}
server_name {{ server_name | default('localhost') }}
port {{ port | default(80) }}
{% endblock %}

{% block security %}
ssl_certificate {{ ssl_cert | default('/etc/ssl/cert.pem') }}
{% endblock %}
""")
        
        self.create_test_template("bad_template.j2", """
{# Bad template with security issues #}
password = "hardcoded_secret_123"
{% for item in items %}
  {% for subitem in item.subitems %}
    {{ subitem | raw }}
  {% endfor %}
{% endfor %}
""")
        
        self.create_test_template("complex_template.j2", """
{# Complex template for performance testing #}
{% if condition1 and condition2 or condition3 and condition4 %}
  {% for i in range(100) %}
    {% for j in range(100) %}
      {{ data[i][j] | filter1 | filter2 | filter3 | filter4 }}
    {% endfor %}
  {% endfor %}
{% endif %}
""")
    
    def create_test_template(self, name, content):
        """Create a test template file"""
        template_path = os.path.join(self.test_dir, name)
        with open(template_path, 'w') as f:
            f.write(content)
        self.test_templates.append(template_path)
        return template_path
    
    def test_template_validator_initialization(self):
        """Test validator initialization"""
        validator = TemplateValidator(self.test_dir)
        assert validator.base_path == Path(self.test_dir)
        assert validator.env is not None
        assert validator.results is not None
    
    def test_good_template_analysis(self):
        """Test analysis of a well-structured template"""
        validator = TemplateValidator(self.test_dir)
        result = validator.analyze_template(self.test_templates[0])
        
        assert result['syntax_valid'] is True
        assert result['security_score'] >= 80
        assert result['performance_score'] >= 80
        assert 'server_name' in result['variables']
        assert 'port' in result['variables']
        assert result['extends'] == 'base.j2'
    
    def test_bad_template_analysis(self):
        """Test analysis of a template with security issues"""
        validator = TemplateValidator(self.test_dir)
        result = validator.analyze_template(self.test_templates[1])
        
        assert result['syntax_valid'] is True
        assert result['security_score'] < 80  # Should be penalized for hardcoded secrets
        assert len(result['security_issues']) > 0
        
        # Check for hardcoded secret detection
        security_categories = [issue['category'] for issue in result['security_issues']]
        assert 'hardcoded_secrets' in security_categories
    
    def test_complex_template_analysis(self):
        """Test analysis of a complex template"""
        validator = TemplateValidator(self.test_dir)
        result = validator.analyze_template(self.test_templates[2])
        
        assert result['syntax_valid'] is True
        assert result['complexity_score'] > 10  # Should be marked as complex
        assert result['performance_score'] < 80  # Should be penalized for nested loops
        
        # Check for performance issues
        perf_issues = [issue['type'] for issue in result.get('performance_issues', [])]
        assert 'nested_loops' in perf_issues
        assert 'complex_conditionals' in perf_issues
    
    def test_inheritance_analysis(self):
        """Test template inheritance pattern analysis"""
        validator = TemplateValidator(self.test_dir)
        inheritance = validator.analyze_inheritance_patterns(self.test_templates)
        
        assert 'inheritance_map' in inheritance
        assert 'base_templates' in inheritance
        assert 'child_templates' in inheritance
        
        # good_template.j2 should be identified as a child template
        child_templates = inheritance['child_templates']
        assert any('good_template.j2' in template for template in child_templates)
    
    def test_full_validation(self):
        """Test full validation process"""
        validator = TemplateValidator(self.test_dir)
        results = validator.validate_templates(self.test_templates)
        
        assert 'summary' in results
        assert 'templates' in results
        assert 'inheritance_analysis' in results
        
        summary = results['summary']
        assert summary['total_templates'] == len(self.test_templates)
        assert summary['valid_templates'] >= 0
        assert summary['average_security_score'] >= 0
        assert summary['average_performance_score'] >= 0

class TestTemplateDocGenerator:
    
    def setup_method(self):
        """Setup test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.doc_dir = os.path.join(self.test_dir, 'docs')
        
        # Create test template
        self.test_template = self.create_test_template("documented_template.j2", """
{# 
This is a well-documented template
It demonstrates proper documentation practices
#}
{% extends 'base.j2' %}

{# Configuration block for server settings #}
{% block configuration %}
server_name {{ server_name | default('localhost') }}
port {{ port | default(80) }}
{% endblock %}

{# Macro for generating SSL configuration #}
{% macro ssl_config(cert_path, key_path) %}
ssl_certificate {{ cert_path }}
ssl_certificate_key {{ key_path }}
{% endmacro %}

{# Include additional configuration #}
{% include 'ssl_settings.j2' %}
""")
    
    def create_test_template(self, name, content):
        """Create a test template file"""
        template_path = os.path.join(self.test_dir, name)
        with open(template_path, 'w') as f:
            f.write(content)
        return template_path
    
    def test_template_info_extraction(self):
        """Test template information extraction"""
        generator = TemplateDocGenerator(self.test_dir)
        info = generator.extract_template_info(self.test_template)
        
        assert info['name'] == 'documented_template.j2'
        assert info['extends'] == 'base.j2'
        assert len(info['documentation']) > 0
        assert len(info['blocks']) > 0
        assert len(info['macros']) > 0
        assert len(info['includes']) > 0
        assert 'server_name' in info['variables']
        assert 'port' in info['variables']
    
    def test_markdown_generation(self):
        """Test markdown documentation generation"""
        generator = TemplateDocGenerator(self.test_dir)
        info = generator.extract_template_info(self.test_template)
        markdown = generator.generate_markdown_doc(info)
        
        assert '# Template: documented_template.j2' in markdown
        assert '### Variables' in markdown
        assert '### Blocks' in markdown
        assert '### Macros' in markdown
        assert '### Inheritance' in markdown
        assert 'base.j2' in markdown
        assert 'server_name' in markdown
        assert 'ssl_config' in markdown
    
    def test_documentation_generation(self):
        """Test full documentation generation process"""
        generator = TemplateDocGenerator(self.test_dir)
        generator.generate_docs_for_templates([self.test_template], self.doc_dir)
        
        # Check if documentation files were created
        assert os.path.exists(os.path.join(self.doc_dir, 'README.md'))
        assert os.path.exists(os.path.join(self.doc_dir, 'summary.json'))
        assert os.path.exists(os.path.join(self.doc_dir, 'documented_template.md'))
        
        # Check summary content
        with open(os.path.join(self.doc_dir, 'summary.json'), 'r') as f:
            summary = json.load(f)
        
        assert summary['total_templates'] == 1
        assert summary['successful_docs'] == 1
        assert len(summary['templates']) == 1

def test_integration():
    """Integration test for both validator and doc generator"""
    test_dir = tempfile.mkdtemp()
    
    # Create a comprehensive test template
    template_content = """
{# Comprehensive test template #}
{% extends 'common_templates/base.j2' %}

{% block header %}
{{ super() }}
# Additional header content
{% endblock %}

{% block configuration %}
# Server configuration
server_name {{ server_name | default('test-server') | e }}
port {{ port | default(8080) }}
workers {{ workers | default(4) }}

{% if ssl_enabled | default(false) %}
# SSL Configuration
ssl_certificate {{ ssl_cert_path | e }}
ssl_certificate_key {{ ssl_key_path | e }}
{% endif %}
{% endblock %}

{% macro upstream_server(name, host, port) %}
upstream {{ name }} {
    server {{ host }}:{{ port }};
}
{% endmacro %}

{% for upstream in upstreams | default([]) %}
{{ upstream_server(upstream.name, upstream.host, upstream.port) }}
{% endfor %}
"""
    
    template_path = os.path.join(test_dir, 'comprehensive_template.j2')
    with open(template_path, 'w') as f:
        f.write(template_content)
    
    # Test validation
    validator = TemplateValidator(test_dir)
    validation_results = validator.validate_templates([template_path])
    
    assert validation_results['summary']['total_templates'] == 1
    assert validation_results['summary']['valid_templates'] == 1
    
    # Test documentation generation
    generator = TemplateDocGenerator(test_dir)
    doc_dir = os.path.join(test_dir, 'docs')
    generator.generate_docs_for_templates([template_path], doc_dir)
    
    assert os.path.exists(os.path.join(doc_dir, 'comprehensive_template.md'))
    
    # Verify documentation content
    with open(os.path.join(doc_dir, 'comprehensive_template.md'), 'r') as f:
        doc_content = f.read()
    
    assert 'comprehensive_template.j2' in doc_content
    assert 'server_name' in doc_content
    assert 'upstream_server' in doc_content
    assert 'common_templates/base.j2' in doc_content

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
